import glob, os
from astropy.io import fits
from astropy.time import Time
import numpy as np
from utils import return_frame_type


def calibrate_frames():

    os.chdir("darks")
    filelist = glob.glob("*")

    ### Make the msater dark
    f = open("input_dark.txt", "w+")
    for fname in filelist:
        f.write(str(fname) + " CAL_DARK" + "\n")
    f.close()
    ### System call to CRIRES pipeline to make the darks
    os.system("esorex crires_spec_dark input_dark.txt")

    #### Make the master dark flat
    os.chdir("../flatdarks")
    filelist = glob.glob("*")
    f = open("input_flatdark.txt", "w+")

    for fname in filelist:
        f.write(str(fname) + " CAL_DARK" + "\n")
    f.close()

    os.system("esorex crires_spec_dark input_flatdark.txt")

    ####### Make the master flat
    os.chdir("../flats")
    filelist = glob.glob("*")
    f = open("input_flat.txt", "w+")

    for fname in filelist:
        f.write(str(fname) + " CAL_FLAT" + "\n")
        ### Add the previously made flatdark and non-lin coeffs.
        f.write("../flatdarks/crires_spec_dark.fits" + " CALPRO_DARK" + "\n")
        f.write("../../../calfiles/CR_PDCO_120123A_ALL.fits" + " COEFFS_CUBE" + "\n")
    f.close()
    os.system("esorex crires_spec_flat input_flat.txt")

    #### Make the science spectrum!
    os.chdir("../obj")
    filelist = glob.glob("*")

    f = open("input_std.txt", "w+")

    ### Input handling to handle flats with weird settings.
    ### This shouldn't be necessary now with better calframe grabbing,
    ### but kept in to prevent failure in the case of suboptimal cals.
    if os.path.isfile("../flats/crires_spec_flat_set03.fits") == True:
        flatpath = "../flats/crires_spec_flat_set03.fits"
        bpmpath = "../flats/crires_spec_flat_set03_bpm.fits"

    elif os.path.isfile("../flats/crires_spec_flat_set02.fits") == True:
        flatpath = "../flats/crires_spec_flat_set02.fits"
        bpmpath = "../flats/crires_spec_flat_set02_bpm.fits"

    elif os.path.isfile("../flats/crires_spec_flat_set01.fits") == True:
        flatpath = "../flats/crires_spec_flat_set01.fits"
        bpmpath = "../flats/crires_spec_flat_set01_bpm.fits"

    else:
        raise Exception("Couldn't find a suitable flatfield and BPM - did esorex run properly?")

    ### Setup input file for making the science frames
    for fname in filelist:
        obs_type = return_frame_type(fname)
        f.write(str(fname) + " " + str(obs_type) + "\n")
    f.write(flatpath + " CALPRO_FLAT" + "\n")
    f.write(bpmpath + " CALPRO_BPM" + "\n")
    f.write("../darks/crires_spec_dark.fits" + " CALPRO_DARK" + "\n")
    f.write("../../../calfiles/CR_PDCO_120123A_ALL.fits" + " COEFFS_CUBE" + "\n")
    f.close()

    os.system("esorex crires_spec_jitter input_std.txt")
    os.chdir("../")

    ### If esorex throws exceptions it'll terminate the script prematurely
    ### More robust would be something like checking if crires_spec_jitter_extracted.FITS exists.
    print("Calibration successful!")
