from shutil import rmtree
from os import remove, path
import glob

### delete calfiles

folderlist = ["darks", "flats", "flatdarks", "masks", "output", "skycalc_temp"]

for folder in folderlist:
    if path.exists(folder) == True:
        rmtree(folder)
    else:
        continue

### delete output from crires_pipeline
for f in glob.glob("std/crires*"):
    remove(f)

pipeline_tempfiles = ["std/esorex.log", "std/input_std.txt"]

for ptemp in pipeline_tempfiles:
    if path.exists(ptemp):
        remove(ptemp)
