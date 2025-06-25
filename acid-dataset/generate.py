#!/usr/bin/env python3
"""Generate test sets for a specific kernel, nstep and nseq."""

import shutil
import zipfile
from collections.abc import Iterator
from runpy import run_path

import numpy as np
import zarr
from kernels import compute
from path import Path, TempDir
from stacie.synthetic import generate
from stepup.core.api import amend
from stepup.core.script import driver

NCASE = 2**6
CASE_FMT = "{}_nstep{:05d}_nseq{:04d}"


def cases() -> Iterator[tuple[str, int, int]]:
    from settings import KERNELS, NSEQS, NSTEPS

    for kernel in KERNELS:
        for nstep in NSTEPS:
            for nseq in NSEQS:
                yield kernel, nstep, nseq


def case_info(kernel: str, nstep: int, nseq: int):
    return {
        "out": Path(f"output/{kernel}_nstep{nstep:05d}_nseq{nseq:04d}.zip"),
        "kernel": kernel,
        "nstep": nstep,
        "nseq": nseq,
    }


def run(out: Path, kernel: str, nstep: int, nseq: int):
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
    """
    if nstep % 2 != 0:
        raise ValueError("Only an even nstep is supported.")
    # Generate 2 times as much and discard the second half
    # to create an aperiodic input with the right spectrum
    nfull = 2 * nstep
    times = np.arange(nfull, dtype=float)
    freqs = np.fft.rfftfreq(nfull)

    path_py = f"kernel_{kernel}.py"
    amend(inp=path_py)
    terms = run_path(path_py)["terms"]
    psd, acf, corrtime_int, typst, latex = compute(terms, freqs, times)

    # Create Zarr archive with some intial data
    tmp_root = Path("./tmp/")
    tmp_root.mkdir_p()
    with TempDir(dir=tmp_root) as path_tmp:
        path_work = path_tmp / "work.zarr"
        store = zarr.storage.LocalStore(path_tmp / "work.zarr")
        root = zarr.group(store)
        root.attrs["corrtime_int"] = corrtime_int
        root.attrs["typst"] = typst
        root.attrs["latex"] = latex
        root["times"] = times[:nstep]
        root["freqs"] = freqs[::2]
        root["psd"] = psd[::2]
        root["acf"] = acf[:nstep]
        sequences = root.create_array(
            "sequences",
            shape=(NCASE, nseq, nstep),
            dtype=np.float32,
        )
        for iseed in range(NCASE):
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
    driver()
