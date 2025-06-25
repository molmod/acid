# Validation of the STable AutoCorrelation Integral Estimator (STACIE) with the ACID test set

Please see the top-level [`README.md`](../README.md) file
for information on licenses, citation and setup of the Python Virtual Environment.

## Description of the Dataset

This dataset (once regenerated) contains the following files:

- `figures/figures/estimate_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.pdf`
  One PDF per set of 64 test inputs with a given kernel, number of steps,
  and number of sequences, using a specific model.
- `output/figures/estimate_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.pickle`
  A Python Pickle file containing a list of 64 `Result` objects defined in the STACIE package.
  These contain all the raw results that are used to create the PDF files
  and the report in [`../report/`](../report/)

## Regeneration of the Raw Validation Results

The raw validation results (in the form of Pickle files and PDF figures)
can be regenerated with the following steps:

1. Follow the instructions to set up a Python Virtual Environment,
   as described in the top-level [`README.md`](../README.md) file.

1. Run the preceding workflow as explained in
   [`../acid-dataset/README.md`](../acid-dataset/README.md).

1. After installing and activating the virtual environment,
   run the following command (ideally on a compute node of a cluster)
   to regenerate the raw validation results:

   ```bash
   stepup boot -n 1.0
   ```

   This takes about 4 hours to complete on 8 cores of an Intel(R) Xeon(R) Gold 6240 CPU.
