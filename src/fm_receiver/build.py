"""Build everything with one command: `uv run fm-build`.

Steps: tests → figures, data and GIF in results/ → report.docx.
Run it from the project root (where report.qmd is).
"""

import argparse
import subprocess
import sys
from pathlib import Path

from fm_receiver import export

REPORT = Path("report.qmd")


def step(title):
    print(f"\n=== {title} ===", flush=True)


def run(command):
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        sys.exit(f"Failed: {' '.join(command)}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build figures, data, GIF and the report."
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="do not run pytest first"
    )
    parser.add_argument(
        "--no-report", action="store_true", help="do not render report.docx"
    )
    parser.add_argument(
        "--results", default="results", help="output folder (default: results)"
    )
    args = parser.parse_args(argv)

    results = Path(args.results)

    if not args.skip_tests:
        step("Tests")
        run([sys.executable, "-m", "pytest", "-q"])

    step("Figures")
    export.export_all_figures(results / "figures")
    step("Data")
    export.export_all_data(results / "data")
    step("Animation")
    export.export_animation(results / "animations")

    if not args.no_report:
        if not REPORT.exists():
            sys.exit(f"{REPORT} not found: run fm-build from the project root")
        step("Report")
        run(["quarto", "render", str(REPORT)])

    step("Done")
    print(f"results: {results.resolve()}")
    if not args.no_report:
        print(f"report:  {Path('report.docx').resolve()}")


if __name__ == "__main__":
    main()
