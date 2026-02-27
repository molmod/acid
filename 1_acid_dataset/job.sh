#!/usr/bin/env bash
#SBATCH --job-name=acid
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --mem=20G

source ./.loadvenv
export PATH=$(realpath ${PWD}/scripts/):$PATH
export PYTHONPATH=$(realpath ${PWD}/lib/):$PYTHONPATH
time stepup boot -n ${SLURM_CPUS_PER_TASK}
