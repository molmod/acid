#!/usr/bin/env python3
"""Generate a lookup table to facilitate the decoding of the integers"""

import argparse

import numpy as np
import scipy as sp
from path import Path

SEQ_DTYPE = np.uint16
IMAX = np.iinfo(SEQ_DTYPE).max + 1


def main():
    args = parse_args()
    run(args.boundary_out, args.midpoint_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Write a .npy file for the mapping of the integers to floats"
    )

    parser.add_argument(
        "boundary_out",
        type=Path,
        help="The output npy path for the mapping with boundary bins.",
    )
    parser.add_argument(
        "midpoint_out",
        type=Path,
        help="The output npy path for mapping with midpoint bins.",
    )
    return parser.parse_args()


def run(boundary_out: Path, midpoint_out: Path):
    cdf = np.array(range(IMAX))

    ppf_boundary = sp.stats.norm(scale=1.0).ppf((cdf) / IMAX).astype(np.float32)
    np.save(boundary_out, ppf_boundary)

    ppf_mid = sp.stats.norm(scale=1.0).ppf((cdf + 0.5) / IMAX).astype(np.float32)
    np.save(midpoint_out, ppf_mid)


if __name__ == "__main__":
    main()
