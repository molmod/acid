#!/usr/bin/env python3

import json
from collections.abc import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from stepup.core.api import amend
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, str]]:
    amend(inp="kernels.json")
    with open("kernels.json") as fh:
        kernels = json.load(fh)
    yield from kernels


CASE_FMT = "{}"
INP_TEMPLATE = (
    "../validation-stacie-calc/output/mc_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_quad.npz"
)


def case_info(kernel: str) -> dict[str]:
    amend(inp="nsteps.json")
    with open("nsteps.json") as fh:
        nsteps = json.load(fh)
    amend(inp="nseqs.json")
    with open("nseqs.json") as fh:
        nseqs = json.load(fh)
    return {
        "inp": ["../matplotlibrc"]
        + [
            INP_TEMPLATE.format(kernel=kernel, nstep=nstep, nseq=nseq)
            for nstep in nsteps
            for nseq in nseqs
        ],
        "out": f"figures/plot_mc_{kernel}.svg",
        "kernel": kernel,
        "nsteps": nsteps,
        "nseqs": nseqs,
    }


def run(inp: list[str], out: str, kernel: str, nsteps: list[int], nseqs: list[int]):
    # Set up the figure
    mpl.rc_file(inp.pop(0))
    fig, axs = plt.subplots(len(nsteps), len(nseqs))

    # Loop over the input files and plot the data
    for irow, nstep in enumerate(nsteps[::-1]):
        for icol, nseq in enumerate(nseqs):
            ax = axs[irow, icol]
            inp = INP_TEMPLATE.format(kernel=kernel, nstep=nstep, nseq=nseq)
            data = np.load(inp)

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
            if irow == len(nsteps) - 1:
                ax.set_xlabel(f"$M ={nseq}$")

    # Save the figure
    fig.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    driver()
