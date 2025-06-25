#!/usr/bin/env python3
"""Definition of the StepUp workflow for analyzing the validation of STACIE with the ACID test set.

See README.md for instructions on how to run this workflow.
"""

from stepup.core.api import glob, mkdir, script, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
glob("../.git/**", _defer=True)
wrap_git("git log -n1 --pretty='format:%cs (%h)'", out="gitline.txt")

static("../validation-stacie-calc/")
glob("../validation-stacie-calc/output/**", _defer=True)

mkdir("figures/")
mkdir("tables/")

static("../matplotlibrc")
glob("*.json")
SCRIPTS = [
    "plot_scaling.py",
    "plot_cutoff.py",
    "plot_monte_carlo.py",
    "plot_sequences.py",
    "tabulate_sanity_checks.py",
]
for path in SCRIPTS:
    static(path)
    script(path)

TYPS = ["report-quad.typ", "report-lorentz.typ"]
for path in TYPS:
    static(path)
    compile_typst(path)
