from pathlib import Path

import matplotlib.pyplot as plt

from fm_receiver import data, plots
from fm_receiver.plot_style.style import STYLE_PATH

DEFAULT_FIGURES_SAVE_PATH = Path("results") / "figures"
DEFAULT_DATA_SAVE_PATH = Path("results") / "data"

FIGURES_DICT = {
    "C_fig": plots.C_and_C_v_of_f_0_fig,
    "U_v_fig": plots.U_v_of_f_0_fig,
    "Z_fig": plots.Z_of_f_fig,
    "K_U_fig": plots.K_U_of_f_fig,
    "Q_fig": plots.Q_of_f_0_fig,
    "BW_fig": plots.BW_of_f_0_fig,
    "A_fig": plots.A_of_f_0_fig,
    "A_map_fig": plots.A_map_of_f_0_fig,
    "A_status_table_fig": plots.A_status_table_fig,
    "dU_df_fig": plots.dU_df_of_f_0_fig,
    "U_tol_fig": plots.U_tol_of_f_0_fig,
}

DATA_DICT = {
    "f_stations_data": data.f_stations_data,
    "f_grid_data": data.f_grid_data,
    "model_params_data": data.model_params_data,
}


def export_all_figures(save_path: Path = DEFAULT_FIGURES_SAVE_PATH):
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    with plt.style.context(STYLE_PATH):
        for fig_name, fig_func in FIGURES_DICT.items():
            fig = fig_func()
            fig.savefig(save_path / (fig_name + ".png"))
            plt.close(fig)


def export_all_data(save_path: Path = DEFAULT_DATA_SAVE_PATH):
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    for data_name, data_func in DATA_DICT.items():
        df, df_normalized = data_func()
        df.to_csv(save_path / (data_name + ".csv"))
        df_normalized.to_csv(
            save_path / (data_name + "_normalized.csv"),
            float_format="%.3g",
        )


if __name__ == "__main__":
    export_all_figures()
    export_all_data()
