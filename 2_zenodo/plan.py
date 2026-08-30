#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

from stepup.core.api import loadns, static
from stepup.reprep.api import sync_zenodo, wrap_git

static("../.git/")
wrap_git(
    "git archive --format=zip --output 2_zenodo/main.zip main",
    out="2_zenodo/main.zip",
    workdir="../",
)

static(
    "zenodo_description.md",
    "sync_zenodo.yaml",
    "../1_dataset/overview.pdf",
    "../1_dataset/settings.json",
    "../3_validation/validation.pdf",
)

settings = loadns("../1_dataset/settings.json", do_amend=True)
archive_paths = [
    "../1_dataset/overview.pdf",
    "main.zip",
    *static([f"../1_dataset/output/{k}.zip" for k in settings.kernels]),
    "../3_validation/validation.pdf",
    *static("../LICENSES/*.txt"),
]
sync_zenodo("sync_zenodo.yaml", archive_paths, path_description="zenodo_description.md")
