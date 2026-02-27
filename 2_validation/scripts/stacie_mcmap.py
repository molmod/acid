#!/usr/bin/env python3
"""Perform Monte Carlo simulations to validate the maximum a posteriori estimate."""

import argparse
import json
import pickle

import emcee
import numpy as np
from numpy.typing import NDArray
from path import Path
from stacie.cost import LowFreqCost
from stacie.cutoff import switch_func


def main():
    args = parse_args()
    run(args.inp, args.out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Perform Monte Carlo simulations to validate the maximum a posteriori estimate."
    )
    parser.add_argument(
        "inp",
        type=Path,
        help="Input pickle file with the results of the cutoff frequency optimization.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="JSON output file to store the MC results.",
    )
    return parser.parse_args()


def sane_covar(covar: NDArray[float]) -> bool:
    """Check whether the covariance is meaningful."""
    if not np.isfinite(covar).all():
        return False
    evals = np.linalg.eigvalsh(covar)
    if not (evals > 0).all():
        return False
    return evals.min() >= 1e-5 * evals.max()


def run(inp: Path, out: Path):
    # Get the results at the cutoff frequency with the lowest criterion.
    with open(inp, "rb") as fh:
        results = pickle.load(fh)
    if len(results) == 0:
        write_stub(out)
    else:
        run_mc(results, out)


def write_stub(out: Path):
    with open(out, "w") as fh:
        fh.write("{}\n")


def run_mc(results, out: Path):
    # The first item in the results list is the one with the lowest estimate
    # of the autocorrelation integral, and is likely to be quite far off.
    # This is a good candidate for detecting MAP failure.
    result = results[0]
    icut = min((props["criterion"], icut) for icut, props in enumerate(result.history))[1]
    props = result.history[icut]
    fcut = props["fcut"]

    print("MAP results (mean, covar, evals)")
    print(props["pars"])
    print(props["pars_covar"])
    print(np.linalg.eigvalsh(props["pars_covar"]))

    # Define the switching function and truncate all arrays
    weights = switch_func(result.spectrum.freqs, fcut, props.get("switch_exponent", 20.0))
    ncut = (weights >= 1e-3).nonzero()[0][-1]
    freqs = result.spectrum.freqs[:ncut]
    ndofs = result.spectrum.ndofs[:ncut]
    amplitudes = result.spectrum.amplitudes[:ncut]
    weights = weights[:ncut]

    # Define the logarithm of the probability density needed for the MC sampling.
    model = result.model
    model.configure_scales(result.spectrum.timestep, freqs, amplitudes)
    low_freq_cost = LowFreqCost(freqs, ndofs, amplitudes, weights, model)

    def lnprob(pars):
        return -low_freq_cost(pars)[0]

    # Define an EMCEE sampler
    npar = model.npar
    nwalker = 400
    rng = np.random.default_rng(0)
    ensemble0 = rng.multivariate_normal(props["pars"], props["pars_covar"], nwalker)
    assert ensemble0.shape == (nwalker, npar)
    sampler = emcee.EnsembleSampler(nwalker, npar, lnprob, vectorize=True)

    # Perform a short burn-in run
    mc_min = 200
    print(f"Burn-in {mc_min} MC iterations.")
    state = sampler.run_mcmc(ensemble0, mc_min)
    tau = sampler.get_autocorr_time(tol=0).max()
    ensemble1 = state.coords
    assert ensemble1.shape == (nwalker, npar)
    sampler.reset()

    # Production run to bring the final state in equilibrium,
    # tracking the autocorrelation of the chain.
    mc_max = 10000
    mc_iter = 0
    tau_fac = 50
    while mc_iter < tau * tau_fac:
        mc_add = int(np.ceil(max(mc_min / 2, tau * tau_fac - mc_iter)))
        if mc_iter + mc_add > mc_max:
            raise RuntimeError("Maximum number of iterations reached.")
        print(
            f"Additional {mc_add} MC iterations. (tau={tau:.1f}, <lp>={state.log_prob.mean():.1f})"
        )
        state = sampler.run_mcmc(ensemble1, mc_add)
        mc_iter += mc_add
        ensemble1 = state.coords
        assert ensemble1.shape == (nwalker, npar)
        tau = sampler.get_autocorr_time(tol=0).max()

    print(
        f"Converged in {mc_iter} iterations. (tau = {tau:.1f}, ncut = {ncut:.1f}, "
        f"<lp> = {state.log_prob.mean():.1f})"
    )
    print("MC results (mean, covar)")
    print(ensemble1.mean(axis=0))
    print(np.cov(ensemble1, rowvar=False, ddof=1))

    results = {
        "fcut": fcut,
        "map_pars": props["pars"].tolist(),
        "map_pars_covar": props["pars_covar"].tolist(),
        "mc_pars": ensemble1.mean(axis=0).tolist(),
        "mc_pars_covar": np.cov(ensemble1, rowvar=False, ddof=1).tolist(),
        "mc_samples": ensemble1.tolist(),
    }
    with open(out, "w") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
