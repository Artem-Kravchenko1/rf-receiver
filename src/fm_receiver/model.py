from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class EntryParameters:
    f_min: float = 88e6
    f_max: float = 108e6
    L: float = 0.1e-6
    R_loss: float = 3e3
    C_par: float = 3e-12
    f_IF: float = 10.7e6
    f_stations: tuple[float, ...] = (88.4e6, 91.4e6, 96.0e6, 100.0e6, 103.6e6, 107.0e6)


@dataclass(frozen=True)
class CVarParameters:
    C_var0: float = 60e-12
    phi: float = 0.7
    gamma: float = 0.5


p = EntryParameters()

p_C_v = CVarParameters()


def C(f_0):
    C = 1 / (4 * np.pi**2 * f_0**2 * p.L)
    return np.where(C > p.C_par, C, -1)


def C_v(f_0):
    C_v = C(f_0) - p.C_par
    return np.where(C_v > 0, C_v, -1)


def U_v(f_0):
    phi, gamma, C_v0 = p_C_v.phi, p_C_v.gamma, p_C_v.C_var0
    U_v = phi * (((C_v0 / C_v(f_0)) ** (1 / gamma)) - 1)
    return np.where(U_v >= 0, U_v, -1)
