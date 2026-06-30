# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Didactic example of how to decode trajectories and compute their ACF, PSD, and MSD."""

import json
import zipfile

import numpy as np
import scipy as sp

kernel_data = np.load("exp1w.zip")

with zipfile.ZipFile("exp1w.zip") as zf, zf.open("meta.json") as f:
    meta = json.load(f)

# Decode the integer-encoded sequences back to floating-point values.
cdfi = kernel_data["nstep01024/nseq0064/sequences_00.npy"]
lookup_table = np.load("codec.zip")["midpoint"]
std = np.sqrt(meta["var"])
sequences = lookup_table[cdfi] * std

nseq, nstep = sequences.shape

# Calculate empirical ACFs
denom = np.arange(nstep, 0, -1)
acf_sum = np.zeros(nstep)
for seq in sequences:
    corr = sp.signal.correlate(seq, seq, mode="full", method="auto")[nstep - 1 :]
    corr /= denom
    acf_sum += corr
acfs = acf_sum / nseq

# Calculate empirical PSDs
psds = (abs(np.fft.rfft(sequences, axis=1)) ** 2).sum(axis=0) / (nstep * nseq)

# Calculate empirical MSDs
antiderivatives = np.cumsum(sequences, axis=1)
msds = np.zeros(nstep)
for delta in range(nstep):
    diffs = antiderivatives[:, delta:] - antiderivatives[:, : nstep - delta]
    msds[delta] = np.mean(diffs**2)
