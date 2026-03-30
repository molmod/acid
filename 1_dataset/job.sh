#!/usr/bin/env bash
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0
#SBATCH --job-name=acid
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --mem=20G

cd ..
source ./.loadvenv
cd ${SLURM_SUBMIT_DIR}
export PATH=$(realpath ${PWD}/scripts/):${PATH}
export PYTHONPATH=$(realpath ${PWD}/lib/):${PYTHONPATH}
time stepup boot -n ${SLURM_CPUS_PER_TASK}
