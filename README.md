# mmbh-mp-gadget
Python scripts to get properties of the most massive black hole from PART and PIG files of MP-Gadget.

# Usage
1. Go to the directory containing PART and PIG files 
2. ``` git clone https://github.com/kuanweih/mmbh-mp-gadget.git ```
3. Check parameters in `mmbh_param.py`
4. Create output directory ``` mkdir output ```
5. Run slurm script: ``` sbatch slurm-coma.sh ``` if using slurm
   OR ``` bash slurm-coma.sh ``` if using bash
   OR run the following scripts:
  - ``` python -W ignore mmbh_parts.py ``` to get the most massive BH's quantities from PART files.
  - ``` python -W ignore mmbh_pigs.py ``` to get the quantities of host galaxy and halo of the most massive BH from PIG files.
  - ``` python -W ignore massfunctions.py ``` to calculate halo and galaxy mass function from PIG files.
6. Check `output` directory for the result.
 
  
