#!/bin/bash
#SBATCH --export=NONE
#SBATCH --partition=long
#SBATCH --ntasks=20
#SBATCH --time=72:00:00
#SBATCH --job-name=mmbh
#SBATCH --output=mmbh


source active mypython3
mkdir output

python  -W  ignore  mmbh_pigs.py
python  -W  ignore  mmbh_parts.py
python  -W  ignore  massfunctions.py
