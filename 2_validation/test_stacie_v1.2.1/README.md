# Validation of STACIE 1.2.1 with the ACID test set

Please see the top-level [`README.md`](../README.md) file
for information on licenses, citation and setup of the Python Virtual Environment.

This directory tests the STACIE 1.2.1 with the `ExpPolyModel([0, 2])` and `LorentzModel()`,
labeled as `quad` and `lorentz` respectively.

## Description of the Data

This dataset (once regenerated) contains the following files:

- `figures/estimate_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.pdf`
  One PDF per set of 64 test inputs with a given kernel, number of steps,
  and number of sequences.
- `output/estimate_{kernel}_nstep{nstep:05d}_nseq{nseq:04d}_{model}.pickle`
  A Python Pickle file containing a list of 64 `Result` objects defined in the STACIE package.
  These contain all the raw results.

## Regeneration of the Raw Results

The validation results (pickle, JSON and PDF figures)
can be regenerated with the following steps:

1. Follow the instructions to set up a Python Virtual Environment,
   as described in the top-level [`README.md`](../README.md) file.

1. Run the preceding workflow as explained in
   [`../../1_acid_dataset/README.md`](../../1_acid_dataset/README.md).

1. Submit the job script to run the StepUp workflow:

   ```bash
   cd 2_validation/test_stacie_v1.2.1
   sbatch job.sh
   ```

   This takes about 4.5 hours to complete on 8 cores of an Intel(R) Xeon(R) Gold 6240 CPU.
