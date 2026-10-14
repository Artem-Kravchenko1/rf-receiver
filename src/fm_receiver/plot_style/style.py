from pathlib import Path

import numpy as np

from fm_receiver.model import DEFAULT_FP

STYLE_PATH = Path(__file__).parent + "/style.mplstyle"


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


def MHz(f):
    return f * 1e-6


def pF(C):
    return C * 1e12


def round_by(val, step, rounding_type="nearest"):
    if rounding_type == "up":
        return np.ceil(val / step) * step
    elif rounding_type == "down":
        return np.floor(val / step) * step
    elif rounding_type == "nearest":
        return np.round(val / step) * step
    else:
        raise ValueError(
            f"Unexpected rounding type {rounding_type!r}, expected 'up', 'down' or 'nearest'"
        )


def setup_f_ax(
    ax,
    fp=DEFAULT_FP,
    f_min=None,
    f_max=None,
    step=2,
    axis_label="$f_0$",
):
    if f_min is None:
        f_min = fp.f_min
    if f_max is None:
        f_max = fp.f_max
    ax.set_xlabel(rf"{axis_label}, MHz")
    ax.set_xlim(MHz(f_min), MHz(f_max))
    ax.set_xticks(
        np.arange(
            round_by(MHz(f_min), step, "up"),
            round_by(MHz(f_max), step, "down") + step / 2,
            step,
        )
    )

    return ax
