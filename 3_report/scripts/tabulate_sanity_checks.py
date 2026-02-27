#!/usr/bin/env python3

import argparse
import json

import numpy as np
from path import Path
from stepup.core.api import loadns


def main():
    args = parse_args()
    run(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tabulate sanity check results.",
    )
    parser.add_argument(
        "kernel",
        type=str,
        help="Kernel name",
    )
    parser.add_argument(
        "settings",
        type=Path,
        help="ACID settings JSON file",
    )
    parser.add_argument(
        "npar",
        type=int,
        help="Number of parameters in the model",
    )
    parser.add_argument(
        "summaries",
        type=Path,
        nargs="+",
        help="List of JSON summary files",
    )
    parser.add_argument(
        "csv_ncomplete",
        type=Path,
        help="Output CSV file for table with number of complete estimates",
    )
    parser.add_argument(
        "csv_neff",
        type=Path,
        help="Output CSV file for neff table",
    )
    parser.add_argument(
        "csv_cost_zscore",
        type=Path,
        help="Output CSV file for cost z-score table",
    )
    parser.add_argument(
        "csv_criterion_zscore",
        type=Path,
        help="Output CSV file for criterion z-score table",
    )
    return parser.parse_args()


def run(args: argparse.Namespace):
    settings = loadns(args.settings)

    # Preprocess inputs
    settings = loadns(args.settings)
    paths_json = {}
    for path_json in args.summaries:
        words = path_json.stem.split("_")
        if words[0] != "summary":
            raise RuntimeError(f"Unexpected summary file name: {path_json}")
        if words[1] != args.kernel:
            raise RuntimeError(f"Unexpected kernel in summary file name: {path_json}")
        nstep = int(words[2].replace("nstep", ""))
        nseq = int(words[3].replace("nseq", ""))
        paths_json[(nstep, nseq)] = path_json

    # Collect data for tables
    col_header = [f"$M={nseq}$" for nseq in settings.nseqs]
    row_header = [f"$N={nstep}$" for nstep in settings.nsteps]
    fields = [
        ("neff", args.npar * 20, False),
        ("cost_zscore", 2.0, True),
        ("criterion_zscore", 2.0, True),
    ]
    cells = {field: [] for field, _, _ in fields}
    cells["ncomplete"] = []
    for nstep in settings.nsteps:
        rows = {}
        for field, _, _ in fields:
            rows[field] = []
            cells[field].append(rows[field])
        rows["ncomplete"] = []
        cells["ncomplete"].append(rows["ncomplete"])
        for nseq in settings.nseqs:
            path_json = paths_json.get((nstep, nseq))
            if path_json is None:
                for field, _, _ in fields:
                    rows[field].append("[N/A]")
                rows["ncomplete"].append("0")
            else:
                with open(path_json) as fh:
                    data = json.load(fh)
                rows["ncomplete"].append(str(len(data["neff"])))
                for field, threshold, upper in fields:
                    values = np.array(data[field])
                    num_safe = (values >= threshold if upper else values <= threshold).sum()
                    rows[field].append(str(num_safe))

    # Write CSV files with table data.
    for field, table in cells.items():
        paths_csv = getattr(args, f"csv_{field}")
        if not paths_csv.endswith(".csv"):
            raise RuntimeError(f"Output {field} file must be a CSV file.")
        with open(paths_csv, "w") as fh:
            print(",".join(["", *col_header]), file=fh)
            for header, row in zip(row_header, table, strict=True):
                print(",".join([header, *row]), file=fh)


if __name__ == "__main__":
    main()
