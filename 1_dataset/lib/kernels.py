# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import attrs
import mpmath as mp
import numpy as np
import scipy as sp
from numpy.typing import NDArray

np.seterr(over="raise", under="ignore", divide="raise", invalid="raise")

__all__ = ("compute",)


ACINT_REF = 1.0


@attrs.define
class BaseTerm:
    a0: float = attrs.field(converter=float)

    @property
    def typst(self):
        raise NotImplementedError

    @property
    def latex(self):
        raise NotImplementedError

    def compute(self, freqs: NDArray[float], times: NDArray[float]):
        raise NotImplementedError


@attrs.define
class PolyTerm(BaseTerm):
    alpha: float = attrs.field(converter=float)
    theta: float = attrs.field(converter=float)

    @property
    def typst(self):
        return f"upright(P)({self.a0}, {self.alpha}, {self.theta})"

    @property
    def latex(self):
        return rf"\operatorname{{P}}({self.a0}, {self.alpha}, {self.theta})"

    def compute(
        self, freqs: NDArray[float], times: NDArray[float]
    ) -> tuple[NDArray[float], NDArray[float], NDArray[float]]:
        alpha = self.alpha
        theta = self.theta
        a0 = self.a0

        if alpha <= 1 or alpha == 2:
            raise ValueError(f"Invalid {alpha=}")

        acf = a0 * (alpha - 1) / (2 * theta) * (1 + abs(times) / theta) ** (-alpha)

        zs = 1j * 2 * np.pi * freqs * theta

        def calculate_real_part_psd(alpha, zs):
            real_parts_psd = np.zeros(zs.shape)
            for index, z in enumerate(zs):
                real_parts_psd[index] = float((mp.e ** (z) * mp.expint(alpha, z)).real)
            return real_parts_psd

        real_parts_psd = calculate_real_part_psd(alpha, zs)

        psd = a0 * (alpha - 1) * real_parts_psd

        msd = (alpha - 2) * abs(times) / theta - 1 + (1 + abs(times) / theta) ** (-alpha + 2)
        msd *= a0 * theta / (alpha - 2)

        return acf, psd, msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        alpha = self.alpha
        order = 80
        theta = self.theta

        def make_grid_rational_chebyshev(order, theta, alpha):
            i = np.arange(order)
            x = -np.cos((2 * i + 1) / (2 * order) * np.pi)
            wx = np.pi / order * np.sqrt(1 - x**2)
            y = (1 + x) / (1 - x)
            wy = wx * 2 / (1 - x) ** 2
            pdf = y ** (alpha - 1) / sp.special.gamma(alpha) * np.exp(-y)
            taus = theta / y
            weights = wy * pdf
            return taus, weights

        taus, weights = make_grid_rational_chebyshev(order, theta, alpha)

        # Prune quadrature grid.
        mask = weights > weights.max() * 1e-34
        taus = taus[mask]
        print(f"The number of taus that we kept is{len(taus)}")
        weights = weights[mask]

        traj = np.zeros((nseq, nstep))

        for tau, weight in zip(taus, weights, strict=True):
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

    def __attrs_post_init__(self):
        omega0 = 2 * np.pi * self.f0

        theta = np.array([[0, 1], [-(omega0**2), -omega0 / self.q]])
        b = np.array([[0, 0], [0, 0.5 * self.a0 * omega0**4]])

        matexp = sp.linalg.expm(theta)
        self.matexp = matexp

        upper = 2 * np.dot(matexp, np.dot(b, matexp.T))
        lower = 2 * b

        covar = sp.linalg.solve_continuous_lyapunov(theta, upper - lower)
        self.covar = covar

    @property
    def typst(self) -> str:
        return f"upright(S)({self.a0}, {self.f0}, {self.q})"

    @property
    def latex(self) -> str:
        return rf"\operatorname{{S}}({self.a0}, {self.f0}, {self.q})"

    def compute(
        self, freqs: NDArray[float], times: NDArray[float]
    ) -> tuple[NDArray[float], NDArray[float], NDArray[float]]:
        a0 = self.a0
        f0 = self.f0
        q = self.q
        eta = np.sqrt(abs(1 / (4 * q**2) - 1))
        ft = 2 * np.pi * f0 * abs(times)
        prefactor = a0 / (2 * np.pi * f0 * q)

        if 0 < q < 0.5:
            exp_arg_plus = (eta - 0.5 / q) * ft
            exp_arg_minus = (-eta - 0.5 / q) * ft
            sinh_prefactor = 1 / (2 * eta * q) * (1 - 3 * q**2)

            acf = q * (np.exp(exp_arg_plus) + np.exp(exp_arg_minus))
            acf += (np.exp(exp_arg_plus) - np.exp(exp_arg_minus)) / (2 * eta)
            acf *= 0.5 * np.pi * a0 * f0

            msd = (1 - q**2) * (np.exp(exp_arg_plus) + np.exp(exp_arg_minus))
            msd += sinh_prefactor * (np.exp(exp_arg_plus) - np.exp(exp_arg_minus))
            msd *= prefactor / 2

        elif q >= 0.5:
            acf = a0 * np.pi * f0 * q * np.exp(-0.5 * ft / q)
            msd = prefactor * np.exp(-ft / (2 * q))
            if q == 0.5:
                acf *= 1 + ft
                msd *= 1 + 2 / 3 * np.pi * f0 * abs(times)
                msd *= 1 - q**2
            else:
                scarg = eta * ft
                sin_prefactor = 1 / (2 * eta * q) * (1 - 3 * q**2)
                acf *= np.cos(scarg) + np.sin(scarg) / (2 * eta * q)
                msd *= (1 - q**2) * np.cos(scarg) + sin_prefactor * np.sin(scarg)
        else:
            raise ValueError(f"Invalid {q=}")

        msd += a0 * abs(times) - prefactor * (1 - q**2)
        psd = a0 * f0**4 / ((freqs**2 - f0**2) ** 2 + (freqs * f0 / q) ** 2)
        return acf, psd, msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        noise = rng.multivariate_normal(np.zeros(2), self.covar, size=(nstep, nseq)).transpose(
            0, 2, 1
        )
        traj = np.zeros((nstep, 2, nseq))
        traj[0, :, :] = noise[0, :, :]

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

    def compute(
        self, freqs: NDArray[float], times: NDArray[float]
    ) -> tuple[NDArray[float], NDArray[float], NDArray[float]]:
        acf = 0.5 * self.a0 / self.tau * np.exp(-abs(times / self.tau))
        psd = self.a0 / (1 + (2 * np.pi * self.tau * freqs) ** 2)
        msd = self.a0 * (times + self.tau * (np.exp(-abs(times) / self.tau) - 1))
        return acf, psd, msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        traj = np.zeros((nseq, nstep))
        var = self.a0 / (2 * self.tau)
        noise = rng.normal(0, np.sqrt(var * (1 - np.exp(-2 / self.tau))), size=(nseq, nstep))
        traj[:, 0] = noise[:, 0]
        prop = np.exp(-1 / self.tau)
        return sp.signal.lfilter([1.0], [1.0, -prop], x=noise)


@attrs.define
class WhiteTerm(BaseTerm):
    @property
    def typst(self) -> str:
        return f"upright(W)({self.a0})"

    @property
    def latex(self) -> str:
        return rf"\operatorname{{W}}({self.a0})"

    def compute(
        self, freqs: NDArray[float], times: NDArray[float]
    ) -> tuple[NDArray[float], NDArray[float], NDArray[float]]:
        acf = np.zeros_like(times)
        acf[0] = self.a0
        psd = np.full_like(freqs, self.a0)
        msd = self.a0 * times
        return acf, psd, msd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        return rng.normal(loc=0.0, scale=np.sqrt(self.a0), size=(nseq, nstep))


def compute(
    terms: list[BaseTerm], freqs: NDArray[float], times: NDArray[float]
) -> tuple[NDArray[float], NDArray[float], NDArray[float], float, float | None, str, str]:
    """Construct a power spectrum and autocorrelation function.

    Parameters
    ----------
    terms
        Terms that contribute to the kernel.
    freqs
        The array of angular frequencies for which to compute the spectrum.
    times
        The array of times for which to compute the autocorrelation function.

    Returns
    -------
    psd
        The power spectrum on the requested grid.
    acf
        The autocorrelation function.
    msd
        The mean-squared displacement.
    corrtime_int
        The integrated correlation time.
    corrtime_exp
        The exponential correlation time, or None if not defined.
    typst
        A typst equation describing the kernel
    latex
        A latex equation describing the kernel
    """
    acf = 0
    psd = 0
    msd = 0
    typst_terms = []
    latex_terms = []
    corrtimes_exp = []
    for term in terms:
        my_acf, my_psd, my_msd = term.compute(freqs, times)
        acf += my_acf
        psd += my_psd
        msd += my_msd
        typst_terms.append(term.typst)
        latex_terms.append(term.latex)
        if isinstance(term, ExpTerm):
            corrtimes_exp.append(term.tau)
        elif not isinstance(term, WhiteTerm):
            corrtimes_exp.append(None)
    acint = psd[0]
    if abs(acint - ACINT_REF) > 1e-10:
        raise ValueError(f"kernel has {acint=}")
    variance = acf[0]
    corrtime_int = 0.5 * acint / variance
    corrtime_exp = None
    if len(corrtimes_exp) == 1 and corrtimes_exp[0] is not None:
        corrtime_exp = corrtimes_exp[0]
    check_quadratic(freqs, psd)
    return (
        psd,
        acf,
        msd,
        corrtime_int,
        corrtime_exp,
        " + ".join(typst_terms),
        " + ".join(latex_terms),
    )


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


def check_quadratic(freqs, psd):
    """Check that the psd is approximately quadratic in the first 40 steps

    - The deviation should be less than 2.5 % for the first 20 steps.
    - The deviation should be less than 10.0 % for the first 40 steps.
    The noise on the spectrum derived from 256 sequences (the highest we consider) is about 5%,
    meaning that a quadratic model will be suitable for a sufficiently large part of the spectrum,
    at least 40 points, if this test passes.
    """
    for nfit, threshold in (20, 0.025), (40, 0.100):
        my_freqs = freqs[:nfit]
        my_psd = psd[:nfit].copy()

        # Fit a simple quadratic, manually for robustness
        my_psd -= my_psd.mean()
        quad = my_freqs**2
        quad -= quad.mean()
        par = np.dot(quad, my_psd) / np.dot(quad, quad)
        fit_psd = par * quad
        relerr = float(np.linalg.norm(fit_psd - my_psd) / np.linalg.norm(my_psd))

        if relerr > threshold:
            raise ValueError(
                "The PSD is not approximated well by a quadratic model in the low-frequency domain:"
                f" {nfit=} {threshold=} {relerr=}"
            )
