#!/usr/bin/env python3
"""Generate test sets for a specific kernel, nstep and nseq."""

import argparse
import shutil
import zipfile
from runpy import run_path

import numpy as np
import zarr
from kernels import compute
from path import Path, TempDir
from stacie.synthetic import generate
from stepup.core.api import amend


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
        help="The output ZARR path.",
    )
    return parser.parse_args()


def run(kernel: str, nstep: int, nseq: int, nseed: int, out: Path):
    """Write synthetic time-correlated data to an ZARR file.

    Parameters
    ----------
    out
        The output ZARR path.
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

    # Create Zarr archive with some intial data
    tmp_root = Path("./tmp/")
    tmp_root.mkdir_p()
    with TempDir(dir=tmp_root) as path_tmp:
        path_work = path_tmp / "work.zarr"
        store = zarr.storage.LocalStore(path_tmp / "work.zarr")
        root = zarr.group(store)
        root.attrs["acint"] = psd[0]
        root.attrs["corrtime_int"] = corrtime_int
        root.attrs["corrtime_exp"] = corrtime_exp
        root.attrs["typst"] = typst
        root.attrs["latex"] = latex
        root["times"] = times[:nstep]
        root["freqs"] = freqs[::2]
        root["psd"] = psd[::2]
        root["acf"] = acf[:nstep]
        sequences = root.create_array(
            "sequences",
            shape=(nseed, nseq, nstep),
            dtype=np.float32,
        )
        for iseed in range(nseed):
            seed = np.frombuffer(f"{out}{iseed:d}".encode("ascii"), dtype=np.uint8)
            rng = np.random.default_rng(seed)
            sequences[iseed] = generate(psd, 1.0, nseq, nstep, rng).astype(np.float32)

        # Zip the Zarr directory to its final location.
        # Low-level features from Python's zipfile module are used to strip time and os metadata.
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in path_work.walkfiles():
                zi = zipfile.ZipInfo(path.relpath(path_work))
                with open(path, "rb") as fi, zf.open(zi, "w") as fo:
                    shutil.copyfileobj(fi, fo)
                zi.external_attr = 0


if __name__ == "__main__":
    main()
