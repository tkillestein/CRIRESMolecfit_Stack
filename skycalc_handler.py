#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:31:02 2019

@author: phugxs
"""

#### make a temp directory
#### create a fully populated skycalc input and almanac field
#### run skycalc-cli and obtain output fits file for each detector


import os, glob
from astropy.io import fits


filename = "test_clean.fits"

#### make skycalc_temp directory
if os.path.isdir("skycalc_temp") == True:
    flist = glob.glob("skycalc_temp/*")
    for f in flist:
        os.remove(f)
else:
    os.mkdir("skycalc_temp")


### Read in key parameters from ESO fits files
hdu = fits.open(filename)
header = hdu[0].header
hdu.close()

### almanac, need ra, dec, observatory, timestamp
ra = hdu[0].header["RA"]
dec = hdu[0].header["DEC"]
obs = "paranal"
date = hdu[0].header["DATE"]

alm_input = open("skycalc_temp/input_almanac.txt", "w+")
alm_input.write("ra : " + str(ra) + "\n")
alm_input.write("dec : " + str(dec) + "\n")
alm_input.write("observatory : " + obs + "\n")
alm_input.write("date : " + str(date) + "\n")
alm_input.close()


#### Now generate files across the detector range
sk_input = open("skycalc_temp/input_skycalc.txt", "w+") 
wmin = header["HIERARCH ESO INS WLEN STRT1"] - 5
wmax = header["HIERARCH ESO INS WLEN END4"] + 5
res = (wmax - wmin) / 4096

sk_input.write("wmin : " + str(wmin) + "\n")
sk_input.write("wmax : " + str(wmax) + "\n")
sk_input.write("wdelta: " + str(res) + "\n")
sk_input.write("msolflux: 130.0" +"\n") # implicitly set the default value, so almanac doesn't make it NaN
sk_input.close()


cmd = "skycalc_cli" + " -a skycalc_temp/input_almanac.txt" + " -o output_tellur.fits" + " -i skycalc_temp/input_skycalc.txt"

os.system(cmd)

