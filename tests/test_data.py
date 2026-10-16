import dataclasses

import numpy as np
import pandas as pd
import pytest

from fm_receiver import data, export, model
from fm_receiver.model import DEFAULT_CP, DEFAULT_FP


@pytest.mark.parametrize(
    "data_func, rows",
    [
        (data.f_stations_data, len(DEFAULT_FP.f_stations)),
        (data.f_grid_data, DEFAULT_FP.N),
        (data.model_params_data, 12),
    ],
)
def test_table_sizes(data_func, rows):
    df, df_normalized = data_func()
    assert len(df) == len(df_normalized) == rows
    assert df.index.is_unique
    assert df_normalized.index.is_unique


def test_grid_bounds():
    df, df_normalized = data.f_grid_data()
    assert df.index[0] == pytest.approx(DEFAULT_FP.f_min)
    assert df.index[-1] == pytest.approx(DEFAULT_FP.f_max)
    assert df_normalized.index[:3].tolist() == [88.0, 88.1, 88.2]


def test_station_values_SI_and_normalized():
    df, df_normalized = data.f_stations_data()
    first_SI = df.iloc[0]
    first = df_normalized.iloc[0]

    assert first_SI["C, F"] == pytest.approx(3.2414e-11, rel=1e-4)
    assert first_SI["U var, V"] == pytest.approx(2.2126, rel=1e-4)
    assert first_SI["A, dB"] == pytest.approx(27.4668, rel=1e-4)

    assert df_normalized.index[0] == 88.4
    assert first["C, pF"] == pytest.approx(32.414)
    assert first["f im, MHz"] == pytest.approx(109.8)
    assert first["U tol, mV"] == pytest.approx(7.262)


def test_normalized_matches_SI():
    df, df_normalized = data.f_stations_data()
    pairs = [
        ("C, F", "C, pF", 1e12),
        ("BW, Hz", "BW, MHz", 1e-6),
        ("dU/df, V/Hz", "dU/df, V/MHz", 1e6),
        ("U tol, V", "U tol, mV", 1e3),
    ]
    for SI_col, col, factor in pairs:
        np.testing.assert_allclose(df_normalized[col], df[SI_col] * factor, atol=5e-4)


@pytest.mark.parametrize(
    "R_loss, expected",
    [
        (3e3, ["OK"] * 6),
        (1.5e3, ["OK", "OK", "OK", "WEAK", "WEAK", "WEAK"]),
        (1e3, ["WEAK"] * 6),
    ],
)
def test_station_statuses(R_loss, expected):
    cp = dataclasses.replace(DEFAULT_CP, R_loss=R_loss)
    df, _ = data.f_stations_data(cp=cp)
    assert df["status"].tolist() == expected
    assert (
        df["status"].tolist() == model.f_0_status(df.index.to_numpy(), cp=cp).tolist()
    )


def test_params_table():
    df, df_normalized = data.model_params_data()
    assert df.loc["f_step"].iloc[0] == pytest.approx(100e3)
    assert df_normalized.loc["L, uH"].iloc[0] == pytest.approx(0.1)
    assert df_normalized.loc["C v0, pF"].iloc[0] == pytest.approx(60)
    assert df_normalized.index[:3].tolist() == [
        "f min, MHz",
        "f max, MHz",
        "f step, MHz",
    ]


def test_params_follow_input():
    cp = dataclasses.replace(DEFAULT_CP, L=0.12e-6)
    _, df_normalized = data.model_params_data(cp=cp)
    assert df_normalized.loc["L, uH"].iloc[0] == pytest.approx(0.12)


def test_export_round_trip(tmp_path):
    export.export_all_data(str(tmp_path))

    expected_files = {
        name + suffix for name in export.DATA_DICT for suffix in ("", "_normalized")
    }
    assert {p.stem for p in tmp_path.glob("*.csv")} == expected_files

    for name, data_func in export.DATA_DICT.items():
        df, df_normalized = data_func()
        for table, suffix in ((df, ""), (df_normalized, "_normalized")):
            loaded = pd.read_csv(tmp_path / f"{name}{suffix}.csv", index_col=0)
            assert loaded.index.is_unique
            assert loaded.shape == table.shape
            numeric = table.select_dtypes("number").columns
            np.testing.assert_allclose(loaded[numeric], table[numeric], rtol=1e-12)
