import numpy as np
from matplotlib import pyplot

from PySDM import Formulae
from PySDM.physics import constants_defaults, si

npoints = 20

clim_ss = (0, 0.25)
nlev_ss = 11
clim_er = (-10, -3)
nlev_er = 8

kappas = np.linspace(0.1, 1.5, npoints)
dry_radii = np.logspace(np.log10(0.05 * si.um), np.log10(0.25 * si.um), npoints)
T = 300 * si.K
sgm = constants_defaults.sgm_w


def test_hygroscopicity_fierce_diagrams(plot=False):
    # arrange
    variants = ("KappaKoehler", "KappaKoehlerLeadingTerms")
    formulae = {}
    for variant in variants:
        formulae[variant] = Formulae(hygroscopicity=variant)

    # act
    S_crit = {k: np.empty((kappas.size, dry_radii.size)) for k in variants}
    for i, kappa in enumerate(kappas):
        for j, dry_radius in enumerate(dry_radii):
            for variant in variants:
                r_cr = formulae[variant].hygroscopicity.r_cr(
                    kappa, dry_radius**3, T, sgm
                )
                S_crit[variant][i, j] = formulae[variant].hygroscopicity.RH_eq(
                    r_cr, T, kappa, dry_radius**3, sgm
                )

    # plot
    fig, axs = pyplot.subplots(3, 1, figsize=(5, 15))
    x, y = dry_radii / si.nm, kappas
    for i, variant in enumerate(variants):
        mpbl = axs[i].contourf(
            x, y, (S_crit[variant] - 1) * 100, levels=np.linspace(*clim_ss, nlev_ss)
        )
        pyplot.colorbar(mpbl, ax=axs[i]).set_label("critical supersaturation [%]")
        mpbl.set_clim(*clim_ss)
        axs[i].set_title(variant)

    axs[2].set_title("log_10(|S_2 - S_1| / S_1)")
    log10_rel_diff = np.log10(
        np.abs(S_crit[variants[1]] - S_crit[variants[0]]) / S_crit[variants[0]]
    )
    mpbl = axs[2].contourf(x, y, log10_rel_diff, levels=np.linspace(*clim_er, nlev_er))
    pyplot.colorbar(mpbl, ax=axs[2]).set_label("log10(relative difference)")
    mpbl.set_clim(*clim_er)

    for ax in axs:
        ax.set_ylabel("kappa")
        ax.set_xscale("log")
        ax.set_xlabel("dry radius [nm]")
    pyplot.subplots_adjust(hspace=0.25)

    if plot:
        fig.show()

    # assert
    assert np.amax(log10_rel_diff) < -4
