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

All files in this dataset are licensed under a
[Creative Commons Attribution Non Commercial Share Alike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).

## Citation

If you use this dataset in your research, please cite the following priprint:

> Gozdenur, T.; Fauconnier, D.; Verstraelen, T.
> "STable AutoCorrelation Integral Estimator (STACIE): Robust and accurate transport properties from molecular dynamics simulations"
> arXiv 2025, arXiv:2506.?????.
>
> ```bibtex
> @article{Toraman2025,
>  title = {STable AutoCorrelation Integral Estimator (STACIE): Robust and accurate transport properties from molecular dynamics simulations},
>  url = {https://arxiv.org/abs/2506.?????},
>  doi = {10.48550/arXiv.2506.?????}
>  publisher = {arXiv},
>  author = {G"{o}zdenur Toraman and Dieter Fauconnier and Toon Verstraelen},
>  year = {2025},
>  month = jun
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

The `README.md` files in these directories provide more details about each project.

## Setup of the Python Virtual Environment

The script `setup-venv-pip.sh` in the root directory of this repository
sets up a Python virtual environment with the required dependencies.
In order to run this script, you need to have Python 3.11 or later installed on your system.
The script is primarily tested on Linux, but may also work on other operating systems.

It is recommended to install and setup [`direnv`](https://direnv.net/)
to automatically activate the virtual environment when you enter the repository directory.
