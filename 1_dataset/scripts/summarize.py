#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Write a CSV file with a summary of the kernels"""

import argparse
from runpy import run_path

import numpy as np
from path import Path
from stepup.core.api import amend, loadns


def main():
    args = parse_args()
    run(args.settings, args.out)


def parse_args():
    parser = argparse.ArgumentParser(description="Write a CSV file with a summary of the kernels")
    parser.add_argument(
        "settings",
        type=Path,
        help="The settings JSON path.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="The output CSV path.",
    )
    return parser.parse_args()


def run(inp: Path, out: Path):
    with open(out, "w") as fh:
        settings = loadns(inp)
        for kernel in settings.kernels:
            path_py = f"kernels/{kernel}.py"
            amend(inp=path_py)
            terms = run_path(path_py)["terms"]
            typst = " + ".join(term.typst for term in terms)
            latex = " + ".join(term.latex for term in terms)
            acint = 0
            variance = 0
            for term in terms:
                acf, psd = term.compute(np.zeros(1), np.zeros(1))
                acint += psd[0]
                variance += acf[0]
            corrtime_int = 0.5 * acint / variance
            print(f'"{kernel}","{typst}","{latex}",{corrtime_int:.3f}', file=fh)


if __name__ == "__main__":
    main()
