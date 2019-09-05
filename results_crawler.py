import os, glob
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.io import fits
from scipy.signal import savgol_filter
from utils import parse_molecfits, parse_fitsheader, mkdir_safe


framelist = sorted(glob.glob("proc/*/*.fits"))
parfilelist = sorted(glob.glob("proc/*/output/*.res.fits"))

print("%s files found!" % len(framelist))

obs_times = []
airmass = []
chisqs = []
wlens = []
ch4_abun = []
e_ch4_abun = []

for i in range(len(parfilelist)):
    t, X, wlen, name = parse_fitsheader(framelist[i])
    ch4, e_ch4, h2o, e_h2o, chisq = parse_molecfits(parfilelist[i])
    obs_times.append(t)
    airmass.append(X)
    chisqs.append(chisq)
    ch4_abun.append(ch4)
    e_ch4_abun.append(e_ch4)

plt.errorbar(obs_times[:len(ch4_abun)], ch4_abun, e_ch4_abun, fmt='.k')

#datablock = np.column_stack((obs_times, airmass, CH4_abun, CH4_err, H2O_abun, H2O_err))
#np.savetxt("20110414_ThetaCrt.txt", datablock)
plt.show()
