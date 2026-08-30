#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Definition of the StepUp workflow to validate the ACID dataset.

See README.md for instructions on how to run this workflow.
"""

from path import Path
from stepup.core.api import loadns, run, shq, static
from stepup.reprep.api import compile_typst, wrap_git

# Write Git information to text file for inclusion in documents.
static("../.git/")
wrap_git("git describe --tags", stdout="git-version.txt")
wrap_git("git log -n1 --pretty='format:(%cs %h)'", stdout="git-date.txt")


dataset_path = Path("../1_dataset/")
dataset_output_path = dataset_path / "output/"

# Declare static files
static(
    dataset_path,
    "../matplotlibrc",
    "scripts/",
    "validation.typ",
    "references.bib",
)

settings = loadns(dataset_path + "settings.json", do_amend=True)

acf_consist_paths = []
stat_paths = []
codec_paths = []
for kernel in settings.kernels:
    paths_inp = [
        dataset_output_path / f"{kernel}.zip",
        dataset_output_path / "codec.zip",
        dataset_path / "settings.json",
    ]
    run(
        f"./scripts/check_acf_consistency.py {shq(paths_inp)} output/{kernel}_acf_consist.npz",
        inp=paths_inp,
        out=f"output/{kernel}_acf_consist.npz",
    )
    acf_consist_paths.append(f"output/{kernel}_acf_consist.npz")
    run(
        f"./scripts/check_stationarity.py {shq(paths_inp)} output/{kernel}_stationarity.npz",
        inp=paths_inp,
        out=f"output/{kernel}_stationarity.npz",
    )
    stat_paths.append(f"output/{kernel}_stationarity.npz")
    run(
        f"./scripts/check_codec.py {kernel} output/{kernel}_codec.npz",
        out=f"output/{kernel}_codec.npz",
    )
    codec_paths.append(f"output/{kernel}_codec.npz")

paths_svg_out = ["output/acf_consist.svg", "output/codec.svg"]
run(
    f"./scripts/plot.py ../matplotlibrc --acf_consist {shq(acf_consist_paths)} "
    f"--codec {shq(codec_paths)} -- {shq(paths_svg_out)}",
    inp=["../matplotlibrc", *acf_consist_paths, *stat_paths, *codec_paths],
    out=paths_svg_out,
)

run(
    f"./scripts/tabulate_stat.py {shq(stat_paths)} output/stationarity.csv",
    inp=stat_paths,
    out=["output/stationarity.csv"],
)

compile_typst(
    "validation.typ",
    inp="output/stationarity.csv",
    sysinp={"stationarity": "output/stationarity.csv"},
)
