# PyCRIRES+molecfit pipeline

Code to automatically process and fit CRIRES spectra of telluric standard stars.
When provided with a set of raw spectra, the code:
* Automatically finds matching calibration frames from the ESO Archive
* Produces input files for the CRIRES pipeline, and calls esorex to produce the frames
* Removes bad pixels and wavelength-calibrates the data
* Creates input files for and runs `molecfit` to determine column densities of greenhouse gases.

### Dependencies:
molecfit
molecfit/bin must be in PATH
Utility scripts like `results_crawler.py` use a modified molecfit code to give higher precision - contact me about this.

CRIRES pipeline

* Python dependencies are `astroquery` and `skycalc-cli`, install with your preferred method.


### Running the code:

* Under `raw/`, create a folder for each observation block - each block should be same exposure time, wavelength
* Inside each observation block directory, put the raw frames to be processed in a subdirectory `obj/`
* From the top-level directory run `python process_frames.py`
* Currently, the calibration frame grabber, pipeline bootstrapper, and wavelength calibration routines run in sequence on each folder, then molecfit runs across N-1 cores.

