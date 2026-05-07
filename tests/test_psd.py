# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Unit tests for the PSD computations of the Exp, SHO, and Power-law kernels.

All tests check whether the PSD can be obtained using the FT of the ACF.
"""

from functools import partial

import mpmath as mp
import numpy as np
import pytest
from kernels import ExpTerm, PowTerm, SHOTerm


def compute_quadosc_psd(freqs, acf):
    """Performs oscillatory quadrature using mpmath to compute the PSD from the ACF"""
    return [
        mp.quadosc(
            lambda t, freq=freq: 2 * acf(t) * mp.cos(2 * mp.pi * freq * t),
            interval=[0, mp.inf],
            omega=freq * 2 * mp.pi,
        )
        for freq in freqs
    ]


def test_exp_psd():
    exp = ExpTerm(1.2, 5.0)
    freqs = np.linspace(0.1, 10.0, 20)
    psd_num = compute_quadosc_psd(freqs, partial(exp.compute_acf, ml=mp))
    psd_analytic = exp.compute_psd(freqs, ml=mp)
    assert psd_analytic == pytest.approx(psd_num, rel=1e-15)


@pytest.mark.parametrize(
    ("a0", "f0", "q"),
    [
        (1.2, 0.15, 0.2),  # overdamped
        (1.2, 0.04, 0.5),  # critically damped
        (1.2, 0.03, 1.4),  # underdamped
    ],
)
def test_sho_psd(a0, f0, q):
    sho = SHOTerm(a0, f0, q)
    freqs = np.linspace(0.1, 10.0, 20)
    psd_num = compute_quadosc_psd(freqs, partial(sho.compute_acf, ml=mp))
    psd_analytic = sho.compute_psd(freqs, ml=mp)
    assert psd_analytic == pytest.approx(psd_num, rel=1e-15)


@pytest.mark.parametrize(
    ("a0", "alpha", "theta"),
    [
        (1.2, 1.5, 0.2),
        (1.2, 1.5, 0.5),
        (1.2, 1.5, 1.0),
    ],
)
def test_pow_psd(a0, alpha, theta):
    power = PowTerm(a0, alpha, theta)
    freqs = np.linspace(0.1, 10.0, 20)
    psd_num = compute_quadosc_psd(freqs, partial(power.compute_acf, ml=mp))
    psd_analytic = power.compute_psd(freqs, ml=mp)
    assert psd_analytic == pytest.approx(psd_num, rel=1e-15)
