#!/usr/bin/env python3
"""Compute results with STACIE for a given test case."""

import argparse
import pickle
from traceback import print_exc

import numpy as np
import zarr
from path import Path
from stacie import compute_spectrum, estimate_acint


def main():
    args = parse_args()
    run(args.case, args.model, args.out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute results with STACIE for a given test case."
    )
    parser.add_argument(
        "case",
        type=Path,
        help="Path to the input zarr file from the ACID dataset.",
    )
    parser.add_argument(
        "model",
        type=str,
        choices=["quad", "lorentz"],
        help="Spectrum model to use for the estimation.",
    )
    parser.add_argument(
        "out",
        type=Path,
        help="Path to the output pickle file to store the results.",
    )
    return parser.parse_args()


def run(inp: Path, model: str, out: Path):
    # Exit early if the file exists, meaning that is not recomputed even if the script changed.
    # You need to remove the files manually.
    if Path(out).is_file():
        return

    # Get the model from a helper function to delay imports.
    # This ensures that the script can work with different versions of STACIE.
    spectrum_model = {
        "quad": get_quad_model,
        "lorentz": get_lorentz_model,
    }[model]()

    # Open the input zarr file and process all sequences.
    store = zarr.storage.ZipStore(inp)
    root = zarr.open_group(store=store, mode="r")
    results = []
    for iseed, sequences in enumerate(root["sequences"]):
        # The prefactor 2.0 is used as a matter of convention. It is not critical.
        # It just facilitates reading plots as the DC component of the PSD will
        # now match the autocorrelation integral without additional factors.
        spectrum = compute_spectrum(((2.0, np.array(row)) for row in sequences), prefactors=None)
        spectrum.amplitudes_ref = np.array(root["psd"])
        try:
            result = estimate_acint(
                spectrum,
                spectrum_model,
                neff_max=max(1024, spectrum.nstep // 8),
            )
            result.props["iseed"] = iseed
            print(f"{iseed:3d} {result.neff:7.1f}   {result.acint:8.5f}")
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            # Catch all exceptions, so we can keep track of how many runs failed.
            print(f"{iseed:3d} {exc}")
            print_exc()
    results.sort(key=lambda r: r.props["acint"])
    with open(out, "bw") as fh:
        pickle.dump(results, fh)


def get_quad_model():
    from stacie.model import ExpPolyModel

    return ExpPolyModel([0, 2])


def get_lorentz_model():
    from stacie.model import LorentzModel

    return LorentzModel()


if __name__ == "__main__":
    main()
