# The AutoCorrelation Integral Drill (ACID) Test Set

Please see the top-level [`README.md`](../README.md) file
for information on licenses, citation and setup of the Python Virtual Environment.

## Description of the Dataset

A full description is given in the Typst document `acid-dataset.typ`,
of which a compiled PDF (`acid-dataset.pdf`) is available as a release artifact of this repository.

## Regeneration of the Dataset

Because the full dataset is about 80 GB in size and relatively easy to regenerate,
we do not provide a download link.
Instead, you can regenerate the dataset (ideally on a compute node of a cluster)
with the following steps:

1. Follow the instructions to set up a Python Virtual Environment,
   as described in the top-level [`README.md`](../README.md) file.

1. After installing and activating the virtual environment,
   run the following command to regenerate the dataset:

   ```bash
   stepup boot -n 1.0
   ```

   This takes about 22 minutes to complete on 8 cores of an Intel(R) Xeon(R) Gold 6240 CPU.
   (Due to a current limitation of Typst,
   you may need to run this twice to build the `acid-dataset.pdf` file.
   The second invocation will only take a few seconds.)
