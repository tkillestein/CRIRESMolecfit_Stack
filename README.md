# PyCRIRES+molecfit pipeline

Code to automatically process and fit CRIRES spectra of telluric standard stars.
When provided with a set of raw spectra, the code:
* Automatically finds matching calibration frames from the ESO Archive
* Produces input files for the CRIRES pipeline, and calls esorex to produce the frames
* Removes bad pixels and wavelength-calibrates the data
* Creates input files for and runs `molecfit` to determine column densities of greenhouse gases.

### Dependencies:
molecfit
molecfit/bin must be in fit_path

CRIRES pipeline

astroquery

ESO skycalc

numpy and astropy

### Installing:
