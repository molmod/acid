#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Write a CSV file with a summary of the kernels"""

import argparse
from runpy import run_path

from kernels import summarize
from path import Path
from stepup.core.api import amend, loadns


def main():
    args = parse_args()
    run(args.settings, args.out)


def parse_args():
    parser = argparse.ArgumentParser(description="Write a CSV file with a summary of the kernels")
    parser.add_argument("settings", type=Path, help="The settings JSON path.")
    parser.add_argument("out", type=Path, help="The output CSV path.")
    return parser.parse_args()


def run(inp: Path, out: Path):
    settings = loadns(inp)
    with open(out, "w") as fh:
        for kernel in settings.kernels:
            path_py = f"kernels/{kernel}.py"
            amend(inp=path_py)
            summary = summarize(run_path(path_py)["terms"])
            corrtime_exp = summary.corrtime_exp
            corrtime_exp_str = "/" if corrtime_exp is None else f"{corrtime_exp:.3f}"
            print(
                f'"{kernel}","{summary.typst}","{summary.latex}",'
                f"{summary.var:.3f},{summary.acint:.3f},{summary.corrtime_int:.3f},"
                f'"{corrtime_exp_str}",{summary.t90},{summary.f90:.3f}',
                file=fh,
            )


if __name__ == "__main__":
    main()
