#!/bin/bash
#PBS -N harpriya_opt
#PBS -j oe
#PBS -l nodes=1:ppn=32
##PBS -l walltime=999:00:00
#PBS -e err_""$PBS_JOBID.err
#PBS -o out_""$PBS_JOBID.out
#echo PBS JOB id is $PBS_JOBID

NPROCS=`wc -l < $PBS_NODEFILE`
cd $PBS_O_WORKDIR

export PYTHON_EXEC=/apps/conda_env/anaconda3-2024/bin/python3.11
$PYTHON_EXEC --version
$PYTHON_EXEC  2IFC.py > 2IFC.out 2>&1
