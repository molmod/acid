#!/usr/bin/env python3
"""Plot results with STACIE for a given test case."""

import argparse
import pickle

import matplotlib as mpl
from path import Path
from stacie import UnitConfig, plot_results


def main():
    args = parse_args()
    run(args.inp, args.mplrc, args.out)


def run(inp: Path, mplrc: Path, out: Path):
    mpl.rc_file(mplrc)
    with open(inp, "rb") as fh:
        results = pickle.load(fh)
    unit_config = UnitConfig()
    plot_results(out, results, unit_config, figsize=(8, 5))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot results with STACIE for a given test case.")
    parser.add_argument(
        "inp",
        type=Path,
        help="Paths to the input pickle file.",
    )
    parser.add_argument(
        "mplrc",
        type=Path,
        help="Path to the matplotlib rc file to use.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="Path to the output figure file to store the results.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
