#!/usr/bin/env python3
"""Definition of the StepUp workflow to rebuild the ACID dataset.

See README.md for instructions on how to run this workflow.
"""

from path import Path
from stepup.core.api import glob, mkdir, script, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
glob("../.git/**", _defer=True)
wrap_git("git log -n1 --pretty='format:%cs (%h)'", out="gitline.txt")

static(
    "acid-dataset.typ", "generate.py", "plot.py", "settings.py", "summarize.py", "../matplotlibrc"
)
glob("kernel*.py")
mkdir("output/")
script("summarize.py")
script("generate.py")
script("plot.py")
compile_typst("acid-dataset.typ", sysinp={"kernels": Path("output/kernels.csv")})
