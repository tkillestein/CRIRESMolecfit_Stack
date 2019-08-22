import os, glob
import numpy as np
from astropy.stats import median_absolute_deviation

def mkdir_safe(dirname):
    if os.path.isdir(dirname) == True:
        flist = glob.glob(dirname + "/*")
        for f in flist:
            os.remove(f)
    else:
        os.mkdir(dirname)


def cosmic_filter(wav, flx):
    newspc = []
    # Chunk size *MUST* be divisor of spectrum length.
    chunk_size = 16

    for i in range(int(len(wav)/chunk_size)):
        a = i*chunk_size
        b = (i+1)*chunk_size
        ### Split the spectrum into (chunk_size) pixel chunks
        subflx = flx[a:b]
        # Compute the median and MAD (robust stdev) for each chunk
        median = np.nanmedian(subflx)
        sigma = median_absolute_deviation(subflx)
        # Pixel more than 5 MAD away from the median get masked
        cleanmsk = np.logical_or(np.array(subflx) > 5*sigma + median, np.array(subflx) < median - 5*sigma)
        subflx[cleanmsk == True] = 'NaN' #np.median(subflx[cleanmsk == False])
        #print("Threshold: %s, Max: %s" % (2*sigma + median, np.max(subflx)))
        # Rebuild the spectrum chunk by chunk
        newspc.extend(subflx)
    return np.array(newspc)
