import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
hdu_model = fits.open("031_proc_out_fit.fits")
model_data = hdu_model[1].data
hdu_model.close()

dets = [2, 3]

fig, ax = plt.subplots(1, 2, sharey = True, figsize=(8,3), dpi=150)

for d in dets:
    idx = dets.index(d)
    model_mask = np.logical_and(model_data["mflux"] > 0, model_data["chip"] == d)
    data_mask = np.logical_and(model_data["chip"] == d, model_data["weight"] > 0)
    ax[idx].plot(model_data['mlambda'][model_mask], model_data["mflux"][model_mask], c='r', lw=0.9, zorder=20)
    ax[idx].plot(model_data["lambda"][data_mask], model_data["flux"][data_mask], c='k')
    ax[idx].set_xlim(np.min(model_data["lambda"][data_mask]), np.max(model_data["lambda"][data_mask]))
    xax_label = "Detector %s ($\mu$m)" % d
    ax[idx].set_xlabel(xax_label)

ax[0].set_ylabel("Flux")

fig.savefig("nicespectrum.png", bbox_inches='tight')
plt.show()
