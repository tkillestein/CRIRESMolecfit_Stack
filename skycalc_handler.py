import os, glob
from astropy.io import fits
import numpy as np

def grab_tellurics(fitsheader):
    #### make skycalc_temp directory
    if os.path.isdir("skycalc_temp") == True:
        flist = glob.glob("skycalc_temp/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir("skycalc_temp")

    ### Read in key parameters from ESO fits files
    ### almanac, need ra, dec, observatory, timestamp
    ra = fitsheader["RA"]
    dec = fitsheader["DEC"]
    date = fitsheader["DATE"]
    airm = 0.5*(fitsheader["HIERARCH ESO TEL AIRM END"] + fitsheader["HIERARCH ESO TEL AIRM END"])
    wmin = fitsheader["HIERARCH ESO INS WLEN STRT1"] - 5 # 5 nm buffer to allow for jitter.
    wmax = fitsheader["HIERARCH ESO INS WLEN END4"] + 5
    res = 0.005

    #### Now generate files across the detector range
    sk_input = open("skycalc_temp/input_skycalc.txt", "w+")
    sk_input.write("observatory : paranal \n")
    sk_input.write("wmin : %s \n" % (np.floor(wmin)))
    sk_input.write("wmax : %s \n" % (np.ceil(wmax)))
    sk_input.write("wdelta : %s \n" % (res))
    sk_input.write("airmass : %s \n" % (airm))
    sk_input.close()

    ### Run the call to Skycalc CLI, outputting the telluric spectrum in the current dir.
    cmd = "skycalc_cli" + " -o telluric_model.fits" + " -i skycalc_temp/input_skycalc.txt"
    os.system(cmd)
