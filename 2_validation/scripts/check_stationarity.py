#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Testing stationarity of the trajectories using the Cramér-von Mises test."""

import argparse
import json
import zipfile

import numpy as np
from path import Path
from scipy.stats import cramervonmises


def main():
    args = parse_args()
    run(args.zip_in, args.codec, args.settings, args.npz_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stationarity test via CvM at different relative times."
    )
    parser.add_argument("zip_in", type=Path, help="The kernel ZIP archive.")
    parser.add_argument("codec", type=Path, help="The codec ZIP to decode integers to floats.")
    parser.add_argument("settings", type=Path, help="The settings.json file.")
    parser.add_argument("npz_out", type=Path, help="The output NPZ path.")
    return parser.parse_args()


REL_TIMES = [0.0, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9]


def run(
    path_kernel: Path,
    path_codec: Path,
    path_settings: Path,
    path_npz: Path,
):
    """
    Pool trajectories across all nseqs and seeds, at the longest available sequence length,
    then run the Cramér-von Mises test at each relative time.

    Parameters
    ----------
    path_kernel
        ZIP archive containing the sequences and reference ACFs.
    path_codec
        Codec ZIP used to decode integer sequences to floating-point values.
    path_settings
        JSON file with nseed, nseqs, nsteps.
    path_npz
        Output NPZ path to store the results.
    """
    lookup_table = np.load(path_codec)["midpoint"]

    with open(path_settings) as f:
        settings = json.load(f)

    nseed = settings["nseed"]
    nseqs = settings["nseqs"]
    nstep = max(settings["nsteps"])  # only the longest available sequence length

    with zipfile.ZipFile(path_kernel) as zf, zf.open("meta.json") as f:
        meta = json.load(f)

    var = meta["var"]
    std = np.sqrt(var)

    unzipped_kernel = np.load(path_kernel)

    ireltime = {reltime: round(reltime * (nstep - 1)) for reltime in REL_TIMES}
    pool = {reltime: [] for reltime in REL_TIMES}

    for nseq in nseqs:
        for iseed in range(nseed):
            seq_path = f"nstep{nstep:05d}/nseq{nseq:04d}/sequences_{iseed:02d}.npy"
            cdfi = unzipped_kernel[seq_path]
            traj = lookup_table[cdfi] * std
            for reltime, idx in ireltime.items():
                pool[reltime].append(traj[:, idx].copy())

    pvalues = np.zeros(len(REL_TIMES))

    for i, frac in enumerate(REL_TIMES):
        x = np.concatenate(pool[frac])
        z = x / std
        cvm = cramervonmises(z, "norm")
        pvalues[i] = cvm.pvalue

    np.savez(path_npz, reltimes=np.array(REL_TIMES), pvalues=pvalues, allow_pickle=False)


if __name__ == "__main__":
    main()
