# Data Generation

Please see the top-level [`README.md`](../README.md) file
for information on licenses, citation and setup of the Python Virtual Environment.

## Description of the Dataset

A full description is given in the Typst document `overview.typ`,
of which a compiled PDF (`overview.pdf`) is available as a release artifact of this repository.

## Instructions for Regenerating the Dataset

As of ACID 2, the full dataset is stored on Zenodo.
You can regenerate it from scratch, if you prefer not to download the pre-generated version, by following the instructions below.

1. Follow the instructions to set up a Python Virtual Environment,
   as described in the top-level [`README.md`](../README.md) file.

1. After installing the virtual environment,
   submit (or run) the following job script:

   ```bash
   sbatch job.sh
   ```

   This takes about 10 minutes to complete on 8 cores of an Intel(R) Xeon(R) Gold 6240 CPU.
   (Due to a limitation of Typst 0.14,
   you may need to run this twice to build the `overview.pdf` file.
   The second invocation will only take a few seconds.)
