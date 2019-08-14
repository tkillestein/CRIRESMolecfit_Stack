import glob, os
from astropy.io import fits
from astropy.time import Time
import numpy as np

##### Make the master dark
def calibrate_frames():

    os.chdir("darks")
    filelist = glob.glob("*")

    def return_frame_type(fname):
        hdu = fits.open(fname)
        ftype = hdu[0].header["HIERARCH ESO DPR TECH"]
        if ftype == 'SPECTRUM,NODDING,OTHER' or ftype == 'SPECTRUM,NODDING':
            return "OBS_NOD"
        if ftype == "SPECTRUM,NODDING,JITTER":
            return "OBS_NOD_JIT"
        else:
            raise Exception("Observation type not matched, check FITS header matches tags above.")

    f = open("input_dark.txt", "w+")

    for fname in filelist:
        f.write(str(fname) + " CAL_DARK" + "\n")
    f.close()

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

    ######################
    for fname in filelist:
        f.write(str(fname) + " CAL_FLAT" + "\n")
        f.write("../flatdarks/crires_spec_dark.fits" + " CALPRO_DARK" + "\n")
        f.write("../../../calfiles/CR_PDCO_120123A_ALL.fits" + " COEFFS_CUBE" + "\n")
    f.close()

    os.system("esorex crires_spec_flat input_flat.txt")

    #### Make the science spectrum!

    os.chdir("../obj")
    filelist = glob.glob("*")

    f = open("input_std.txt", "w+")

    for fname in filelist:
        obs_type = return_frame_type(fname)
        f.write(str(fname) + " " + str(obs_type) + "\n")
        f.write("../flats/crires_spec_flat_set01.fits" + " CALPRO_FLAT" + "\n")
        f.write("../flats/crires_spec_flat_set01_bpm.fits" + " CALPRO_BPM" + "\n")
        f.write("../darks/crires_spec_dark.fits" + " CALPRO_DARK" + "\n")
        f.write("../../../calfiles/CR_PDCO_120123A_ALL.fits" + " COEFFS_CUBE" + "\n")
    f.close()


    #### This is the call to run esorex on the resultant frames
    os.system("esorex crires_spec_jitter input_std.txt")
    os.chdir("../")

    #### This block is here for when I chain all the scripts together, will prevent
    #### later steps trying to execute if the pipeline has failed
    print("Calibration successful!")
