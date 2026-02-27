#!/usr/bin/env python3
"""Definition of the StepUp workflow for analyzing the validation of STACIE with the ACID test set.

See README.md for instructions on how to run this workflow.
"""

from stepup.core.api import glob, loadns, mkdir, runpy, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
glob("../.git/**", _defer=True)
wrap_git("git describe --tags", out="git-version.txt")
wrap_git("git log -n1 --pretty='format:(%cs %h)'", out="git-date.txt")

# Declare static files.
static(
    "../1_acid_dataset/",
    "../1_acid_dataset/output/",
    "../1_acid_dataset/settings.json",
    "../matplotlibrc",
    "scripts/",
    "input/",
    "cases.yaml",
    "overview.typ",
    "plan_report.py",
    "report.typ",
    "references.bib",
    "summary_stats.typ",
)
glob("scripts/*.py")

# Extract and plot short sequences from ACID dataset for inclusion in documents.
settings = loadns("../1_acid_dataset/settings.json", do_amend=True)
mkdir("reports/")
mkdir("reports/shared/")
for kernel in settings.kernels:
    path_zip = f"../1_acid_dataset/output/{kernel}_nstep01024_nseq0256.zip"
    static(path_zip)
    runpy(
        "./${inp} ${out}",
        inp=[
            "scripts/plot_sequences_subset.py",
            path_zip,
            "../matplotlibrc",
        ],
        out=f"reports/shared/subset_{kernel}.svg",
    )

# Collect all JSON input files and hand them over to a report planning script.
for m in glob("input/${*case}/"):
    mkdir(f"reports/{m.case}/")
    paths_json = glob(f"input/{m.case}/*.json")
    runpy(
        f"./${{inp}} {m.case}",
        inp=["plan_report.py", *paths_json],
    )
compile_typst("overview.typ")
