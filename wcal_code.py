#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:25:14 2019

@author: mbrogi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 12:18:30 2019

@author: mbrogi
"""

import numpy as np
from scipy import interpolate
from astropy.io import fits
import matplotlib.pyplot as plt
import time as tim
import sys
import emcee
import corner

def mycc(fVec,gVec):
    N, = fVec.shape
    Id = np.ones(N)
    fVec -= (fVec @ Id) / N
    gVec -= (gVec @ Id) / N
    sf2 = fVec @ fVec
    sg2 = gVec @ gVec
    return ((fVec @ gVec) / np.sqrt(sf2*sg2))

''' Getting 2nd-order wlen solution given a triplet of pixel-wlen points '''
def get_wl_sol(y1,y2,y3):
    x1 = 255.
    x2 = 511.
    x3 = 767.
    aa = (y2-y1)/(x2-x1)
    bb = (y3-y1)/(x3-x1)
    dd = (x2+x1)/(x3-x2)
    c = (bb-aa)/(x3-x2)
    b = dd*(aa-bb)+aa
    a = y1 - b*x1 - c*x1**2.
    xx = np.arange(1024)
    return (a + b*xx + c*xx**2.)

''' Likelihood estimator '''
def get_logL(theta,cs_tell,spc):
    lam1, lam2, lam3 = theta
    wlGuess = get_wl_sol(lam1,lam2,lam3)
    fModel = interpolate.splev(wlGuess,cs_tell,der=0)
    iok = np.isfinite(spc)
    N = iok.sum()
    cc = mycc(spc[iok],fModel[iok])
    return (-0.5 * N * np.log(1.0 - cc**2.0))

''' Priors '''
def lnprior(theta, initPos):
    L1, L2, L3 = theta
    L01, L02, L03 = initPos
    if L01-1.5 < L1 < L01+1.5 and L02-1.5 < L2 < L02+1.5 and L03-1.5 < L3 < L03+1.5: return 0.0
    return -np.Inf

''' Likelihood computation '''
def lnprob(theta, initPos, cs_tell,spc):
    lp = lnprior(theta, initPos)
    if not np.isfinite(lp):
        return -np.inf
    logL = get_logL(theta,cs_tell,spc)
    return lp + logL

''' Actual MCMC run with parameter estimation '''
def run_emcee(initPos,initDeltas,cs_tell,spc,plot=False):
    nPar = len(initPos)
    nWalkers = 20
    chainLen = 1000
    nBurn = 500
    # Stuff for progress bar
    barW = 25
    n = 0
    sys.stdout.write("\r[{0}{1}]".format('#'*n, ' '*(barW-n)))
    tstart = tim.time()
    # Initialisation of MCMC
    pos = [initPos + initDeltas*np.random.randn(nPar) for i in range(nWalkers)]
    sampler = emcee.EnsembleSampler(nWalkers, nPar, lnprob, args=(initPos,cs_tell,spc))
    # Running the chains
    for iRun in range(25):
        pos, prob, state = sampler.run_mcmc(pos, chainLen//25)
        n = int((barW+1)*float(iRun+1)/25)
        sys.stdout.write("\r[{0}{1}]".format('#'*n, ' '*(barW-n)))
    tstop = tim.time()
    print('{:2.1f} s elapsed; acceptance {:0.3f}'.format(tstop-tstart,np.mean(sampler.acceptance_fraction)))
    l1 = np.median(sampler.chain[:,nBurn:,0].flatten())
    l2 = np.median(sampler.chain[:,nBurn:,1].flatten())
    l3 = np.median(sampler.chain[:,nBurn:,2].flatten())
    if plot:
        samples = sampler.flatchain[nBurn:,]
        corner.corner(samples, labels=["$\lambda_1$", "$\lambda_2$", "$\lambda_3$"],truths=[l1,l2,l3])
        plt.show()
    return l1,l2,l3

''' Fitting for wavelength, resolution, PWV, vsini at once '''
def wcal(filename, telluric_name):
    tel = fits.getdata(telluric_name)
    fTel = tel['trans']
    wTel = tel['lam']*1E3
    cs_tell = interpolate.splrep(wTel,fTel,s=0.0)
    wlen = np.load('../../wlsol_01.npy')     # Guess wavelengths
    no, nx = wlen.shape
    # Set starting parameters
    x1 = 255
    x2 = 511
    x3 = 767
    # Initialise vectors
    hdul = fits.open(filename)
    for io in range(no):
        print('Processing detector {:1}'.format(io+1))
        wlout = np.zeros(nx)
        d = hdul[io+1].data
        wlen = d['Wavelength']
        # Identify and mask bad pixels
        spc = d['Extracted_OPT']
        spcRect = d['Extracted_RECT']
        iok = np.isfinite(spc) * np.isfinite(spcRect)
        rat = np.zeros(1024)
        rat[iok] = spc[iok] / spcRect[iok] - 1
        rat[iok == False] = 'NaN'
        spc[np.isfinite(rat) == False] = 'NaN'
        spc[np.abs(rat) > 0.1] = 'NaN'
        # Additional correction for hot pixels affecting RECT and OPT equally
        newmask = np.logical_or(spc > 2500, spc < 0)
        spc[newmask] = 'NaN'
        #plt.plot(spc)
        #plt.show()
        l1 = wlen[x1]
        l2 = wlen[x2]
        l3 = wlen[x3]
        pars = (l1,l2,l3)
        deltas = (1E-3,1E-3,1E-3)
        ll1, ll2, ll3 = run_emcee(pars,deltas,cs_tell,spc,plot=False)
        wlout = get_wl_sol(ll1,ll2,ll3)
        d['WAVELENGTH'] = wlout
        hdul[io+1].data = d

    out_file = filename[:-5] + "_proc.fits"
    hdul.writeto(out_file,overwrite=True)
    return

#wcal()
