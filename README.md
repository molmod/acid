<!--
SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

:rotating_light:
This repository is being refactored to prepare for the next major release, ACID 2.
The information below describes how ACID 2 will be organized after the refactoring has been completed.

You can view the latest version of the ACID 1 dataset and validation results at the following URLs:

- https://github.com/molmod/acid/tree/acid1
- https://zenodo.org/records/18044643

# The AutoCorrelation Integral Drill (ACID) 2 -- Dataset

This repository contains the scripts and
[StepUp workflow](https://reproducible-reporting.github.io/stepup-core/stable/)
to regenerate the "AutoCorrelation Integral Drill" (ACID) dataset.
The ACID dataset set comprises a diverse collection of synthetic time series
designed to evaluate the performance of algorithms that compute the autocorrelation integral.
The set contains in total 15360 test cases, and each case consists of one or more time series.
The cases differ in the kernel characterizing the time correlations, the number of time series,
and the length of the time series.
For each combination of kernel, number of sequences and sequence length,
64 test cases are generated with different random seeds
to allow for a systematic validation of uncertainty estimates.
The total dataset, once generated, is about 43 GB in size.

In ACID 1 releases, the validation of STACIE with ACID was included in this repository.
As of ACID 2, the validation results are released separately in a different repository:
<https://github.com/molmod/acid-test>.

A description, the full data and and an archived copy of this repository can be found on Zenodo:
[10.5281/zenodo.15722902](https://doi.org/10.5281/zenodo.15722902).

## License

The copyright disclaimer and license conditions are specified at the beginning of each file in the repository,
or, when the header cannot be edited, in the `RESUSE.toml` file.

In summary, the majority of the files in this repository are licensed under
the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).
The main exceptions are the Python files, which have a choice of license between
CC BY-SA 4.0 and the GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later).

License deeds and legal code for all licenses used in this repository are available in the `LICENSES/` directory.
They can also be consulted online at the following URLs:

- <https://creativecommons.org/licenses/by-sa/4.0/>
- <https://www.gnu.org/licenses/lgpl-3.0.html>
- <https://creativecommons.org/publicdomain/zero/1.0/>

## Citation

If you use this dataset in your research, please cite the following publication:

> Gözdenur Toraman, Dieter Fauconnier, and Toon Verstraelen
> "STable AutoCorrelation Integral Estimator (STACIE):
> Robust and accurate transport properties from molecular dynamics simulations"
> *Journal of Chemical Information and Modeling* 2025, 65 (19), 10445–10464,
> [doi:10.1021/acs.jcim.5c01475](https://doi.org/10.1021/acs.jcim.5c01475),
> [arXiv:2506.20438](https://arxiv.org/abs/2506.20438).
>
> ```bibtex
> @article{Toraman2025,
>  author = {G\"{o}zdenur Toraman and Dieter Fauconnier and Toon Verstraelen},
>  title = {STable AutoCorrelation Integral Estimator (STACIE): Robust and accurate transport properties from molecular dynamics simulations},
>  journal = {Journal of Chemical Information and Modeling},
>  volume = {65},
>  number = {19},
>  pages = {10445--10464},
>  year = {2025},
>  month = {sep},
>  url = {https://doi.org/10.1021/acs.jcim.5c01475},
>  doi = {10.1021/acs.jcim.5c01475},
> }
> ```

## Overview

This repository consists of three parts:

1. [`1_dataset/`](1_dataset/):
   A workflow to generate the ACID 2 dataset.
1. [`2_validation/`](2_validation/):
   A workflow to validate the generated dataset.
1. [`3_zenodo/`](3_zenodo/):
   A workflow to package and upload the generated data to Zenodo.

## How to Run the Workflows

The workflows in this repository can be executed on a compute cluster
that supports [SLURM](https://slurm.schedmd.com/) job scheduling,
or on a local machine with sufficient resources.
All results on Zenodo were generated on an `x86_64` Linux system, the Tier2 VSC compute cluster Donphan.
For development, the software environment can also be set up on macOS (Apple Silicon).
Note that time series generated on macOS are not guaranteed to be identical to those on Linux,
due to differences in floating-point arithmetic and numerical libraries.
They are, however, equally valid samples of the same stochastic processes.

### Setting up the software environment

The software environment is defined in `pyproject.toml`,
and the exact versions of all Python packages are pinned in `uv.lock`.
The same pins are exported to `pylock.toml`,
the standard Python lock file format ([PEP 751](https://peps.python.org/pep-0751/)),
which can also be installed without uv, e.g. with `pip install -r pylock.toml` (pip 26.1 or newer).
To create the environment, you only need `curl` and one of the following systems:

- Linux on `x86_64`,
- macOS 14 or newer on Apple Silicon (`arm64`).

Run the following script in the root of the repository:

```bash
./setup.sh
```

This script downloads a fixed version of [uv](https://docs.astral.sh/uv/)
and uses it to create a virtual environment in the `.venv` directory,
with Python 3.14 and exactly the package versions listed in `uv.lock`.
It also installs the [Typst](https://typst.app/) compiler in `.venv/bin`.
Everything is installed in the `.venv` directory, including the uv cache,
so you can remove it and run `setup.sh` again to start from scratch.

### Activating the environment

The `setup.sh` script creates three ways to activate the environment:

- Run `./shell.sh` to start a subshell with the environment activated.
  When you exit the subshell, you will return to your original environment.

- Load the LMod module `acid`, which is the most convenient option on an HPC cluster:

  ```bash
  module use .venv/modules
  module load acid
  ```

- If you use [`direnv`](https://direnv.net/),
  the generated `.envrc` file activates the environment when you `cd` into the repository.
  You can safely remove `.envrc` if you do not want to use `direnv`.
  (It is not checked into Git.)

Running only `source .venv/bin/activate` is not sufficient,
because the environment also sets `PYTHONPATH`, so that the scripts can import the modules in `lib/`,
`STEPUP_PATH_FILTER`, so that StepUp reruns steps when files in `lib/` change,
`TYPST_IGNORE_SYSTEM_FONTS`, so that Typst only uses its built-in fonts,
and `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR`, so that uv keeps its files in `.venv`.

If you use a VSCode Tunnel, first activate the environment in a terminal,
and then start the tunnel from that terminal, so it inherits the environment variables.

### Running the workflows

After the environment has been created,
you can run or submit the script `job.sh` in `1_dataset/`, `2_validation/`, or `3_zenodo/`.
For example:

```bash
cd 1_dataset/
sbatch job.sh
```

The job scripts load the `acid` module, so they require LMod.
Alternatively, you can activate the environment yourself
and run `sb` or `stepup build` in one of these directories.
StepUp's watch mode, which reruns steps when files change, is only supported on Linux.

### Updating the software environment

The environment is managed with [uv](https://docs.astral.sh/uv/).
After activating the environment, the following commands are useful:

```bash
uv add somepackage     # Add a new package to the environment
uv remove somepackage  # Remove a package from the environment
uv lock --upgrade      # Upgrade all packages to their latest versions
uv sync --locked       # Make the environment match uv.lock, e.g. after a git pull
```

The first three commands update `pyproject.toml` and/or `uv.lock`.
The pre-commit hook (see below) regenerates `pylock.toml` from `uv.lock`.
Commit these files to Git, so that others get exactly the same package versions.
The supported platforms are listed under `required-environments` in `pyproject.toml`,
so that `uv lock` only selects package versions with wheels for all of them.

The Python, uv and Typst versions are set at the beginning of `setup.sh`:

- To change the Python version, update `PYTHON_VERSION` in `setup.sh`.
  For a new minor version (e.g. 3.15), also update `requires-python` in `pyproject.toml`
  and run `uv lock`.
  Then remove `.venv` and run `setup.sh` again.
- To upgrade uv, change `UV_VERSION` and the `UV_SHA256` checksums of both platforms in `setup.sh`,
  and the `rev` of `uv-pre-commit` in `.pre-commit-config.yaml`.
  Then run `setup.sh` again.
  The SHA256 checksums are listed in `uv-x86_64-unknown-linux-musl.tar.gz.sha256`
  and `uv-aarch64-apple-darwin.tar.gz.sha256`
  on the [uv releases page](https://github.com/astral-sh/uv/releases).
- To upgrade Typst, change `TYPST_VERSION` and the `TYPST_SHA256` checksums of both platforms
  in `setup.sh` and run it again.
  The SHA256 checksums are listed next to `typst-x86_64-unknown-linux-musl.tar.xz`
  and `typst-aarch64-apple-darwin.tar.xz`
  on the [Typst releases page](https://github.com/typst/typst/releases).

All documents and figures use only the fonts that come with Typst and Matplotlib,
so no fonts need to be installed on the system.
For Typst, this is enforced by `TYPST_IGNORE_SYSTEM_FONTS` in the activated environment.

## How to Work With This Git Repository

Please, follow these guidelines to make clean commits to this repository:

1. Set up the software environment as explained above.
   It includes [pre-commit](https://pre-commit.com/).
1. Install the pre-commit hook by running `pre-commit install` in the root directory of this repository.
1. Update the file `CHANGELOG.md` to describe changes.
1. Use `git commit` as you normally would.

With the environment activated,
the unit tests in `tests/` can be run with `pytest` in the root directory of this repository.

## How to Make a New Release

After having updated actual contents of the dataset, the following steps are needed
to make a new release on GitHub and Zenodo:

- Update `CHANGELOG.md` with a new version section.
  Double check the changes since the last release.

- Update the version number in `3_zenodo/sync_zenodo.yaml` and `pyproject.toml`,
  and run `uv lock` to update `uv.lock` accordingly.

- Upload a draft release to Zenodo by running

  ```bash
  (cd 3_zenodo/; sbatch job.sh)
  ```

- Visit the dataset page on Zenodo and click on "New version".
  The files and metadata will already be present due to the previous step.
  Request the DOI for the new draft and add this information to `CHANGELOG.md`.

- Commit all changes to Git and run `git tag` with the new version number.

- Recompile the PDF file with the dataset description to include the Git hash in the PDF frontmatter:

  ```bash
  (cd 1_dataset/; sbatch job.sh)
  ```

- Sync your local data one last time with Zenodo:

  ```bash
  (cd 3_zenodo/; sbatch job.sh)
  ```

- Log in to <https://zenodo.org/>, go to your draft release,
  check that all files have been uploaded correctly, and publish the release.

- Push your commits and tags to GitHub.
