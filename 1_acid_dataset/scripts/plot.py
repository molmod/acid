#!/usr/bin/env python3

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import zarr
from path import Path
from stacie.spectrum import compute_spectrum


def main():
    args = parse_args()
    for path_svg in [args.svg_seqs, args.svg_acs, args.svg_psds]:
        if not path_svg.endswith(".svg"):
            raise ValueError(f"Output path {path_svg} must end with .svg")
    run(args.mplrc, args.zips, args.svg_seqs, args.svg_acs, args.svg_psds)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot sequences, autocorrelations, and power spectral densities"
    )
    parser.add_argument(
        "mplrc",
        type=Path,
        help="The matplotlibrc path.",
    )
    parser.add_argument(
        "zips",
        type=Path,
        nargs="+",
        help="The input ZIP paths.",
    )
    parser.add_argument(
        "svg_seqs",
        type=Path,
        help="The output SVG path for sequences.",
    )
    parser.add_argument(
        "svg_acs",
        type=Path,
        help="The output SVG path for autocorrelations.",
    )
    parser.add_argument(
        "svg_psds",
        type=Path,
        help="The output SVG path for power spectral densities.",
    )
    return parser.parse_args()


def run(
    path_mplrc: Path,
    paths_zip: list[Path],
    path_svg_seqs: Path,
    path_svg_acs: Path,
    path_svg_psds: Path,
):
    mpl.rc_file(path_mplrc)
    fig1, axs1 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)
    fig3, axs3 = plt.subplots(4, 3, figsize=(7, 11), sharex=True, sharey=True)

    for i, path_zip in enumerate(paths_zip):
        kernel = path_zip.name.split("_", 1)[0]
        store = zarr.storage.ZipStore(path_zip)
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

    fig1.savefig(path_svg_seqs)
    fig2.savefig(path_svg_acs)
    fig3.savefig(path_svg_psds)


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
    main()
