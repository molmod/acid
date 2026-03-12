#!/usr/bin/env python3
"""Generate test sets for a specific kernel, nstep and nseq."""

import argparse
import io
import json
import zipfile
from runpy import run_path

import numpy as np
import scipy as sp
from kernels import compute
from numpy.typing import NDArray
from path import Path
from stacie.synthetic import generate
from stepup.core.api import amend

SEQ_DTYPE = np.uint16
IMAX = np.iinfo(SEQ_DTYPE).max + 1


def main():
    args = parse_args()
    run(args.kernel, args.nstep, args.nseq, args.nseed, args.out)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate test sets for a specific kernel, nstep and nseq."
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


def run(kernel: str, nstep: int, nseq: int, nseed: int, out: Path):
    """Write synthetic time-correlated data to a ZIP file.

    Parameters
    ----------
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
            ppfi = sp.stats.norm(scale=std).cdf(sequence) * IMAX
            ppfi = np.floor(ppfi)
            if ppfi.max() >= IMAX:
                raise ValueError(f"ppfi exceeds {IMAX - 1}")
            if ppfi.min() < 0:
                raise ValueError("Negative ppfi values found")
            ppfi = ppfi.astype(SEQ_DTYPE)
            dump_npy(f"sequences_{iseed:02d}.npy", zf, ppfi)


def dump_npy(name: str, zf: zipfile.ZipFile, array: NDArray):
    """Dump a NumPy array to a ZIP file as a .npy file."""
    zi = default_zipinfo(name)
    buf = io.BytesIO()
    np.save(buf, array, allow_pickle=False)
    zf.writestr(zi, buf.getvalue())


def dump_meta(name: str, zf: zipfile.ZipFile, data):
    zi = default_zipinfo(name)
    zf.writestr(zi, json.dumps(data))


def default_zipinfo(name: str) -> zipfile.ZipInfo:
    """Create a ZipInfo object with a fixed date."""
    zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    zi.external_attr = 0
    zi.create_system = 0
    return zi


if __name__ == "__main__":
    main()
