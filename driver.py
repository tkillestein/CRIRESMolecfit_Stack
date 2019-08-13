import os, glob

from cal_selector import grab_calfiles
from crires_pipeline_bootstrapper import calibrate_frames


######## Handle calibration files
BASEPATH = os.getcwd()


folders = glob.glob("raw/*")
print(folders)

for f in folders:
    os.chdir(f)
    #grab_calfiles()
    calibrate_frames()
    os.chdir(BASEPATH)
