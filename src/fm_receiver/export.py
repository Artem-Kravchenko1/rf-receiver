from pathlib import Path

import matplotlib.pyplot as plt

from fm_receiver import plots
from fm_receiver.plot_style.style import STYLE_PATH

DEFAULT_SAVE_PATH = Path("results") / "figures"

FIGURES_DICT = {
    "C_fig": plots.C_and_C_v_of_f_0_fig,
    "U_v_fig": plots.U_v_of_f_0_fig,
}


def export_all_figures(save_path: Path = DEFAULT_SAVE_PATH):
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    with plt.style.context(STYLE_PATH):
        for fig_name, fig_func in FIGURES_DICT.items():
            fig = fig_func()
            fig.savefig(save_path / (fig_name + ".png"))
            plt.close(fig)


if __name__ == "__main__":
    export_all_figures()
