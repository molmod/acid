#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Definition of the StepUp workflow to validate the ACID dataset.

See README.md for instructions on how to run this workflow.
"""

from path import Path
from stepup.core.api import glob, loadns, mkdir, runpy, static
from stepup.reprep.api import wrap_git

# Write Git information to text file for inclusion in documents.
glob("../.git/**", _defer=True)
wrap_git("git describe --tags", out="git-version.txt")
wrap_git("git log -n1 --pretty='format:(%cs %h)'", out="git-date.txt")


dataset_path = Path("../1_dataset/")
dataset_output_path = dataset_path + "output/"

# Declare static files
static(
    dataset_path,
    dataset_path + "settings.json",
    dataset_path + "kernels/",
    dataset_output_path,
    "../matplotlibrc",
    "scripts/",
)

glob(dataset_output_path + "*.zip")
glob(dataset_path + "kernels/*.py")
glob("scripts/*.py")
mkdir("output/")
settings = loadns(dataset_path + "settings.json", do_amend=True)

acf_consist_paths = []
stat_paths = []
codec_paths = []
for kernel in settings.kernels:
    runpy(
        "./${inp} ${out}",
        inp=[
            "scripts/check_acf_consistency.py",
            dataset_output_path + f"{kernel}.zip",
            dataset_output_path + "codec.zip",
            dataset_path + "settings.json",
        ],
        out=[f"output/{kernel}_acf_consist.npz"],
    )
    acf_consist_paths.append(f"output/{kernel}_acf_consist.npz")
    runpy(
        "./${inp} ${out}",
        inp=[
            "scripts/check_stationarity.py",
            dataset_output_path + f"{kernel}.zip",
            dataset_output_path + "codec.zip",
            dataset_path + "settings.json",
        ],
        out=[f"output/{kernel}_stationarity.npz"],
    )
    stat_paths.append(f"output/{kernel}_stationarity.npz")
    runpy(
        f"./${{inp}} {kernel} ${{out}}",
        inp=[
            "scripts/check_codec.py",
        ],
        out=[f"output/{kernel}_codec.npz"],
    )
    codec_paths.append(f"output/{kernel}_codec.npz")

runpy(
    f"./scripts/plot.py ../matplotlibrc --acf_consist {' '.join(acf_consist_paths)} "
    f"--stat {' '.join(stat_paths)} --codec {' '.join(codec_paths)} -- ${{out}}",
    inp=["scripts/plot.py", "../matplotlibrc", *acf_consist_paths, *stat_paths, *codec_paths],
    out=["output/acf_consist.svg", "output/stationarity.svg", "output/codec.svg"],
)
