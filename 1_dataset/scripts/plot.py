#!/usr/bin/env python3

import argparse
import json
import zipfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
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
    fig1, axs1 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig3, axs3 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)

    for i, path_zip in enumerate(paths_zip):
        with zipfile.ZipFile(path_zip) as zf, zf.open("meta.json") as f:
            meta = json.load(f)
        # Compute spectrum with Stacie, to be included in plot, only for first seed
        std = np.sqrt(meta["var"])
        data = np.load(path_zip)
        cfdi = data["sequences_00.npy"]
        imax = np.iinfo(cfdi.dtype).max + 1
        sequences = sp.stats.norm(scale=std).ppf((cfdi + 0.5) / imax)
        spectrum = compute_spectrum(sequences, prefactors=2)
        empirical_psd = spectrum.amplitudes
        empirical_acf = np.fft.irfft(spectrum.amplitudes)

        row = i // 3
        col = i % 3
        plot_seq(axs1[row, col], meta, data, sequences, row == 3, col == 0)
        plot_ac(axs2[row, col], meta, data, empirical_acf, row == 3, col == 0)
        plot_psd(axs3[row, col], meta, data, empirical_psd, row == 3, col == 0)

    fig1.savefig(path_svg_seqs)
    fig2.savefig(path_svg_acs)
    fig3.savefig(path_svg_psds)


def plot_seq(ax, meta, data, sequences, xlabel, ylabel):
    nstep = 150
    times = data["times"][:nstep]
    ax.plot(times, sequences[0, :nstep])
    if xlabel:
        ax.set_xlabel("Time $t$")
    if ylabel:
        ax.set_ylabel(r"$\hat{x}(t)$")
    ax.set_title(meta["kernel"])


def plot_ac(ax, meta, data, empirical_acf, xlabel, ylabel):
    ndelta = 50
    times = data["times"][:ndelta]
    acf = data["acf"][:ndelta]
    ax.plot(times, acf, "k:", lw=2)
    ax.plot(times, empirical_acf[:ndelta], "r-")
    if xlabel:
        ax.set_xlabel(r"Time lag $\Delta_t$")
    if ylabel:
        ax.set_ylabel(r"COV[$\hat{x}(t)$, $\hat{x}(t+\Delta_t)$]")
    ax.set_title(meta["kernel"])


def plot_psd(ax, meta, data, empirical_psd, xlabel, ylabel):
    freqs = data["freqs"][:]
    nfreq = freqs.searchsorted(0.1)
    freqs = freqs[:nfreq]
    psd = data["psd"][:nfreq]
    ax.plot(freqs, psd, "k:", lw=2)
    ax.plot(freqs, empirical_psd[:nfreq], "r-")
    if xlabel:
        ax.set_xlabel(r"Frequency $f$")
    if ylabel:
        ax.set_ylabel(r"Amplitude")
    ax.set_title(meta["kernel"])


if __name__ == "__main__":
    main()
