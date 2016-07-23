#!/bin/sh
cp slurm_template.sh exec.sh
echo "$1" >>  exec.sh
sbatch exec.sh 
