import os, glob, subprocess
from multiprocessing import Pool, cpu_count
from astropy.io import fits
import time
import numpy as np


def mkdir_safe(dirname):
    if os.path.isdir(dirname) == True:
        flist = glob.glob(dirname + "/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir(dirname)

proc_path = "20110414_proc"

folders = sorted(glob.glob(proc_path + "/*"))
#print(folders)

parent_path = os.getcwd()

def molecfit_run(f):
    os.chdir(f)
    current_path = os.getcwd()

    mkdir_safe("output")
    mkdir_safe("masks")

    pixmask = open("masks/pixmask.txt", "w+")
    pixmask.write("0001 0020 \n")
    pixmask.write("1005 1044 \n")
    pixmask.write("2029 2068 \n")
    pixmask.write("3053 3112 \n")
    pixmask.write("4057 4096 \n")
    pixmask.close()

    pix_path = os.path.join(current_path, "masks/pixmask.txt")

    wavmask = open("masks/wavmask.txt", "w+")
    wavmask.write(" ")
    wavmask.close()
    wav_path = os.path.join(current_path, "masks/wavmask.txt")

    ### Write the fit range to file
    ### Use FITS header to get relevant wavelength ranges

    #detectors = input("Which detector(s)? \nType numbers with no spaces between \n")
    #detchoice = list(set(list(detectors)))

    detchoice = ["1", "2", "3", "4"]

    filename = glob.glob("*.fits")[0]
    file_path = os.path.join(current_path, filename)
    frame = fits.open(filename)

    fitmask = open("masks/fitmask.txt", "w+")
    fit_path = os.path.join(current_path, "masks/fitmask.txt")
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

    template = open(os.path.join(parent_path, "template.par"), "r")
    data = template.readlines()
    template.close()

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

    outfile_path = os.path.join(current_path, "output/output.par")
    print(outfile_path)
    print("Starting molecfit call")
    #os.system("molecfit " + str(outfile_path))
    os.system("cd ~/mod_molecfit && ./bin/molecfit " + str(outfile_path))

    os.chdir(parent_path)
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
