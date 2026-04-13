#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Definition of the StepUp workflow to rebuild the ACID dataset.

See README.md for instructions on how to run this workflow.
"""

from path import Path
from stepup.core.api import glob, loadns, mkdir, runpy, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
glob("../.git/**", _defer=True)
wrap_git("git describe --tags", out="git-version.txt")
wrap_git("git log -n1 --pretty='format:(%cs %h)'", out="git-date.txt")

# Declare static files
static("overview.typ", "settings.json", "../matplotlibrc", "kernels/", "lib/", "scripts/")
glob("kernels/*.py")
glob("lib/*.py")
glob("scripts/*.py")
mkdir("output/")
runpy(
    "./${inp} ${out}",
    inp=["scripts/generate_lookup.py"],
    out=["output/codec.zip"],
)

zip_paths = []
# Generate all ZIP files
settings = loadns("settings.json", do_amend=True)
for kernel in settings.kernels:
    runpy(
        f"./${{inp}} {kernel} ${{out}}",
        inp=["scripts/generate.py", "output/codec.zip", "settings.json"],
        out=[f"output/{kernel}.zip"],
    )
    zip_paths.append(Path(f"output/{kernel}.zip"))

# Generate summary plots, table and report.
runpy("./${inp} ${out}", inp=["scripts/summarize.py", "settings.json"], out="output/kernels.csv")

runpy(
    "./${inp} ${out}",
    inp=["scripts/plot.py", "../matplotlibrc", "output/codec.zip", "settings.json", *zip_paths],
    out=[
        "output/plot_seqs.svg",
        "output/plot_acs.svg",
        "output/plot_psds.svg",
        "output/plot_msds.svg",
    ],
)
compile_typst("overview.typ", sysinp={"kernels": Path("output/kernels.csv")})
