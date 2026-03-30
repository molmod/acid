# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later

import io
import json
import zipfile

import numpy as np
from numpy.typing import NDArray


def dump_npy(name: str, zf: zipfile.ZipFile, array: NDArray):
    """Dump a NumPy array to a ZIP file as a .npy file."""
    zi = default_zipinfo(name)
    buf = io.BytesIO()
    np.save(buf, array, allow_pickle=False)
    zf.writestr(zi, buf.getvalue())


def default_zipinfo(name: str) -> zipfile.ZipInfo:
    """Create a ZipInfo object with a fixed date."""
    zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    zi.external_attr = 0
    zi.create_system = 0
    return zi


def dump_meta(name: str, zf: zipfile.ZipFile, data):
    """Dump metadata to a ZIP file as a .json file."""
    zi = default_zipinfo(name)
    zf.writestr(zi, json.dumps(data))


def lookup_integer(sequence: NDArray[float], std: float, table: NDArray[float]) -> NDArray[int]:
    r"""Lookup to which integer the floats should be mapped according to the lookup table.
    This lookup table is based on the mapping of the sequence to a cumulative distribution function,
    belonging to a Gaussian distribtion with standard deviation ``std``.

    Parameters
    ----------
    sequence
        The input sequences, which is an array with shape ``(nindep, nstep)``.
        Each row is a time-dependent sequence.
    std
        The standard deviation of the sequence.
    table
        The lookup table to map the floats to integers.

    Returns
    -------
    An array that contains the original floats mapped to integers

    """
    return np.searchsorted(table, sequence / std)
