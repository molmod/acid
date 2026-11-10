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
    for path_svg in [args.svg_acf_consist, args.svg_codec]:
        if not path_svg.endswith(".svg"):
            raise ValueError(f"Output path {path_svg} must end with .svg")

    if len(args.acf_consist_npz_paths) != len(args.codec_npz_paths):
        raise ValueError(
            "The number of acf_consist NPZ files must match the number of stationarity NPZ files"
        )

    run(
        args.mplrc,
        args.acf_consist_npz_paths,
        args.codec_npz_paths,
        args.svg_acf_consist,
        args.svg_codec,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Plot validation plots.")
    parser.add_argument(
        "mplrc",
        type=Path,
        help="The matplotlibrc path.",
    )
    parser.add_argument(
        "--acf_consist",
        dest="acf_consist_npz_paths",
        type=Path,
        nargs="+",
        help="The paths to the NPZ files with the data for the acf_consist plots.",
    )
    parser.add_argument(
        "--codec",
        dest="codec_npz_paths",
        type=Path,
        nargs="+",
        help="The paths to the NPZ files with the data for the codec validation plots.",
    )
    parser.add_argument(
        "svg_acf_consist",
        type=Path,
        help="Output SVG path for the Cramér-von Mises plot.",
    )
    parser.add_argument(
        "svg_codec",
        type=Path,
        help="Output SVG path for the codec validation plot.",
    )

    return parser.parse_args()


def run(
    path_mplrc: Path,
    paths_acf_consist_npz: Path,
    paths_codec_npz: Path,
    path_svg_acf_consist: Path,
    path_svg_codec: Path,
):
    mpl.rc_file(path_mplrc)
    fig1, axs1 = plt.subplots(8, 3, figsize=(7, 10))
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 10), sharex=True)

    for i, path_acf_npz in enumerate(paths_acf_consist_npz):
        row = i // 3
        col = i % 3
        plot_acf_consist(
            axs1[2 * row, col],
            axs1[2 * row + 1, col],
            path_acf_npz,
            col == 0,
            row == 0 and col == 2,
        )

        plot_codec(
            axs2[row, col],
            paths_codec_npz[i],
            row == 3,
            col == 0,
        )

    fig1.savefig(path_svg_acf_consist)
    fig2.savefig(path_svg_codec)


def plot_acf_consist(ax_p, ax_hist, npz, ylabel, legend):
    data = np.load(npz)
    p_distr_pvalue = data["p_distr_pvalue"]

    dts = data["dts"]
    pvalues = data["pvalues"]
    low_covars = data["low_covars"].astype(bool)

    dts_normal = dts[~low_covars]
    pvals_normal = pvalues[~low_covars]
    dts_low = dts[low_covars]
    pvals_low = pvalues[low_covars]

    ax_p.scatter(dts_normal, pvals_normal, marker="o", color="k", s=2)
    if len(dts_low):
        ax_p.scatter(dts_low, pvals_low, marker="o", s=2, color="lightgray", label="low covar")
    ax_p.axhline(0.05, color="red", linestyle="--", linewidth=0.8, label=r"$\alpha = 0.05$")

    if ylabel:
        ax_p.set_ylabel(r"$p$-value")

    if legend:
        ax_p.legend(fontsize="x-small", loc="right", framealpha=0.6)
    ax_p.set_xscale("log")
    ax_p.set_xlabel("Time lag")
    ax_p.set_title(npz.stem.split("_")[0])

    # p-dist histogram
    ax_hist.hist(pvals_normal, bins=10, range=(0, 1), color="k", density=True, alpha=0.8)
    ax_hist.set_xlabel(r"$p$-value")
    if ylabel:
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


def plot_codec(ax, npz, xlabel, ylabel):
    data = np.load(npz)
    resolutions = data["resolutions"]
    rmse_raw_per_seed = data["rmse_raw_per_seed"]
    rmse_codec_per_seed = data["rmse_codec_per_seed"]
    rmses_codec = rmse_codec_per_seed.mean(axis=1)

    # Production resolution (uint16)
    production_resolution = 2**16
    prod_idx = list(resolutions).index(production_resolution)

    ax.plot(resolutions, rmses_codec, marker="o", markersize=4, linewidth=1, color="k")
    ax.plot(production_resolution, rmses_codec[prod_idx], marker="o", markersize=4, color="r")
    ax.set_title(npz.stem.split("_")[0])
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    if xlabel:
        ax.set_xlabel(r"Encoding resolution $R$")
    if ylabel:
        ax.set_ylabel(r"$\mathrm{RMSE}(\bar{C}^{(R)}_{\text{codec}}, \bar{C}_{\text{float}})$")
    ax.set_xticks(resolutions)
    ax.set_xticklabels([f"$2^{{{int(np.log2(r))}}}$" for r in resolutions])

    rmse_baseline = rmse_raw_per_seed.mean()
    power10 = int(np.floor(np.log10(rmse_baseline)))
    coeff = rmse_baseline / 10**power10
    ax.text(
        0.98,
        0.9,
        (
            rf"$\mathrm{{RMSE}}(\bar{{C}}_{{\text{{float}}}}, C_{{\text{{ref}}}}) "
            rf"\approx {coeff:.2f} \times 10^{{{power10}}}$"
        ),
        transform=ax.transAxes,
        fontsize=mpl.rcParams["xtick.labelsize"],
        ha="right",
        va="top",
        bbox={"facecolor": "white", "edgecolor": "lightgrey", "alpha": 0.8},
    )


if __name__ == "__main__":
    main()
