# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import functools
from collections.abc import Callable

import attrs
import mpmath as mp
import numpy as np
import scipy as sp
from numpy.typing import NDArray

from .utils import make_grid_pow_rational_chebyshev

__all__ = (
    "BaseTerm",
    "ExpTerm",
    "KernelSummary",
    "PowTerm",
    "SHOTerm",
    "WhiteTerm",
    "compute",
    "sample",
    "strict_fp",
    "summarize",
)


ACINT_REF = 1.0


def strict_fp[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Decorator for functions that should raise instead of warn on floating point issues.

    The default of NumPy is to warn instead of raise for `over`, `divide` and `invalid`,
    which are too easily missed in data generation jobs running on a headless compute node.
    Underflow is deliberately ignored.

    A new `np.errstate` is created for each call,
    so decorated functions can be nested, recursive or used from multiple threads.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with np.errstate(over="raise", under="ignore", divide="raise", invalid="raise"):
            return func(*args, **kwargs)

    return wrapper


@attrs.define
class BaseTerm:
    a0: float = attrs.field(converter=float)

    @property
    def typst(self):
        raise NotImplementedError

    @property
    def latex(self):
        raise NotImplementedError

    def compute_acf(self, times: NDArray[float], ml=np) -> NDArray[float]:
        raise NotImplementedError

    def compute_psd(self, freqs: NDArray[float], ml=np) -> NDArray[float]:
        raise NotImplementedError

    def compute_msd(self, times: NDArray[float], ml=np) -> NDArray[float]:
        raise NotImplementedError

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        raise NotImplementedError


@attrs.define
class PowTerm(BaseTerm):
    alpha: float = attrs.field(converter=float)
    theta: float = attrs.field(converter=float)
    taus: NDArray[float] = attrs.field(init=False)
    weights: NDArray[float] = attrs.field(init=False)

    def __attrs_post_init__(self):
        # Order of the numerical quadrature
        order = 135
        taus, weights = make_grid_pow_rational_chebyshev(order, self.theta, self.alpha)

        self.taus = taus
        self.weights = weights

    @property
    def typst(self):
        return f"upright(P)({self.a0}, {self.alpha}, {self.theta})"

    @property
    def latex(self):
        return rf"\operatorname{{P}}({self.a0}, {self.alpha}, {self.theta})"

    def compute_acf(self, times: NDArray[float], ml=np) -> NDArray[float]:
        alpha = self.alpha
        theta = self.theta
        a0 = self.a0

        if alpha <= 1 or alpha == 2:
            raise ValueError(f"Invalid {alpha=}")

        return a0 * (alpha - 1) / (2 * theta) * (1 + abs(times) / theta) ** (-alpha)

    def compute_psd(self, freqs: NDArray[float], ml=np) -> NDArray[float]:
        alpha = self.alpha
        theta = self.theta
        a0 = self.a0

        if alpha <= 1 or alpha == 2:
            raise ValueError(f"Invalid {alpha=}")

        zs = 1j * 2 * ml.pi * freqs * theta
        # Compute the real part of exp(z) * E_\alpha(z), required for the analytical PSD
        # expint is always evaluated with mpmath
        real_parts_psd = np.array([float((mp.exp(z) * mp.expint(alpha, z)).real) for z in zs])
        return a0 * (alpha - 1) * real_parts_psd

    def compute_msd(self, times: NDArray[float], ml=np) -> NDArray[float]:
        alpha = self.alpha
        theta = self.theta
        a0 = self.a0

        if alpha <= 1 or alpha == 2:
            raise ValueError(f"Invalid {alpha=}")

        msd = (alpha - 2) * abs(times) / theta - 1 + (1 + abs(times) / theta) ** (-alpha + 2)
        msd *= a0 * theta / (alpha - 2)
        return msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        alpha = self.alpha
        theta = self.theta

        traj = np.zeros((nseq, nstep))

        for tau, weight in zip(self.taus, self.weights, strict=True):
            traj += np.sqrt(weight) * ExpTerm(self.a0 * (alpha - 1) / (theta) * tau, tau).sample(
                nseq, nstep, rng
            )
        return traj


@attrs.define
class SHOTerm(BaseTerm):
    f0: float = attrs.field(converter=float)
    q: float = attrs.field(converter=float)
    matexp: NDArray[float] = attrs.field(init=False)
    covar: NDArray[float] = attrs.field(init=False)
    stat_covar: NDArray[float] = attrs.field(init=False)

    def __attrs_post_init__(self):
        omega0 = 2 * np.pi * self.f0

        theta = np.array([[0, 1], [-(omega0**2), -omega0 / self.q]])
        b = np.array([[0, 0], [0, 0.5 * self.a0 * omega0**4]])

        matexp = sp.linalg.expm(theta)
        self.matexp = matexp

        upper = 2 * np.dot(matexp, np.dot(b, matexp.T))
        lower = 2 * b

        self.covar = sp.linalg.solve_continuous_lyapunov(theta, upper - lower)
        self.stat_covar = sp.linalg.solve_continuous_lyapunov(theta, -lower)

    @property
    def typst(self) -> str:
        return f"upright(S)({self.a0}, {self.f0}, {self.q})"

    @property
    def latex(self) -> str:
        return rf"\operatorname{{S}}({self.a0}, {self.f0}, {self.q})"

    def compute_acf(self, times: NDArray[float], ml=np) -> NDArray[float]:
        a0 = self.a0
        f0 = self.f0
        q = self.q
        eta = ml.sqrt(abs(1 / (4 * q**2) - 1))
        ft = 2 * ml.pi * f0 * abs(times)

        if 0 < q < 0.5:
            exp_arg_plus = (eta - 0.5 / q) * ft
            exp_arg_minus = (-eta - 0.5 / q) * ft

            acf = q * (ml.exp(exp_arg_plus) + ml.exp(exp_arg_minus))
            acf += (ml.exp(exp_arg_plus) - ml.exp(exp_arg_minus)) / (2 * eta)
            acf *= 0.5 * ml.pi * a0 * f0

        elif q >= 0.5:
            acf = a0 * ml.pi * f0 * q * ml.exp(-0.5 * ft / q)
            if q == 0.5:
                acf *= 1 + ft
            else:
                scarg = eta * ft
                acf *= ml.cos(scarg) + ml.sin(scarg) / (2 * eta * q)
        else:
            raise ValueError(f"Invalid {q=}")

        return acf

    def compute_psd(self, freqs: NDArray[float], ml=np) -> NDArray[float]:
        return (
            self.a0 * self.f0**4 / ((freqs**2 - self.f0**2) ** 2 + (freqs * self.f0 / self.q) ** 2)
        )

    def compute_msd(self, times: NDArray[float], ml=np) -> NDArray[float]:
        a0 = self.a0
        f0 = self.f0
        q = self.q
        eta = ml.sqrt(abs(1 / (4 * q**2) - 1))
        ft = 2 * ml.pi * f0 * abs(times)
        prefactor = a0 / (2 * ml.pi * f0 * q)

        if 0 < q < 0.5:
            exp_arg_plus = (eta - 0.5 / q) * ft
            exp_arg_minus = (-eta - 0.5 / q) * ft
            sinh_prefactor = 1 / (2 * eta * q) * (1 - 3 * q**2)

            msd = (1 - q**2) * (ml.exp(exp_arg_plus) + ml.exp(exp_arg_minus))
            msd += sinh_prefactor * (ml.exp(exp_arg_plus) - ml.exp(exp_arg_minus))
            msd *= prefactor / 2

        elif q >= 0.5:
            msd = prefactor * ml.exp(-ft / (2 * q))
            if q == 0.5:
                msd *= 1 + 2 / 3 * ml.pi * f0 * abs(times)
                msd *= 1 - q**2
            else:
                scarg = eta * ft
                sin_prefactor = 1 / (2 * eta * q) * (1 - 3 * q**2)
                msd *= (1 - q**2) * ml.cos(scarg) + sin_prefactor * ml.sin(scarg)
        else:
            raise ValueError(f"Invalid {q=}")

        msd += a0 * abs(times) - prefactor * (1 - q**2)
        return msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        noise = rng.multivariate_normal(
            np.zeros(2), self.covar, size=(nstep, nseq), method="cholesky"
        ).transpose(0, 2, 1)
        traj = np.zeros((nstep, 2, nseq))
        traj[0, :, :] = rng.multivariate_normal(
            np.zeros(2), self.stat_covar, size=nseq, method="cholesky"
        ).T

        for istep in range(1, nstep):
            traj[istep, :, :] = noise[istep, :, :] + self.matexp @ traj[istep - 1, :, :]
        return traj[:, 0, :].transpose(1, 0)


@attrs.define
class ExpTerm(BaseTerm):
    tau: float = attrs.field(converter=float)

    @property
    def typst(self) -> str:
        return f"upright(E)({self.a0}, {self.tau})"

    @property
    def latex(self) -> str:
        return rf"\operatorname{{E}}({self.a0}, {self.tau})"

    def compute_acf(self, times: NDArray[float], ml=np) -> NDArray[float]:
        return 0.5 * self.a0 / self.tau * ml.exp(-abs(times / self.tau))

    def compute_psd(self, freqs: NDArray[float], ml=np) -> NDArray[float]:
        return self.a0 / (1 + (2 * ml.pi * self.tau * freqs) ** 2)

    def compute_msd(self, times: NDArray[float], ml=np) -> NDArray[float]:
        return self.a0 * (times + self.tau * (ml.exp(-abs(times) / self.tau) - 1))

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        var = self.a0 / (2 * self.tau)
        noise = rng.normal(0, np.sqrt(var * (1 - np.exp(-2 / self.tau))), size=(nseq, nstep))
        prop = np.exp(-1 / self.tau)
        x0 = rng.normal(0, np.sqrt(var), size=nseq)
        zi = (x0 * prop)[:, np.newaxis]  # shape (nseq, 1)
        result, _ = sp.signal.lfilter([1.0], [1.0, -prop], x=noise, zi=zi)
        return result


@attrs.define
class WhiteTerm(BaseTerm):
    @property
    def typst(self) -> str:
        return f"upright(W)({self.a0})"

    @property
    def latex(self) -> str:
        return rf"\operatorname{{W}}({self.a0})"

    def compute_acf(self, times: NDArray[float], ml=np) -> NDArray[float]:
        acf = np.zeros_like(times)
        acf[0] = self.a0
        return acf

    def compute_psd(self, freqs: NDArray[float], ml=np) -> NDArray[float]:
        return np.full_like(freqs, self.a0)

    def compute_msd(self, times: NDArray[float], ml=np) -> NDArray[float]:
        return self.a0 * times

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        return rng.normal(loc=0.0, scale=np.sqrt(self.a0), size=(nseq, nstep))


@strict_fp
def compute(
    terms: list[BaseTerm], freqs: NDArray[float], times: NDArray[float]
) -> tuple[NDArray[float], NDArray[float], NDArray[float]]:
    """Construct a power spectrum, autocorrelation function and mean-squared displacement.

    Parameters
    ----------
    terms
        Terms that contribute to the kernel.
    freqs
        The array of frequencies for which to compute the spectrum.
    times
        The array of times for which to compute the autocorrelation function.

    Returns
    -------
    psd
        The power spectrum on the requested grid, with the same shape as ``freqs``.
    acf
        The autocorrelation function, with the same shape as ``times``.
    msd
        The mean-squared displacement, with the same shape as ``times``.
    """
    acf = 0
    psd = 0
    msd = 0
    for term in terms:
        acf += term.compute_acf(times)
        psd += term.compute_psd(freqs)
        msd += term.compute_msd(times)
    return psd, acf, msd


def compute_t90(
    nonwhite_terms: list[BaseTerm],
    acf_total: float,
    tol: float = 0.1,
    tmax: int = 1024,
    max_doublings: int = 2,
    doubling_index: int = 0,
) -> float:
    """
    Compute the settling time-lag of a kernel's analytical ACF integral.

    Parameters
    ----------
    nonwhite_terms
        A list of kernel terms, excluding white noise.
    acf_total
        Target value of the ACF integral, excluding the white noise terms.
    tol
        Relative tolerance within which the ACF integral is considered settled.
    tmax
        Maximum time lag to be considered in the cumsum.
    max_doublings
        Maximum number of times ``tmax`` may be doubled.
    doubling_index
        Number of times ``tmax`` has already been doubled.

    Returns
    -------
    t90
        Smallest lag from which the ACF integral stays within the tolerance ``tol``.

    Raises
    ------
    RuntimeError
        If the integral has not settled after ``max_doublings`` doublings.
    """
    lags = np.arange(tmax + 1, dtype=float)
    acf = sum(term.compute_acf(lags) for term in nonwhite_terms)
    captured = acf[0] + 2.0 * np.concatenate(([0.0], np.cumsum(acf[1:])))
    frac = captured / acf_total

    outside_band = np.abs(frac - 1.0) > tol
    if not outside_band.any():
        return lags[0]
    last_outside = np.where(outside_band)[0][-1]
    if last_outside != len(frac) - 1:
        return lags[last_outside + 1]

    if doubling_index == max_doublings:
        raise RuntimeError(
            f"ACF integral did not settle with a tolerance of {tol:.0%} "
            f"after doubling the range {max_doublings} times."
        )

    return compute_t90(
        nonwhite_terms,
        acf_total,
        tol=tol,
        tmax=2 * tmax,
        max_doublings=max_doublings,
        doubling_index=doubling_index + 1,
    )


def compute_f90(
    nonwhite_terms: list[BaseTerm],
    variance_total: float,
    df: float = 1e-3,
    fmax: float = 0.5,
    max_doublings: int = 2,
    doubling_index: int = 0,
) -> float:
    """
    Compute the frequency at which the cumulative PSD integral reaches 90% of ``variance_total``.

    Parameters
    ----------
    nonwhite_terms
        A list of kernel terms, excluding white noise.
    variance_total
        Target value of the variance, excluding the white noise terms.
    df
        Frequency-grid spacing.
    fmax
        Maximum frequency to be considered in the cumsum.
    max_doublings
        Maximum number of times ``fmax`` may be doubled.
    doubling_index
        Number of times ``fmax`` has already been doubled.

    Returns
    -------
    f90
        Frequency at which the cumulative PSD integral reaches 90% of ``variance_total``.

    Raises
    ------
    RuntimeError
        If the target fraction has not been reached after ``max_doublings`` doublings.
    """
    freqs = np.arange(0.0, fmax + df, df)
    psd = sum(term.compute_psd(freqs) for term in nonwhite_terms)
    captured = (psd[0] + 2.0 * np.concatenate(([0.0], np.cumsum(psd[1:])))) * df
    frac = captured / variance_total

    idx = np.argmax(frac >= 0.9)
    if frac[idx] >= 0.9:
        return freqs[idx]

    if doubling_index == max_doublings:
        raise RuntimeError(
            f"PSD integral did not reach 90% of the analytical variance "
            f"after doubling the frequency range {max_doublings} times."
        )

    return compute_f90(
        nonwhite_terms,
        variance_total,
        df=df,
        fmax=2 * fmax,
        max_doublings=max_doublings,
        doubling_index=doubling_index + 1,
    )


@attrs.define
class KernelSummary:
    """Container class holding the grid-independent properties of a kernel."""

    var: float = attrs.field(converter=float)
    """The variance."""

    acint: float = attrs.field(converter=float)
    """The ACF integral."""

    corrtime_int: float = attrs.field(converter=float)
    """The integrated correlation time."""

    corrtime_exp: float | None = attrs.field(converter=attrs.converters.optional(float))
    """The exponential correlation time, or None if not defined."""

    t90: int = attrs.field(converter=int)
    """The settling lag of the ACF integral, see :func:`compute_t90`."""

    f90: float = attrs.field(converter=float)
    """The 90% frequency of the PSD integral, see :func:`compute_f90`."""

    typst: str = attrs.field()
    """A typst equation describing the kernel."""

    latex: str = attrs.field()
    """A latex equation describing the kernel."""


@strict_fp
def summarize(terms: list[BaseTerm]) -> KernelSummary:
    """Compute the properties of the kernel
    that do not depend on the sequence length or the number of sequences.

    Parameters
    ----------
    terms
        Terms that contribute to the kernel.

    Returns
    -------
    summary
        The grid-independent properties of the kernel,
        including its typst and latex equations.
    """
    acint = 0.0
    variance = 0.0
    acint_nonwhite = 0.0
    variance_nonwhite = 0.0
    nonwhite_terms = []
    corrtimes_exp = []
    for term in terms:
        acf0 = term.compute_acf(np.zeros(1))[0]
        psd0 = term.compute_psd(np.zeros(1))[0]
        acint += psd0
        variance += acf0

        # Filter out the white noise terms
        if not isinstance(term, WhiteTerm):
            nonwhite_terms.append(term)
            acint_nonwhite += psd0
            variance_nonwhite += acf0
            corrtimes_exp.append(term.tau if isinstance(term, ExpTerm) else None)

    if abs(acint - ACINT_REF) > 1e-10:
        raise ValueError(f"kernel has {acint=}")
    corrtime_exp = None
    if len(corrtimes_exp) == 1 and corrtimes_exp[0] is not None:
        corrtime_exp = corrtimes_exp[0]
    return KernelSummary(
        var=variance,
        acint=acint,
        corrtime_int=0.5 * acint / variance,
        corrtime_exp=corrtime_exp,
        t90=compute_t90(nonwhite_terms, acint_nonwhite),
        f90=compute_f90(nonwhite_terms, variance_nonwhite),
        typst=" + ".join(term.typst for term in terms),
        latex=" + ".join(term.latex for term in terms),
    )


@strict_fp
def sample(
    terms: list[BaseTerm], nseq: int, nstep: int, rng: np.random.Generator
) -> NDArray[float]:
    """Sample a trajectory following a given autocorrelation function kernel,
    using linear stochastic differential equations.

    Parameters
    ----------
    terms
        Terms that contribute to the kernel.
    nseq
        Number of sequences.
    nstep
        Number of steps in a sequence.
    rng
        Random number generator.

    Returns
    -------
    trajectory
        A trajectory sampled according to the ACF kernel.

    """
    trajectory = np.zeros((nseq, nstep))

    for term in terms:
        trajectory += term.sample(nseq, nstep, rng)

    return trajectory
