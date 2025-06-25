#!/usr/bin/env bash
#SBATCH --job-name=acid
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --mem=20G

cd ../
source activate
cd ${SLURM_SUBMIT_DIR}
time stepup boot -n ${SLURM_CPUS_PER_TASK}
