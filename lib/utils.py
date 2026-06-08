# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import io
import json
import zipfile

import numpy as np
import scipy as sp
from numpy.typing import NDArray


def dump_npy(name: str, zf: zipfile.ZipFile, array: NDArray):
    """Dump a NumPy array to a ZIP file as a .npy file."""
    zi = default_zipinfo(name)
    buf = io.BytesIO()
    np.save(buf, array, allow_pickle=False)
    zf.writestr(zi, buf.getvalue())


def default_zipinfo(name: str) -> zipfile.ZipInfo:
    """Create a ZipInfo object with a fixed date."""
    zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    zi.external_attr = 0
    zi.create_system = 0
    return zi


def dump_meta(name: str, zf: zipfile.ZipFile, data):
    """Dump metadata to a ZIP file as a .json file."""
    zi = default_zipinfo(name)
    zf.writestr(zi, json.dumps(data))


def generate_codec(resolution: int) -> tuple[NDArray, NDArray]:
    """
    Generate lookup tables for Gaussian-based encoding/decoding of trajectories.


    Parameters
    ----------
    resolution
        The number of bins for the codec representation.

    Returns
    -------
    boundary
        Bin boundaries.
    midpoint
        Bin midpoints.
    """
    cdf = np.arange(resolution)
    boundary = sp.stats.norm.ppf(cdf[1:] / resolution).astype(np.float32)
    midpoint = sp.stats.norm.ppf((cdf + 0.5) / resolution).astype(np.float32)
    return boundary, midpoint


def lookup_integer(sequence: NDArray[float], std: float, table: NDArray[float]) -> NDArray[int]:
    r"""Lookup to which integer the floats should be mapped according to the lookup table.
    This lookup table is based on the mapping of the sequence to a cumulative distribution function,
    belonging to a Gaussian distribtion with standard deviation ``std``.

    Parameters
    ----------
    sequence
        The input sequences, which is an array with shape ``(nindep, nstep)``.
        Each row is a time-dependent sequence.
    std
        The standard deviation of the sequence.
    table
        The lookup table to map the floats to integers.

    Returns
    -------
    An array that contains the original floats mapped to integers
    """
    return np.searchsorted(table, sequence / std)


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


def compute_acfs(sequences: NDArray[float]) -> NDArray[float]:
    """
    Compute the autocorrelation function (ACF) from a batch of sequences.

    Parameters
    ----------
    sequences
        The input sequences, which is an array with shape ``(nindep, nstep)``.
        Each row is a time-dependent sequence.

    Returns
    -------
    acfs
        A numpy array that contains the ACFs of the sequence.
    """
    nseq, nstep = sequences.shape

    # Normalization for unbiased ACF estimator
    denom = np.arange(nstep, 0, -1)

    acfs = np.zeros(nstep)
    for seq in sequences:
        corr = sp.signal.correlate(seq, seq, mode="full", method="auto")[nstep - 1 :]
        corr /= denom
        acfs += corr

    return acfs / nseq


def compute_msds(sequences: NDArray[float]) -> NDArray[float]:
    """
    Compute the mean-squared displacements (MSD) from a batch of sequences.

    Parameters
    ----------
    sequences
        The input sequences, which is an array with shape ``(nindep, nstep)``.
        Each row is a time-dependent sequence.

    Returns
    -------
    msds
        A numpy array that contains the MSDs of the sequence.
        Note that the average of squared displacements is computed over all available time origins,
        `range(0, nstep-delta)`, where `delta` is the integer time lag and `nstep` is the sequence length.
    """
    nstep = sequences.shape[1]

    # Integrated trajectories
    antiderivatives = np.cumsum(sequences, axis=1)

    msds = np.zeros(nstep)
    for delta in range(nstep):
        diffs = antiderivatives[:, delta:] - antiderivatives[:, : nstep - delta]
        msds[delta] = np.mean(diffs**2)

    return msds


def make_grid_pow_rational_chebyshev(
    order: int, theta: float, alpha: float, threshold: float = 1e-34
) -> tuple[NDArray[float], NDArray[float]]:
    r"""
    Constructs quadrature nodes and weights using rational Chebyshev quadrature.

    The change of variables maps the semi-infinite interval :math:`tau \in \[0, \infty \)`
    to :math:`x \in \[-1, 1\]`, enabling Chebyshev integration of the first kind.

    Parameters
    ----------
    order
        Order of the quadrature.
    theta
        The scaling factor of the power-term kernel.
    alpha
        Power-law exponent.
    threshold
        Relative threshold used to prune the quadrature grid,
        using :math:`weights.max() * threshold`.

    Returns
    -------
    taus
        The taus for which the exponentials are sampled.
    weights
        Quadrature weights associated with each tau.
    """
    i = np.arange(order)
    x = -np.cos((2 * i + 1) / (2 * order) * np.pi)
    wx = np.pi / order * np.sqrt(1 - x**2)

    # The distribution of the mapped variable y = (1+x)/(1-x)
    # is fixed by the quadrature order.
    # However, this mapping provides limited resolution at long time scales (small y).
    #
    # To improve coverage in this regime,
    # we introduce a dimensionless scaling factor (0 < scale <= 1),
    # which shifts more quadrature nodes toward the small-y (large-τ) region.
    # This scaling is empirically tuned to obtain accurate results
    # within a fixed maximum nstep of 2**16.
    #
    # Without this scaling, taus are directly proportional to theta,
    # so variations in theta strongly shift the quadrature grid.
    # As a result, a fixed scale would not perform consistently
    # across the relevant range of thetas [2.0, 5.0]:
    # a value that works well for smaller theta leads to insufficient resolution
    # for larger theta (and vice versa).
    # The chosen theta-dependent scaling provides a more consistent scaling
    # by modifying the proportionality of the taus to 25 + 2 theta,
    # thereby significantly reducing the theta-dependence.
    scale = theta / (25 + 2 * theta)
    y = ((1 + x) / (1 - x)) * scale
    wy = wx * 2 * scale / (1 - x) ** 2
    pdf = y ** (alpha - 1) / sp.special.gamma(alpha) * np.exp(-y)
    taus = theta / y
    weights = wy * pdf

    # Prune quadrature grid.
    mask = weights > weights.max() * threshold
    taus = taus[mask]
    weights = weights[mask]

    return taus, weights
