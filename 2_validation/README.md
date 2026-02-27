# Validation Workflows

This directory contains workflows to test how well selected software packages can estimate
the integrals of the autocorrelation function of time series in the ACID test set.
It is currently used to validate the [STACIE](https://molmod.github.io/stacie/) package,
but it can be adapted to validate other tools as well.

Each software package (version and configuration) tested has its own `test_*` subdirectory.
These subdirectories contain a `job.sh` and `requirements.in` file
as explained in the top-level [`README.md`](../README.md) file.
The `scripts` subdirectory contains helper scripts for setting up and running the tests.
