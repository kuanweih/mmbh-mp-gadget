#!/bin/bash
#SBATCH --export=NONE
#SBATCH --partition=long
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=72:00:00
#SBATCH --job-name=mmbh

source activate mypython3

mkdir output

python  -W  ignore  mmbh_pigs.py
python  -W  ignore  mmbh_parts.py
python  -W  ignore  massfunctions.py
