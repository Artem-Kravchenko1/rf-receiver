from pathlib import Path

import matplotlib.pyplot as plt

from fm_receiver import plots
from fm_receiver.plot_style.style import STYLE_PATH

DEFAULT_SAVE_PATH = Path("results") / "figures"

plots_dict = {
    "C_plot": plots.C_and_C_v_of_f_0_fig,
    "U_v_plot": plots.U_v_of_f_0_fig,
}


def export_all_plots(save_path: Path = DEFAULT_SAVE_PATH):
    save_path.mkdir(parents=True, exist_ok=True)

    for plot_name, plot_fig_func in plots_dict.items():
        with plt.style.context(STYLE_PATH):
            fig = plot_fig_func()
            fig.savefig(save_path / (plot_name + ".png"))


if __name__ == "__main__":
    export_all_plots()
