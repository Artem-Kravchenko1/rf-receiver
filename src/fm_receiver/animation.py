import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from fm_receiver import plots
from fm_receiver.model import DEFAULT_CP, DEFAULT_FP

DEFAULT_FRAMES_AMOUNT = 41

K_U_Y_LIMITS = (-45, 3)


def K_U_sweep_animation(
    frames_amount=DEFAULT_FRAMES_AMOUNT, cp=DEFAULT_CP, fp=DEFAULT_FP
):
    """K_U(f) while the circuit is retuned from f_min to f_max (one f_0 per frame)."""
    fig, ax = plt.subplots()
    f_0_values = np.linspace(fp.f_min, fp.f_max, frames_amount)

    def draw_frame(f_0):
        ax.clear()
        plots.K_U_of_f_ax(ax, f_0_params=(f_0,), cp=cp, fp=fp)
        ax.set_ylim(*K_U_Y_LIMITS)
        # labels near the right edge must not resize the axes, otherwise frames jump
        for text in ax.texts:
            text.set_in_layout(False)
        ax.legend(loc="lower left")

    animation = FuncAnimation(fig, draw_frame, frames=f_0_values)

    return fig, animation
