# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Unit tests for the MSD and ACF computations of the Exp and SHO kernels.

Both tests simply check that the second derivative of the MSD divided by 2 matches the ACF.
"""

import numdifftools as nd
import numpy as np
import pytest
from kernels import ExpTerm, SHOTerm


def make_wrappers(term):
    """Return a functions that compute the ACF and MSD for a given term."""

    def acf(times):
        freqs = np.ones_like(times)
        return term.compute(freqs, times)[0]

    def msd(times):
        freqs = np.ones_like(times)
        return term.compute(freqs, times)[2]

    return acf, msd


def test_exp_msd():
    exp = ExpTerm(1.2, 5.0)
    acf, msd = make_wrappers(exp)
    times = np.linspace(0.1, 10.0, 20)
    acf_analytic = acf(times)
    acf_numeric = nd.Derivative(msd, n=2)(times) / 2
    assert acf_analytic == pytest.approx(acf_numeric, rel=1e-5)


@pytest.mark.parametrize(
    ("a0", "f0", "q"),
    [
        (1.2, 0.15, 0.2),  # overdamped
        (1.2, 0.04, 0.5),  # critically damped
        (1.2, 0.03, 1.4),  # underdamped
    ],
)
def test_sho_msd(a0, f0, q):
    sho = SHOTerm(a0, f0, q)
    acf, msd = make_wrappers(sho)

    times = np.linspace(0.1, 10.0, 20)
    acf_analytic = acf(times)
    acf_numeric = nd.Derivative(msd, n=2)(times) / 2
    assert acf_analytic == pytest.approx(acf_numeric, rel=1e-5)
