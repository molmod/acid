<!--
SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

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

## Testing with a Lighter Version of the Dataset

For development and testing, e.g. on a laptop,
it can be convenient to generate a lighter version of the dataset.
To facilitate such local development, you can create a file `local-settings.json`
in this directory (`1_dataset/`), next to `settings.json`.
Unlike `settings.json`, which is part of the Git repository, `local-settings.json` is ignored by Git.
If `local-settings.json` is present,
the workflow `1_dataset/plan.py` copies it to `output/settings.json`,
instead of using the official `settings.json`.

The consistency between `1_dataset/settings.json` and `1_dataset/output/settings.json`
is used throughout the repository to check if the settings match the official ones.
The PDFs will contain a warning in the footer when using local settings,
and the `3_zenodo` workflow fails with an error if the `REPREP_ZENODO_TOKEN` is set.

For example, with the following settings, each workflow takes less than a minute.
The `kernels` are copied unchanged from `settings.json`,
while `nseqs`, `nsteps` and `nseed` are reduced:

```json
{
  "kernels": [
    "exp1p",
    "exp1w",
    "exp2",
    "sho1pcrit",
    "sho1punder",
    "sho1wcrit",
    "sho1wunder",
    "sho2crit",
    "sho2under",
    "pow1p",
    "pow1exp",
    "pow1sho"
  ],
  "nseqs": [
    1,
    4,
    16,
    64
  ],
  "nsteps": [
    256,
    1024
  ],
  "nseed": 8
}
```

This covers the same code paths as the full set and should run without errors.
Of course, the resulting data are statistically much weaker.

If you make further modifications to the local settings,
note that the workflows require the following to work properly:

- (At most) 12 kernels can be used.
- `nseed` must be strictly positive.
- The usage script `example_usage.py` is tested as part of the validation workflow.
  It expects data for kernel `exp1w` with `nstep=1024` and `nseq=64`,
  so these must be included.
- Some figures reference `nsteps[1]` and `nseqs[-1]`.
