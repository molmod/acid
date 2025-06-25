# Figures Summarizing the Validation of the STACIE with the ACID test set

Please see the top-level [`README.md`](../README.md) file
for information on licenses, citation and setup of the Python Virtual Environment.

## Description of the Dataset

A full description is given in the Typst documents `report-quad.typ` and `report-lorentz.typ`,
of which compiled PDFs are made available as release artifacts of this repository.

## Regeneration of the Validation Reports

The validation reports (in the form of PDF documents)
can be regenerated with the following steps:

1. Follow the instructions to set up a Python Virtual Environment,
   as described in the top-level [`README.md`](../README.md) file.

1. Run the preceding workflows as explained in
   [`../acid-dataset/README.md`](../acid-dataset/README.md)
   and [`../validation-stacie-report/README.md`](../validation-stacie-report/README.md).

1. Run the following command to regenerate the validation reports:

   ```bash
   stepup boot -n 1.0
   ```

   This takes a couple of minutes to complete.
   (Due to a current limitation of Typst,
   you may need to run this twice to build the `report-*.pdf` files.
   The second invocation will only take a few seconds.)
