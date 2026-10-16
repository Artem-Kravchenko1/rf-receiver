import dataclasses

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from fm_receiver import export, plots
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP
from fm_receiver.plot_style.style import STYLE_PATH, setup_f_ax
from fm_receiver.units import dB


@pytest.mark.parametrize("fig_func", export.FIGURES_DICT.values())
def test_figure_builds_with_style(fig_func):
    with plt.style.context(STYLE_PATH):
        fig = fig_func()
    assert isinstance(fig, Figure)
    assert len(fig.axes) > 0


@pytest.mark.parametrize("fig_func", export.FIGURES_DICT.values())
def test_figure_builds_without_style(fig_func):
    assert isinstance(fig_func(), Figure)


def test_export_creates_all_files(tmp_path):
    export.export_all_figures(str(tmp_path / "figures"))
    files = sorted(p.stem for p in (tmp_path / "figures").glob("*.png"))
    assert files == sorted(export.FIGURES_DICT)
    assert plt.get_fignums() == []


def test_dB():
    assert dB(10) == pytest.approx(20)
    assert dB(1) == pytest.approx(0)


@pytest.mark.parametrize(
    "f_min, f_max, expected_ticks",
    [
        (88e6, 108e6, [88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108]),
        (80e6, 130e6, [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130]),
    ],
)
def test_f_axis_ticks(f_min, f_max, expected_ticks):
    fig, ax = plt.subplots()
    setup_f_ax(ax, f_min=f_min, f_max=f_max)
    fig.canvas.draw()
    visible = [t for t in ax.get_xticks() if f_min * 1e-6 <= t <= f_max * 1e-6]
    assert visible == pytest.approx(expected_ticks)


def test_f_axis_locators_are_independent():
    fig, (ax_a, ax_b) = plt.subplots(1, 2)
    setup_f_ax(ax_a)
    setup_f_ax(ax_b, f_min=80e6, f_max=130e6)
    fig.canvas.draw()
    assert ax_a.get_xticks()[:3] == pytest.approx([88, 90, 92])


def test_C_par_annotation_follows_params():
    cp = dataclasses.replace(DEFAULT_CP, C_par=5e-12)
    ax = plots.C_and_C_v_of_f_0_fig(cp=cp).axes[0]
    assert any("5.0 pF" in t.get_text() for t in ax.texts)


def test_U_v_station_labels_follow_params():
    cvp = dataclasses.replace(DEFAULT_CVP, gamma=0.4)
    ax = plots.U_v_of_f_0_fig(cvp=cvp).axes[0]
    labels = [t.get_text() for t in ax.texts]
    assert len(labels) == len(DEFAULT_FP.f_stations)
    assert "11.5 V" in labels[-1]  # 107 MHz with gamma = 0.4


def test_K_U_markers_match_curve_colors():
    ax = plots.K_U_of_f_fig().axes[0]
    curves = [line for line in ax.lines if line.get_marker() == "None"][:3]
    markers = [line for line in ax.lines if line.get_marker() == "o"]
    assert [c.get_color() for c in curves] == [m.get_color() for m in markers]


def test_A_map_threshold_markers():
    ax = plots.A_map_of_f_0_fig().axes[0]
    markers = next(line for line in ax.lines if line.get_marker() == "o")
    _, R_kOhm, A = markers.get_data_3d()
    expected = [1.265, 1.348, 1.481, 1.602, 1.714, 1.824]
    assert R_kOhm == pytest.approx(expected, abs=2e-3)
    assert A == pytest.approx(DEFAULT_FP.A_threshold)


def test_A_map_no_markers_outside_data():
    fp = dataclasses.replace(DEFAULT_FP, A_threshold=40)
    ax = plots.A_map_of_f_0_fig(fp=fp).axes[0]
    markers = next(line for line in ax.lines if line.get_marker() == "o")
    assert np.all(np.isnan(markers.get_data_3d()[1]))


def test_status_table_row_1_5_kOhm():
    ax = plots.A_status_table_fig(R_loss_params=(1.5e3,)).axes[0]
    statuses = [t.get_text().split("\n")[0] for t in ax.texts]
    assert statuses == ["OK", "OK", "OK", "WEAK", "WEAK", "WEAK"]


def test_dU_df_values_at_100_MHz():
    top, bottom = plots.dU_df_of_f_0_fig().axes
    i = np.argmin(np.abs(top.lines[0].get_xdata() - 100))
    gamma_values = [line.get_ydata()[i] for line in top.lines]
    C_par_values = [line.get_ydata()[i] for line in bottom.lines]
    assert gamma_values == pytest.approx([0.470, 0.229, 0.079], abs=2e-3)
    assert C_par_values == pytest.approx([0.177, 0.229, 0.353], abs=2e-3)


def test_U_tol_values_at_100_MHz():
    ax = plots.U_tol_of_f_0_fig().axes[0]
    i = np.argmin(np.abs(ax.lines[0].get_xdata() - 100))
    values = [line.get_ydata()[i] for line in ax.lines]
    assert values == pytest.approx([2.293, 11.465, 22.931], rel=1e-3)
