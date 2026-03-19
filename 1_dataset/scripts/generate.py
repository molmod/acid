#!/usr/bin/env python3
"""Generate test sets for a specific kernel, nstep and nseq."""

import argparse
import zipfile
from runpy import run_path

import numpy as np
from kernels import compute
from numpy.typing import NDArray
from path import Path
from stacie.synthetic import generate
from stepup.core.api import amend
from utils import dump_meta, dump_npy

SEQ_DTYPE = np.uint16
IMAX = np.iinfo(SEQ_DTYPE).max + 1


def main():
    args = parse_args()
    run(args.lookup_table, args.kernel, args.nstep, args.nseq, args.nseed, args.out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate test sets for a specific kernel, nstep and nseq."
    )
    parser.add_argument(
        "lookup_table",
        type=str,
        help="The codec zip to encode the floats into integers.",
    )
    parser.add_argument(
        "kernel",
        type=str,
        help="The kernel to use.",
    )
    parser.add_argument(
        "nstep",
        type=int,
        help="The number of steps in a sequence.",
    )
    parser.add_argument(
        "nseq",
        type=int,
        help="The number of sequences.",
    )
    parser.add_argument(
        "nseed",
        type=int,
        help="The number of repeats with different seeds.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="The output ZIP path.",
    )
    return parser.parse_args()


def run(path_lookup: Path, kernel: str, nstep: int, nseq: int, nseed: int, out: Path):
    """Write synthetic time-correlated data to a ZIP file.

    Parameters
    ----------
    path_lookup
        The npy file that contains the lookup table to map the floats to integers
    out
        The output ZIP path.
    kernel
        The kernel to use.
    nstep
        The number of steps in a sequence.
    nseq
        The number of sequences.
    nseed
        The number of repeats with different seeds.
    """
    if nstep % 2 != 0:
        raise ValueError("Only an even nstep is supported.")

    # Generate 2 times as much and discard the second half
    # to create an aperiodic input with the right spectrum
    nfull = 2 * nstep
    times = np.arange(nfull, dtype=float)
    freqs = np.fft.rfftfreq(nfull)

    path_py = f"kernels/{kernel}.py"
    amend(inp=path_py)
    terms = run_path(path_py)["terms"]
    psd, acf, corrtime_int, corrtime_exp, typst, latex = compute(terms, freqs, times)

    # Create ZIP archive with data and metadata.
    tmp_root = Path("./tmp/")
    tmp_root.mkdir_p()

    # Load the lookup table
    lookup_table = np.load(path_lookup)["lookup_boundary"]

    with zipfile.ZipFile(out, mode="w") as zf:
        dump_meta(
            "meta.json",
            zf,
            {
                "kernel": kernel,
                "nstep": nstep,
                "nseq": nseq,
                "nseed": nseed,
                "var": acf[0],
                "acint": psd[0],
                "corrtime_int": corrtime_int,
                "corrtime_exp": corrtime_exp,
                "typst": typst,
                "latex": latex,
            },
        )
        dump_npy("times.npy", zf, times[:nstep])
        dump_npy("acf.npy", zf, acf[:nstep])
        dump_npy("freqs.npy", zf, freqs[::2])
        dump_npy("psd.npy", zf, psd[::2])
        std = np.sqrt(acf[0])
        for iseed in range(nseed):
            seed = np.frombuffer(f"{iseed:d}{out}".encode("ascii"), dtype=np.uint8)
            rng = np.random.default_rng(seed)
            # Generate the sequence
            sequence = generate(psd, 1.0, nseq, nstep, rng)
            # Map to uint16 representation
            ppfi = lookup_integer(sequence, std, lookup_table)
            if ppfi.max() >= IMAX:
                raise ValueError(f"ppfi exceeds {IMAX - 1}")
            if ppfi.min() < 0:
                raise ValueError("Negative ppfi values found")
            ppfi = ppfi.astype(SEQ_DTYPE)
            dump_npy(f"sequences_{iseed:02d}.npy", zf, ppfi)


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
    return np.searchsorted(table, sequence / std, side="right") - 1


if __name__ == "__main__":
    main()
