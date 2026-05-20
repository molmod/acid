<!--
SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
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

This repository consits of two parts:

1. [`1_dataset/`](1_dataset/):
   A workflow to generate the ACID 2 dataset.
1. [`2_zenodo/`](2_zenodo/):
   A workflow to package and upload the generated data to Zenodo.
1. [`3_validation/`](3_validation):
   A workflow to validate the generated dataset.

## How to Run the Workflows

The workflows in this repository can be executed on a compute cluster
that supports [SLURM](https://slurm.schedmd.com/) job scheduling,
or on a local machine with sufficient resources.

A Python virtual environment is defined in the `requirements.in` file.
To (re)create the virtual environment for a workflow,
run or submit the script `setup-venv-pip.sh`.
If you want this script to use a specific Python version,
set the `PYTHON3` environment variable before running it.
For example:

```bash
export PYTHON3=/usr/bin/python3.13  # optional
sbatch setup-venv-pip.sh
```

After the virtual environment has been created,
you can run or submit the script `job.sh` in `1_dataset/`, `2_zenodo/`, or `3_validation/`.
If you want to work interactively within the virtual environment,
you can source the `.loadvenv` script.

Note that the workflows and scripts in this repository require Python 3.11 or higher.
They have only been tested on an `x86_64` Linux system (so far).
All results on Zenodo were generated using the following module
on the Tier2 VSC compute cluster donphan

```bash
module load Python/3.13.5-GCCcore-14.3.0
```

When the `setup-venv-pip.sh` script detects the presence of the `$VSC_HOME`
environment variable, it will automatically load this Python module
and include it in the generated `.loadvenv` script.

## How to Work With This Git Repository

Please, follow these guidelines to make clean commits to this repository:

1. Install [pre-commit](https://pre-commit.com/) on your system.
   (It is included in the `requirements.in` file,
   so it will be installed in the virtual environment when you run `setup-venv-pip.sh`.)
1. Install the pre-commit hook by running `pre-commit install` in the root directory of this repository.
1. Update the file `CHANGELOG.md` to describe changes.
1. Use `git commit` as you normally would.

If you are working in an environment with limited permissions,
you can install pre-commit locally by running the following commands:

```bash
wget https://github.com/pre-commit/pre-commit/releases/download/v4.5.1/pre-commit-4.5.1.pyz
python pre-commit-4.5.1.pyz install
```

## How to Make a New Release

After having updated actual contents of the dataset, the following steps are needed
to make a new release on GitHub and Zenodo:

- Update `CHANGELOG.md` with a new version section.
  Double check the changes since the last release.

- Update the version number in `2_zenodo/zenodo.yaml`.

- Upload a draft release to Zenodo by running

  ```bash
  (cd 2_zenodo/; sbatch job.sh)
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
  (cd 2_zenodo/; sbatch job.sh)
  ```

- Log in to <https://zenodo.org/>, go to your draft release,
  check that all files have been uploaded correctly, and publish the release.

- Push your commits and tags to GitHub.
