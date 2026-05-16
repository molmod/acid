# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Check the low-frequency part of the PSD."""

import json
from runpy import run_path

import numpy as np
from kernels import compute
from numpy.typing import NDArray
from stepup.core.api import amend


def test_low_freqs():
    """Check the low-frequency behavior of the PSD of each kernel"""
    with open("./1_dataset/settings.json") as f:
        settings = json.load(f)

    nstep = 1024
    times = np.arange(nstep, dtype=float)
    freqs = np.fft.rfftfreq(nstep)

    for kernel_name in settings["kernels"]:
        path_py = f"./1_dataset/kernels/{kernel_name}.py"
        amend(inp=path_py)
        terms = run_path(path_py)["terms"]
        psd = compute(terms, freqs, times)[0]
        check_low_freq(kernel_name, freqs, psd)


def check_low_freq(kernel: str, freqs: NDArray[float], psd: NDArray[float]):
    """
    Check the low-frequency PSD against simple reference models.

    The low-frequency part of the spectrum is compared against two
    simple models:
        - Quadratic dependence on frequency
        - Power-law dependence on frequency with exponent 1/2

    The best fit of these two models is selected and required to meet
    fixed relative error thresholds over increasing frequency ranges:
        - The deviation should be less than 2.5 % for the first 10 frequency points.
        - The deviation should be less than 10.0 % for the first 20 frequency points.

    The relative noise in derived from 256 sequences is approximately 5 %.
    If this test passes,
    the low-frequency spectrum is sufficiently smooth for simple descriptions to
    remain valid over at least the first 20 frequency points.

    Parameters
    ----------
    kernel
        The name of the kernel.
    freqs
         The array of frequencies for which to compute the spectrum.
    psd
        The power spectrum on the requested grid.
    """
    for nfit, threshold in (10, 0.025), (20, 0.100):
        my_freqs = freqs[:nfit]
        my_psd = psd[:nfit].copy()

        # Fit a simple quadratic, manually for robustness
        my_psd -= my_psd[0]
        quad = my_freqs**2
        par_quad = np.dot(quad, my_psd) / np.dot(quad, quad)
        fit_quad = par_quad * quad
        relerr_quad = float(np.linalg.norm(fit_quad - my_psd) / np.linalg.norm(my_psd))

        # Fit a power-law function with exponent = 1/2
        sqrt = np.sqrt(my_freqs)
        par_sqrt = np.dot(sqrt, my_psd) / np.dot(sqrt, sqrt)
        fit_sqrt = par_sqrt * sqrt
        relerr_sqrt = float(np.linalg.norm(fit_sqrt - my_psd) / np.linalg.norm(my_psd))

        relerr_best_fit = min(relerr_quad, relerr_sqrt)

        assert relerr_best_fit <= threshold, (
            f"The PSD for {kernel=} is not approximated well by a simple model "
            f"in the low-frequency domain "
            f"({nfit=}, {threshold=}, {relerr_best_fit=})"
        )
