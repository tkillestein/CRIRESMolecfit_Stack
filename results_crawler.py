import os, glob
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.io import fits
from scipy.signal import savgol_filter

def mkdir_safe(dirname):
    if os.path.isdir(dirname) == True:
        flist = glob.glob(dirname + "/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir(dirname)

mkdir_safe("fit_results")

os.system("find ./proc -name \"*fit.res\" -type f -exec cp {} ./fit_results \;")

### get date and time:
obs_times = []
airmass = []
filelist = sorted(glob.glob("proc/*/*.fits"))
#print(filelist)
#print(filelist)
for frame in filelist:
    temphead = (fits.open(frame))[0].header
    obs_times.append(Time(temphead["DATE-OBS"]).mjd)
    airmass.append(0.5*(temphead["HIERARCH ESO TEL AIRM START"] + temphead["HIERARCH ESO TEL AIRM END"]))


filelist = sorted(glob.glob("fit_results/*"))
print("%s files found!" % len(filelist))

H2O_abun = []
H2O_err = []

CH4_abun = []
CH4_err = []


for f in filelist:
    file = open(f, "r")
    data = file.readlines()
    file.close()

    print("### %s ###" % (filelist.index(f)))

    CH4_temp = data[-4]
    H2O_temp = data[-6]

    try:
        CH4_abun.append(np.float(CH4_temp[5:15]))
        CH4_err.append(np.float(CH4_temp[18:-1]))
        print("CH4: " + CH4_temp[5:15] + "\t" + CH4_temp[18:-1])
    except:
        CH4_err.append(0.0014)

    try:
        H2O_abun.append(np.float(H2O_temp[5:15]))
        H2O_err.append(np.float(H2O_temp[18:-1]))
        print("H2O: " + H2O_temp[5:15] + "\t" + H2O_temp[18:-1])
    except:
        H2O_err.append(0.7)

#datablock = np.column_stack((obs_times, airmass, CH4_abun, CH4_err, H2O_abun, H2O_err))
#np.savetxt("consolidated_fits/20110414_extract.txt", datablock)

plt.errorbar(obs_times[:len(H2O_abun)], H2O_abun, H2O_err, fmt='.k')
plt.xlabel("MJD")
plt.ylabel("H2O abundance (ppm)")
plt.show()
plt.errorbar(obs_times[:len(CH4_abun)], 1000*np.array(CH4_abun), 1000*np.array(CH4_err), fmt='.k')
plt.xlabel("MJD")
plt.ylabel("CH4 abundance (ppb)")
plt.show()
plt.errorbar(CH4_abun, H2O_abun, xerr=CH4_err, yerr=H2O_err, fmt='.k')
plt.ylabel("H2O abundance (ppm)")
plt.xlabel("CH4 abundance (ppm)")
plt.show()

plt.errorbar(airmass[:len(H2O_abun)], H2O_abun, H2O_err, fmt='.k')
plt.xlabel("X")
plt.ylabel("H2O abundance (ppm)")
plt.show()

plt.errorbar(airmass[:len(CH4_abun)], CH4_abun, CH4_err, fmt='.k')
plt.xlabel("X")
plt.ylabel("CH4 abundance (ppm)")
plt.show()

fig, ax = plt.subplots(2, 1)
plt.subplots_adjust(hspace=0.5)
ax[0].hist(H2O_abun, bins=15)
ax[0].set_xlabel("H2O abundance (ppm)")
ax[1].hist(CH4_abun, bins=15)
ax[1].set_xlabel("CH4 abundance (ppm)")
plt.show()
