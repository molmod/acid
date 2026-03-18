#!/usr/bin/env python3
from path import Path
from stepup.core.api import glob, loadns, render_jinja, runsh, static
from stepup.reprep.api import sync_zenodo, wrap_git

glob("../.git/**", _defer=True)
wrap_git(
    "git archive --format=zip --output 2_zenodo/main.zip main",
    out="2_zenodo/main.zip",
    workdir="../",
)

dataset_path = Path("../1_dataset/")
output_path = Path("../1_dataset/output/")

static(
    "zenodo.md",
    "zenodo_yaml_template.yaml.jinja",
    dataset_path,
    dataset_path + "overview.pdf",
    dataset_path + "settings.json",
    output_path,
)
settings = loadns(dataset_path + "settings.json", do_amend=True)


for kernel in settings.kernels:
    zip_files = glob(output_path + f"{kernel}_*.zip")
    runsh(
        "zip -0 -j ${out} ${inp}",
        inp=zip_files,
        out=f"{kernel}.zip",
    )
render_jinja("zenodo_yaml_template.yaml.jinja", {"kernels": settings.kernels}, "zenodo.yaml")
glob("../LICENSE-*.txt")
sync_zenodo("zenodo.yaml")
