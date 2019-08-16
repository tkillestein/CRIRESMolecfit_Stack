import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import median_absolute_deviation

hdu = fits.open("000.fits")
spec = hdu[4].data

wav = spec["Wavelength"]
flx = spec["EXTRACTED_OPT"]

plt.plot(wav, flx)

newspc = []

for i in range(int(1024/16)):
    a = i*16
    b = (i+1)*16
    subwav = wav[a:b]
    subflx = flx[a:b]
    median = np.nanmedian(subflx)
    sigma = median_absolute_deviation(subflx)
    cleanmsk = np.logical_or(np.array(subflx) > 5*sigma + median, np.array(subflx) < 0)
    print("Threshold: %s, Max: %s" % (2*sigma + median, np.max(subflx)))

    for i in range(len(subflx)):
        if cleanmsk[i] == True:
            subflx[i] = 'NaN'

    newspc.extend(subflx)


plt.plot(wav, np.array(newspc))
plt.show()
