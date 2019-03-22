#!/bin/bash
#SBATCH --export=NONE
#SBATCH --partition=long
#SBATCH --ntasks=30
#SBATCH --time=72:00:00
#SBATCH --job-name=BT2
#SBATCH --output=BT2.out


# export OMP_NUM_THREADS=1

# cd $PBS_O_WORKDIR

source active mypython3

python  mmbh_pigs.py  1>stdout-pig  2>stderr-pig
#python  mmbh_parts.py  1>stdout-part  2>stderr-part
python  massfunctions.py  1>stdout-mf  2>stderr-mf
