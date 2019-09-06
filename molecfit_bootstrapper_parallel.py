import os, glob, subprocess
from multiprocessing import Pool, cpu_count
from astropy.io import fits
import time
import numpy as np
from utils import mkdir_safe

def molecfit_run(f):
    #### f is a directory output by the previous stages of the script
    parent_path = os.getcwd()
    os.chdir(f)
    current_path = os.getcwd()

    #### make dirs for file structure
    mkdir_safe("output")
    mkdir_safe("masks")

    #### Write out the pixel masks
    pixmask = open("masks/pixmask.txt", "w+")
    pixmask.write("0001 0020 \n")
    pixmask.write("1005 1044 \n")
    pixmask.write("2029 2068 \n")
    pixmask.write("3053 3112 \n")
    pixmask.write("4057 4096 \n")
    pixmask.close()

    pix_path = os.path.join(current_path, "masks/pixmask.txt")

    #### Make a wavelength mask file.
    wavmask = open("masks/wavmask.txt", "w+")
    wavmask.write(" ")
    wavmask.close()
    wav_path = os.path.join(current_path, "masks/wavmask.txt")

    #### Choose detectors to fit here - some combo of "1", "2", "3", "4"
    #### Although it doesn't matter, for consistency write in increasing order.
    detchoice = ["2", "3"]

    filename = glob.glob("*.fits")[0]
    file_path = os.path.join(current_path, filename)
    frame = fits.open(filename)

    #### Write out the fit ranges for each detector
    fitmask = open("masks/fitmask.txt", "w+")
    fit_path = os.path.join(current_path, "masks/fitmask.txt")

    #### This line sets the offset term for molecfit, it is intended to sit
    #### above the spectrum since molecfit seems to fit nicely with this.
    meanflux = 1.2*np.nanpercentile(frame[2].data["Extracted_OPT"], 90)

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
    frame.close()

    #### Read in the template file
    template = open(os.path.join(parent_path, "template.par"), "r")
    data = template.readlines()
    template.close()

    #### Write a modified template file to output.par
    out_path = os.path.join(current_path, "output")
    data[5] = "filename: " + str(file_path) + "\n"
    data[34] = "wrange_include: " + str(fit_path) + "\n"
    data[38] = "wrange_exclude: " + str(wav_path) + "\n"
    data[42] = "prange_exclude: " + str(pix_path) + "\n"
    data[47] = "output_dir: " + str(out_path) + "\n"
    data[52] = "output_name: " + str(filename[:-5]) + "_out"  + "\n"
    data[114] = "cont_const: %s\n" % (meanflux)

    output = open("output/output.par", "w+")
    output.writelines(data)
    output.close()

    #### Call molecfit executable on output file generated.
    outfile_path = os.path.join(current_path, "output/output.par")
    #print(outfile_path)
    print("Starting molecfit call")
    os.system("molecfit " + str(outfile_path))

    #### chdir back to the starting path ready to run again
    os.chdir(parent_path)

### This code left here as example on how to invoke multiprocessing
'''
tick = time.time()

THREAD_COUNT = cpu_count() - 2
print("Spawning %s threads" % (THREAD_COUNT))
### two summer students working on the cluster
### give them a core each

if __name__ == '__main__':
    pool = Pool(THREAD_COUNT)
    pool.map(molecfit_run, folders)

pool.close()

tock = time.time()
timespent = np.round((tock - tick)/60)


print("Time taken: %s mins with %d threads" % (timespent, THREAD_COUNT))
print("%d spectra successfully processed!" % (len(folders)))
'''
