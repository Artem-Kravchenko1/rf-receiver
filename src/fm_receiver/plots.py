import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from fm_receiver import model
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP
from fm_receiver.plot_style.style import (
    DEFAULT_ANOT_ARROW,
    DEFAULT_BBOX,
    MHz,
    dB,
    kOhm,
    pF,
    setup_f_ax,
)

DEFAULT_F_GRID = {
    "f_min": 80e6,
    "f_max": 130e6,
    "points_amount": 501,
}

DEFAULT_F_0_PARAMS = (88e6, 98e6, 108e6)


def C_and_C_v_of_f_0_ax(ax, *, cp=DEFAULT_CP, fp=DEFAULT_FP):
    f_0 = model.freq_set(fp)
    ax = setup_f_ax(ax, fp=fp)

    ax.plot(MHz(f_0), pF(model.C_total(f_0, cp=cp)), label=r"$C_\mathrm{total}$")
    ax.plot(MHz(f_0), pF(model.C_v(f_0, cp=cp)), label=r"$C_\mathrm{v}$")

    ax.set_ylabel(r"$C$, pF")

    anot_x_f = (fp.f_min + fp.f_max) / 2
    anot_y_C = model.C_total(anot_x_f, cp=cp)
    anot_y_C_v = model.C_v(anot_x_f, cp=cp)
    ax.annotate(
        "",
        xy=(MHz(anot_x_f), pF(anot_y_C)),
        xytext=(MHz(anot_x_f), pF(anot_y_C_v)),
        arrowprops={"arrowstyle": "<->"},
    )

    anot_arrow = DEFAULT_ANOT_ARROW.copy()
    anot_arrow["arrowstyle"] = "-"
    ax.annotate(
        rf"$C_\mathrm{{par}}$ = {pF(cp.C_par):.1f} pF",
        xy=(MHz(anot_x_f), pF((anot_y_C + anot_y_C_v) / 2)),
        xytext=(MHz(anot_x_f) + MHz(fp.f_max - fp.f_min) * 0.1, pF(anot_y_C)),
        arrowprops=anot_arrow,
        va="bottom",
        bbox=DEFAULT_BBOX,
    )

    return ax


def C_and_C_v_of_f_0_fig(cp=DEFAULT_CP, fp=DEFAULT_FP):
    fig, ax = plt.subplots()

    ax = C_and_C_v_of_f_0_ax(ax, cp=cp, fp=fp)

    ax.legend()

    return fig


def U_v_of_f_0_ax(ax, *, cp=DEFAULT_CP, cvp=DEFAULT_CVP, fp=DEFAULT_FP):
    f_0 = model.freq_set(fp)
    ax = setup_f_ax(ax, fp=fp)

    ax.plot(MHz(f_0), model.U_v(f_0, cp=cp, cvp=cvp), label=r"$U_\mathrm{v}$")

    stations_f = np.array(fp.f_stations)
    stations_U_v = model.U_v(stations_f, cp=cp, cvp=cvp)
    ax.plot(MHz(stations_f), stations_U_v, "o", label="stations")

    ax.set_ylabel(r"$U_\mathrm{v}$, V")

    for i, (station_f, station_U_v) in enumerate(zip(stations_f, stations_U_v)):
        station_label_ha = "left" if i == 0 else "center"
        station_text_offset = (0, 20) if i == 0 else (0, 24)
        ax.annotate(
            rf"$f_0$ = {MHz(station_f):.1f} MHz"
            + "\n"
            + rf"$U_\mathrm{{v}}$ = {station_U_v:.1f} V",
            xy=(MHz(station_f), station_U_v),
            textcoords="offset points",
            xytext=station_text_offset,
            arrowprops=DEFAULT_ANOT_ARROW,
            ha=station_label_ha,
            va="bottom",
            fontsize="x-small",
            bbox=DEFAULT_BBOX,
        )

    return ax


def U_v_of_f_0_fig(cp=DEFAULT_CP, cvp=DEFAULT_CVP, fp=DEFAULT_FP):
    fig, ax = plt.subplots()

    ax = U_v_of_f_0_ax(ax, cp=cp, cvp=cvp, fp=fp)

    ax.legend()

    return fig


def mag_Z_of_f_ax(
    ax,
    *,
    f_grid=DEFAULT_F_GRID,
    f_0_params=DEFAULT_F_0_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    f_min, f_max, points_amount = f_grid.values()
    f = np.linspace(
        start=f_min,
        stop=f_max,
        num=points_amount,
    )

    ax = setup_f_ax(
        ax,
        fp=fp,
        f_min=f_grid["f_min"],
        f_max=f_grid["f_max"],
        axis_label="$f$",
    )

    ax.set_ylabel(r"$|Z|$, k$\Omega$")

    for f_0 in f_0_params:
        ax.plot(
            MHz(f),
            kOhm(np.abs(model.Z_total(f, f_0, cp=cp))),
            label=rf"$f_0$ = {MHz(f_0)} MHz",
        )

    return ax


def phase_Z_of_f_ax(
    ax,
    *,
    f_grid=DEFAULT_F_GRID,
    f_0_params=DEFAULT_F_0_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    f_min, f_max, points_amount = f_grid.values()
    f = np.linspace(
        start=f_min,
        stop=f_max,
        num=points_amount,
    )

    ax = setup_f_ax(
        ax,
        fp=fp,
        f_min=f_min,
        f_max=f_max,
        axis_label="$f$",
    )

    ax.set_ylabel(r"$\arg Z$, $\degree$")

    for f_0 in f_0_params:
        ax.plot(
            MHz(f),
            np.angle(model.Z_total(f, f_0, cp=cp), deg=True),
            label=rf"$f_0$ = {MHz(f_0)} MHz",
        )

    ax.yaxis.set_major_locator(MultipleLocator(45))

    return ax


def Z_of_f_fig(
    f_grid=DEFAULT_F_GRID,
    f_0_params=DEFAULT_F_0_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(6.7, 6))

    axs[0] = mag_Z_of_f_ax(axs[0], f_grid=f_grid, f_0_params=f_0_params, cp=cp, fp=fp)
    axs[1] = phase_Z_of_f_ax(axs[1], f_grid=f_grid, f_0_params=f_0_params, cp=cp, fp=fp)

    for ax in axs:
        ax.label_outer()
        ax.legend()

    return fig


def K_U_of_f_ax(
    ax,
    *,
    f_grid=DEFAULT_F_GRID,
    f_0_params=DEFAULT_F_0_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    f_min, f_max, points_amount = f_grid.values()
    f = np.linspace(
        start=f_min,
        stop=f_max,
        num=points_amount,
    )

    ax = setup_f_ax(
        ax,
        fp=fp,
        f_min=f_grid["f_min"],
        f_max=f_grid["f_max"],
        axis_label="$f$",
    )

    ax.set_ylabel(r"$K_{U}$, dB")

    text_offset = (0, -20)

    for f_0 in f_0_params:
        ax.plot(
            MHz(f),
            dB(model.K_U(f, f_0, cp=cp)),
            label=rf"$f_0$ = {MHz(f_0)} MHz",
        )

        line_color = ax.lines[-1].get_color()

        f_im = model.f_im(f_0, fp=fp)
        K_U_of_f_im = model.K_U(f_im, f_0, cp=cp)
        ax.plot(
            MHz(f_im),
            dB(K_U_of_f_im),
            marker="o",
            color=line_color,
        )

        A = model.A(f_0, cp=cp, fp=fp)
        ax.annotate(
            rf"$f_\mathrm{{im}}$ = {MHz(f_im):.1f} MHz" + "\n" + rf"$A$ = {A:.1f} dB",
            xy=(MHz(f_im), dB(K_U_of_f_im)),
            textcoords="offset points",
            xytext=text_offset,
            arrowprops=DEFAULT_ANOT_ARROW,
            ha="center",
            va="top",
            fontsize="x-small",
            bbox=DEFAULT_BBOX,
        )

    ax.axhline(
        -fp.A_threshold,
        color="grey",
        linestyle="dashed",
        label=rf"$A_\mathrm{{th}}$ = {fp.A_threshold:.1f} dB",
    )

    return ax


def K_U_of_f_fig(
    f_grid=DEFAULT_F_GRID,
    f_0_params=DEFAULT_F_0_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, ax = plt.subplots()
    ax = K_U_of_f_ax(ax, f_grid=f_grid, f_0_params=f_0_params, cp=cp, fp=fp)
    ax.legend()

    return fig
