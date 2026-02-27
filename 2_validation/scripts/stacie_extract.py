#!/usr/bin/env python3
"""Extraction of STACIE estimation results and store them in a JSON file."""

import argparse
import json
import pickle

from path import Path


def main():
    args = parse_args()
    run(args.inp, args.out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extraction of STACIE estimation results and store them in JSON file."
    )
    parser.add_argument("inp", type=Path, help="Input pickle file with STACIE estimation results.")
    parser.add_argument("out", type=Path, help="Output JSON file.")
    return parser.parse_args()


def run(inp: Path, out: Path):
    with open(inp, "rb") as fh:
        results = pickle.load(fh)
    if len(results) == 0:
        data = {}
    else:
        data = {
            "acint": [r.acint for r in results],
            "acint_std": [r.acint_std for r in results],
            "neff": [r.neff for r in results],
            "fcut": [r.fcut for r in results],
            "cost_zscore": [r.props["cost_zscore"] for r in results],
            "criterion_zscore": [r.props["criterion_zscore"] for r in results],
            "npar": results[0].model.npar,
        }
        if "corrtime_exp" in results[0].props:
            data["corrtime_exp"] = [r.props["corrtime_exp"] for r in results]
            data["corrtime_exp_std"] = [r.props["corrtime_exp_std"] for r in results]
    with open(out, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
