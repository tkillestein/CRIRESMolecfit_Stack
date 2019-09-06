# Initialise script for the CRIRES stack
# This only works for csh at the moment.

echo "Setting up directory structure"
mkdir -p calfiles
mkdir -p raw/example_set/obj
mkdir -p proc

echo "Grabbing calibration files"
cd calfiles
wget -nc ftp://ftp.eso.org/pub/dfo/CRIRES/fits/CR_PDCO_120123A_ALL.fits
wget -nc ftp://ftp.eso.org/pub/dfo/CRIRES/fits/CR_PDCO_110409A_ALL.fits

cd ../

if (`where molecfit` == "") then
  echo "Molecfit not found in PATH, exiting setup."
  exit
endif

echo "molecfit install detected"

if (`where esorex` == "") then
  echo "Esorex not found in PATH, exiting setup."
  exit
endif

echo "esorex install detected"
echo "Setup complete with no errors!"
