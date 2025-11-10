#!/usr/bin/env python3

import pickle
from collections.abc import Iterator

import matplotlib as mpl
from stacie import UnitConfig, plot_results
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int, int, str, str]]:
    from settings import KERNELS, NSEQS, NSTEPS

    for kernel, models in KERNELS.items():
        for nseq in NSEQS:
            for nstep in NSTEPS:
                for model in models:
                    yield kernel, nstep, nseq, model


CASE_FMT = "{}_nstep{:05d}_nseq{:04d}_{}"


def case_info(kernel: str, nstep: int, nseq: int, model: str):
    suffix = f"{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}"
    return {
        "inp": [
            "../matplotlibrc",
            f"output/estimate_{suffix}.pickle",
        ],
        "out": f"figures/estimate_{suffix}.pdf",
    }


def run(inp: list[str], out: str):
    mpl.rc_file(inp.pop(0))
    with open(inp.pop(0), "rb") as fh:
        results = pickle.load(fh)
    unit_config = UnitConfig()
    plot_results(out, results, unit_config, figsize=(6, 4))


if __name__ == "__main__":
    driver()
