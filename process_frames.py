import os, glob, shutil
from astropy.io import fits
import time

### Stages of the pipeline.
from cal_selector import grab_calfiles
from crires_pipeline_bootstrapper import calibrate_frames
from skycalc_handler import grab_tellurics
from utils import mkdir_safe
from wcal_code import wcal
from molecfit_bootstrapper_parallel import molecfit_run

BASEPATH = os.getcwd()

folders = glob.glob("raw/*")
print(folders)

for f in sorted(folders):
    os.chdir(f)
    grab_calfiles()
    calibrate_frames()

    ### Read FITS header from crires_spec_jitter_extracted.FITS
    temphdu = fits.open("obj/crires_spec_jitter_extracted.fits")
    header = temphdu[0].header
    temphdu.close()
    ### Pass this to the telluric grabber
    grab_tellurics(header)
    ### Run wavelength alignment
    wcal("obj/crires_spec_jitter_extracted.fits", "telluric_model.fits")
    ### Copy processed file to proc/
    proc_path = os.path.join(BASEPATH, "proc", f[4:])
    mkdir_safe(proc_path)
    shutil.copy("obj/crires_spec_jitter_extracted_proc.fits", proc_path + "/%s%s" % (f[4:], ".fits"))

    os.chdir(BASEPATH)
    print("Folder %s of %s complete" % (sorted(folders).index(f) + 1, len(folders)))

#### Molecfit executed seperately to allow parallel processing - waits til all this is doneself.

folders = glob.glob("proc/*")

for f in folders:
    molecfit_run(f)
