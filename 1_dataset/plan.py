#!/usr/bin/env python3
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
static("acid-dataset.typ", "settings.json", "../matplotlibrc", "kernels/", "lib/", "scripts/")
glob("kernels/*.py")
glob("lib/*.py")
glob("scripts/*.py")

# Generate all ZIP files
settings = loadns("settings.json", do_amend=True)
mkdir("output/")
paths_examples = []
for kernel in settings.kernels:
    for nstep in settings.nsteps:
        for nseq in settings.nseqs:
            runpy(
                f"./${{inp}} {kernel} {nstep} {nseq} {settings.nseed} ${{out}}",
                inp="scripts/generate.py",
                out=f"output/{kernel}_nstep{nstep:05d}_nseq{nseq:04d}.zip",
            )
    paths_examples.append(
        Path(f"output/{kernel}_nstep{settings.nsteps[0]:05d}_nseq{settings.nseqs[-1]:04d}.zip")
    )

# Generate summary plots, table and report.
runpy("./${inp} ${out}", inp=["scripts/summarize.py", "settings.json"], out="output/kernels.csv")
runpy(
    "./${inp} ${out}",
    inp=["scripts/plot.py", "../matplotlibrc", *paths_examples],
    out=["output/plot_seqs.svg", "output/plot_acs.svg", "output/plot_psds.svg"],
)
compile_typst("acid-dataset.typ", sysinp={"kernels": Path("output/kernels.csv")})
