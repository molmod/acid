#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Testing stationarity of the trajectories using the Cramér-von Mises test."""

import argparse
import json
import zipfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from path import Path
from scipy.stats import cramervonmises, norm


def main():
    args = parse_args()
    run(args.mplrc, args.zip_in, args.codec, args.settings, args.svg_out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stationarity test via CvM at relative time points."
    )
    parser.add_argument("mplrc", type=Path, help="The matplotlibrc path.")
    parser.add_argument("zip_in", type=Path, help="The kernel ZIP archive.")
    parser.add_argument("codec", type=Path, help="The codec ZIP to decode integers to floats.")
    parser.add_argument("settings", type=Path, help="The settings.json file.")
    parser.add_argument("svg_out", type=Path, help="Output SVG path for the QQ plot.")
    return parser.parse_args()


def run(
    path_mplrc: Path,
    path_kernel: Path,
    path_codec: Path,
    path_settings: Path,
    path_svg: Path,
):
    """
    Pool trajectories across all nsteps, nseqs, and seeds, then run the
    Cramér-von Mises test for the trajectory at early, mid, and late
    times.

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
    path_svg
        Output SVG path for the QQ plots.
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
                    pool[frac].append(traj[:, idx])

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

    plot_qq(results, std, path_svg)


def plot_qq(results, std, path_svg):
    fig, ax = plt.subplots()

    # Upper limit on the number of points in the plot
    max_points = 5000

    for result in results:
        empirical_qs = result["x_sorted"]
        label = (
            rf"$t/N = {result['time']:.2f}$  "
            rf"($p = {result['pvalue']:.3f}$, "
            rf"$T = {result['statistic']:.3f}$)"
        )

        nsamples = len(empirical_qs)
        probs = (np.arange(1, nsamples + 1) - 0.5) / nsamples
        theoretical_qs = norm(scale=std).ppf(probs)

        # Reduce the number of datapoints in the plot
        if nsamples > max_points:
            idx = np.linspace(0, nsamples - 1, max_points).astype(int)
            empirical_qs = empirical_qs[idx]
            theoretical_qs = theoretical_qs[idx]

        ax.scatter(theoretical_qs, empirical_qs, s=0.5, label=label, alpha=0.6)

    lim = np.max(np.abs(ax.get_xlim() + ax.get_ylim()))
    ax.plot([-lim, lim], [-lim, lim], color="black", linewidth=0.6, linestyle=":", label="y=x")
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Empirical quantiles")
    ax.legend(fontsize="x-small", markerscale=1)

    fig.savefig(path_svg)
    plt.close(fig)


if __name__ == "__main__":
    main()
