from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CircuitParameters:
    L: float = 0.1e-6
    R_loss: float = 3e3
    C_par: float = 3e-12


@dataclass(frozen=True)
class FrequencyParameters:
    f_min: float = 88e6
    f_max: float = 108e6
    f_tol: float = 50e3
    N: int = 201
    f_IF: float = 10.7e6
    f_stations: tuple[float, ...] = (88.4e6, 91.4e6, 96.0e6, 100.0e6, 103.6e6, 107.0e6)
    A_threshold: float = 20


@dataclass(frozen=True)
class CVarParameters:
    C_v0: float = 60e-12
    phi: float = 0.7
    gamma: float = 0.5


DEFAULT_CP = CircuitParameters()
DEFAULT_FP = FrequencyParameters()
DEFAULT_CVP = CVarParameters()


def freq_set(fp: FrequencyParameters = DEFAULT_FP):
    return np.linspace(fp.f_min, fp.f_max, fp.N)


f_set = freq_set()


def C_total(f_0, cp: CircuitParameters = DEFAULT_CP):
    res_C = 1 / (4 * np.pi**2 * f_0**2 * cp.L)
    return np.where(res_C > cp.C_par, res_C, np.nan)


def C_v(f_0, cp: CircuitParameters = DEFAULT_CP):
    res_C_v = C_total(f_0, cp) - cp.C_par
    return np.where(res_C_v > 0, res_C_v, np.nan)


def U_v(f_0, cp: CircuitParameters = DEFAULT_CP, cvp: CVarParameters = DEFAULT_CVP):
    phi, gamma, C_v0 = cvp.phi, cvp.gamma, cvp.C_v0
    res_U_v = phi * (((C_v0 / C_v(f_0, cp)) ** (1 / gamma)) - 1)
    return np.where(res_U_v >= 0, res_U_v, np.nan)


def Z_total(f, f_0, cp: CircuitParameters = DEFAULT_CP):
    res_Z_total = 1 / (
        1 / cp.R_loss
        + 1j * 2 * np.pi * f * C_total(f_0, cp)
        + 1 / (1j * 2 * np.pi * f * cp.L)
    )
    return res_Z_total


def K_U(f, f_0, cp: CircuitParameters = DEFAULT_CP):
    return np.abs(Z_total(f, f_0, cp)) / np.abs(Z_total(f_0, f_0, cp))


def Q(f_0, cp: CircuitParameters = DEFAULT_CP):
    return 2 * np.pi * f_0 * C_total(f_0, cp) * cp.R_loss


def BW(f_0, cp: CircuitParameters = DEFAULT_CP):
    return f_0 / Q(f_0, cp)


def f_im(f_0, fp: FrequencyParameters = DEFAULT_FP):
    return f_0 + 2 * fp.f_IF


def A(f_0, cp: CircuitParameters = DEFAULT_CP, fp: FrequencyParameters = DEFAULT_FP):
    return 20 * np.log10(1 / K_U(f_im(f_0, fp), f_0, cp))


def station_status(
    f_0, cp: CircuitParameters = DEFAULT_CP, fp: FrequencyParameters = DEFAULT_FP
):
    return np.where(A(f_0, cp, fp) >= fp.A_threshold, "OK", "WEAK")


def dU_df_0(f_0, cp: CircuitParameters = DEFAULT_CP, cvp: CVarParameters = DEFAULT_CVP):
    h = f_0 * 1e-5
    return (U_v(f_0 + h, cp, cvp) - U_v(f_0 - h, cp, cvp)) / (2 * h)


def U_tol(
    f_0,
    cp: CircuitParameters = DEFAULT_CP,
    fp: FrequencyParameters = DEFAULT_FP,
    cvp: CVarParameters = DEFAULT_CVP,
):
    return dU_df_0(f_0, cp, cvp) * fp.f_tol
