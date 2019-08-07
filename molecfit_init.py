#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 14:49:57 2019

@author: phugxs
"""

import os, glob, subprocess
from astropy.io import fits

### create masks folder
    ### create fit range file automatically
    ### create pixel mask file
    ### create wavelength mask file
    
### create molecfit config file
    ### automatically plumb filepaths
    ### possibly using a template



def mkdir_safe(dirname):    
    if os.path.isdir(dirname) == True:
        flist = glob.glob(dirname + "/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir(dirname)
        

mkdir_safe("masks")
mkdir_safe("output")

######## sort out the masks


### Write standard CRIRES detector edgemasks
### See molecfit tutorial
pixmask = open("masks/pixmask.txt", "w+")
pixmask.write("0001 0020 \n")
pixmask.write("1005 1044 \n")
pixmask.write("2029 2068 \n")
pixmask.write("3053 3112 \n")
pixmask.write("4057 4096 \n")
pixmask.close()

wavmask = open("masks/wavmask.txt", "w+")
wavmask.write(" ")
wavmask.close()

### Write the fit range to file
### Use FITS header to get relevant wavelength ranges

#detectors = input("Which detector(s)? \nType numbers with no spaces between \n")
#detchoice = list(set(list(detectors)))

detchoice = ["1", "2", "3", "4"]



filename = "test.fits"
frame = fits.open(filename)

fitmask = open("masks/fitmask.txt", "w+")

for det in detchoice:
    if det == "1":
        wav = frame[int(det)].data["WAVELENGTH"] * 0.001
        fitmask.write(str(wav[20]) + " " + str(wav[1020]) + "\n")

    if det == "2":
        wav = frame[int(det)].data["WAVELENGTH"] * 0.001
        fitmask.write(str(wav[20]) + " " + str(wav[1020]) + "\n")
        
    if det == "3":
        wav = frame[int(det)].data["WAVELENGTH"] * 0.001
        fitmask.write(str(wav[20]) + " " + str(wav[1020]) + "\n")
    
    if det == "4":
        wav = frame[int(det)].data["WAVELENGTH"] * 0.001
        fitmask.write(str(wav[20]) + " " + str(wav[1020]) + "\n")

fitmask.close()


#### Write the template parameter file 
# Need to change:
#   path to each mask
#   path to the output dir
#   path to the input frame
#   choice of molecules.

parent_path = os.getcwd()
file_path = os.path.join(parent_path, filename)
pix_path = os.path.join(parent_path, "masks/pixmask.txt")
wav_path = os.path.join(parent_path, "masks/wavmask.txt")
fit_path = os.path.join(parent_path, "masks/fitmask.txt")
out_path = os.path.join(parent_path, "output")
data_path = os.path.join(parent_path, filename)


template = open("template.par", "r")
data = template.readlines()
template.close()


data[5] = "filename: " + str(file_path) + "\n"
data[34] = "wrange_include: " + str(fit_path) + "\n"
data[38] = "wrange_exclude: " + str(wav_path) + "\n"
data[42] = "prange_exclude: " + str(pix_path) + "\n"
data[47] = "output_dir: " + str(out_path) + "\n"
data[52] = "output_name: " + str(filename[:-5]) + "_out"  + "\n"

output = open("output.par", "w+")
output.writelines(data)
output.close()
frame.close()

outfile_path = os.path.join(parent_path, "output.par")

print("Starting molecfit call")
os.system("cd ~/molecfit && ./bin/molecfit " + str(outfile_path))
#os.popen("cd ~/molecfit && ./bin/molecfit " + str(outfile_path)).read()

#### shell=True is insecure, be careful with outfile_path!

#with subprocess.Popen(["cd ~/molecfit && ./bin/molecfit " + str(outfile_path)], stdout=PIPE, shell=True) as proc:
#    print(proc.stdout.read())
