# CRIRES/Molecfit Stack V1.0

Code to automatically process and fit CRIRES spectra of telluric standard stars.
When provided with a set of raw spectra, the code:
* Automatically finds matching calibration frames from the ESO Archive
* Produces input files for the CRIRES pipeline, and calls esorex to produce the frames
* Removes bad pixels and wavelength-calibrates the data
* Creates input files for and runs `molecfit` to determine column densities of greenhouse gases.

### Dependencies:
##### molecfit
Install from <https://www.eso.org/sci/software/pipelines/skytools/molecfit> - GUI isn't required for this code.
For the scripting to work properly, add the INSTALL_DIR/bin directory containing the `molecfit` executable to PATH.

##### CRIRES Pipeline
Install from <http://www.eso.org/sci/software/pipelines/> - installing without `esoreflex` and `gasgano` is fine.
Add the INSTALL_DIR/bin directory containing the `esorex` executable to PATH also.

##### Python packages
`astroquery`, `skycalc-cli`, `tqdm`, and `emcee` - install with your preferred method.

##### pigz
Currently the code uses `pigz` for marginal improvements in speed when decompressing. If you don't have it/want to use it, see `cal_selector.py`  for code to swap to `gzip`.

### Install:
* The setup script included will grab the necessary calfiles, as well as set up the directory structure, dropping an example of how to format your input in /raw.
* In the code for `cal_selector.py`, set your username. On first run, the keychain will request to store your password. After first run, you shouldn't be prompted again.

### Running the code:
* Under `raw/`, create a folder for each observation block - each block should be same exposure time, wavelength
* Inside each observation block directory, put the raw frames to be processed in a subdirectory `obj/`
* From the top-level directory run `python process_frames.py`
* Currently, the calibration frame grabber, pipeline bootstrapper, and wavelength calibration routines run in sequence on each folder, then molecfit runs across N-1 cores.
* Note that each stage of the pipeline requires the previous one to have run successfully, so if the code crashes/fails to run, the next stage of the pipeline likely cannot find what it is looking for. Check the full documentation to find what is missing.

#### Known issues:
* In `calibrate_frames.py`, errors thrown by `esorex` will cause the code to crash. To fix: remove all sets that have already processed and remove the troublesome set, then re-run the code.
* molecfit has some sporadic segfaults for certain wavelength ranges. It's unclear why this happens for some datasets and not for others at the same wavelength range, further work needed. For now, tweak the wavelength ranges in `molecfit_bootstrapper_parallel.py`.
