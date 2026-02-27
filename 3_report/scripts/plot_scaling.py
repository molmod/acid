#!/usr/bin/env python3
"""Plot scaling of statistics."""

import argparse
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import zarr
from path import Path
from stepup.core.api import loadns


def main():
    args = parse_args()
    run(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot scaling of statistics.",
    )
    parser.add_argument(
        "kernel",
        type=str,
        help="Kernel name",
    )
    parser.add_argument(
        "quantity",
        type=str,
        choices=["acint", "corrtime_exp"],
        help="Quantity to plot",
    )
    parser.add_argument(
        "settings",
        type=Path,
        help="ACID settings JSON file",
    )
    parser.add_argument(
        "zarr",
        type=Path,
        help="The Zarr ZIP file with full data, used to get reference values",
    )
    parser.add_argument(
        "mplrc",
        type=Path,
        help="Matplotlib rc file",
    )
    parser.add_argument(
        "summaries",
        type=Path,
        nargs="+",
        help="List of JSON summary files",
    )
    parser.add_argument(
        "svg_scaling",
        type=Path,
        help="Output SVG file for scaling plot",
    )
    parser.add_argument(
        "svg_ratios",
        type=Path,
        help="Output SVG file for ratios plot",
    )
    parser.add_argument(
        "csv_stats",
        type=Path,
        help="Output CSV file with the statistics shown in the plots.",
    )
    parser.add_argument(
        "json_stats",
        type=Path,
        help="Output JSON file with the statistics shown in the plots.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace):
    if not args.svg_scaling.endswith(".svg"):
        raise RuntimeError("Output scaling file must be an SVG file.")
    if not args.svg_ratios.endswith(".svg"):
        raise RuntimeError("Output ratios file must be an SVG file.")
    if not args.csv_stats.endswith(".csv"):
        raise RuntimeError("Output stats file must be a CSV file.")
    if not args.json_stats.endswith(".json"):
        raise RuntimeError("Output stats file must be a JSON file.")

    # Get reference value from Zarr file
    if args.kernel not in args.zarr.stem:
        raise RuntimeError("Zarr file does not match the specified kernel.")
    store = zarr.storage.ZipStore(args.zarr)
    root = zarr.open_group(store=store, mode="r")
    ref = root.attrs[args.quantity]

    # Preprocess inputs
    settings = loadns(args.settings)
    paths_json = {}
    for path_json in args.summaries:
        words = path_json.stem.split("_")
        if words[0] != "summary":
            raise RuntimeError(f"Unexpected summary file name: {path_json}")
        if words[1] != args.kernel:
            raise RuntimeError(f"Unexpected kernel in summary file name: {path_json}")
        nstep = int(words[2].replace("nstep", ""))
        nseq = int(words[3].replace("nseq", ""))
        paths_json[(nstep, nseq)] = path_json

    mpl.rc_file(args.mplrc)
    colors = list(plt.rcParams["axes.prop_cycle"].by_key()["color"])[: len(settings.nsteps)]
    step_corrs = [-0.3, -0.1, 0.1, 0.3]

    fig0, ax0 = plt.subplots()
    fig1, ax1 = plt.subplots()
    value_min = None
    value_max = None
    rows = []
    for nstep, step_corr, color in zip(settings.nsteps, step_corrs, colors, strict=True):
        xs = []
        value_std = []
        value_rmspe = []
        value_bias = []
        for nseq in settings.nseqs:
            if (nstep, nseq) not in paths_json:
                continue

            path_json = paths_json[(nstep, nseq)]
            with open(path_json) as fh:
                data = json.load(fh)

            x = np.log2(nseq)
            xs.append(x)
            values = np.array(data[args.quantity]) / ref
            values_std = np.array(data[f"{args.quantity}_std"]) / ref
            if len(values) > 1:
                value_std.append(np.std(values))
                value_rmspe.append(rms(values_std))
                value_bias.append(values.mean() - 1.0)
                rows.append(
                    [
                        nstep,
                        nseq,
                        len(values),
                        value_std[-1],
                        value_rmspe[-1],
                        value_bias[-1],
                    ]
                )
            else:
                value_std.append(np.nan)
                value_rmspe.append(np.nan)
                value_bias.append(np.nan)
        xs = np.array(xs)
        value_std = np.array(value_std)
        value_rmspe = np.array(value_rmspe)
        value_bias = np.array(value_bias)

        # Plot scaling
        ax0.plot(xs, value_std, color=color, label=f"$N={nstep}$", lw=0, marker="s")
        ax0.plot(xs, value_rmspe, color=color, ls=":")
        value_min_curr = np.nanmin(np.concatenate([value_std, value_rmspe]))
        value_max_curr = np.nanmax(np.concatenate([value_std, value_rmspe]))
        if value_min is None or value_min_curr < value_min:
            value_min = value_min_curr
        if value_max is None or value_max_curr > value_max:
            value_max = value_max_curr
        # ax0.plot(xs + 0.25, abs(value_bias), color=color, lw=0, marker=".")

        # plot ratio statistics
        ax1.plot(
            step_corr + xs,
            100 * value_std / value_rmspe,
            color=color,
            lw=0,
            marker="s",
            label=f"$N={nstep}$",
        )
        ax1.plot(step_corr + xs, 100 * value_bias / value_rmspe, color=color, lw=0, marker=".")

    # Draw grid lines
    nseqs = np.array([0.5 * settings.nseqs[0], *settings.nseqs, 2 * settings.nseqs[-1]])
    xs = np.log2(nseqs)

    ax0.autoscale(False)
    for scale in 2.0 ** np.arange(-10, 50):
        ax0.plot(xs, scale / np.sqrt(nseqs), color="k", lw=0.5, alpha=0.2)
    ax0.set_ylim(value_min * 0.8, value_max * 1.2)
    ax0.set_yscale("log")
    ax0.set_ylabel("Relative error")
    ax0.legend()
    ax1.axhline(0, color="k", lw=0.5, alpha=0.2)
    ax1.axhline(100, color="k", lw=0.5, alpha=0.2)
    ax1.set_ylabel(r"$100 \times$ Empirical error / Predicted error")
    ax1.set_ylim(top=200)
    ax1.legend(ncols=2, loc="upper center")

    for ax in [ax0, ax1]:
        ax.set_xticks(xs[1:-1], [f"{2**x:.0f}" for x in xs[1:-1]])
        ax.set_xlim(xs[1] - 0.5, xs[-2] + 0.5)
        ax.set_xlabel("Number of sequences $M$")

    # Perform a simple analysis of the statistics and write a JSON file.
    stats = get_stats(rows, settings)
    with open(args.json_stats, "w") as fh:
        json.dump(stats, fh, indent=4)

    fig0.savefig(args.svg_scaling)
    plt.close(fig0)
    fig1.savefig(args.svg_ratios)
    plt.close(fig1)
    df = pd.DataFrame(rows, columns=["nstep", "nseq", "ncomplete", "std", "rmspe", "bias"])
    df.to_csv(args.csv_stats, index=False)


def get_stats(rows: list[list], settings) -> dict:
    nstep, nseq, ncomplete, std, rmspe, bias = np.array(rows).T
    w = np.sqrt(ncomplete)
    dm = (np.array([np.ones(len(nstep)), -np.log10(nseq), -np.log10(nstep)]) * w).T
    ev = np.log10(std) * w
    pars = np.linalg.lstsq(dm, ev, rcond=None)[0]
    ntotal = len(settings.nsteps) * len(settings.nseqs) * settings.nseed
    return {
        "frac_complete": float(np.sum(ncomplete) / ntotal),
        "log10_prefac": float(pars[0]),
        "coeff_nseq": float(pars[1]),
        "coeff_nstep": float(pars[2]),
        "mean_uc": float(np.mean(std / rmspe)),
        "rms_uc": rms(std / rmspe - 1),
        "mean_bias": float(np.mean(bias / rmspe)),
        "rms_bias": rms(bias / rmspe),
    }


def rms(x):
    return np.sqrt(np.mean(x**2))


if __name__ == "__main__":
    main()
