#!/bin/bash
#SBATCH --job-name=fj-test
#SBATCH --account=project_2005083
#SBATCH --time=00:01:00
#SBATCH --partition=test
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10

module load python-data
srun python workflow.py