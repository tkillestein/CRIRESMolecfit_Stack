#import numpy as np
import glob, os, shutil
import numpy as np
#import matplotlib.pyplot as plt
from astroquery.eso import Eso
from astropy.io import fits
from astropy.time import Time
import astropy.units as u

def grab_calfiles():
    workingdir = os.getcwd()
    handler = Eso()

    ### Set your username here!
    USERNAME = ""

    handler.ROW_LIMIT = 10000
    handler.login(USERNAME, store_password=True)

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

    mkdir_safe("flats")
    mkdir_safe("flatdarks")
    mkdir_safe("darks")

    # Read the first FITS in the folder
    filelist = glob.glob("obj/*.fits")
    print(os.getcwd())
    temphdu = fits.open(filelist[0])
    header = temphdu[0].header
    print("FITS header loaded")

    # Extract relevant query params from science frame
    prop_ID = header["HIERARCH ESO OBS PROG ID"]
    date = Time(header["DATE-OBS"])
    sci_exp = header["EXPTIME"]
    # Set start and end time of search - may need to tweak this manually to find the right calfiles.
    # Best to be generous with this window since need to find flats, darks, and flat-darks for the pipeline to run.
    stime = date
    etime = date + 18*u.hour
    win_size = header["HIERARCH ESO DET WINDOW NY"]
    sci_wav = header["HIERARCH ESO INS WLEN CWLEN"]
    #print(filelist[0], sci_wav, date)

    # Query flat frames - check they match
    print("Querying ESO Archive")
    flat_table = handler.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value ,'dp_type':'FLAT', 'ins_wlen_cwlen':sci_wav})
    flat_header = handler.get_headers(flat_table["DP.ID"])
    mask = flat_header["HIERARCH ESO DET WINDOW NY"] != win_size
    flat_table = flat_table[~mask]

    #### if flat_exp_time not all the same value, choose the highest one
    #### Download flat fields
    flat_exp_time = np.max(flat_table["EXPTIME"])
    flat_files = handler.retrieve_data(flat_table["DP.ID"])
    #print(flat_files)

    for f in flat_files:
        shutil.copy(f, "flats")

    #### Grab the dark frames matching the science exposure time
    dark_table = handler.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':sci_exp})
    dark_header = handler.get_headers(dark_table['DP.ID'])
    mask = dark_header["HIERARCH ESO DET WINDOW NY"] != win_size
    dark_table = dark_table[~mask]
    dark_files = handler.retrieve_data(dark_table["DP.ID"])

    for d in dark_files:
        shutil.copy(d, "darks")

    #### Grab darks matched to flat fields
    flatdark_table = handler.query_instrument("crires", column_filters={'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':flat_exp_time})
    flatdark_header = handler.get_headers(flatdark_table["DP.ID"])
    mask = flatdark_header["HIERARCH ESO DET WINDOW NY"] != win_size
    flatdark_table = flatdark_table[~mask]
    flatdark_files = handler.retrieve_data(flatdark_table["DP.ID"])

    for d in flatdark_files:
        shutil.copy(d, "flatdarks")

    print("Unpacking and moving!")

    ### Unpack all the files -- several possible commands for thisself.

    ### maximum compatibility use "gzip -d *.Z"
    ### pigz is a parallel gzip, but also it can't decompress in parallel apparently.
    ### if you want to use it despite this, "pigz -d *.Z"

    ### For maximum SPEED you could try "ls *.Z | parallel pigz -d" if you have GNU parallel installed.


    os.chdir("flats")
    os.system("pigz -d *.Z")

    os.chdir("../flatdarks")
    os.system("pigz -d *.Z")

    os.chdir("../darks")
    os.system("pigz -d *.Z")

    os.chdir("../")
    print("Calibration selection complete!")
