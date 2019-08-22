import os, glob, shutil
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time

FILEPATH = "/storage/astro2/phugxs/crires_downloads/2012"
NEWPATH = "/storage/astro2/phugxs/crires_processed/2012"

filelist = glob.glob(FILEPATH + "/*.fits")

print("%s files detected" % (len(filelist)))

### Need some sort of table to list the frames, then select matching NAME, WAVELENGTH, and if sorted it should work.
dates = []
names = []
nods = []
wavs = []

for f in filelist:
    temphdu = fits.open(f)
    head = temphdu[0].header
    temphdu.close()
    date = head['DATE-OBS']
    obj = head['HIERARCH ESO OBS TARG NAME']
    nodstat = head['HIERARCH ESO SEQ NODPOS']
    wav = head['HIERARCH ESO INS WLEN CWLEN']
    #print(date, obj, wav, nodstat)
    dates.append(Time(date))
    names.append(obj)
    nods.append(nodstat)
    wavs.append(wav)

frametable = Table([filelist, dates, names, nods, wavs], names=('flist', 'date', 'obj', 'nodstate', 'wave'))

unique_tgts = list(set(names))

for u in unique_tgts:
    print("##### %s ######" % u)
    subset = frametable[frametable['obj'] == u]
    unique_wavs = list(set(list(subset['wave'])))
    for w in unique_wavs:
        #print("##### %s ######" % w)
        subsubset = subset[subset['wave'] == w]
        As = subsubset[subsubset['nodstate'] == 'A']
        As.sort('date')
        Bs = subsubset[subsubset['nodstate'] == 'B']
        Bs.sort('date')
        failstring = len(As) != len(Bs)

        if failstring == True:
            continue
        else:
            for i in range(len(As)):
                date = Time(As[i]['date'], out_subfmt='date')
                folderpath = "/%s_%s_%su_set%s/obj" % (date, u, int(w)/1000, i+1)
                basepath = NEWPATH + folderpath

                if not os.path.exists(basepath):
                    os.makedirs(basepath)

                Afile = As[i]['flist']
                Bfile = Bs[i]['flist']

                shutil.copy(Afile, basepath)
                shutil.copy(Bfile, basepath)
