#!/usr/bin/env python3

import pickle
from collections.abc import Iterator

import matplotlib as mpl
from stacie import UnitConfig, plot_results
from stepup.core.script import driver

# For some low-data cases, the Lorentz model does not find any cutoff frequency
# for which the exponential correlation time can be estimated reliably.
# For these cases, it will consistenly fail to produce any results,
# making it impossible to plot the results.
KNOWN_FAILURES = (
    # (kernel, nstep, nseq, model)
    ("exp1p", 1024, 1, "lorentz"),
    ("exp1w", 1024, 1, "lorentz"),
    ("exp1w", 1024, 4, "lorentz"),
    ("exp1w", 4096, 1, "lorentz"),
)


def cases() -> Iterator[tuple[str, int, int, str, str]]:
    from settings import KERNELS, NSEQS, NSTEPS

    for kernel, models in KERNELS.items():
        for nseq in NSEQS:
            for nstep in NSTEPS:
                for model in models:
                    t = kernel, nstep, nseq, model
                    if t not in KNOWN_FAILURES:
                        yield t


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
