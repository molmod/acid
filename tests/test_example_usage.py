# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Sanity check for the standalone example script shown in the dataset overview."""

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


def test_example_usage(monkeypatch):
    monkeypatch.chdir(OUTPUT)
    example_namespace = run_path(str(EXAMPLE_SCRIPT))

    sequences = example_namespace["sequences"]

    assert sequences.dtype == float
    assert np.array_equal(example_namespace["acfs"], compute_acfs(sequences))
    assert np.array_equal(example_namespace["psds"], compute_amplitudes(sequences))
    assert np.array_equal(example_namespace["msds"], compute_msds(sequences))
