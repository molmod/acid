#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

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
    run(
        args.mplrc, args.codec, args.settings, args.zips, args.svg_seqs, args.svg_acs, args.svg_psds
    )


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
        "codec",
        type=Path,
        help="The codec zip to decode the integers to floats",
    )
    parser.add_argument(
        "settings",
        type=Path,
        help="The settings.json file.",
    )
    parser.add_argument(
        "zips",
        type=Path,
        nargs="+",
        help="The input ZIP paths for each kernel.",
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
    path_codec: Path,
    path_settings: Path,
    paths_zip: Path,
    path_svg_seqs: Path,
    path_svg_acs: Path,
    path_svg_psds: Path,
):
    mpl.rc_file(path_mplrc)
    fig1, axs1 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig2, axs2 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)
    fig3, axs3 = plt.subplots(4, 3, figsize=(7, 10), sharex=True, sharey=True)

    with open(path_settings) as f0:
        settings = json.load(f0)

    # Load the lookup table
    lookup_table = np.load(path_codec)["midpoint"]

    for i, path_kernel in enumerate(paths_zip):
        with zipfile.ZipFile(path_kernel) as zf, zf.open("meta.json") as f:
            meta = json.load(f)
        unzipped_kernel = np.load(path_kernel)
        sample_path = (
            f"nstep{settings['nsteps'][0]:05d}/nseq{settings['nseqs'][-1]:04d}/sequences_00.npy"
        )
        step_path = f"nstep{settings['nsteps'][0]:05d}/"
        times = unzipped_kernel[step_path + "times.npy"]
        freqs = unzipped_kernel[step_path + "freqs.npy"]
        acf = unzipped_kernel[step_path + "acf.npy"]
        psd = unzipped_kernel[step_path + "psd.npy"]
        std = np.sqrt(meta["var"])
        cdfi = unzipped_kernel[sample_path]
        sequences = lookup_table[cdfi] * std
        empirical_psd = compute_amplitudes(sequences)
        empirical_acf = np.fft.irfft(empirical_psd)

        row = i // 3
        col = i % 3
        plot_seq(axs1[row, col], meta, times, sequences, row == 3, col == 0)
        plot_ac(axs2[row, col], meta, times, acf, empirical_acf, row == 3, col == 0)
        plot_psd(axs3[row, col], meta, freqs, psd, empirical_psd, row == 3, col == 0)

    fig1.savefig(path_svg_seqs)
    fig2.savefig(path_svg_acs)
    fig3.savefig(path_svg_psds)


def compute_amplitudes(sequences: NDArray[float], timestep: float = 1.0) -> NDArray[float]:
    r"""Compute the amplitudes of a batch of sequences as follows:

    .. math::

    C_k = \frac{1}{M}\sum_{m=1}^M \frac{h}{N} \left|
        \sum_{n=0}^{N-1} x^{(m)}_n \exp\left(-i \frac{2 \pi n k}{N}\right)
    \right|^2

    where:

    - :math:`h` is the timestep,
    - :math:`N` is the number of time steps in the input sequences,
    - :math:`M` is the number of independent sequences,
    - :math:`x^{(m)}_n` is the value of the :math:`m`-th sequence at time step :math:`n`,
    - :math:`k` is the frequency index.

    This normalization differs from conventional discrete Fourier transforms,
    where the factor :math:`\frac{1}{N}` is typically applied in the inverse transform.
    Applying the normalization directly in the forward transform ensures that the resulting spectrum
    is an intensive property,
    which is important in the context of transport properties,
    where the zero-frequency limit is the quantity of interest.
    Likewise, the factor :math:`\frac{1}{M}` ensures that the averaged spectrum is also intensive
    with respect to the number of independent sequences :math:`M`.

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


def plot_seq(ax, meta, times, sequences, xlabel, ylabel):
    nstep = 150
    times = times[:nstep]
    ax.plot(times, sequences[0, :nstep])
    if xlabel:
        ax.set_xlabel("Time $t$")
    if ylabel:
        ax.set_ylabel(r"$\hat{x}(t)$")
    ax.set_title(meta["kernel"])


def plot_ac(ax, meta, times, acf, empirical_acf, xlabel, ylabel):
    ndelta = 50
    times = times[:ndelta]
    acf = acf[:ndelta]
    ax.plot(times, acf, "k:", lw=2)
    ax.plot(times, empirical_acf[:ndelta], "r-")
    if xlabel:
        ax.set_xlabel(r"Time lag $\Delta_t$")
    if ylabel:
        ax.set_ylabel(r"COV[$\hat{x}(t)$, $\hat{x}(t+\Delta_t)$]")
    ax.set_title(meta["kernel"])


def plot_psd(ax, meta, freqs, psd, empirical_psd, xlabel, ylabel):
    freqs = freqs[:]
    nfreq = freqs.searchsorted(0.1)
    freqs = freqs[:nfreq]
    psd = psd[:nfreq]
    ax.plot(freqs, psd, "k:", lw=2)
    ax.plot(freqs, empirical_psd[:nfreq], "r-")
    if xlabel:
        ax.set_xlabel(r"Frequency $f$")
    if ylabel:
        ax.set_ylabel(r"Amplitude")
    ax.set_title(meta["kernel"])


if __name__ == "__main__":
    main()
