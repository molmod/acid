# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Validate derivation of the expected PSD of a finite sequence."""

import numpy as np
import pytest
import scipy as sp


@pytest.mark.parametrize("size", [1, 2, 3, 4, 5, 10, 15])
def test_toeplitz_psd(size):
    # Some random ACF values
    rng = np.random.default_rng(seed=size)
    acf = rng.uniform(size=size)

    # Construct the expected PSD via the Toeplitz covariance matrix
    covar = sp.linalg.toeplitz(acf)
    assert covar.shape == (size, size)
    assert covar == pytest.approx(covar.T)
    psd1 = np.diag(np.fft.fft(np.fft.ifft(covar, axis=1), axis=0))

    # PSD should be real-valued
    assert abs(psd1.imag).max() < 1e-10
    psd1 = psd1.real

    # Construct the same PSD with a 1D FFT of a modified ACF
    tmp = acf * np.arange(size, 0, -1) / size
    tmp[1:] += tmp[:0:-1]
    psd2 = np.fft.fft(tmp)

    # PSD should be real-valued
    assert abs(psd2.imag).max() < 1e-10
    psd2 = psd2.real

    # Check consistency
    assert psd1 == pytest.approx(psd2)
