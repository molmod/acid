#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Sanity check for the standalone example script shown in the dataset overview."""

import argparse
from runpy import run_path

import numpy as np
from acidic.utils import compute_acfs, compute_amplitudes, compute_msds
from path import Path


def main():
    args = parse_args()
    run(args.example, args.data_dir)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the example script and compare its results with the acidic package."
    )
    parser.add_argument("example", type=Path, help="The example script to run.")
    parser.add_argument(
        "data_dir", type=Path, help="Directory with the dataset files used by the example."
    )
    return parser.parse_args()


def run(path_example: Path, data_dir: Path):
    """Run the example script in the data directory and validate its results.

    Parameters
    ----------
    path_example
        The example script, which reads hardcoded filenames.
    data_dir
        The directory containing the files read by the example script.
    """
    path_example = path_example.absolute()
    with data_dir:
        namespace = run_path(path_example)

    sequences = namespace["sequences"]
    if sequences.dtype != float:
        raise TypeError(f"Expected float sequences, got {sequences.dtype}")
    np.testing.assert_array_equal(namespace["acfs"], compute_acfs(sequences))
    np.testing.assert_array_equal(namespace["psds"], compute_amplitudes(sequences))
    np.testing.assert_array_equal(namespace["msds"], compute_msds(sequences))


if __name__ == "__main__":
    main()
