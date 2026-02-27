#!/usr/bin/env python3

import argparse
import json
from collections.abc import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import zarr
from path import Path
from stepup.core.api import amend


def cases() -> Iterator[tuple[str, int, str, str]]:
    amend(inp="kernels.json")
    with open("kernels.json") as fh:
        kernels = json.load(fh)
    for kernel, models in kernels.items():
        for nseq in [64]:
            for model in models:
                yield kernel, nseq, model


def main():
    args = parse_args()
    run(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot as a function of the cutoff frequency and effective number of points.",
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
        "svg_cutoff",
        type=Path,
        help="Output SVG file for the cutoff plot",
    )
    return parser.parse_args()


def run(args: argparse.Namespace):
    if not args.svg_cutoff.endswith(".svg"):
        raise RuntimeError("Output file must be an SVG file.")

    # Get reference value from Zarr file
    if args.kernel not in args.zarr.stem:
        raise RuntimeError("Zarr file does not match the specified kernel.")
    store = zarr.storage.ZipStore(args.zarr)
    root = zarr.open_group(store=store, mode="r")
    ref = root.attrs[args.quantity]

    # Preprocess summary files
    paths_json = {}
    for path_json in args.summaries:
        words = path_json.stem.split("_")
        if words[0] != "summary":
            raise RuntimeError(f"Unexpected summary file name: {path_json}")
        if words[1] != args.kernel:
            raise RuntimeError(f"Unexpected kernel in summary file name: {path_json}")
        nstep = int(words[2].replace("nstep", ""))
        nseq = int(words[3].replace("nseq", ""))
        if nseq != 64:
            raise RuntimeError(f"Unexpected nseq in summary file name: {path_json}")
        paths_json[nstep] = path_json

    mpl.rc_file(args.mplrc)
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for nstep, path_json in sorted(paths_json.items()):
        # Load data
        with open(path_json) as fh:
            data = json.load(fh)

        # Take relevant arrays
        fcuts = np.asarray(data["fcut"])
        neffs = np.asarray(data["neff"])
        values = np.asarray(data[args.quantity]) / ref
        values_std = np.asarray(data[f"{args.quantity}_std"]) / ref

        # Plot
        lc = ax1.errorbar(
            neffs,
            values,
            values_std,
            fmt="o",
            lw=1,
            ms=2,
            ls="none",
            label=f"$N = {nstep}$",
        )
        lc = ax2.errorbar(
            fcuts,
            values,
            values_std,
            fmt="o",
            lw=1,
            ms=2,
            ls="none",
            label=f"$N = {nstep}$",
        )
        for ax in ax1, ax2:
            ax.axhline(np.mean(values), color=lc[0].get_color())

    ax1.set_xlabel("Effective number of points")
    ax2.set_xlabel("Cutoff frequency")
    for ax in ax1, ax2:
        ax.set_xscale("log")
        ax.set_ylabel("Relative error")
    fig.savefig(args.svg_cutoff)


if __name__ == "__main__":
    main()
