#!/usr/bin/env python3

import pickle
from collections.abc import Iterator

import numpy as np
import zarr
from path import Path
from stacie import ExpPolyModel, LorentzModel, compute_spectrum, estimate_acint
from stepup.core.script import driver


def cases() -> Iterator[tuple[str, int, int, str, str]]:
    from settings import KERNELS, NSEQS, NSTEPS

    for kernel, models in KERNELS.items():
        for model in models:
            for nseq in NSEQS:
                for nstep in NSTEPS:
                    yield kernel, nstep, nseq, model


CASE_FMT = "{}_nstep{:05d}_nseq{:04d}_{}"


def case_info(kernel: str, nstep: int, nseq: int, model: str):
    name = f"{kernel}_nstep{nstep:05d}_nseq{nseq:04d}"
    return {
        "inp": f"../acid-dataset/output/{name}.zip",
        "out": f"output/estimate_{name}_{model}.pickle",
        "model": model,
    }


def run(inp: str, out: str, model: str):
    # Exit early if the file exists, meaning that is not recomputed even if the script changed.
    # You need to remove the files manually.
    if Path(out).is_file():
        return

    # Configure calculation
    spectrum_model = {
        "quad": ExpPolyModel([0, 2]),
        "lorentz": LorentzModel(),
    }[model]

    store = zarr.storage.ZipStore(inp)
    root = zarr.open_group(store=store, mode="r")
    results = []
    for iseed, sequences in enumerate(root["sequences"]):
        spectrum = compute_spectrum(((2.0, np.array(row)) for row in sequences), prefactors=None)
        spectrum.amplitudes_ref = np.array(root["psd"])
        try:
            result = estimate_acint(
                spectrum,
                spectrum_model,
                neff_max=max(1024, spectrum.nstep // 8),
            )
            print(f"{iseed:3d} {result.neff:7.1f}   {result.acint:8.5f}")
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            print(f"{iseed:3d} {exc}")
    results.sort(key=lambda r: r.props["acint"])
    with open(out, "bw") as fh:
        pickle.dump(results, fh)


if __name__ == "__main__":
    driver()
