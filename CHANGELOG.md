# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

(no changes yet)

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
[unreleased]: https://github.com/molmod/acid
