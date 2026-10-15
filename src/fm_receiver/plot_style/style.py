from pathlib import Path

import numpy as np
from matplotlib.ticker import MaxNLocator, MultipleLocator

from fm_receiver.model import DEFAULT_FP

STYLE_PATH = Path(__file__).parent / "style.mplstyle"

DEFAULT_BBOX = {
    "boxstyle": "round,pad=0.2",
    "fc": "white",
    "ec": "gray",
    "alpha": 0.75,
}

DEFAULT_ANOT_ARROW = {
    "arrowstyle": "->",
    "lw": 0.8,
}

DEFAULT_MAJOR_LOCATOR_PARAMS = {
    "nbins": 10,
    "steps": [1, 2, 2.5, 5, 10],
}


def MHz(f):
    return f * 1e-6


def pF(C):
    return C * 1e12


def kOhm(R):
    return R * 1e-3


def dB(x):
    return 20 * np.log10(x)


def setup_f_ax(
    ax,
    *,
    fp=DEFAULT_FP,
    f_min=None,
    f_max=None,
    step=None,
    axis_label="$f_0$",
):
    if f_min is None:
        f_min = fp.f_min
    if f_max is None:
        f_max = fp.f_max
    if step is not None:
        major_locator = MultipleLocator(MHz(step))
    else:
        major_locator = MaxNLocator(**DEFAULT_MAJOR_LOCATOR_PARAMS)
    ax.set_xlabel(rf"{axis_label}, MHz")
    ax.set_xlim(MHz(f_min), MHz(f_max))

    ax.xaxis.set_major_locator(major_locator)

    return ax
