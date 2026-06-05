#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Validate the encoding and decoding scheme by comparing sampled PSDs against
the reference PSD derived from the covariance matrix.
"""

import argparse
from runpy import run_path

import numpy as np
import scipy.linalg
from kernels import compute, sample
from path import Path
from stepup.core.api import amend
from utils import compute_amplitudes, generate_codec, lookup_integer

RESOLUTIONS = [2**10, 2**12, 2**14, 2**16, 2**18]

NSTEP = 1024
NSEQ = 256 * 64


def main():
    args = parse_args()
    run(args.kernel_name, args.npz_out)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate codec via Toeplitz-based reference PSD.")
    parser.add_argument("kernel_name", type=str, help="The kernel name.")
    parser.add_argument("npz_out", type=Path, help="The output NPZ path.")
    return parser.parse_args()


def run(kernel_name: str, path_npz: Path):
    """
    Compare the PSD of sampled trajectories with the reference PSD,
    and quantify the error introduced by the codec at different resolutions.

    Parameters
    ----------
    kernel_name
        The name of the kernel.
    path_npz
        Output NPZ path to store the results.
    """
    path_py = f"../1_dataset/kernels/{kernel_name}.py"
    amend(inp=path_py)
    terms = run_path(path_py)["terms"]

    # Compute analytical ACF and std
    times = np.arange(NSTEP, dtype=float)
    freqs = np.fft.rfftfreq(NSTEP)
    _, acf_anal, _, _, _, _, _ = compute(terms, freqs, times)
    std = np.sqrt(acf_anal[0])

    covar = scipy.linalg.toeplitz(acf_anal)
    # Compute F ACF F^dagger via two FFTs
    transformed_covar = np.fft.fft(np.fft.ifft(covar, axis=1), axis=0)

    # Keep only positive-frequency terms of the diagonal
    psd_ref = np.real(np.diag(transformed_covar))[: NSTEP // 2 + 1]

    # Sample trajectories
    seed = np.frombuffer(kernel_name.encode("ascii"), dtype=np.uint8)
    rng = np.random.default_rng(seed)
    traj_raw = sample(terms, NSEQ, NSTEP, rng)

    # PSD of raw float trajectories
    psd_raw = compute_amplitudes(traj_raw)
    rmse_raw = np.sqrt(np.mean((psd_raw - psd_ref) ** 2))

    # PSD of codec-encoded trajectories at each resolution
    rmse_ref_per_resolution = {}
    rmse_raw_per_resolution = {}
    for resolution in RESOLUTIONS:
        boundary, midpoint = generate_codec(resolution)
        indices = lookup_integer(traj_raw, std, boundary)
        traj_coded = midpoint[indices] * std
        psd_coded = compute_amplitudes(traj_coded)
        rmse_ref_per_resolution[resolution] = np.sqrt(np.mean((psd_coded - psd_ref) ** 2))
        rmse_raw_per_resolution[resolution] = np.sqrt(np.mean((psd_coded - psd_raw) ** 2))

    np.savez(
        path_npz,
        rmse_ref_per_resolution=rmse_ref_per_resolution,
        rmse_raw=rmse_raw,
        rmse_raw_per_resolution=rmse_raw_per_resolution,
    )


if __name__ == "__main__":
    main()
