#!/usr/bin/env python3

import pickle
from collections.abc import Iterator

import numpy as np
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int]]:
    from settings import KERNELS, NSEQS, NSTEPS

    for kernel, models in KERNELS.items():
        for nstep in NSTEPS:
            for nseq in NSEQS:
                for model in models:
                    yield kernel, nstep, nseq, model


CASE_FMT = "{}_nstep{:05d}_nseq{:04d}_{}"


def case_info(kernel: str, nstep: int, nseq: int, model: str):
    name = f"{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}"
    return {
        "inp": f"output/estimate_{name}.pickle",
        "out": f"output/extract_{name}.npz",
        "model": model,
    }


def run(inp: str, out: str, model: str):
    with open(inp, "rb") as fh:
        results = pickle.load(fh)
    extra = {}
    if model == "lorentz":
        extra["corrtimes_exp"] = [r.props["corrtime_exp"] for r in results]
        extra["corrtimes_exp_std"] = [r.props["corrtime_exp_std"] for r in results]
    np.savez_compressed(
        out,
        allow_pickle=False,
        acints=[r.acint for r in results],
        acints_std=[r.acint_std for r in results],
        neffs=[r.neff for r in results],
        fcuts=[r.fcut for r in results],
        cost_zscores=[r.props["cost_zscore"] for r in results],
        criterion_zscores=[r.props["criterion_zscore"] for r in results],
        **extra,
    )


if __name__ == "__main__":
    driver()
