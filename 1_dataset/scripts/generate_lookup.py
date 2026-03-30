#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Generate a lookup table to facilitate the decoding of the integers"""

import argparse
import zipfile

import numpy as np
import scipy as sp
from path import Path
from utils import dump_npy

SEQ_DTYPE = np.uint16
IMAX = np.iinfo(SEQ_DTYPE).max + 1


def main():
    args = parse_args()
    run(args.zip_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Write a .npy file for the mapping of the integers to floats."
    )
    parser.add_argument(
        "zip_out",
        type=Path,
        help="The output zip path that contains both the mapping with boundary and midpoint bins.",
    )
    return parser.parse_args()


def run(zip_out: Path):
    cdf = np.array(range(IMAX))
    ppf_boundary = sp.stats.norm(scale=1.0).ppf((cdf[1:]) / IMAX).astype(np.float32)
    ppf_mid = sp.stats.norm(scale=1.0).ppf((cdf + 0.5) / IMAX).astype(np.float32)
    with zipfile.ZipFile(zip_out, mode="w") as zf:
        dump_npy("boundary.npy", zf, ppf_boundary)
        dump_npy("midpoint.npy", zf, ppf_mid)


if __name__ == "__main__":
    main()
