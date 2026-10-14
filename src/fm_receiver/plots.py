import matplotlib.pyplot as plt
from matplotlib.layout_engine import ConstrainedLayoutEngine
import numpy as np

from fm_receiver import model
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP


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


def C_and_C_v_of_f_0_ax(ax, f_0, cp=DEFAULT_CP, fp=DEFAULT_FP):
    ax = setup_f_ax(ax, fp=fp)

    ax.plot(MHz(f_0), pF(model.C_total(f_0, cp=cp)), label=r"$C_\mathrm{total}$")
    ax.plot(MHz(f_0), pF(model.C_v(f_0, cp=cp)), label=r"$C_\mathrm{v}$")

    ax.set_ylabel(r"$C$, pF")

    anot_x_f = np.round((fp.f_min + fp.f_max) / 2)
    anot_y_C = model.C_total(anot_x_f, cp=cp)
    anot_y_C_v = model.C_v(anot_x_f, cp=cp)
    ax.annotate(
        "",
        xy=(MHz(anot_x_f), pF(anot_y_C)),
        xytext=(MHz(anot_x_f), pF(anot_y_C_v)),
        arrowprops={"arrowstyle": "<->"},
    )

    ax.annotate(
        rf"$C_\mathrm{{par}}$ = {pF(cp.C_par):.1f} pF",
        xy=(MHz(anot_x_f), pF((anot_y_C + anot_y_C_v) / 2)),
        xytext=(MHz(anot_x_f) + MHz(fp.f_max - fp.f_min) * 0.1, pF(anot_y_C)),
        arrowprops={
            "arrowstyle": "-",
            "lw": 0.8,
        },
        va="bottom",
        bbox={
            "boxstyle": "round,pad=0.2",
            "fc": "white",
            "ec": "gray",
            "alpha": 0.75,
        },
    )

    ax.grid()
    ax.legend()

    return ax


def C_and_C_v_of_f_0_fig(cp=DEFAULT_CP, fp=DEFAULT_FP):
    fig, ax = plt.subplots(layout=ConstrainedLayoutEngine(w_pad=0.15, h_pad=0.15))

    f_0 = model.freq_set(fp)
    ax = C_and_C_v_of_f_0_ax(ax, f_0, cp, fp)

    return fig


def U_v_of_f_0_ax(ax, f_0, cp=DEFAULT_CP, cvp=DEFAULT_CVP, fp=DEFAULT_FP):
    ax = setup_f_ax(ax, fp=fp)

    ax.plot(MHz(f_0), model.U_v(f_0, cp=cp, cvp=cvp), label=r"$U_\mathrm{v}$")

    stations_f = np.array(fp.f_stations)
    stations_U_v = model.U_v(stations_f, cp=cp, cvp=cvp)
    ax.plot(MHz(stations_f), stations_U_v, "o", label="stations")

    ax.set_ylabel(r"$U_\mathrm{v}$, V")

    U_v_min_lim, U_v_max_lim = ax.get_ylim()
    ax_height = U_v_max_lim - U_v_min_lim

    for i, (station_f, station_U_v) in enumerate(zip(stations_f, stations_U_v)):
        station_label_ha = "left" if i == 0 else "center"
        ax.annotate(
            rf"$f_0$ = {MHz(station_f):.1f} MHz"
            + "\n"
            + rf"$U_\mathrm{{v}}$ = {station_U_v:.1f} V",
            xy=(MHz(station_f), station_U_v),
            xytext=(
                MHz(station_f),
                station_U_v + ax_height * 0.1,
            ),
            arrowprops={
                "arrowstyle": "->",
                "lw": 0.8,
            },
            ha=station_label_ha,
            va="bottom",
            fontsize=8,
            bbox={
                "boxstyle": "round,pad=0.2",
                "fc": "white",
                "ec": "gray",
                "alpha": 0.75,
            },
        )

    ax.grid()
    ax.legend()

    return ax


def U_v_of_f_0_fig(cp=DEFAULT_CP, cvp=DEFAULT_CVP, fp=DEFAULT_FP):
    fig, ax = plt.subplots(layout=ConstrainedLayoutEngine(w_pad=0.15, h_pad=0.15))

    f_0 = model.freq_set(fp)
    ax = U_v_of_f_0_ax(ax, f_0, cp, cvp, fp)

    return fig
