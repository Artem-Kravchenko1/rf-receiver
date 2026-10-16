import dataclasses

import pytest

from fm_receiver import model
from fm_receiver.model import DEFAULT_CP, DEFAULT_FP

DEFAULT_REL_ERROR = 1e-3
DEFAULT_ABS_ERROR = 0


def kHz(f):
    return f"{f / 1e3:g}kHz"


def MHz(f):
    return f"{f / 1e6:g}MHz"


def kOhm(R):
    return f"{R / 1e3:g}kOhm"


C_CASES = [
    (88e6, 3.270958e-11),
    (100e6, 2.533030e-11),
    (108e6, 2.171665e-11),
]


@pytest.mark.parametrize(
    "f_0, C_expected",
    C_CASES,
    ids=[f"f_0 = {MHz(f_0)}" for f_0, _ in C_CASES],
)
def test_C_of_f_0(f_0, C_expected):
    assert model.C_total(f_0) == pytest.approx(
        C_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


C_V_CASES = [
    (88e6, 2.970958e-11),
    (100e6, 2.233030e-11),
    (108e6, 1.871665e-11),
]


@pytest.mark.parametrize(
    "f_0, C_v_expected",
    C_V_CASES,
    ids=[f"f_0 = {MHz(f_0)}" for f_0, _ in C_V_CASES],
)
def test_C_v_of_f_0(f_0, C_v_expected):
    assert model.C_v(f_0) == pytest.approx(
        C_v_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


U_V_CASES = [
    (88e6, 2.155010),
    (100e6, 4.353725),
    (108e6, 6.493570),
]


@pytest.mark.parametrize(
    "f_0, U_v_expected",
    U_V_CASES,
    ids=[f"f_0 = {MHz(f_0)}" for f_0, _ in U_V_CASES],
)
def test_U_v_of_f_0(f_0, U_v_expected):
    assert model.U_v(f_0) == pytest.approx(
        U_v_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


K_U_CASES = [
    (88e6, 90e6, 0.379378),
    (88e6, 100e6, 0.071708),
    (88e6, 110e6, 0.040923),
    (100e6, 90e6, 0.098724),
    (100e6, 100e6, 1.000000),
    (100e6, 110e6, 0.109052),
    (108e6, 90e6, 0.061572),
    (108e6, 100e6, 0.145252),
    (108e6, 110e6, 0.524680),
]


@pytest.mark.parametrize(
    "f_0, f, K_U_expected",
    K_U_CASES,
    ids=[f"f_0 = {MHz(f_0)}, f = {MHz(f)}" for f_0, f, _ in K_U_CASES],
)
def test_K_U_of_f_0_and_f(f_0, f, K_U_expected):
    assert model.K_U(f, f_0) == pytest.approx(
        K_U_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


Q_CASES = [
    (88e6, 1e3, 18.0858),
    (88e6, 3e3, 54.2574),
    (88e6, 10e3, 180.8579),
    (100e6, 1e3, 15.9155),
    (100e6, 3e3, 47.7465),
    (100e6, 10e3, 159.1549),
    (108e6, 1e3, 14.7366),
    (108e6, 3e3, 44.2097),
    (108e6, 10e3, 147.3657),
]


@pytest.mark.parametrize(
    "f_0, R_loss, Q_expected",
    Q_CASES,
    ids=[f"f_0 = {MHz(f_0)}, R_loss = {kOhm(R_loss)}" for f_0, R_loss, _ in Q_CASES],
)
def test_Q_of_f_0_and_R_loss(f_0, R_loss, Q_expected):
    cp_modified = dataclasses.replace(DEFAULT_CP, R_loss=R_loss)
    assert model.Q(f_0, cp=cp_modified) == pytest.approx(
        Q_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


BW_CASES = [
    (88e6, 1.621900e6),
    (100e6, 2.094395e6),
    (108e6, 2.442902e6),
]


@pytest.mark.parametrize(
    "f_0, BW_expected",
    BW_CASES,
    ids=[f"f_0 = {MHz(f_0)}" for f_0, _ in BW_CASES],
)
def test_BW_of_f_0(f_0, BW_expected):
    assert model.BW(f_0) == pytest.approx(
        BW_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


F_IM_AND_A_CASES = [
    (88e6, 1.094e8, 27.5420),
    (100e6, 1.214e8, 25.4188),
    (108e6, 1.294e8, 24.1379),
]


@pytest.mark.parametrize(
    "f_0, f_im_expected, A_expected",
    F_IM_AND_A_CASES,
    ids=[f"f_0 = {MHz(f_0)}" for f_0, _, _ in F_IM_AND_A_CASES],
)
def test_f_im_and_A_of_f_0(f_0, f_im_expected, A_expected):
    assert model.f_im(f_0) == pytest.approx(
        f_im_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )
    assert model.A(f_0) == pytest.approx(
        A_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


U_TOL_CASES = [
    (100e6, 10e3, 2.293070e-3),
    (100e6, 50e3, 1.146535e-2),
    (100e6, 100e3, 2.293070e-2),
]


@pytest.mark.parametrize(
    "f_0, f_tol, U_tol_expected",
    U_TOL_CASES,
    ids=[f"f_0 = {MHz(f_0)}, f_tol = {kHz(f_tol)}" for f_0, f_tol, _ in U_TOL_CASES],
)
def test_U_tol_of_f_tol(f_0, f_tol, U_tol_expected):
    fp_modified = dataclasses.replace(DEFAULT_FP, f_tol=f_tol)
    assert model.U_tol(f_0, fp=fp_modified) == pytest.approx(
        U_tol_expected, rel=DEFAULT_REL_ERROR, abs=DEFAULT_ABS_ERROR
    )


F_0_STATUS_CASES = [
    (88.4e6, 1e3, "WEAK"),
    (91.4e6, 1e3, "WEAK"),
    (96.0e6, 1e3, "WEAK"),
    (100.0e6, 1e3, "WEAK"),
    (103.6e6, 1e3, "WEAK"),
    (107.0e6, 1e3, "WEAK"),
    (88.4e6, 1.5e3, "OK"),
    (91.4e6, 1.5e3, "OK"),
    (96.0e6, 1.5e3, "OK"),
    (100.0e6, 1.5e3, "WEAK"),
    (103.6e6, 1.5e3, "WEAK"),
    (107.0e6, 1.5e3, "WEAK"),
    (88.4e6, 3e3, "OK"),
    (91.4e6, 3e3, "OK"),
    (96.0e6, 3e3, "OK"),
    (100.0e6, 3e3, "OK"),
    (103.6e6, 3e3, "OK"),
    (107.0e6, 3e3, "OK"),
]


@pytest.mark.parametrize(
    "f_0, R_loss, f_0_status_expected",
    F_0_STATUS_CASES,
    ids=[
        f"f_0 = {MHz(f_0)}, R_loss = {kOhm(R_loss)}"
        for f_0, R_loss, _ in F_0_STATUS_CASES
    ],
)
def test_f_0_status_of_f_0_and_R_loss(f_0, R_loss, f_0_status_expected):
    cp_modified = dataclasses.replace(DEFAULT_CP, R_loss=R_loss)
    assert model.f_0_status(f_0, cp=cp_modified) == f_0_status_expected
