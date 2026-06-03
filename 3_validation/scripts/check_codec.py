#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Validate the encoding and decoding scheme by comparing sampled PSDs against
the analytical PSD derived from the Toeplitz covariance matrix.
"""

import argparse
from runpy import run_path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg
from kernels import compute, sample
from path import Path
from stepup.core.api import amend
from utils import compute_amplitudes, generate_codec, lookup_integer

# Production resolution (uint16)
RESOLUTION_PRODUCTION = 2**16

RESOLUTIONS = [2**10, 2**12, 2**14, RESOLUTION_PRODUCTION, 2**18]

NSTEP = 1024
NSEQ = 256 * 64
NSEQ = 256


def main():
    args = parse_args()
    run(args.mplrc, args.kernel_name, args.svg_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate codec via Toeplitz-based analytical PSD."
    )
    parser.add_argument("mplrc", type=Path, help="The matplotlibrc path.")
    parser.add_argument("kernel_name", type=str, help="The kernel name.")
    parser.add_argument("svg_out", type=Path, help="Output SVG path.")
    return parser.parse_args()


def run(path_mplrc: Path, kernel_name: str, path_svg: Path):
    mpl.rc_file(path_mplrc)

    path_py = f"../1_dataset/kernels/{kernel_name}.py"
    amend(inp=path_py)
    terms = run_path(path_py)["terms"]

    # Compute analytical ACF and std
    times = np.arange(NSTEP, dtype=float)
    freqs = np.fft.rfftfreq(NSTEP)
    _, acf_anal, _, _, _, _, _ = compute(terms, freqs, times)
    std = np.sqrt(acf_anal[0])

    covar = scipy.linalg.toeplitz(acf_anal)
    # Compute F ACF F^dagger via two FFTs:
    transformed_covar = np.fft.fft(np.fft.ifft(covar, axis=1), axis=0)

    # Keep only positive-frequency terms
    psd_anal = np.real(np.diag(transformed_covar))[: NSTEP // 2 + 1]

    # Sample trajectories
    seed = np.frombuffer(kernel_name.encode("ascii"), dtype=np.uint8)
    rng = np.random.default_rng(seed)
    traj_raw = sample(terms, NSEQ, NSTEP, rng)

    # PSD of raw float trajectories
    psd_raw = compute_amplitudes(traj_raw)
    rmse_raw = float(np.sqrt(np.mean((psd_raw - psd_anal) ** 2)))

    # PSD of codec-encoded trajectories at each resolution
    rmse_per_resolution = {}
    for resolution in RESOLUTIONS:
        boundary, midpoint = generate_codec(resolution)
        indices = lookup_integer(traj_raw, std, boundary)
        traj_coded = midpoint[indices] * std
        psd_coded = compute_amplitudes(traj_coded)
        rmse_per_resolution[resolution] = float(np.sqrt(np.mean((psd_coded - psd_anal) ** 2)))

    plot(rmse_raw, rmse_per_resolution, path_svg)


def plot(
    rmse_raw: float,
    rmse_per_resolution: dict,
    path_svg: Path,
) -> None:
    fig, (ax_rmse, ax_diff) = plt.subplots(2, 1, sharex=True)

    resolutions = list(rmse_per_resolution.keys())
    rmses = np.array([rmse_per_resolution[r] for r in resolutions])
    diffs = np.abs(rmses - rmse_raw)
    prod_idx = list(resolutions).index(RESOLUTION_PRODUCTION)

    ax_rmse.axhline(rmse_raw, color="r", linestyle="--", linewidth=0.8, label="Float precision")
    ax_rmse.plot(resolutions, rmses, marker="o", markersize=4, linewidth=1, color="k")
    ax_rmse.plot(
        RESOLUTION_PRODUCTION,
        rmses[prod_idx],
        marker="o",
        markersize=4,
        color="r",
        label="Production resolution",
    )
    ax_rmse.set_xscale("log", base=2)
    ax_rmse.set_ylabel("Absolute RMSE")
    ax_rmse.set_xticks(resolutions)
    ax_rmse.set_xticklabels([f"$2^{{{int(np.log2(r))}}}$" for r in resolutions])
    ax_rmse.legend()

    ax_diff.plot(
        resolutions,
        diffs,
        marker="o",
        markersize=4,
        linewidth=1,
        color="k",
    )
    ax_diff.plot(
        RESOLUTION_PRODUCTION,
        diffs[prod_idx],
        marker="o",
        markersize=4,
        color="r",
        label="Production resolution",
    )
    ax_diff.set_xscale("log", base=2)
    ax_diff.set_yscale("log")
    ax_diff.set_xlabel("Codec resolution (number of bins)")
    ax_diff.set_ylabel(r"$|\mathrm{RMSE}_\mathrm{codec} - \mathrm{RMSE}_\mathrm{float}|$")
    ax_diff.set_xticks(resolutions)
    ax_diff.set_xticklabels([f"$2^{{{int(np.log2(r))}}}$" for r in resolutions])

    fig.savefig(path_svg)
    plt.close(fig)


if __name__ == "__main__":
    main()
