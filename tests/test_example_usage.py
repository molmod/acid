# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Sanity check for the standalone example script shown in the dataset overview."""

import os
from pathlib import Path
from runpy import run_path

import numpy as np
import pytest
from utils import compute_acfs, compute_amplitudes, compute_msds

EXAMPLE_SCRIPT = Path(__file__).resolve().parents[1] / "1_dataset" / "scripts" / "example_usage.py"
OUTPUT = Path(__file__).resolve().parents[1] / "1_dataset" / "output"

# The example script reads hardcoded filenames,
# so these tests require the generated dataset in 1_dataset/output/.
pytestmark = pytest.mark.skipif(
    not (OUTPUT / "exp1w.zip").exists(),
    reason="Generated dataset not present, run the 1_dataset workflow first.",
)


@pytest.fixture(scope="module")
def namespace():
    original_cwd = os.getcwd()
    os.chdir(OUTPUT)
    try:
        return run_path(str(EXAMPLE_SCRIPT))
    finally:
        os.chdir(original_cwd)


def test_decode(namespace):
    assert namespace["sequences"].dtype == float


def test_acf(namespace):
    assert np.array_equal(namespace["acfs"], compute_acfs(namespace["sequences"]))


def test_psd(namespace):
    assert np.array_equal(namespace["psds"], compute_amplitudes(namespace["sequences"]))


def test_msd(namespace):
    assert np.array_equal(namespace["msds"], compute_msds(namespace["sequences"]))
