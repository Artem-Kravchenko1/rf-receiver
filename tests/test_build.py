import pytest

from fm_receiver import build


def test_build_runs_export_steps_in_order(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        build.export, "export_all_figures", lambda path: calls.append(("figures", path))
    )
    monkeypatch.setattr(
        build.export, "export_all_data", lambda path: calls.append(("data", path))
    )
    monkeypatch.setattr(
        build.export, "export_animation", lambda path: calls.append(("animation", path))
    )

    build.main(["--skip-tests", "--no-report", "--results", str(tmp_path)])

    assert calls == [
        ("figures", tmp_path / "figures"),
        ("data", tmp_path / "data"),
        ("animation", tmp_path / "animations"),
    ]


def test_build_needs_report_source(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no report.qmd here
    for name in ("export_all_figures", "export_all_data", "export_animation"):
        monkeypatch.setattr(build.export, name, lambda path: None)

    with pytest.raises(SystemExit, match="report.qmd not found"):
        build.main(["--skip-tests"])
