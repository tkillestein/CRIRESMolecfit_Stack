import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import median_absolute_deviation

### Move this to utils?

hdu = fits.open("000.fits")
spec = hdu[1].data
wav = spec["Wavelength"]
flx = spec["EXTRACTED_OPT"]
plt.plot(wav, flx)



def cosmic_filter(flx):
# Init new spectrum
    newspc = []

    # Chunk size *MUST* be divisor of spectrum length.
    chunk_size = 8

    for i in range(int(len(wav)/chunk_size)):
        a = i*chunk_size
        b = (i+1)*chunk_size
        ### Split the spectrum into 16 pixel chunks
        subflx = flx[a:b]
        # Compute the median and MAD (robust stdev) for each chunk
        median = np.nanmedian(subflx)
        sigma = median_absolute_deviation(subflx)
        # Pixel more than 5 MAD away from the median get masked
        cleanmsk = np.logical_or(np.array(subflx) > 5*sigma + median, np.array(subflx) < 0)
        subflx[cleanmsk == True] = 'NaN' #np.median(subflx[cleanmsk == False])
        #print("Threshold: %s, Max: %s" % (2*sigma + median, np.max(subflx)))
        # Rebuild the spectrum chunk by chunk
        newspc.extend(subflx)
    return newspc

newspc = cosmic_filter(flx)
# Check plot
plt.plot(wav, np.array(newspc))
plt.show()
