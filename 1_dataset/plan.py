#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Definition of the StepUp workflow to rebuild the ACID dataset.

See README.md for instructions on how to run this workflow.
"""

from path import Path
from stepup.core.api import hold, loadns, run, shq, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
static("../.git/")
wrap_git("git describe --tags", stdout="git-version.txt")
wrap_git("git log -n1 --pretty='format:(%cs %h)'", stdout="git-date.txt")

# Declare static files
static(
    "overview.typ",
    "references.bib",
    "settings.json",
    "../matplotlibrc",
    "kernels/",
    "../lib/",
    "scripts/",
)
run(
    "./scripts/generate_lookup.py output/codec.zip",
    out="output/codec.zip",
)

zip_paths = []
# Generate all ZIP files
settings = loadns("settings.json", do_amend=True)
with hold():
    # Holding back the steps until they are all declared, so the slowest steps are run first.
    for kernel in settings.kernels:
        generate_inp = ["output/codec.zip", "settings.json"]
        run(
            f"./scripts/generate.py {shq(generate_inp)} {kernel} output/{kernel}.zip",
            inp=generate_inp,
            out=f"output/{kernel}.zip",
            # Indicate that pow is slower, only needed for run from scratch.
            # Later, actual timings are used.
            duration=2 if "pow" in kernel else 1,
        )
        zip_paths.append(Path(f"output/{kernel}.zip"))

# Generate summary plots, table and report.
run(
    "./scripts/summarize.py settings.json output/kernels.csv",
    inp="settings.json",
    out="output/kernels.csv",
)

plot_inp = ["../matplotlibrc", "output/codec.zip", "settings.json", *zip_paths]
plot_out = [
    "output/plot_seqs.svg",
    "output/plot_acs.svg",
    "output/plot_psds.svg",
    "output/plot_msds.svg",
]
run(f"./scripts/plot.py {shq(plot_inp)} {shq(plot_out)}", inp=plot_inp, out=plot_out)
compile_typst("overview.typ", inp="output/kernels.csv", sysinp={"kernels": "output/kernels.csv"})
