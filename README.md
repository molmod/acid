<!-- markdownlint-disable line-length -->

# The AutoCorrelation Integral Drill (ACID) Test Set

This repository contains the scripts and
[StepUp workflows](https://reproducible-reporting.github.io/stepup-core/stable/)
to regenerate the "AutoCorrelation Integral Drill" (ACID) test set.
The ACID test set comprises a diverse collection of algorithmically generated time series
designed to evaluate the performance of algorithms that compute the autocorrelation integral.
The set contains in total 15360 test cases, and each case consists of one or more time series.
The cases differ in the kernel characterizing the time correlations, the number of time series,
and the length of the time series.
For each combination of kernel, number of sequences and sequence length,
64 test cases are generated with different random seeds
to allow for a systematic validation of uncertainty estimates.
The total dataset, once generated, is about 80 GB in size.

In addition to the ACID test set, this repository also contains scripts and workflows
to validate [STACIE](https://molmod.github.io/stacie/),
a software package for the computation of the autocorrelation integral.

A description of the dataset, a summary of the validation results,
and an archived version of this repository can be found on Zenodo:
[10.5281/zenodo.15722903](https://doi.org/10.5281/zenodo.15722903).

## License

All files in this dataset are distributed under a choice of license:
either the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0)
or the GNU Lesser General Public License, version 3 or later (LGPL-v3+).
The SPDX License Expression for the documentation is `CC-BY-SA-4.0 OR LGPL-3.0-or-later`.

You should have received a copy of the CC BY-SA 4.0 and LGPL-v3+ licenses along with the data set.
If not, see:

- <https://creativecommons.org/licenses/by-sa/4.0/>
- <https://www.gnu.org/licenses/>

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

This repository contains three smaller projects:

1. [`1_acid_dataset/`](1_acid_dataset/):
   A workflow to generate the ACID test set.
1. [`2_validation/`](2_validation/):
   Workflows to recompute the validation of STACIE with the ACID test set.
   Subdirectories contain workflows for different versions or settings of STACIE.
1. [`3_report/`](3_report/):
   A workflow with post-processing scripts of the validation results
   to regenerate the figures and tables used in the STACIE paper.
1. [`4_zenodo/`](4_zenodo/):
   A workflow to package and upload the generated data to Zenodo.

When regenerating the data and the validation of results, the workflows
in these directories must be executed in the order listed above.
Each directory contains a `README.md` file that provides more details.

## Roadmap Towards ACID 2.0

The objective for the next major release of this dataset include:

1. [x] Support testing multiple estimators, not just one version of STACIE,
   with summary reports comparing the performance of different estimators.

1. [ ] Separate Git repositories for the dataset generation and the validation of results.
   This will allow for more regular releases of validation results for the same data.

1. [ ] Rewrite of the data generation workflow by exact integration of linear stochastic differential equations,
   of which the covariance kernels can be derived analytically.
   The resulting time series will be aperiodic by construction,
   which is more representative of real-world applications.
   This change will allow for more precise testing of aliasing artifacts.

1. [ ] Improve data storage efficiency and release engineering.
   By storing the current datasert in single precesion (which is sufficient for stochastic time series),
   we can reduce the size of the dataset by a factor of two and store it in full on Zenodo (40 GB).
   This way, prospective users are not forced to regenerate the dataset,
   which lowers the barrier to usage and allows for more reproducible research.
   NPZ files will be used instead of ZARR files to further simplify the data reuse.

1. [ ] Test more versions of STACIE and also other (open-source) MD post-processing tools
   to estimate transport properties. We're considering the following:

   - Kute: <https://gitlab.com/nafomat/kute>
   - Sportran: <https://github.com/sissaschool/sportran>
   - Binary-based time sampling (MSD method): <https://doi.org/10.1063/5.0188081>
   - MSD implementation in MDAnalysis: <https://docs.mdanalysis.org/2.0.0/documentation_pages/analysis/msd.html#computing-an-msd>
   - Tidydynamics: <https://lab.pdebuyl.be/tidynamics/>

   Unlike STACIE, some of these tools require manual inspection of intermediate results,
   which makes it impossible to apply them systematically to all 15360 test cases.
   Where needed, we will (try to) work with reasonable defaults
   to avoid any manual intervention and user bias.

## How to Run the Workflows

The workflows in this repository can be executed on a compute cluster
that supports [SLURM](https://slurm.schedmd.com/) job scheduling,
or on a local machine with sufficient resources.

Each workflow uses its own Python virtual environment to manage the required Python packages.
This allows for benchmarking different versions of packages in isolation.
In a workflow directory, you will find a `requirements.in` file.
To (re)create the virtual environment for a workflow,
run or submit the top-level `setup-venv-pip.sh` from the directory that contains the `job.sh` script.
If you want this script to use a specific Python version,
set the `PYTHON3` environment variable before running it.
For example:

```bash
export PYTHON3=/usr/bin/python3.13
cd acid-dataset/
sbatch ../setup-venv-pip.sh
```

After the virtual environment has been created,
you can run or submit the script `job.sh` to perform the actual work.
If you want to work interactively within the virtual environment,
you can source the `.loadvenv` script in the workflow directory.

Note that the workflows and scripts in this repository require Python 3.11 or higher.
They are only expected to run on an x86_64 Linux system.
All results on Zenodo were generated using the following module
on the Tier2 VSC compute cluster donphan

```bash
module load Python/3.13.5-GCCcore-14.3.0
```

## How to Work With This Git Repository

To make clean commits to this repository, please follow these guidelines:

1. Install [pre-commit](https://pre-commit.com/) on your system.
1. Install the pre-commit hook by running `pre-commit install` in the root directory of this repository.
1. Use `git commit` as you normally would.

If you are working in an environment with limited permissions,
you can install pre-commit locally by running the following commands:

```bash
wget https://github.com/pre-commit/pre-commit/releases/download/v4.5.1/pre-commit-4.5.1.pyz
python pre-commit-4.5.1.pyz install
```

## How to Make a New Release

After having updated actual contents of the dataset, the following steps are needed
to make a new release on Zenodo:

- Update `CHANGELOG.md` with a new version section, describing the changes since the last release.

- Update the version number in `4_zenodo/zenodo.yaml`.

- Upload a draft release to Zenodo by running

  ```bash
  (cd 4_zenodo/; sbatch job.sh)
  ```

- Visit the dataset page on Zenodo and click on "New version".
  The files and metadata will already be present due to the previous step.
  Request the DOI for the new draft and add this information to `CHANGELOG.md`.

- Commit all changes to Git and run `git tag` with the new version number.

- Recompile all PDF files in the repository to include the Git hash in the PDF frontmatter:

  ```bash
  (cd 1_acid_dataset/; sbatch job.sh)
  (cd 2_validation/; sbatch job.sh)
  ```

- Sync your local data one last time with Zenodo:

  ```bash
  (cd 4_zenodo/; sbatch job.sh)
  ```

- Log in to <https://zenodo.org/>, go to your draft release,
  check that all files have been uploaded correctly, and publish the release.

- Push your commits and tags to GitHub.
