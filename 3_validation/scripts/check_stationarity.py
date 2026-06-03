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
        description="Stationarity test via CvM at relative time points."
    )
    parser.add_argument("zip_in", type=Path, help="The kernel ZIP archive.")
    parser.add_argument("codec", type=Path, help="The codec ZIP to decode integers to floats.")
    parser.add_argument("settings", type=Path, help="The settings.json file.")
    parser.add_argument("npz_out", type=Path, help="The output NPZ path.")
    return parser.parse_args()


def run(
    path_kernel: Path,
    path_codec: Path,
    path_settings: Path,
    path_npz: Path,
):
    """
    Pool trajectories across all nsteps, nseqs, and seeds, then run the
    Cramér-von Mises test for the trajectory at early, mid, and late
    times.

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
    nsteps = settings["nsteps"]

    with zipfile.ZipFile(path_kernel) as zf, zf.open("meta.json") as f:
        meta = json.load(f)

    var = meta["var"]
    std = np.sqrt(var)

    # Relative time points probing early, mid, and late trajectory
    time_fractions = [0.01, 0.5, 0.9]

    unzipped_kernel = np.load(path_kernel)

    pool = {frac: [] for frac in time_fractions}

    for nstep in nsteps:
        times = {frac: round(frac * (nstep - 1)) for frac in time_fractions}
        for nseq in nseqs:
            for iseed in range(nseed):
                seq_path = f"nstep{nstep:05d}/nseq{nseq:04d}/sequences_{iseed:02d}.npy"
                cdfi = unzipped_kernel[seq_path]
                traj = lookup_table[cdfi] * std
                for frac, idx in times.items():
                    pool[frac].append(traj[:, idx].copy())

    results = []

    for frac in time_fractions:
        x = np.concatenate(pool[frac])
        z = x / std
        cvm = cramervonmises(z, "norm")

        results.append(
            {
                "time": frac,
                "x_sorted": np.sort(x),
                "statistic": cvm.statistic,
                "pvalue": cvm.pvalue,
            }
        )

    np.savez(path_npz, results=results, std=std)


if __name__ == "__main__":
    main()
