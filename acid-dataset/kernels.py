import attrs
import numpy as np
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
    typst
        A typst equation describing the kernel
    latex
        A latex equation describing the kernel
    """
    acf = 0
    psd = 0
    typst_terms = []
    latex_terms = []
    for term in terms:
        my_acf, my_psd = term.compute(freqs, times)
        acf += my_acf
        psd += my_psd
        typst_terms.append(term.typst)
        latex_terms.append(term.latex)
    acint = psd[0]
    if abs(acint - ACINT_REF) > 1e-10:
        raise ValueError(f"kernel has {acint=}")
    variance = acf[0]
    corrtime_int = 0.5 * acint / variance
    check_quadratic(freqs, psd)
    return psd, acf, corrtime_int, " + ".join(typst_terms), " + ".join(latex_terms)


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
        if False:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            ax.plot(my_freqs, my_psd)
            ax.plot(my_freqs, fit_psd)
            fig.savefig(f"tmp{nfit}.pdf")
        # print(nfit, relerr)
        if relerr > threshold:
            raise ValueError(
                "The PSD is not approximated well by a quadratic model in the low-frequency domain:"
                f" {nfit=} {threshold=} {relerr=}"
            )
