#!/bin/bash
#SBATCH --job-name=fusion-data-pipeline
#SBATCH --account=project_2005083
#SBATCH --time=03:00:00
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

module load allas
source /appl/opt/csc-tools/allas-cli-utils/allas_conf -f -k --mode s3cmd
rclone copy ./tmp/out s3allas:$S3_TARGET/data
rclone ls s3allas:$S3_TARGET