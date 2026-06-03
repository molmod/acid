#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Testing whether the trajectories are samples of the desired distributions,
using the Cramér-von Mises test"""

import argparse
import json
import zipfile

import matplotlib as mpl
import numpy as np
from path import Path
from scipy.stats import cramervonmises


def main():
    args = parse_args()
    run(args.mplrc, args.zip_in, args.codec, args.settings, args.npz_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cramér-von Mises test on the sampled trajectories."
    )
    parser.add_argument("mplrc", type=Path, help="The matplotlibrc path.")
    parser.add_argument("zip_in", type=Path, help="The kernel ZIP archive.")
    parser.add_argument("codec", type=Path, help="The codec ZIP to decode integers to floats.")
    parser.add_argument("settings", type=Path, help="The settings.json file.")
    parser.add_argument("npz_out", type=Path, help="The output NPZ path.")
    return parser.parse_args()


def run(
    path_mplrc: Path,
    path_kernel: Path,
    path_codec: Path,
    path_settings: Path,
    path_npz: Path,
):
    """
    Pool trajectories across all nsteps, nseqs, and seeds, then run the
    Cramér-von Mises test for each desired time lag.

    Parameters
    ----------
    path_mplrc
        Path to the matplotlib configuration file.
    path_kernel
        ZIP archive containing the sequences and reference ACFs.
    path_codec
        Codec ZIP used to decode integer sequences to floating-point values.
    path_settings
        JSON file with nseed, nseqs, nsteps.
    path_npz
        Output NPZ path to store the results.
    """
    mpl.rc_file(path_mplrc)

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
    dt_max = max(nsteps) - 1

    # Small time lags have the largest covariances and are therefore sampled more densely.
    dts = np.unique(
        np.concatenate(
            (
                np.linspace(1, 50, 50),
                np.linspace(56, 256, 150),
                np.geomspace(256, dt_max, dt_max // 256 * 2),
            )
        ).astype(int)
    )

    acf_path = f"nstep{max(nsteps):05d}/acf.npy"

    unzipped_kernel = np.load(path_kernel)
    acf = unzipped_kernel[acf_path]

    pool = {dt: [] for dt in dts}

    for nstep in nsteps:
        valid_dts = dts[dts < nstep]
        if len(valid_dts) == 0:
            continue
        for nseq in nseqs:
            for iseed in range(nseed):
                seq_path = f"nstep{nstep:05d}/nseq{nseq:04d}/sequences_{iseed:02d}.npy"
                cdfi = unzipped_kernel[seq_path]
                traj = lookup_table[cdfi] * std

                seed = np.frombuffer(seq_path.encode("ascii"), dtype=np.uint8)
                rng = np.random.default_rng(seed)
                for dt in valid_dts:
                    t0 = rng.integers(0, nstep - dt)
                    pool[dt].append(traj[:, t0 + dt] - traj[:, t0])

    results = []

    for dt, samples in pool.items():
        y = np.concatenate(samples)
        cov = acf[dt]
        var_y = 2 * (var - cov)

        # Time lags with low covariance are excluded, as for these lags var_y approaches 2 * var
        # and the statistics of y are dominated by the variance rather than correlations.
        # In this regime, the test effectively reduces to probing stationarity,
        # which is already tested elsewhere.
        low_covar = abs(cov) <= 1e-8

        if var_y < 0:
            raise ValueError("Negative variance encountered.")

        if var_y == 0:
            raise ValueError("Zero variance encountered.")

        # Standardize
        z = y / np.sqrt(var_y)

        # Test whether the z follows the standard normal distribution
        cvm = cramervonmises(z, "norm")
        results.append(
            {
                "dt": dt,
                "pvalue": cvm.pvalue,
                "low_covar": low_covar,
            }
        )

    filtered_pvals = np.array([r["pvalue"] for r in results if not r["low_covar"]])

    # Test whether the p-values follow the U(0,1) distribution
    p_distr_test = cramervonmises(filtered_pvals, "uniform")
    if p_distr_test.pvalue < 0.05:
        raise RuntimeError(
            "The p-values do not follow the uniform distribution U(0,1),\n"
            f"for n_pvals = {len(filtered_pvals)}, p-value = {p_distr_test.pvalue:.6f}."
        )

    np.savez(path_npz, results=results, p_value=p_distr_test.pvalue)


if __name__ == "__main__":
    main()
