# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import attrs
import numpy as np
import scipy as sp
from numpy.typing import NDArray

__all__ = ("compute",)


ACINT_REF = 1.0


@attrs.define
class BaseTerm:
    c0: float = attrs.field(converter=float)

    @property
    def typst(self):
        raise NotImplementedError

    @property
    def latex(self):
        raise NotImplementedError

    def compute(self, freqs: NDArray[float], times: NDArray[float]):
        raise NotImplementedError


@attrs.define
class SHOTerm(BaseTerm):
    f0: float = attrs.field(converter=float)
    q: float = attrs.field(converter=float)
    matexp: NDArray[float] = attrs.field(init=False)
    covar: NDArray[float] = attrs.field(init=False)

    def __attrs_post_init__(self):
        omega0 = 2 * np.pi * self.f0

        theta = np.array([[0, 1], [-(omega0**2), -omega0 / self.q]])
        b = np.array([[0, 0], [0, 0.5 * self.c0 * omega0**4]])

        matexp = sp.linalg.expm(theta)
        self.matexp = matexp

        upper = 2 * np.dot(matexp, np.dot(b, matexp.T))
        lower = 2 * b

        covar = sp.linalg.solve_continuous_lyapunov(theta, upper - lower)
        self.covar = covar

    @property
    def typst(self):
        return f"upright(S)({self.c0}, {self.f0}, {self.q})"

    @property
    def latex(self):
        return rf"\operatorname{{S}}({self.c0}, {self.f0}, {self.q})"

    def compute(self, freqs: NDArray[float], times: NDArray[float]):
        c0 = self.c0
        f0 = self.f0
        q = self.q
        eta = np.sqrt(abs(1 / (4 * q**2) - 1))
        ft = 2 * np.pi * f0 * times
        if 0 < q < 0.5:
            acf = q * (np.exp((eta - 0.5 / q) * ft) + np.exp((-eta - 0.5 / q) * ft))
            acf += (np.exp((eta - 0.5 / q) * ft) - np.exp((-eta - 0.5 / q) * ft)) / (2 * eta)
            acf *= 0.5 * np.pi * c0 * f0
        elif q >= 0.5:
            acf = c0 * np.pi * f0 * q * np.exp(-0.5 * ft / q)
            if q == 0.5:
                acf *= 1 + ft
            else:
                scarg = eta * ft
                acf *= np.cos(scarg) + np.sin(scarg) / (2 * eta * q)
        else:
            raise ValueError(f"Invalid {q=}")
        psd = c0 * f0**4 / ((freqs**2 - f0**2) ** 2 + (freqs * f0 / q) ** 2)
        return acf, psd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        noise = rng.multivariate_normal(np.zeros(2), self.covar, size=(nseq, nstep)).transpose(
            2, 0, 1
        )
        traj = np.zeros((2, nseq, nstep))
        traj[:, :, 0] = noise[:, :, 0]

        for istep in range(1, nstep):
            traj[:, :, istep] = noise[:, :, istep] + self.matexp @ traj[:, :, istep - 1]
        return traj[0, :, :]


@attrs.define
class ExpTerm(BaseTerm):
    tau: float = attrs.field(converter=float)

    @property
    def typst(self):
        return f"upright(E)({self.c0}, {self.tau})"

    @property
    def latex(self):
        return rf"\operatorname{{E}}({self.c0}, {self.tau})"

    def compute(self, freqs: NDArray[float], times: NDArray[float]):
        acf = 0.5 * self.c0 / self.tau * np.exp(-abs(times / self.tau))
        psd = self.c0 / (1 + (2 * np.pi * self.tau * freqs) ** 2)
        return acf, psd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        traj = np.zeros((nseq, nstep))
        var = self.c0 / (2 * self.tau)
        noise = rng.normal(0, np.sqrt(var * (1 - np.exp(-2 / self.tau))), size=(nseq, nstep))
        traj[:, 0] = noise[:, 0]
        prop = np.exp(-1 / self.tau)
        for istep in range(1, nstep):
            traj[:, istep] = noise[:, istep] + prop * traj[:, istep - 1]

        return traj


@attrs.define
class WhiteTerm(BaseTerm):
    @property
    def typst(self):
        return f"upright(W)({self.c0})"

    @property
    def latex(self):
        return rf"\operatorname{{W}}({self.c0})"

    def compute(self, freqs: NDArray[float], times: NDArray[float]):
        acf = np.zeros_like(times)
        acf[0] = self.c0
        psd = np.full_like(freqs, self.c0)
        return acf, psd

    def sample(self, nseq: int, nstep: int, rng: np.random.Generator) -> NDArray[float]:
        return rng.normal(loc=0.0, scale=np.sqrt(self.c0), size=(nseq, nstep))


def compute(
    terms: list[BaseTerm], freqs: NDArray[float], times: NDArray[float]
) -> tuple[NDArray[float], NDArray[float], float, str, str]:
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
    typst_terms = []
    latex_terms = []
    corrtimes_exp = []
    for term in terms:
        my_acf, my_psd = term.compute(freqs, times)
        acf += my_acf
        psd += my_psd
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
    return psd, acf, corrtime_int, corrtime_exp, " + ".join(typst_terms), " + ".join(latex_terms)


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

        # print(nfit, relerr)
        if relerr > threshold:
            raise ValueError(
                "The PSD is not approximated well by a quadratic model in the low-frequency domain:"
                f" {nfit=} {threshold=} {relerr=}"
            )
