#!/usr/bin/env bash
#SBATCH --job-name=acid
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mem=5G

source ./.loadvenv
export PATH=$(realpath ${PWD}/scripts/):$PATH
time stepup boot -n ${SLURM_CPUS_PER_TASK}
