#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Tabulate the stationarity CvM test results into a CSV."""

import argparse

import numpy as np
from path import Path


def main():
    args = parse_args()
    run(args.stat_npz_paths, args.csv_out)


def parse_args():
    parser = argparse.ArgumentParser(description="Tabulate stationarity test results into a CSV.")
    parser.add_argument(
        "stat_npz_paths",
        type=Path,
        nargs="+",
        help="The paths to the stationarity NPZ files.",
    )
    parser.add_argument("csv_out", type=Path, help="Output CSV path for the stationarity results.")
    return parser.parse_args()


def run(paths_stat_npz, path_csv):
    header = None
    with open(path_csv, "w") as fh:
        for stat_npz in paths_stat_npz:
            kernel = stat_npz.stem.split("_")[0]
            data = np.load(stat_npz)
            reltimes = data["reltimes"]
            pvalues = data["pvalues"]

            if header is None:
                header = [""]  # Empty string to keep all rows the same length
                header.extend(f"{reltime:.2f}" for reltime in reltimes)
                print(",".join(header), file=fh)

            fields = [kernel]
            fields.extend(f"{pvalue:.3f}" for pvalue in pvalues)
            print(",".join(fields), file=fh)


if __name__ == "__main__":
    main()
