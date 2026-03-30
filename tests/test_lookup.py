# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import numpy as np
from utils import lookup_integer


def test_lookup_integer():
    assert (
        lookup_integer(np.array([-0.2, 0.2]), 1.0, np.array([0.0, 0.5, 0.1])) == [0, 1]
    ).all(), "Incorrect mapping from floats to integers."
