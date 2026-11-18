<!--
SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
SPDX-License-Identifier: LGPL-3.0-or-later
-->

# AutoCorrelation Integral Drill: Internal Components (ACIDIC)

[![PyPI Version](https://img.shields.io/pypi/v/acidic)](https://pypi.org/project/acidic/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/acidic)
![LGPL-3 License](https://img.shields.io/badge/License-LGPL_v3-blue.svg)

The `acidic` Python package contains "internal components" used to generate and validate the [ACID dataset](https://doi.org/10.5281/zenodo.15722902).
It is packaged and published on PyPI because some of its features
are useful beyond the scope of the ACID dataset.
Consult the [ACID dataset GitHub Repository](https://github.com/molmod/acid) for more details.

For now, this README file is a stub and it will be expanded later.

## Development Setup

To work on the development of Acidic, we recommend setting up the ACID Git repository,
as documented in the top-level [README](https://github.com/molmod/acid).
Once installed, you can run the tests with `pytest`:

```bash
pytest -v
```

A live preview of the documentation can be launched with:

```bash
cd acidic/
pdoc -d numpy --math --no-browser src/acidic
```

Then click on the link to open it in your favorite browser,
i.e. not the one that pdoc would open by default.

## How to Release the acidic Package

The `acidic` package is released independently of the dataset,
using tags of the form `acidic-vX.Y.Z` (the plain `vX.Y.Z` tags are reserved for the dataset).

- Update `acidic/CHANGELOG.md` with a new version section (`## [X.Y.Z] - YYYY-MM-DD`)
  and update the version number in `acidic/pyproject.toml`.
- Commit the changes and run `git tag acidic-vX.Y.Z`.
- Push the commit and the tag to GitHub.
  The `release.yaml` workflow then publishes the package to PyPI
  and creates a GitHub release with Sigstore signatures.
  Pushes to the main branch only publish to TestPyPI.
