#!/usr/bin/env python3

import json
from collections.abc import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from stacie.plot import rms
from stepup.core.api import amend
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, str, str, str]]:
    amend(inp="kernels.json")
    with open("kernels.json") as fh:
        kernels = json.load(fh)
    for kernel, models in kernels.items():
        for model in models:
            yield kernel, model


CASE_FMT = "{}_{}"
NSEED = 2**6
INP_TEMPLATE = (
    "../validation-stacie-calc/output/extract_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.npz"
)


def case_info(kernel: str, model: str):
    amend(inp="nsteps.json")
    with open("nsteps.json") as fh:
        nsteps = json.load(fh)
    amend(inp="nseqs.json")
    with open("nseqs.json") as fh:
        nseqs = json.load(fh)
    out = [
        f"figures/plot_acint_scaling_{kernel}_{model}.svg",
        f"figures/plot_acint_ratios_{kernel}_{model}.svg",
    ]
    if model == "lorentz":
        out += [
            f"figures/plot_corrtime_exp_scaling_{kernel}_{model}.svg",
            f"figures/plot_corrtime_exp_ratios_{kernel}_{model}.svg",
        ]
    return {
        "inp": ["../matplotlibrc"]
        + [
            INP_TEMPLATE.format(
                kernel=kernel,
                nstep=nstep,
                nseq=nseq,
                model=model,
            )
            for nseq in nseqs
            for nstep in nsteps
        ],
        "out": out,
        "kernel": kernel,
        "nsteps": nsteps,
        "nseqs": nseqs,
        "model": model,
    }


def run(
    inp: list[str],
    out: str,
    kernel: str,
    nsteps: list[int],
    nseqs: list[int],
    model: str,
):
    mpl.rc_file(inp.pop(0))
    run_prop(inp, out[:2], kernel, nsteps, nseqs, model, "acints", 1.0, (7e-4, 4e-1))
    if model == "lorentz":
        run_prop(inp, out[2:], kernel, nsteps, nseqs, model, "corrtimes_exp", 5.0, (1e-3, 1))


def run_prop(
    inp: list[str],
    out: str,
    kernel: str,
    nsteps: list[int],
    nseqs: list[int],
    model: str,
    key: str,
    ref: float,
    ylim: tuple[float, float],
):
    colors = list(plt.rcParams["axes.prop_cycle"].by_key()["color"])[: len(nsteps)]
    step_corrs = [-0.3, -0.1, 0.1, 0.3]

    fig0, ax0 = plt.subplots()
    fig1, ax1 = plt.subplots()
    for nstep, step_corr, color in zip(nsteps, step_corrs, colors, strict=True):
        xs = []
        value_std = []
        value_rmspe = []
        value_bias = []
        for nseq in nseqs:
            inp = INP_TEMPLATE.format(
                kernel=kernel,
                nstep=nstep,
                nseq=nseq,
                model=model,
            )
            data = np.load(inp)
            x = np.log2(nseq)
            xs.append(x)
            values = np.array(data[key]) / ref
            values_std = np.array(data[f"{key}_std"]) / ref
            if len(values) > 1:
                value_std.append(np.std(values))
                value_rmspe.append(rms(values_std))
                value_bias.append(values.mean() - 1.0)
            else:
                value_std.append(np.nan)
                value_rmspe.append(np.nan)
                value_bias.append(np.nan)
        xs = np.array(xs)
        value_std = np.array(value_std)
        value_rmspe = np.array(value_rmspe)
        value_bias = np.array(value_bias)

        # Plot scaling
        ax0.plot(xs, value_std, color=color, label=f"$N={nstep}$", lw=0, marker="s")
        ax0.plot(xs, value_rmspe, color=color, ls=":")
        # ax0.plot(xs + 0.25, abs(value_bias), color=color, lw=0, marker=".")

        # plot ratio statistics
        ax1.plot(
            step_corr + xs,
            100 * value_std / value_rmspe,
            color=color,
            lw=0,
            marker="s",
            label=f"$N={nstep}$",
        )
        ax1.plot(step_corr + xs, 100 * value_bias / value_rmspe, color=color, lw=0, marker=".")

    # Draw grid lines
    nseqs = np.array([0.5 * nseqs[0], *nseqs, 2 * nseqs[-1]])
    xs = np.log2(nseqs)

    ax0.autoscale(False)
    for scale in 2.0 ** np.arange(-10, 50):
        ax0.plot(xs, scale / np.sqrt(nseqs), color="k", lw=0.5, alpha=0.2)
    ax0.set_ylim(*ylim)
    ax0.set_yscale("log")
    ax0.set_ylabel("Relative error")
    ax0.legend()
    ax1.axhline(0, color="k", lw=0.5, alpha=0.2)
    ax1.axhline(100, color="k", lw=0.5, alpha=0.2)
    ax1.set_ylabel(r"$100 \times$ Empirical error / Predicted error")
    ax1.set_ylim(top=200)
    ax1.legend(ncols=2, loc="upper center")

    for ax in [ax0, ax1]:
        ax.set_xticks(xs[1:-1], [f"{2**x:.0f}" for x in xs[1:-1]])
        ax.set_xlim(xs[1] - 0.5, xs[-2] + 0.5)
        ax.set_xlabel("Number of sequences $M$")

    fig0.savefig(out[0])
    plt.close(fig0)
    fig1.savefig(out[1])
    plt.close(fig1)


if __name__ == "__main__":
    driver()
