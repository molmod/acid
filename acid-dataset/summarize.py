#!/usr/bin/env python3
"""Write a CSV file with a summary of the kernels"""

from runpy import run_path

import numpy as np
from settings import KERNELS
from stepup.core.api import amend
from stepup.core.script import driver


def info():
    return {"out": "output/kernels.csv"}


def run(out: str):
    with open(out, "w") as fh:
        for kernel in KERNELS:
            path_py = f"kernel_{kernel}.py"
            amend(inp=path_py)
            terms = run_path(path_py)["terms"]
            typst = " + ".join(term.typst for term in terms)
            latex = " + ".join(term.latex for term in terms)
            acint = 0
            variance = 0
            for term in terms:
                acf, psd = term.compute(np.zeros(1), np.zeros(1))
                acint += psd[0]
                variance += acf[0]
            corrtime_int = 0.5 * acint / variance
            print(f'"{kernel}","{typst}","{latex}",{corrtime_int:.3f}', file=fh)


if __name__ == "__main__":
    driver()
