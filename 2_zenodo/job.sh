#!/usr/bin/env bash
#SBATCH --job-name=zenodo
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mem=5G

cd ..
source ./.loadvenv
cd ${SLURM_SUBMIT_DIR}
time stepup boot -n ${SLURM_CPUS_PER_TASK}
