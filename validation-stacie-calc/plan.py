#!/usr/bin/env python3
"""Definition of the StepUp workflow for the validation of STACIE with the ACID test set.

See README.md for instructions on how to run this workflow.
"""

from stepup.core.api import glob, mkdir, script, static

static("../acid-dataset/")
glob("../acid-dataset/output/**", _defer=True)
static("settings.py", "../matplotlibrc")
mkdir("output/")
mkdir("figures/")

SCRIPTS = [
    "take_subset.py",
    "estimate.py",
    "extract.py",
    "monte_carlo.py",
    "plot_estimate.py",
]
for path in SCRIPTS:
    static(path)
    script(path)
