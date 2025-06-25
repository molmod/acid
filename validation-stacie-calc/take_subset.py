#!/usr/bin/env python3
"""Extract a small subset from the full data suitable for plotting the inputs."""

from collections.abc import Iterator

import numpy as np
import zarr
from stacie.spectrum import compute_spectrum
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int, int]]:
    from settings import KERNELS

    for kernel in KERNELS:
        for nstep in [1024]:
            for nseq in [256]:
                yield kernel, nstep, nseq


CASE_FMT = "{}_nstep{:05d}_nseq{:04d}"


def case_info(kernel: str, nstep: int, nseq: int):
    name = f"{kernel}_nstep{nstep:05d}_nseq{nseq:04d}"
    return {
        "inp": f"../acid-dataset/output/{name}.zip",
        "out": f"output/subset_{name}.npz",
    }


def run(inp: str, out: str):
    store = zarr.storage.ZipStore(inp)
    root = zarr.open_group(store=store, mode="r")

    # Compute spectrum with Stacie, to be included in plot, only for first seed
    spectrum = compute_spectrum(root["sequences"][0], prefactors=2)
    empirical_acf = np.fft.irfft(spectrum.amplitudes)

    # Write a summary to an NPZ file
    np.savez_compressed(
        out,
        allow_pickle=False,
        times=root["times"],
        freqs=root["freqs"],
        corrtime_int=root.attrs["corrtime_int"],
        acf=root["acf"],
        psd=root["psd"],
        empirical_acf=empirical_acf,
        empirical_psd=spectrum.amplitudes,
        # Only take the first four sequences for plotting
        sequences=root["sequences"][:4],
    )


if __name__ == "__main__":
    driver()
