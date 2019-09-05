from wcal_code import wcal
from skycalc_handler import grab_tellurics
from astropy.io import fits

filename = "000.fits"
hdu = fits.open(filename)
header = hdu[0].header

grab_tellurics(header)
wcal(filename, "telluric_model.fits")
