#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import os

from stepup.core.api import glob, loadns, static
from stepup.reprep.api import sync_zenodo, wrap_git

static("../.git/")
wrap_git(
    "git archive --format=zip --output 3_zenodo/main.zip HEAD",
    out="3_zenodo/main.zip",
    workdir="../",
)

static("zenodo_description.md", "sync_zenodo.yaml", "../1_dataset/")

archive_paths = [
    "../1_dataset/overview.pdf",
    *static("../2_validation/validation.pdf"),
    "../1_dataset/output/settings.json",
    "../1_dataset/output/kernels.csv",
    "main.zip",
    *glob("../1_dataset/output/*.zip"),
    *static("../LICENSES/*.txt"),
]

official = loadns("../1_dataset/settings.json", do_amend=True)
used = loadns("../1_dataset/output/settings.json", do_amend=True)
if official != used and os.getenv("REPREP_ZENODO_TOKEN") is not None:
    raise RuntimeError("Refusing to upload data generated with local settings.")

sync_zenodo("sync_zenodo.yaml", archive_paths, path_description="zenodo_description.md")
