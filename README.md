# The AutoCorrelation Integral Drill (ACID) Test Set and Its Application to the Validation of the STable AutoCorrelation Integral Estimator (STACIE)

## License

All files in this dataset are licensed under a
[Creative Commons Attribution Non Commercial Share Alike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).

## Citation

If you use this dataset in your research, please cite the following paper:

> TODO

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

## TODO

- Explain figures and tables in report PDFs, add short descriptions above figures and tables.
- Use oxifmt to format paths.
- Fix problem with error bar on exp corr time.
