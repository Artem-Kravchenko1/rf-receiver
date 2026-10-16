from dataclasses import asdict

import numpy as np
import pandas as pd

from fm_receiver import model
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP
from fm_receiver.units import (
    MHz,
    as_is,
    kHz,
    kOhm,
    mV,
    per_MHz,
    pF,
    uH,
)


def f_grid_data(f_grid=None, fp=DEFAULT_FP, cp=DEFAULT_CP, cvp=DEFAULT_CVP):
    if f_grid is None:
        f_grid = model.freq_set(fp=fp)

    C = model.C_total(f_grid, cp=cp)
    C_v = model.C_v(f_grid, cp=cp)
    U_v = model.U_v(f_grid, cp=cp, cvp=cvp)
    Q = model.Q(f_grid, cp=cp)
    BW = model.BW(f_grid, cp=cp)
    f_im = model.f_im(f_grid, fp=fp)
    A = model.A(f_grid, cp=cp, fp=fp)
    f_0_status = model.f_0_status(f_grid, cp=cp, fp=fp)
    dU_v_df = model.dU_df_0(f_grid, cp=cp, cvp=cvp)
    U_tol = model.U_tol(f_grid, cp=cp, fp=fp, cvp=cvp)

    df = pd.DataFrame(
        {
            "C, F": C,
            "C var, F": C_v,
            "U var, V": U_v,
            "Q": Q,
            "BW, Hz": BW,
            "f im, Hz": f_im,
            "A, dB": A,
            "status": f_0_status,
            "dU/df, V/Hz": dU_v_df,
            "U tol, V": U_tol,
        },
        index=f_grid,
    )

    df.index.name = "f 0, Hz"

    conversions = {
        "C, F": ("C, pF", pF),
        "C var, F": ("C var, pF", pF),
        "BW, Hz": ("BW, MHz", MHz),
        "f im, Hz": ("f im, MHz", MHz),
        "dU/df, V/Hz": ("dU/df, V/MHz", per_MHz),
        "U tol, V": ("U tol, mV", mV),
    }

    df_normalized = df.copy()

    for col_name, (_, conv) in conversions.items():
        df_normalized[col_name] = conv(df_normalized[col_name])

    df_normalized = df_normalized.rename(
        columns={old: new for old, (new, _) in conversions.items()}
    )

    df_normalized.index = MHz(df_normalized.index)
    df_normalized.index.name = "f 0, MHz"

    return df, df_normalized


def f_stations_data(fp=DEFAULT_FP, cp=DEFAULT_CP, cvp=DEFAULT_CVP):
    return f_grid_data(np.array(fp.f_stations), fp=fp, cp=cp, cvp=cvp)


def model_params_data(fp=DEFAULT_FP, cp=DEFAULT_CP, cvp=DEFAULT_CVP):
    params = {**asdict(fp), **asdict(cp), **asdict(cvp)}
    params.pop("f_stations")
    params["f_step"] = (params["f_max"] - params["f_min"]) / (params["N"] - 1)
    params.pop("N")

    values_col_name = "Value, SI"
    df = pd.DataFrame(params.values(), columns=[values_col_name], index=params.keys())
    df.index.name = "Parameter"

    conversions = {
        "f_min": ("f min, MHz", MHz),
        "f_max": ("f max, MHz", MHz),
        "f_step": ("f step, MHz", MHz),
        "f_tol": ("f tol, kHz", kHz),
        "f_IF": ("f IF, MHz", MHz),
        "A_threshold": ("A th, dB", as_is),
        "L": ("L, uH", uH),
        "R_loss": ("R loss, kOhm", kOhm),
        "C_par": ("C par, pF", pF),
        "C_v0": ("C v0, pF", pF),
        "phi": ("phi, V", as_is),
        "gamma": ("gamma", as_is),
    }

    df = df.loc[list(conversions)]

    df_normalized = df.copy()

    for param_name, (_, conv) in conversions.items():
        df_normalized.loc[param_name, values_col_name] = conv(
            df_normalized.loc[param_name, values_col_name]
        )

    values_normalized_col_name = "Value"

    df_normalized = df_normalized.rename(
        index={old: new for old, (new, _) in conversions.items()},
        columns={values_col_name: values_normalized_col_name},
    )

    return df, df_normalized
