#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from path import Path


def main():
    args = parse_args()
    for path_svg in [args.svg_acf_consist]:
        if not path_svg.endswith(".svg"):
            raise ValueError(f"Output path {path_svg} must end with .svg")
    run(
        args.mplrc,
        args.npz_paths,
        args.svg_acf_consist,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Plot validation plots.")
    parser.add_argument(
        "mplrc",
        type=Path,
        help="The matplotlibrc path.",
    )
    parser.add_argument(
        "acf_consist_npz_paths",
        type=Path,
        nargs="+",
        help="The paths to the NPZ files with the data for the acf_consist plots.",
    )
    parser.add_argument(
        "svg_acf_consist",
        type=Path,
        help="Output SVG path for the Cramér-von Mises plot.",
    )

    return parser.parse_args()


def run(
    path_mplrc: Path,
    paths_npzs: Path,
    path_svg_acf_consist: Path,
):
    mpl.rc_file(path_mplrc)
    fig1, axs1 = plt.subplots(8, 3, figsize=(7, 10))

    for i, path_kernel in enumerate(paths_npzs):
        row = i // 3
        col = i % 3
        plot_acf_consist(axs1[2 * row, col], axs1[2 * row + 1, col], path_kernel)

    fig1.savefig(path_svg_acf_consist)


def plot_acf_consist(ax_p, ax_hist, npz):
    data = np.load(npz, allow_pickle=True)
    results = data["results"]
    p_distr_pvalue = data["p_value"]

    # Split data based on the covar
    low_covar = [r for r in results if r["low_covar"]]
    normal_covar = [r for r in results if not r["low_covar"]]

    dts_normal = np.array([r["dt"] for r in normal_covar])
    pvals_normal = np.array([r["pvalue"] for r in normal_covar])
    dts_low = np.array([r["dt"] for r in low_covar])
    pvals_low = np.array([r["pvalue"] for r in low_covar])

    ax_p.scatter(dts_normal, pvals_normal, marker="o", color="k", s=2)
    if len(dts_low):
        ax_p.scatter(dts_low, pvals_low, marker="o", s=2, color="lightgray", label="low covar")
    ax_p.axhline(0.05, color="red", linestyle="--", linewidth=0.8, label=r"$\alpha = 0.05$")
    ax_p.set_ylabel(r"$p$-value")
    ax_p.legend(fontsize="x-small", loc="right", framealpha=0.6)
    ax_p.set_xscale("log")
    ax_p.set_xlabel("Time lag")
    ax_p.set_title(npz.stem.split("_")[0])

    # p-dist histogram
    ax_hist.hist(pvals_normal, bins=10, range=(0, 1), color="k", density=True, alpha=0.8)
    ax_hist.axhline(1.0, color="red", linestyle="--", label="Uniform density")
    ax_hist.set_xlabel(r"$p$-value")
    ax_hist.set_ylabel("Density")
    ax_hist.text(
        0.03,
        0.95,
        rf"$p_{{U(0,1)}} = {p_distr_pvalue:.3f}$",
        transform=ax_hist.transAxes,
        fontsize="small",
        va="top",
        bbox={
            "facecolor": "white",
            "edgecolor": "lightgrey",
            "alpha": 0.8,
        },
    )


if __name__ == "__main__":
    main()
