#!/usr/bin/env python3
"""Workflow for the report of a single case (program + version + settings)."""

import argparse
import json

from path import Path
from stepup.core.api import amend, loadns, runpy
from stepup.reprep.api import compile_typst


def main():
    args = parse_args()
    plan(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Workflow for the report of a single case (program + version + settings).",
    )
    parser.add_argument(
        "jsons",
        type=Path,
        nargs="+",
        help="List of JSON input files to include in the report.",
    )
    parser.add_argument(
        "case",
        type=str,
        help="Case name (program_version_settings) to generate the report for.",
    )
    return parser.parse_args()


def plan(args: argparse.Namespace):
    # Analyze the provided JSON inputs to decide what to include in the report.
    has_acint = True
    has_corretime_exp = True
    has_neff = True
    summaries = {}
    mcmaps = {}
    npar = None
    for path_json in args.jsons:
        data = loadns(path_json)
        if len(vars(data)) == 0:
            continue  # Skip empty summary files.
        kernel = path_json.stem.split("_")[1]
        if path_json.stem.startswith("summary"):
            if npar is None:
                npar = data.npar
            elif npar != data.npar:
                raise RuntimeError(
                    "All summary files must have the same number of model parameters."
                )
            if not hasattr(data, "acint"):
                has_acint = False
            if not hasattr(data, "corrtime_exp"):
                has_corretime_exp = False
            for field in "neff", "fcut", "cost_zscore", "criterion_zscore":
                if not hasattr(data, field):
                    has_neff = False
            summaries.setdefault(kernel, []).append(path_json)
        elif path_json.stem.startswith("mcmap"):
            # For now, we only plot MC results for 2D parameter spaces.
            if len(data.map_pars) == 2:
                mcmaps.setdefault(kernel, []).append(path_json)

    if not has_acint:
        raise RuntimeError("ACINT results are required for the report generation.")
    if not has_corretime_exp:
        print("Warning: exponential correlation times missing in some results.")
    if not has_neff:
        print("Warning: effective number of points or cutoff frequency missing in some results.")

    # Plot and tabulate results
    path_settings = "../1_acid_dataset/settings.json"
    for kernel, paths_json in summaries.items():
        plan_scaling(args.case, kernel, "acint", path_settings, paths_json)
        if has_corretime_exp:
            plan_scaling(args.case, kernel, "corrtime_exp", path_settings, paths_json)
        if has_neff:
            plan_cutoff(args.case, kernel, "acint", paths_json)
            if has_corretime_exp:
                plan_cutoff(args.case, kernel, "corrtime_exp", paths_json)
            plan_tables(args.case, kernel, path_settings, npar, paths_json)

    for kernel, paths_json in mcmaps.items():
        plan_mcmap(args.case, kernel, path_settings, paths_json)

    # Write flags with available results to a JSON file to configure the Typst report.
    path_config = Path(f"reports/{args.case}/report_config.json")
    amend(out=path_config)
    with open(path_config, "w") as fh:
        json.dump(
            {
                "has_corrtime_exp": has_corretime_exp,
                "has_neff": has_neff,
                "has_mcmap": len(mcmaps) > 0,
                "case": args.case,
                "kernels": list(summaries.keys()),
                "npar": npar,
            },
            fh,
        )

    # Compile the Typst report.
    compile_typst(
        "report.typ",
        dest=f"reports/{args.case}/report.pdf",
        sysinp={"config": path_config},
    )


def plan_scaling(
    case: str, kernel: str, quantity: str, path_settings: Path, paths_json: list[Path]
):
    path_zarr = f"../1_acid_dataset/output/{kernel}_nstep01024_nseq0256.zip"
    path_scaling = f"reports/{case}/{kernel}_{quantity}_scaling.svg"
    path_ratios = f"reports/{case}/{kernel}_{quantity}_ratios.svg"
    path_csv_stats = f"reports/{case}/{kernel}_{quantity}_stats.csv"
    paths_json_stats = f"reports/{case}/{kernel}_{quantity}_stats.json"
    runpy(
        f"./scripts/plot_scaling.py {kernel} {quantity} {path_settings} {path_zarr} ../matplotlibrc"
        f" {' '.join(str(p) for p in paths_json)} "
        f"{path_scaling} {path_ratios} {path_csv_stats} {paths_json_stats}",
        inp=[
            "scripts/plot_scaling.py",
            path_settings,
            path_zarr,
            "../matplotlibrc",
            *paths_json,
        ],
        out=[
            path_scaling,
            path_ratios,
            path_csv_stats,
            paths_json_stats,
        ],
    )


def plan_cutoff(case: str, kernel: str, quantity: str, paths_json: list[Path]):
    path_zarr = f"../1_acid_dataset/output/{kernel}_nstep01024_nseq0256.zip"
    path_cutoff = f"reports/{case}/{kernel}_{quantity}_cutoff.svg"
    paths_json = [p for p in paths_json if "nseq0064" in p.stem]
    runpy(
        f"./scripts/plot_cutoff.py {kernel} {quantity} {path_zarr} ../matplotlibrc"
        f" {' '.join(str(p) for p in paths_json)} {path_cutoff}",
        inp=[
            "scripts/plot_cutoff.py",
            path_zarr,
            "../matplotlibrc",
            *paths_json,
        ],
        out=[
            path_cutoff,
        ],
    )


def plan_tables(case: str, kernel: str, path_settings: Path, npar: int, paths_json: list[Path]):
    path_ncomplete = f"reports/{case}/{kernel}_ncomplete.csv"
    path_neff = f"reports/{case}/{kernel}_neff.csv"
    path_cost_zscore = f"reports/{case}/{kernel}_cost_zscore.csv"
    path_criterion_zscore = f"reports/{case}/{kernel}_criterion_zscore.csv"
    runpy(
        f"./scripts/tabulate_sanity_checks.py {kernel} {path_settings} {npar}"
        f" {' '.join(str(p) for p in paths_json)}"
        f" {path_ncomplete} {path_neff} {path_cost_zscore} {path_criterion_zscore}",
        inp=[
            "scripts/tabulate_sanity_checks.py",
            path_settings,
            *paths_json,
        ],
        out=[
            path_ncomplete,
            path_neff,
            path_cost_zscore,
            path_criterion_zscore,
        ],
    )


def plan_mcmap(case: str, kernel: str, path_settings: Path, paths_json: list[Path]):
    path_mcmap = f"reports/{case}/{kernel}_mcmap.svg"
    runpy(
        f"./scripts/plot_monte_carlo.py {kernel} {path_settings} ../matplotlibrc"
        f" {' '.join(str(p) for p in paths_json)} {path_mcmap}",
        inp=[
            "scripts/plot_monte_carlo.py",
            path_settings,
            "../matplotlibrc",
            *paths_json,
        ],
        out=[
            path_mcmap,
        ],
    )


if __name__ == "__main__":
    main()
