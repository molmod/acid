#!/usr/bin/env python3

import json
from collections.abc import Iterator

import numpy as np
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
    out_prefix = f"tables/{kernel}_{model}"
    return {
        "inp": [
            INP_TEMPLATE.format(
                kernel=kernel,
                nstep=nstep,
                nseq=nseq,
                model=model,
            )
            for nseq in nseqs
            for nstep in nsteps
        ],
        "out": [
            f"{out_prefix}_neff.csv",
            f"{out_prefix}_cost_zscore.csv",
            f"{out_prefix}_criterion_zscore.csv",
        ],
        "out_prefix": out_prefix,
        "kernel": kernel,
        "nsteps": nsteps,
        "nseqs": nseqs,
        "model": model,
    }


def run(
    out_prefix: str,
    kernel: str,
    nsteps: list[int],
    nseqs: list[int],
    model: str,
):
    # Collect data for tables
    col_header = [f"$M={nseq}$" for nseq in nseqs]
    row_header = [f"$N={nstep}$" for nstep in nsteps]
    fields = [
        ("neff", 40, False),
        ("cost_zscore", 2.0, True),
        ("criterion_zscore", 2.0, True),
    ]
    cells = {field: [] for field, _, _ in fields}
    for nstep in nsteps:
        rows = {}
        for field, _, _ in fields:
            rows[field] = []
            cells[field].append(rows[field])
        for nseq in nseqs:
            inp = INP_TEMPLATE.format(
                kernel=kernel,
                nstep=nstep,
                nseq=nseq,
                model=model,
            )
            data = np.load(inp)
            for field, threshold, upper in fields:
                values = data[field + "s"]
                num_safe = (values >= threshold if upper else values <= threshold).sum()
                rows[field].append(str(num_safe))

    # Write CSV files with table data.
    for field, _, _ in fields:
        with open(f"{out_prefix}_{field}.csv", "w") as fh:
            print(",".join(["", *col_header]), file=fh)
            for header, row in zip(row_header, cells[field], strict=True):
                print(",".join([header, *row]), file=fh)


if __name__ == "__main__":
    driver()
