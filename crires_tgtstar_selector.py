### A big, slow, ugly, autonomous script to grab entire years of data from the CRIRES Archive
### Apply cuts based on time, wavelength, spectral type, windowing, etcself.
### Auto-downloads valid filelist

from astroquery.simbad import Simbad
from astroquery.eso import Eso
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.table import Table
from astropy.time import Time
import numpy as np
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from astropy.io import fits, ascii
import os, glob, shutil


def mkdir_safe(dirname):
    '''
    Check if directory exists - if it doesn't, make it, if it does, clear it out
    '''
    if os.path.isdir(dirname) == True:
        flist = glob.glob(dirname + "/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir(dirname)

handler = Simbad()
handler.add_votable_fields("mk", "flux(K)", "v*")

### Forces only the closest match to be returned
handler.ROW_LIMIT = 1

crires_cat = Table.read("crires_fulldb.csv")
### Select frames within a given time period
date_init, date_final = (Time("2012-01-01"), Time("2012-12-31"))
timemask = np.logical_and(crires_cat['DATE OBS'] > date_init, crires_cat['DATE OBS'] < date_final)
print("Filter by time: %s of %s targets remain" % (np.sum(timemask), len(timemask)))

### Subset of frames between 2 and 2.3 micron
wavmin, wavmax = (1500, 1600)
wavmask = np.logical_and(crires_cat['INS WLEN CWLEN'] > wavmin, crires_cat['INS WLEN CWLEN'] < wavmax)

initmask = np.logical_and(wavmask, timemask)
print("Filter by wavelength: %s of %s targets remain" % (np.sum(initmask), len(initmask)))

cat_subset = crires_cat[initmask]
#print(cat_subset.colnames)

spectype = []
varstat = []
#Kmag = []

### Extract galactic coordinates and read spectral type from each
### Must be as a vectorised query

for c in tqdm(cat_subset['Target Ra Dec'], desc="Querying SIMBAD:", ascii=True):
    coord = SkyCoord(c, unit=(u.hourangle, u.deg))
    results_table = handler.query_region(coord, radius=1*u.arcmin)
    spectype.append(results_table[0]['MK_Spectral_type'].decode())
    varstat.append(results_table[0]['V__vartyp'])
    #Kmag.append(results_table[0]['FLUX_K'])
    time.sleep(0.3) # Don't remove this - here to comply with SIMBAD rate limit

print(varstat)

### If it's G K M or otherwise, reject

def spectral_type_cut(entry):
    if any(["O" in entry, "B" in entry, "A" in entry, "F" in entry]) == True:
        return True
    else:
        return False

typemask = [spectral_type_cut(x) for x in spectype]

new_subset = cat_subset[typemask]
print("Filter by spectral_type: %s of %s targets remain" % (np.sum(typemask), len(initmask)))

science_frames = new_subset["DP.ID"]

eso = Eso()
eso.login("tkillestein")

### Mask all that have non-512 window
heads = eso.get_headers(science_frames)

goodmsk = heads['HIERARCH ESO DET WINDOW NY'] == 512
print("Filter by windowing: %s of %s targets remain" % (np.sum(goodmsk), len(initmask)))

check_calib_list = heads[goodmsk]

final_frames = []
frames_rejected = 0

for head in tqdm(check_calib_list, ascii=True, desc="Checking availability of calfiles"):
    prop_ID = head["HIERARCH ESO OBS PROG ID"]
    date = Time(head["DATE-OBS"])
    sci_exp = head["EXPTIME"]
    stime = date
    etime = date + 12*u.hour
    win_size = head["HIERARCH ESO DET WINDOW NY"]
    sci_wav = head["HIERARCH ESO INS WLEN CWLEN"]
    #print("Querying ESO Archive")
    flat_table = eso.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value ,'dp_type':'FLAT', 'ins_wlen_cwlen':sci_wav})
    dark_table = eso.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':sci_exp})

    try:
        flat_head = eso.get_headers(flat_table["DP.ID"])
        mask = flat_head["HIERARCH ESO DET WINDOW NY"] != win_size
        flat_table = flat_head[~mask]
        flat_exp_time = np.max(flat_table["EXPTIME"])
        dark_header = eso.get_headers(dark_table['DP.ID'])
        flatdark_table = eso.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':flat_exp_time})
        flatdark_header = eso.get_headers(flatdark_table["DP.ID"])

        final_frames.append(head["DP.ID"])
    except:
        print("Frame rejected: no flats found")
        frames_rejected += 1
        continue

if frames_rejected % 2 != 0:
    print("Error - odd number of frames rejected. \n Inspect files before continuing")


FILEPATH = "/storage/astro2/phugxs/crires_downloads/2012_co2"

mkdir_safe(FILEPATH)

science_files = eso.retrieve_data(final_frames)

for f in science_files:
    shutil.copy(f, FILEPATH)

print("Download complete!")


### Modified version of obs_pairer to produce input files for the pipeline
"date_target_exp_setnum" # folder structure