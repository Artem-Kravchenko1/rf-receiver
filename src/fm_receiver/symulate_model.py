import sympy as sp

from fm_receiver.model import (
    DEFAULT_CP,
    DEFAULT_CVP,
    DEFAULT_FP,
    CircuitParameters,
    CVarParameters,
)
from dataclasses import asdict

f_0, f, f_IF, f_im = sp.symbols("f_0 f f_IF f_im", positive=True)
L, C, C_par, C_v, R_loss = sp.symbols("L C C_par C_v R_loss", positive=True)
U_v, C_v0, phi, gamma = sp.symbols("U_v C_v0 phi gamma", positive=True)
K_U, BW, Q = sp.symbols("K_U BW Q", positive=True)
xi = sp.symbols("xi", real=True)
Z = sp.symbols("Z")

defs = {
    C_v: C_v0 / ((1 + (U_v / phi)) ** gamma),
    C: C_v + C_par,
    Z: 1 / (1 / R_loss + sp.I * 2 * sp.pi * f * C + 1 / (sp.I * 2 * sp.pi * f * L)),
    Q: 2 * sp.pi * f_0 * C * R_loss,
    BW: f_0 / Q,
    xi: Q * (f / f_0 - f_0 / f),
    K_U: 1 / ((1 + xi**2) ** sp.Rational(1, 2)),
    f_im: f_0 + 2 * f_IF,
}

results = {}

eq_resonance = sp.Eq(2 * sp.pi * f_0 * L, 1 / (2 * sp.pi * f_0 * C))
results["f_0"] = sp.solve(eq_resonance, f_0)[0]

results["C(f_0)"] = sp.solve(eq_resonance, C)[0]

results["C_v(f_0)"] = sp.solve(sp.Eq(C, defs[C]), C_v)[0].subs(C, results["C(f_0)"])
results[U_v] = sp.solve(sp.Eq(C_v, defs[C_v]), U_v)[0]

results["U_v(f_0)"] = results[U_v].subs(C_v, results["C_v(f_0)"])

results["dU_v/df_0"] = sp.diff(results["U_v(f_0)"], f_0)


_dU_v_df_0_func = sp.lambdify([f_0, phi, gamma, C_v0, C_par, L], results["dU_v/df_0"])


def dU_v_df_0_func(
    f_0, cp: CircuitParameters = DEFAULT_CP, cvp: CVarParameters = DEFAULT_CVP
):
    return _dU_v_df_0_func(f_0, cvp.phi, cvp.gamma, cvp.C_v0, cp.C_par, cp.L)


BW_low_limit_eq = sp.Eq(defs[xi].subs(Q, defs[Q]), -1)
BW_high_limit_eq = sp.Eq(defs[xi].subs(Q, defs[Q]), 1)
BW_low_limit_roots = sp.solve(BW_low_limit_eq, f)
BW_high_limit_roots = sp.solve(BW_high_limit_eq, f)


def select_limit(roots):
    limit = sp.nan
    positive_roots = []
    default_values = {**asdict(DEFAULT_CP), **asdict(DEFAULT_CVP)}

    for i in range(len(roots)):
        root = roots[i]
        root = root.subs(C, results["C(f_0)"])
        free_symbols = {s.name: s for s in root.free_symbols}
        needed_default_values = [var for var in free_symbols if var in default_values]
        root = root.subs(
            [(free_symbols[var], default_values[var]) for var in needed_default_values]
        )
        if root.free_symbols != set({f_0}):
            continue
        if root.subs(f_0, DEFAULT_FP.f_min) > 0:
            positive_roots.append(roots[i])

    if len(positive_roots) > 0:
        limit = positive_roots[0]

    return limit


BW_low_limit = select_limit(BW_low_limit_roots)
BW_high_limit = select_limit(BW_high_limit_roots)

BW_practical = BW_high_limit - BW_low_limit

BW_of_R_loss = "BW(R_loss)"
results[BW_of_R_loss] = defs[BW].subs(Q, defs[Q])


def is_BW_equal():
    return results[BW_of_R_loss].equals(BW_practical)


xi_norm = defs[xi] / Q
xi_norm_ser = (xi_norm).series(f, f_0, 2)


delta_xi_norm = sp.cancel((xi_norm_ser.removeO() - (xi_norm)) / xi_norm)

delta_xi_norm_func = sp.lambdify([f, f_0], delta_xi_norm)
