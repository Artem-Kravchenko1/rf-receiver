import dataclasses

import numpy as np
import pytest

from fm_receiver import model
from fm_receiver import symulate_model as sm
from fm_receiver.model import DEFAULT_CP, DEFAULT_CVP, DEFAULT_FP


def test_BW_limits_give_f0_over_Q():
    assert sm.is_BW_equal()


@pytest.mark.parametrize(
    "cp, cvp",
    [
        (DEFAULT_CP, DEFAULT_CVP),
        (dataclasses.replace(DEFAULT_CP, L=0.12e-6), DEFAULT_CVP),
        (DEFAULT_CP, dataclasses.replace(DEFAULT_CVP, gamma=0.45)),
    ],
)
def test_symbolic_dU_df_matches_model(cp, cvp):
    f_0 = model.freq_set(DEFAULT_FP)
    np.testing.assert_allclose(
        sm.dU_v_df_0_func(f_0, cp=cp, cvp=cvp),
        model.dU_df_0(f_0, cp=cp, cvp=cvp),
        rtol=1e-6,
    )


@pytest.mark.parametrize(
    "f_0, expected",
    [(88e6, 0.1084), (100e6, 0.0967), (108e6, 0.0901)],
)
def test_xi_approximation_error_at_image_frequency(f_0, expected):
    f_im = model.f_im(f_0, DEFAULT_FP)
    assert sm.delta_xi_norm_func(f_im, f_0) == pytest.approx(expected, abs=1e-4)


def test_approximation_error_formula():
    # relative error of xi ≈ 2·Δf/f0 equals (f − f0)/(f + f0)
    assert sm.sp.simplify(sm.delta_xi_norm - (sm.f - sm.f_0) / (sm.f + sm.f_0)) == 0
