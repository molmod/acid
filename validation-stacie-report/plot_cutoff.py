#!/usr/bin/env python3

import json
from collections.abc import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from stepup.core.api import amend
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int, str, str]]:
    amend(inp="kernels.json")
    with open("kernels.json") as fh:
        kernels = json.load(fh)
    for kernel, models in kernels.items():
        for nseq in [64]:
            for model in models:
                yield kernel, nseq, model


CASE_FMT = "{}_nseq{:04d}_{}"
INP_TEMPLATE = (
    "../validation-stacie-calc/output/extract_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.npz"
)


def case_info(kernel: str, nseq: int, model: str):
    amend(inp="nsteps.json")
    with open("nsteps.json") as fh:
        nsteps = json.load(fh)
    out = [f"figures/plot_cutoff_acint_{kernel}_nseq{nseq:04d}_{model}.svg"]
    if model == "lorentz":
        out.append(f"figures/plot_cutoff_corrtime_exp_{kernel}_nseq{nseq:04d}_{model}.svg")
    return {
        "inp": ["../matplotlibrc"]
        + [
            INP_TEMPLATE.format(kernel=kernel, nstep=nstep, nseq=nseq, model=model)
            for nstep in nsteps
        ],
        "out": out,
        "nsteps": nsteps,
        "model": model,
    }


def run(inp: list[str], out: list[str], nsteps: list[int], model: str):
    mpl.rc_file(inp.pop(0))
    run_prop(inp, out[0], nsteps, "acints", "AC Integral")
    if model == "lorentz":
        run_prop(inp, out[1], nsteps, "corrtimes_exp", "Exponential corr. time")


def run_prop(inp: list[str], out: str, nsteps: list[int], key: str, label: str):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for nstep, path_extract in zip(nsteps, inp, strict=True):
        data = np.load(path_extract)
        fcuts = np.asarray(data["fcuts"])
        neffs = np.asarray(data["neffs"])
        values = np.asarray(data[key])
        values_std = np.asarray(data[f"{key}_std"])

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
        ax.set_ylabel(label)
    fig.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    driver()
