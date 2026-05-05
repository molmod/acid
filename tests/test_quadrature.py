# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Validate the quadrature-based representation of the power-law kernel."""

import numpy as np
import pytest
from utils import make_grid_pow_rational_chebyshev


@pytest.mark.parametrize(
    ("a0", "alpha", "theta"),
    [
        (1.2, 1.5, 0.2),
        (1.2, 1.5, 0.5),
        (1.2, 1.5, 1.0),
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
    order = 80
    nstep = 2**18
    times = np.arange(nstep, dtype=float)
    taus, weights = make_grid_pow_rational_chebyshev(order, theta, alpha)

    prefactor = a0 * (alpha - 1) / (2 * theta)
    quadrature_acf = (weights * prefactor) @ np.exp(-np.outer(1 / taus, times))
    analytical_acf = prefactor * (1 + abs(times) / theta) ** (-alpha)
    diff = np.abs(quadrature_acf - analytical_acf)
    assert max(diff) <= 1e-6, (
        f"Quadrature does not reproduce analytical ACF within tolerance {max(diff)=}."
    )
