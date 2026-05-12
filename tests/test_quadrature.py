# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Validate the quadrature-based representation of the power-law kernel."""

import numpy as np
import pytest
from utils import make_grid_pow_rational_chebyshev


@pytest.mark.parametrize(
    ("a0", "alpha", "theta"),
    [
        (1.0, 1.5, 2.0),
        (1.0, 1.5, 3.5),
        (1.0, 1.5, 5.0),
    ],
)
def test_power_law_kernel_quadrature(a0, alpha, theta):
    """
    Compare quadrature-based and analytical autocorrelation functions.

    This function constructs the power-law ACID autocorrelation function
    using a rational Chebyshev quadrature over exponential kernels and
    compares it against the closed-form analytical expression.
    """
    # Quadrature order
    order = 115
    nstep = 2**16
    times = np.arange(nstep, dtype=float)

    taus, weights = make_grid_pow_rational_chebyshev(order, theta, alpha)

    prefactor = a0 * (alpha - 1) / (2 * theta)
    quadrature_acf = (weights * prefactor) @ np.exp(-np.outer(1 / taus, times))
    analytical_acf = prefactor * (1 + abs(times) / theta) ** (-alpha)
    diff_acf = np.abs(quadrature_acf - analytical_acf)
    max_rel_diff_acf = np.max(diff_acf / analytical_acf)

    analytical_psd = np.fft.rfft(analytical_acf)
    quadrature_psd = np.fft.rfft(quadrature_acf)
    diff_psd = np.abs(quadrature_psd - analytical_psd)
    max_rel_diff_psd = np.max(diff_psd / analytical_psd)

    assert max_rel_diff_acf <= 1e-8, (
        f"Quadrature does not reproduce analytical ACF within tolerance {max_rel_diff_acf=}."
    )
    assert max_rel_diff_psd <= 1e-8, (
        f"Quadrature does not reproduce analytical PSD within tolerance {max_rel_diff_psd=}."
    )

    acfint_lico = 2 * np.dot(taus, prefactor * weights)
    assert acfint_lico == pytest.approx(1.0, rel=1e-8), (
        f"The ACF integral is not reproduced within tolerance: {acfint_lico=}."
    )
