#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Generate test sets for a specific kernel, nstep and nseq."""

import argparse
import json
import zipfile
from runpy import run_path

import numpy as np
from kernels import compute, sample
from path import Path
from stepup.core.api import amend
from utils import dump_meta, dump_npy, lookup_integer

SEQ_DTYPE = np.uint16
IMAX = np.iinfo(SEQ_DTYPE).max + 1


def main():
    args = parse_args()
    run(args.codec, args.settings, args.kernel, args.out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate test sets for a specific kernel, nstep and nseq."
    )
    parser.add_argument(
        "codec",
        type=str,
        help="The codec zip to encode the floats into integers.",
    )
    parser.add_argument(
        "settings",
        type=str,
        help="The settings.json that contains the nsteps, nseqs, and nseeds.",
    )
    parser.add_argument(
        "kernel",
        type=str,
        help="The kernel to use.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="The output ZIP path.",
    )
    return parser.parse_args()


def run(path_codec: Path, path_settings: Path, kernel: str, out: Path):
    """Write synthetic time-correlated data to a ZIP file.

    Parameters
    ----------
    path_codec
        The npy file that contains the lookup table to map the floats to integers.
    path_settings
        The settings.json that contains the nsteps, nseqs, and nseeds.
    kernel
        The kernel to use.
    out
        The output ZIP path.
    """
    # Load the lookup table
    lookup_table = np.load(path_codec)["boundary"]

    with open(path_settings) as f:
        settings = json.load(f)

    nsteps = settings["nsteps"]
    nseqs = settings["nseqs"]
    nseed = settings["nseed"]

    path_py = f"kernels/{kernel}.py"
    amend(inp=path_py)
    terms = run_path(path_py)["terms"]

    with zipfile.ZipFile(out, mode="w") as zf:
        for nstep in nsteps:
            nstep_path = Path(f"nstep{nstep:05d}/")
            if nstep % 2 != 0:
                raise ValueError("Only an even nstep is supported.")

            times = np.arange(nstep, dtype=float)
            freqs = np.fft.rfftfreq(nstep)
            psd, acf, msd, corrtime_int, corrtime_exp, typst, latex = compute(terms, freqs, times)

            dump_npy(nstep_path + "times.npy", zf, times)
            dump_npy(nstep_path + "acf.npy", zf, acf)
            dump_npy(nstep_path + "msd.npy", zf, msd)
            dump_npy(nstep_path + "freqs.npy", zf, freqs)
            dump_npy(nstep_path + "psd.npy", zf, psd)

            std = np.sqrt(acf[0])

            for nseq in nseqs:
                nseq_path = nstep_path + f"nseq{nseq:04d}/"
                for iseed in range(nseed):
                    seed = np.frombuffer(f"{iseed:d}{out}".encode("ascii"), dtype=np.uint8)
                    rng = np.random.default_rng(seed)
                    # Generate the sequence
                    sequence = sample(terms, nseq, nstep, rng)
                    # Map to uint16 representation
                    ppfi = lookup_integer(sequence, std, lookup_table)
                    if ppfi.max() >= IMAX:
                        raise ValueError(f"ppfi exceeds {IMAX - 1}")
                    if ppfi.min() < 0:
                        raise ValueError("Negative ppfi values found")
                    ppfi = ppfi.astype(SEQ_DTYPE)
                    dump_npy(nseq_path + f"sequences_{iseed:02d}.npy", zf, ppfi)

        dump_meta(
            "meta.json",
            zf,
            {
                "kernel": kernel,
                "nseed": nseed,
                "var": acf[0],
                "acint": psd[0],
                "corrtime_int": corrtime_int,
                "corrtime_exp": corrtime_exp,
                "typst": typst,
                "latex": latex,
            },
        )


if __name__ == "__main__":
    main()
