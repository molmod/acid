#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Write a CSV file with a summary of the kernels"""

import argparse
from runpy import run_path

import numpy as np
from kernels import BaseTerm, ExpTerm, WhiteTerm
from path import Path
from stepup.core.api import amend, loadns

TMAX = 1024
FREQ_STEP = 1e-3
FMAX = 0.5
MAX_DOUBLINGS = 2


def main():
    args = parse_args()
    run(args.settings, args.out)


def parse_args():
    parser = argparse.ArgumentParser(description="Write a CSV file with a summary of the kernels")
    parser.add_argument("settings", type=Path, help="The settings JSON path.")
    parser.add_argument("out", type=Path, help="The output CSV path.")
    return parser.parse_args()


def compute_n90(
    nonwhite_terms: list[BaseTerm],
    acf_total: float,
    tmax: int = TMAX,
    doubling_index: int = 0,
) -> float:
    """
    Compute the settling time-lag of a kernel's analytical ACF integral
    with a tolerance of 10%.

    Parameters
    ----------
    nonwhite_terms
        A list of kernel terms, excluding white noise.
    acf_total
        Target value of the ACF integral, excluding the white noise terms.
    tmax
        Maximum time lag to be considered in the cumsum.
    doubling_index
        Number of times ``nlags`` has already been doubled.

    Returns
    -------
    n90
        Smallest lag beyond which the ACF integral has settled
        with a tolerance of 10%.

    Raises
    ------
    RuntimeError
        If the integral has not settled after ``MAX_DOUBLINGS`` doublings.
    """
    tol = 0.1
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

    if doubling_index == MAX_DOUBLINGS:
        raise RuntimeError(
            f"ACF integral did not settle with a tolerance of 10% "
            f"after doubling the range {MAX_DOUBLINGS} times."
        )

    return compute_n90(nonwhite_terms, acf_total, tmax=2 * tmax, doubling_index=doubling_index + 1)


def compute_f90(
    nonwhite_terms: list[BaseTerm],
    variance_total: float,
    df: float = FREQ_STEP,
    fmax: float = FMAX,
    doubling_index: int = 0,
) -> float:
    """
    Compute the frequency below which the cumulative PSD integral first reaches
    90% of ``variance_total``.

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
    doubling_index
        Number of times ``fmax`` has already been doubled.

    Returns
    -------
    f90
        Frequency at which the cumulative PSD integral first reaches
        90% of ``variance_total``.

    Raises
    ------
    RuntimeError
        If the target fraction has not been reached after ``MAX_DOUBLINGS`` doublings.
    """
    freqs = np.arange(0.0, fmax + df, df)
    psd = sum(term.compute_psd(freqs) for term in nonwhite_terms)
    captured = (psd[0] + 2.0 * np.concatenate(([0.0], np.cumsum(psd[1:])))) * df
    frac = captured / variance_total

    idx = np.argmax(frac >= 0.9)
    if frac[idx] >= 0.9:
        return freqs[idx]

    if doubling_index == MAX_DOUBLINGS:
        raise RuntimeError(
            f"PSD integral did not reach 90% of the analytical variance"
            f"after doubling the frequency range {MAX_DOUBLINGS} times."
        )

    return compute_f90(
        nonwhite_terms,
        variance_total,
        df=df,
        fmax=2 * fmax,
        doubling_index=doubling_index + 1,
    )


def run(inp: Path, out: Path):
    with open(out, "w") as fh:
        settings = loadns(inp)
        for kernel in settings.kernels:
            path_py = f"kernels/{kernel}.py"
            amend(inp=path_py)
            terms = run_path(path_py)["terms"]
            typst = " + ".join(term.typst for term in terms)
            latex = " + ".join(term.latex for term in terms)

            acint = 0.0
            variance = 0.0
            corrtimes_exp = []
            nonwhite_terms = []
            acint_nonwhite = 0.0
            variance_nonwhite = 0.0
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
                    if isinstance(term, ExpTerm):
                        corrtimes_exp.append(term.tau)
                    else:
                        corrtimes_exp.append(None)

            corrtime_int = 0.5 * acint / variance
            corrtime_exp = None
            if len(corrtimes_exp) == 1 and corrtimes_exp[0] is not None:
                corrtime_exp = corrtimes_exp[0]
            corrtime_exp_str = "/" if corrtime_exp is None else f"{corrtime_exp:.3f}"
            n90 = compute_n90(nonwhite_terms, acint_nonwhite)
            f90 = compute_f90(nonwhite_terms, variance_nonwhite)

            print(
                f'"{kernel}","{typst}","{latex}",{variance:.3f},{acint:.3f},'
                f'{corrtime_int:.3f},"{corrtime_exp_str}",{int(n90)},{f90:.3f}',
                file=fh,
            )


if __name__ == "__main__":
    main()
