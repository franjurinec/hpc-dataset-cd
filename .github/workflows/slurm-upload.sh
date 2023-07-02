#!/bin/bash
#SBATCH --job-name=fusion-data-pipeline
#SBATCH --account=project_2005083
#SBATCH --time=03:00:00
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

module load allas
srun allas-conf --mode s3cmd
srun mkdir s3allas:github-test
srun rclone copy ./tmp/out s3allas:github-test
srun rclone ls s3allas:github-test"