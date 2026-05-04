<!--
SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

A major refactoring of the ACID dataset.

### Added

- Added the power-law kernel model.
- Added analytical mean-squared displacements (MSDs) for all covariance kernels to the dataset.
- Added empirical MSD calculations from the trajectories.
- Added a section on trajectory generation using linear stochastic differential equations in `overview.typ`.
- Added a note on the calculation of `corrtime_int` in `overview.typ`.

### Changed

- Updated the kernel set to a new collection of 12 kernels, including the power-law kernel model.
- Renamed directories to make the order of execution more explicit.
- Included reference `acint` and `corrtime_exp` metadata in ZIP files.
- All trajectories are sampled using linear stochastic differential equations.
- Trajectory generation no longer depends on STACIE.
- More efficient storage of time series, using a customized integer encoding of real numbers.
  The encoding/decoding is stored in a file as part of the data generation.
- Data is stored in ordinary ZIP files, mostly compatible with the NPZ format.
- Data is now uploaded to Zenodo as one ZIP file per kernel instead of a single ZIP file containing the full dataset.
  Each ZIP file also includes a `meta.json` file with metadata.
- Changed the file organization in `overview.typ`,
  following the new structure introduced by this release.

### Removed

- The validation workflows have been migrated to a separate repository,
  and are no longer included here.
  See <https://github.com/molmod/acid-test>

## [1.2.1] - 2026-05-04

### Fixed

- Rename symbol `C_0` to `A_0` to avoid confusion with the Lorentz model parameter `C_0` in STACIE,
  which has a different meaning.
- Fix mistake in the Typst equation for ACF of the stochastic harmonic oscillator.

## [1.2.0] - 2025-12-24

### Changed

- Rerun STACIE validation for the Lorentz model reformulation in STACIE 1.2.
  (The actual test data has not changed and the purpose of this release is
  to confirm that that validation results are not affected by this reformulation.)

### Fixed

- Corrected affiliation typo.
- Corrected number of parameters in `report-lorentz.pdf` (40 -> 60).

## [1.1.0] - 2025-11-11

### Added

- Documented the release process in `README.md`.
- Added a remark on determinism in `acid-dataset.typ`.

### Changed

- Rerun STACIE validation for the Lorentz model improvements in STACIE 1.1.
  Previously excluded test cases are now all included.
  (The actual test data has not changed; only the validation results have been updated.)
- Add citation of the initial STACIE paper to the validation reports.

### Fixed

- Added the git commit hash to the PDF frontmatter of `acid-dataset/acid-dataset.pdf`.

## [1.0.1] - 2025-10-18

Switch to a choice of license: `CC-BY-SA-4.0 OR LGPL-3.0-or-later`.

## [1.0.0] - 2025-06-26

Initial version released.

[1.0.0]: https://doi.org/10.5281/zenodo.15722903
[1.0.1]: https://doi.org/10.5281/zenodo.17387376
[1.1.0]: https://doi.org/10.5281/zenodo.17573835
[1.2.0]: https://doi.org/10.5281/zenodo.18044643
[1.2.1]: https://github.com/molmod/acid
