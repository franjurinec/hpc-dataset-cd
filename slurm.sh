#!/bin/bash
#SBATCH --job-name=fusion-data-pipeline
#SBATCH --account=project_2005083
#SBATCH --time=03:00:00
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

module load python-data
srun python workflow.py