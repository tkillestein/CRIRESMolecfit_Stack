#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import numpy as np
import glob, os, shutil
#import matplotlib.pyplot as plt
from astroquery.eso import Eso
from astropy.io import fits
from astropy.time import Time
import astropy.units as u

workingdir = os.getcwd()

handler = Eso()
handler.ROW_LIMIT = 10000
handler.login("tkillestein")


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


##### Password requested here

# Read the first FITS in the folder
filelist = glob.glob("std/*.fits")
temphdu = fits.open(filelist[0])
header = temphdu[0].header
print("FITS header loaded")

prop_ID = header["HIERARCH ESO OBS PROG ID"]
date = Time(header["DATE-OBS"])
sci_exp = header["EXPTIME"]
stime = date - 12*u.hour
etime = date + 12*u.hour

sci_wav = header["HIERARCH ESO INS WLEN CWLEN"]
print(prop_ID, sci_wav, date)

print("Querying ESO Archive")
flat_table = handler.query_instrument("crires", column_filters={'prog_id':prop_ID, 'stime':stime.value, 'etime':etime.value ,'dp_type':'FLAT', 'ins_wlen_cwlen':sci_wav})

try:
    flat_exp_time = flat_table["EXPTIME"][0]

except:
    print("No suitable calfiles found, widening matching time window")
    stime = date - 24*u.hour
    etime = date + 24*u.hour
    flat_table = handler.query_instrument("crires", column_filters={'prog_id':prop_ID, 'stime':stime.value, 'etime':etime.value ,'dp_type':'FLAT', 'ins_wlen_cwlen':sci_wav})

finally:
    flat_exp_time = flat_table["EXPTIME"][0]

flat_files = handler.retrieve_data(flat_table["DP.ID"])
print(flat_files)

for f in flat_files:
    shutil.move(f, "flats")

dark_table = handler.query_instrument("crires", column_filters={'prog_id':prop_ID, 'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':sci_exp})
dark_files = handler.retrieve_data(dark_table["DP.ID"])

for d in dark_files:
    shutil.move(d, "darks")

flatdark_table = handler.query_instrument("crires", column_filters={'prog_id':prop_ID, 'stime':stime.value, 'etime':etime.value, 'dp_type':'DARK', 'exptime':flat_exp_time})
flatdark_files = handler.retrieve_data(flatdark_table["DP.ID"])


for d in flatdark_files:
    shutil.move(d, "flatdarks")

print("Unpacking and moving!")

os.chdir("flats")
os.system("uncompress *.Z")

os.chdir("../flatdarks")
os.system("uncompress *.Z")

os.chdir("../darks")
os.system("uncompress *.Z")

print("Calibration selection complete!")
exit()


 
