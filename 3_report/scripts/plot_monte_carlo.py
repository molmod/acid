#!/usr/bin/env python3

import argparse
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from path import Path
from stepup.core.api import loadns


def main():
    args = parse_args()
    run(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Monte Carlo parameter maps.",
    )
    parser.add_argument(
        "kernel",
        type=str,
        help="Kernel name",
    )
    parser.add_argument(
        "settings",
        type=Path,
        help="ACID settings JSON file",
    )
    parser.add_argument(
        "mplrc",
        type=Path,
        help="Matplotlib rc file",
    )
    parser.add_argument(
        "mcmaps",
        type=Path,
        nargs="+",
        help="List of JSON mcmap files",
    )
    parser.add_argument(
        "svg_mcmap",
        type=Path,
        help="Output SVG file for MC map plot",
    )
    return parser.parse_args()


def run(args):
    if not args.svg_mcmap.endswith(".svg"):
        raise RuntimeError("Output file must be an SVG file.")

    # Preprocess the JSON inputs
    settings = loadns(args.settings)
    paths_json = {}
    for path_json in args.mcmaps:
        words = path_json.stem.split("_")
        if words[0] != "mcmap":
            raise RuntimeError(f"Unexpected mcmap file name: {path_json}")
        if words[1] != args.kernel:
            raise RuntimeError(f"Unexpected kernel in mcmap file name: {path_json}")
        nstep = int(words[2].replace("nstep", ""))
        nseq = int(words[3].replace("nseq", ""))
        paths_json[(nstep, nseq)] = path_json

    # Set up the figure
    mpl.rc_file(args.mplrc)
    fig, axs = plt.subplots(len(settings.nsteps), len(settings.nseqs))

    # Loop over the input files and plot the data
    for irow, nstep in enumerate(settings.nsteps[::-1]):
        for icol, nseq in enumerate(settings.nseqs):
            path_json = paths_json[(nstep, nseq)]
            with open(path_json) as fh:
                data = json.load(fh)

            ax = axs[irow, icol]

            # Define a transformation to reduced parameters
            evals, evecs = np.linalg.eigh(data["map_pars_covar"])
            basis = evecs / np.sqrt(evals)
            points = np.dot(data["mc_samples"], basis)
            ax.plot(points[:, 0], points[:, 1], "k.", ms=1.5, mew=0, alpha=0.5)

            for key, color in ("map", "b"), ("mc", "r"):
                pars = np.dot(basis.T, data[f"{key}_pars"])
                covar = np.dot(basis.T, np.dot(data[f"{key}_pars_covar"], basis))
                ax.plot([pars[0]], [pars[1]], color + "+")
                evals, evecs = np.linalg.eigh(covar)
                coords = np.zeros((90, 2))
                for i in range(coords.shape[0]):
                    alpha = i * 2 * np.pi / coords.shape[0]
                    coords[i] = (
                        pars
                        + 2 * np.sqrt(evals[0]) * np.cos(alpha) * evecs[:, 0]
                        + 2 * np.sqrt(evals[1]) * np.sin(alpha) * evecs[:, 1]
                    )
                ax.plot(coords[:, 0], coords[:, 1], color=color)
            ax.set_aspect("equal", "datalim")
            ax.set_xticks([])
            ax.set_xticks([], minor=True)
            ax.set_yticks([])
            ax.set_yticks([], minor=True)
            if icol == 0:
                ax.set_ylabel(f"$N = {nstep}$")
            if irow == len(settings.nsteps) - 1:
                ax.set_xlabel(f"$M ={nseq}$")

    # Save the figure
    fig.savefig(args.svg_mcmap)
    plt.close(fig)


if __name__ == "__main__":
    main()
