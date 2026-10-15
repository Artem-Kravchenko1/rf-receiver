import dataclasses
from functools import partial

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import MultipleLocator

from fm_receiver import model
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP
from fm_receiver.plot_style.style import (
    DEFAULT_ANOT_ARROW,
    DEFAULT_BBOX,
    DEFAULT_HELPER_LINE,
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

DEFAULT_R_LOSS_PARAMS = (1e3, 1.5e3, 3e3)

DEFAULT_POINTS_AMOUNT_FOR_3D = 51

DEFAULT_R_LOSS_GRID = {
    "R_loss_min": 0.5e3,
    "R_loss_max": 5e3,
    "points_amount": 51,
}


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
        **DEFAULT_HELPER_LINE,
        label=rf"$-A_\mathrm{{th}}$ = {-fp.A_threshold:.1f} dB",
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


def Q_BW_A_of_f_0_ax(
    ax,
    *,
    plot_func,
    format_func=lambda x: x,
    plot_label="",
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    f_0 = model.freq_set(fp=fp)

    ax = setup_f_ax(
        ax,
        fp=fp,
        axis_label="$f_0$",
    )

    ax.set_ylabel(plot_label)

    for R_loss in R_loss_params:
        cp_modified = dataclasses.replace(cp, R_loss=R_loss)
        ax.plot(
            MHz(f_0),
            format_func(plot_func(f_0, cp=cp_modified)),
            label=rf"$R_\mathrm{{loss}}$ = {kOhm(R_loss)} k$\Omega$",
        )

    return ax


def Q_of_f_0_ax(
    ax,
    *,
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    ax = Q_BW_A_of_f_0_ax(
        ax,
        plot_func=model.Q,
        plot_label="$Q$",
        R_loss_params=R_loss_params,
        cp=cp,
        fp=fp,
    )

    return ax


def Q_of_f_0_fig(
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, ax = plt.subplots()
    ax = Q_of_f_0_ax(ax, R_loss_params=R_loss_params, cp=cp, fp=fp)
    ax.legend()

    return fig


def BW_of_f_0_ax(
    ax,
    *,
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    ax = Q_BW_A_of_f_0_ax(
        ax,
        plot_func=model.BW,
        format_func=MHz,
        plot_label="BW, MHz",
        R_loss_params=R_loss_params,
        cp=cp,
        fp=fp,
    )

    return ax


def BW_of_f_0_fig(
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, ax = plt.subplots()
    ax = BW_of_f_0_ax(ax, R_loss_params=R_loss_params, cp=cp, fp=fp)
    ax.legend()

    return fig


def A_of_f_0_ax(
    ax,
    *,
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    A_plot_func = partial(model.A, fp=fp)
    ax = Q_BW_A_of_f_0_ax(
        ax,
        plot_func=A_plot_func,
        plot_label="A, dB",
        R_loss_params=R_loss_params,
        cp=cp,
        fp=fp,
    )

    ax.axhline(
        fp.A_threshold,
        **DEFAULT_HELPER_LINE,
        label=rf"$A_\mathrm{{th}}$ = {fp.A_threshold:.1f} dB",
    )

    return ax


def A_of_f_0_fig(
    R_loss_params=DEFAULT_R_LOSS_PARAMS,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, ax = plt.subplots()
    ax = A_of_f_0_ax(ax, R_loss_params=R_loss_params, cp=cp, fp=fp)
    ax.legend(loc="upper right")

    return fig


def A_map_of_f_0_ax(
    ax,
    *,
    f_0_points_amount=DEFAULT_POINTS_AMOUNT_FOR_3D,
    R_loss_grid=DEFAULT_R_LOSS_GRID,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fp_modified = dataclasses.replace(fp, N=f_0_points_amount)
    f_0 = model.freq_set(fp=fp_modified)
    R_loss = np.linspace(
        R_loss_grid["R_loss_min"],
        R_loss_grid["R_loss_max"],
        R_loss_grid["points_amount"],
    )

    setup_f_ax(ax, fp=fp, step=5e6)

    f_0_coords, R_loss_coords = np.meshgrid(f_0, R_loss)

    cp_modified = dataclasses.replace(cp, R_loss=R_loss_coords)

    A_map = model.A(f_0_coords, cp=cp_modified, fp=fp)

    ax.computed_zorder = False

    custom_norm = TwoSlopeNorm(
        vmin=min(A_map.min(), fp.A_threshold * 0.9, fp.A_threshold - 1),
        vcenter=fp.A_threshold,
        vmax=max(A_map.max(), fp.A_threshold * 1.1, fp.A_threshold + 1),
    )
    custom_cmap = LinearSegmentedColormap.from_list(
        "status", ["tab:red", "white", "tab:green"]
    )

    A_surface = ax.plot_surface(
        MHz(f_0_coords),
        kOhm(R_loss_coords),
        A_map,
        norm=custom_norm,
        cmap=custom_cmap,
        zorder=1,
    )

    ax.set_ylabel(r"$R_\mathrm{loss}$, k$\Omega$")
    ax.set_zlabel(r"$A$, dB")

    A_th_contours = ax.contour(
        MHz(f_0_coords),
        kOhm(R_loss_coords),
        A_map,
        levels=[fp.A_threshold],
        zorder=2,
        linestyle="dashed",
        colors="black",
        linewidth=2,
        label="A threshold",
    )

    stations_contours = ax.contour(
        MHz(f_0_coords),
        kOhm(R_loss_coords),
        A_map,
        levels=MHz(np.array(fp.f_stations)),
        zdir="x",
        zorder=2,
        colors="purple",
        linewidth=2,
        label="stations",
    )

    f_stations_coords, R_loss_coords2 = np.meshgrid(np.array(fp.f_stations), R_loss)

    cp_modified2 = dataclasses.replace(cp, R_loss=R_loss_coords2)
    A_of_R_loss = model.A(f_stations_coords, cp=cp_modified2, fp=fp)

    R_th = np.array(
        [
            np.interp(fp.A_threshold, A_col, R_loss, left=np.nan, right=np.nan)
            for A_col in A_of_R_loss.T
        ]
    )

    stations_threshold_markers = ax.plot(
        MHz(np.array(fp.f_stations)),
        kOhm(R_th),
        fp.A_threshold,
        zorder=3,
        color="blue",
        marker="o",
        linestyle="",
        label=r"stations $R_\mathrm{loss}$ threshold",
    )

    A_th_handles, _ = A_th_contours.legend_elements()
    stations_handles, _ = stations_contours.legend_elements()
    stations_threshold_markers_handle = stations_threshold_markers[0]
    A_th_handles[0].set_label(A_th_contours.get_label())
    stations_handles[0].set_label(stations_contours.get_label())
    OK_status_handle = mpatches.Patch(color="tab:green", label="OK status")
    WEAK_status_handle = mpatches.Patch(color="tab:red", label="WEAK status")

    legend_handles = [
        A_th_handles[0],
        stations_handles[0],
        stations_threshold_markers_handle,
        OK_status_handle,
        WEAK_status_handle,
    ]

    return ax, A_surface, legend_handles


def A_map_of_f_0_fig(
    f_0_points_amount=DEFAULT_POINTS_AMOUNT_FOR_3D,
    R_loss_grid=DEFAULT_R_LOSS_GRID,
    cp=DEFAULT_CP,
    fp=DEFAULT_FP,
):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(4, 6))
    ax, surface, legend_handles = A_map_of_f_0_ax(
        ax, f_0_points_amount=f_0_points_amount, R_loss_grid=R_loss_grid, cp=cp, fp=fp
    )
    A_threshold_cbar = fig.colorbar(
        surface, ax=ax, label="A, dB", location="bottom", shrink=0.75, pad=0.1
    )
    A_threshold_cbar.ax.axvline(fp.A_threshold, color="black", linewidth=2)
    x_text_middle_offset = 0.35
    y_text_offset = 1.2

    A_threshold_cbar.ax.text(
        0.5 - x_text_middle_offset,
        y_text_offset,
        "WEAK",
        transform=A_threshold_cbar.ax.transAxes,
        va="bottom",
        ha="center",
    )
    A_threshold_cbar.ax.text(
        0.5 + x_text_middle_offset,
        y_text_offset,
        "OK",
        transform=A_threshold_cbar.ax.transAxes,
        va="bottom",
        ha="center",
    )

    fig.legend(handles=legend_handles, loc="outside lower center", ncols=2)

    return fig
