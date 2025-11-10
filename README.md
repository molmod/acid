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

If you use this dataset in your research, please cite the following priprint:

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

1. [`acid-dataset/`](acid-dataset/):
   A workflow to generate the ACID test set.
1. [`validation-staciei-calc/`](validation-stacie-calc/):
   A workflow to recompute the validation of STACIE with the ACID test set.
1. [`validation-stacie-report/`](validation-stacie-report/):
   A workflow with post-processing scripts of the validation results
   to regenerate the figures and tables used in the STACIE paper.

When regenerating the data and the validation of results for STACIE, the workflows
in these three projects must be executed in the order listed above.
The `README.md` files in these directories provide more details.

## Setup of the Python Virtual Environment

The script `setup-venv-pip.sh` in the root directory of this repository
sets up a Python virtual environment with the required dependencies.
In order to run this script, you need to have Python 3.11 or later installed on your system.
The script is primarily tested on Linux, but may also work on other operating systems.

It is recommended to install and setup [`direnv`](https://direnv.net/)
to automatically activate the virtual environment when you enter the repository directory.

## How to make a new release

After having updated actual contents of the dataset, the following steps are needed
to make a new release on Zenodo:

- Update `CHANGELOG.md` with a new version section, describing the changes since the last release.

- Update the version number in `zenodo/zenodo.yaml`.

- Upload a draft release to Zenodo by running

  ```bash
  (cd zenodo/; stepup boot)
  ```

  Request the DOI for the new draft on <https://zenodo.org/> and add this information to `CHANGELOG.md`.

- Commit all changes to Git and run `git tag` with the new version number.

- Recompile all PDF files in the repository to include the Git hash in the PDF frontmatter:

  ```bash
  (cd acid-dataset/; stepup boot)
  (cd validation-stacie-report/; stepup boot)
  ```

- Sync your local data one last time with Zenodo:

  ```bash
  (cd zenodo/; stepup sync)
  ```
