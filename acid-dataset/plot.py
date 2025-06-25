#!/usr/bin/env python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import zarr
from stacie.spectrum import compute_spectrum
from stepup.core.script import driver


def info():
    from settings import KERNELS

    return {
        "inp": ["../matplotlibrc"]
        + [f"output/{kernel}_nstep01024_nseq0256.zip" for kernel in KERNELS],
        "out": [
            "plot_seqs.svg",
            "plot_acs.svg",
            "plot_psds.svg",
        ],
        "kernels": KERNELS,
    }


def run(inp, out, kernels):
    mpl.rc_file(inp.pop(0))
    fig1, axs1 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)
    fig3, axs3 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)

    for i, (kernel, path) in enumerate(zip(kernels, inp, strict=False)):
        store = zarr.storage.ZipStore(path)
        root = zarr.open_group(store=store, mode="r")
        # Compute spectrum with Stacie, to be included in plot, only for first seed
        spectrum = compute_spectrum(root["sequences"][0], prefactors=2)
        empirical_psd = spectrum.amplitudes
        empirical_acf = np.fft.irfft(spectrum.amplitudes)

        row = i // 3
        col = i % 3
        plot_seq(axs1[row, col], kernel, root, row == 3, col == 0)
        plot_ac(axs2[row, col], kernel, root, empirical_acf, row == 3, col == 0)
        plot_psd(axs3[row, col], kernel, root, empirical_psd, row == 3, col == 0)

    fig1.savefig(out.pop(0))
    fig2.savefig(out.pop(0))
    fig3.savefig(out.pop(0))


def plot_seq(ax, kernel, root, xlabel, ylabel):
    nstep = 150
    times = root["times"][:nstep]
    seq = root["sequences"][0, 0, :nstep]
    ax.plot(times, seq)
    if xlabel:
        ax.set_xlabel("Time $t$")
    if ylabel:
        ax.set_ylabel(r"$\hat{x}(t)$")
    ax.set_title(kernel)


def plot_ac(ax, kernel, root, empirical_acf, xlabel, ylabel):
    ndelta = 50
    times = root["times"][:ndelta]
    acf = root["acf"][:ndelta]
    ax.plot(times, acf, "k:", lw=2)
    ax.plot(times, empirical_acf[:ndelta], "r-")
    if xlabel:
        ax.set_xlabel(r"Time lag $\Delta_t$")
    if ylabel:
        ax.set_ylabel(r"COV[$\hat{x}(t)$, $\hat{x}(t+\Delta_t)$]")
    ax.set_title(kernel)


def plot_psd(ax, kernel, root, empirical_psd, xlabel, ylabel):
    freqs = root["freqs"][:]
    nfreq = freqs.searchsorted(0.1)
    freqs = freqs[:nfreq]
    psd = root["psd"][:nfreq]
    ax.plot(freqs, psd, "k:", lw=2)
    ax.plot(freqs, empirical_psd[:nfreq], "r-")
    if xlabel:
        ax.set_xlabel(r"Frequency $f$")
    if ylabel:
        ax.set_ylabel(r"Amplitude")
    ax.set_title(kernel)


if __name__ == "__main__":
    driver()
