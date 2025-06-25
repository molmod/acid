#!/usr/bin/env python3

import json
from collections.abc import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from stepup.core.api import amend
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int, int]]:
    amend(inp="kernels.json")
    with open("kernels.json") as fh:
        kernels = json.load(fh)
    yield from kernels


CASE_FMT = "{}"


def case_info(kernel: str):
    suffix = f"{kernel}_nstep01024_nseq0256"
    return {
        "inp": ["../matplotlibrc", f"../validation-stacie-calc/output/subset_{suffix}.npz"],
        "out": f"figures/plot_acid_sequences_{suffix}.svg",
    }


def run(inp: list[str], out: str):
    mpl.rc_file(inp.pop(0))
    data = np.load(inp.pop(0))

    fig, axs = plt.subplots(1, 3, figsize=(7, 2.3))
    plot_inputs(axs[0], data["times"], data["sequences"])
    plot_acf(axs[1], data["times"], data["acf"], data["empirical_acf"])
    plot_psd(axs[2], data["freqs"], data["psd"], data["empirical_psd"])
    fig.savefig(out)
    plt.close(fig)


def plot_inputs(ax, times, sequences):
    nseq = 1
    nstep = 100
    ax.plot(times[:nstep], sequences[0, :nseq, :nstep].T, color="k")
    ax.set_xlabel("Time $t$")
    ax.set_ylabel(r"$\hat{x}(t)$")
    ax.set_title("Example input sequence")


REF_PROPS = {"ls": ":", "lw": 2, "color": "k", "alpha": 0.5}


def plot_acf(ax, times, model_acf, data_acf):
    ndelta = 100
    ax.plot(times[:ndelta], data_acf[:ndelta], color="C4")
    ax.plot(times[:ndelta], model_acf[:ndelta], **REF_PROPS)
    ax.set_xlabel(r"Time lag $\Delta_t$")
    ax.set_ylabel(r"COV[$\hat{x}(t)$, $\hat{x}(t+\Delta_t)$]")
    ax.set_title("Autocorrelation Function")


def plot_psd(ax, freqs, model_psd, data_psd):
    nfreq = freqs.searchsorted(0.1)
    ax.plot(freqs[:nfreq], data_psd[:nfreq], color="C9")
    ax.plot(freqs[:nfreq], model_psd[:nfreq], **REF_PROPS)
    ax.set_xlabel(r"Frequency $f$")
    ax.set_ylabel(r"Amplitude")
    ax.set_ylim(0, None)
    ax.set_title("Power Spectral Density")


if __name__ == "__main__":
    driver()
