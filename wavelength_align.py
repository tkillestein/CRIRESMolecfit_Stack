#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 16:30:27 2019

@author: phugxs
"""

import numpy as np
from astropy.io import fits
import os

def CRIRES_remove_bad_pix(filename):

    testdata = fits.open(filename)
    new_fname = filename[:-5] + "_clean.fits"
    
    if os.path.exists(new_fname):
        os.remove(new_fname)
    
    for i in range(1,5):
        #wav = testdata[i].data["Wavelength"]
        rect = testdata[i].data["Extracted_RECT"]
        opt = testdata[i].data["Extracted_OPT"]
        
        #plt.figure(dpi=120)
        #plt.plot(wav, opt)
        #plt.ylim(np.percentile(opt, 1)*0.7, np.percentile(opt, 99)*1.3)
        
        cosmic_filter = np.abs(rect/opt - 1)
        mask = np.logical_or(cosmic_filter > 0.05, opt == 0)
        mask = np.logical_or(mask, opt > 4000)
        
            
        print(str(np.sum(mask)) + " bad pixels cleaned")
        
        opt_clean = opt
        
        for j in range(len(opt_clean)):
            if mask[j] == True:
                opt_clean[j] = np.nan
        
        #plt.figure(dpi=120)
        #plt.plot(wav, opt_clean)
    
        testdata[i].data["Extracted_OPT"] = opt_clean


    testdata.writeto(new_fname)

CRIRES_remove_bad_pix("test.fits")
