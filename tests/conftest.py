import matplotlib

matplotlib.use("Agg")  # draw into memory only, no windows during tests

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")
