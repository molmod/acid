#!/usr/bin/env python3

import argparse
import json
import zipfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from path import Path


def main():
    args = parse_args()
    for path_svg in [args.svg_seqs, args.svg_acs, args.svg_psds]:
        if not path_svg.endswith(".svg"):
            raise ValueError(f"Output path {path_svg} must end with .svg")
    run(args.mplrc, args.lookup_table, args.zips, args.svg_seqs, args.svg_acs, args.svg_psds)


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
        "lookup_table",
        type=Path,
        help="The codec zip to decode the integers to floats",
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
    path_lookup: Path,
    paths_zip: list[Path],
    path_svg_seqs: Path,
    path_svg_acs: Path,
    path_svg_psds: Path,
):
    mpl.rc_file(path_mplrc)
    fig1, axs1 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig3, axs3 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)

    # Load the lookup table
    lookup_table = np.load(path_lookup)["lookup_midpoint"]

    for i, path_zip in enumerate(paths_zip):
        with zipfile.ZipFile(path_zip) as zf, zf.open("meta.json") as f:
            meta = json.load(f)
        # Compute spectrum to be included in plot, only for first seed
        std = np.sqrt(meta["var"])
        data = np.load(path_zip)
        cdfi = data["sequences_00.npy"]
        sequences = lookup_table[cdfi] * std
        empirical_psd = compute_amplitudes(sequences)
        empirical_acf = np.fft.irfft(empirical_psd)

        row = i // 3
        col = i % 3
        plot_seq(axs1[row, col], meta, data, sequences, row == 3, col == 0)
        plot_ac(axs2[row, col], meta, data, empirical_acf, row == 3, col == 0)
        plot_psd(axs3[row, col], meta, data, empirical_psd, row == 3, col == 0)

    fig1.savefig(path_svg_seqs)
    fig2.savefig(path_svg_acs)
    fig3.savefig(path_svg_psds)


def compute_amplitudes(sequences: NDArray[float], timestep: float = 1.0) -> NDArray[float]:
    r"""Compute the amplitudes of a batch of sequences as follows:

    .. math::

    C_k = \frac{1}{M}\sum_{m=1}^M \frac{F_m h}{2 N} \left|
        \sum_{n=0}^{N-1} x^{(m)}_n \exp\left(-i \frac{2 \pi n k}{N}\right)
    \right|^2

    where:

    - :math:`F_m` is the given prefactor (may be different for each sequence),
    - :math:`h` is the timestep,
    - :math:`N` is the number of time steps in the input sequences,
    - :math:`M` is the number of independent sequences,
    - :math:`x^{(m)}_n` is the value of the :math:`m`-th sequence at time step :math:`n`,
    - :math:`k` is the frequency index.

    Parameters
    ----------
    sequences
        The input sequences, which is an array with shape ``(nindep, nstep)``.
        Each row is a time-dependent sequence.
    timestep
        The time step of the input sequence.

    Returns
    -------
    amplitudes
        A numpy array that contains the amplitudes of the spectrum.
    """
    nindep = sequences.shape[0]
    nstep = sequences.shape[1]
    return timestep * (abs(np.fft.rfft(sequences, axis=1)) ** 2).sum(axis=0) / (nstep * nindep)


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
