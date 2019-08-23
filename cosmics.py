import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import median_absolute_deviation
from scipy.ndimage import gaussian_filter1d

### Move this to utils?

hdu = fits.open("000.fits")
spec = hdu[2].data
wav = spec["Wavelength"]
flx = spec["EXTRACTED_OPT"]
plt.plot(wav, flx)

def median_filter(flx, chunk_size, coldpix):
# Init new spectrum
    newspc = []
    # Chunk size *MUST* be divisor of spectrum length.
    if len(flx) % chunk_size != 0:
        raise("Chunk size not factor of spectrum length")

    for i in range(int(len(wav)/chunk_size)):
        a = i*chunk_size
        b = (i+1)*chunk_size
        ### Split the spectrum into 16 pixel chunks
        subflx = flx[a:b]
        # Compute the median and MAD (robust stdev) for each chunk
        median = np.nanmedian(subflx)
        sigma = median_absolute_deviation(subflx)
        # Pixel more than 5 MAD away from the median get masked
        if coldpix == True:
            cleanmsk = np.logical_or(np.array(subflx) > 5*sigma + median, np.array(subflx) < median - 7*sigma)
        else:
            cleanmsk = np.array(subflx) > 5*sigma + median
        subflx[cleanmsk == True] = 'NaN' #np.median(subflx[cleanmsk == False])
        #print("Threshold: %s, Max: %s" % (2*sigma + median, np.max(subflx)))
        # Rebuild the spectrum chunk by chunk
        newspc.extend(subflx)
    return np.array(newspc)


for i in range(10):
    newspc = median_filter(flx, 128, False)
    newspc = median_filter(newspc, 4, True)


plt.plot(wav, np.array(newspc))
plt.show()
