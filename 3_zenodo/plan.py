#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import os

from stepup.core.api import glob, loadns, run, static
from stepup.data.api import make_inventory, sync_zenodo

run(
    "git archive --format=zip --output 3_zenodo/main.zip HEAD",
    out="3_zenodo/main.zip",
    workdir="../",
    recheck=True,
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
make_inventory("sync_zenodo_inventory.jsonl", paths=archive_paths)

official_settings = loadns("../1_dataset/settings.json", do_amend=True)
used_settings = loadns("../1_dataset/output/settings.json", do_amend=True)
if official_settings == used_settings:
    # Only schedule the sync step with official settings.
    # This guarantees that, even if plan.py is skipped upon restarting the workflow,
    # no results derived from local settings are accidentally uploaded.
    sync_zenodo("sync_zenodo.yaml", "zenodo_description.md", "sync_zenodo_inventory.jsonl")
elif "STEPUP_DATA_ZENODO_TOKEN" in os.environ:
    raise RuntimeError("Refusing to upload data generated with local settings.")
