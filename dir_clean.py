from shutil import rmtree
from os import remove, path
import glob

### delete calfiles

folderlist = ["darks", "flats", "flatdarks"]

for folder in folderlist:
    if path.exists(folder) == True:
        rmtree(folder)
    else:
        continue

### delete output from crires_pipeline
for f in glob.glob("std/crires*"):
    remove(f)

remove("std/esorex.log")
remove("std/input_std.txt")

