import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from PIL import Image

from fm_receiver import export

EXPLORE_PATH = Path(__file__).parents[1] / "explore.py"


def test_animation_export(tmp_path):
    export.export_animation(str(tmp_path), frames_amount=3)
    gif = tmp_path / "K_U_sweep.gif"
    with Image.open(gif) as image:
        assert image.n_frames == 3
    assert plt.get_fignums() == []


# marimo itself uses an asyncio API deprecated in Python 3.14; not our code
@pytest.mark.filterwarnings("ignore::DeprecationWarning:marimo")
def test_explore_notebook_runs():
    spec = importlib.util.spec_from_file_location("explore", EXPLORE_PATH)
    explore = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(explore)

    _, defs = explore.app.run()

    stations_table = defs["stations_table"]
    assert len(stations_table) == 6
    assert (stations_table["status"] == "OK").all()
