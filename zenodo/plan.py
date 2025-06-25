#!/usr/bin/env python3
from stepup.core.api import glob, static
from stepup.reprep.api import sync_zenodo, wrap_git

glob("../.git/**", _defer=True)
wrap_git(
    "git archive --format=zip --output zenodo/main.zip main", out="zenodo/main.zip", workdir="../"
)
static(
    "zenodo.md",
    "zenodo.yaml",
    "../acid-dataset/",
    "../acid-dataset/acid-dataset.pdf",
    "../validation-stacie-report/",
    "../validation-stacie-report/report-quad.pdf",
    "../validation-stacie-report/report-lorentz.pdf",
)
sync_zenodo("zenodo.yaml")
