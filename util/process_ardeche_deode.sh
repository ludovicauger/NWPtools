#!/bin/bash

module purge
module load eccodes4epygram/2.38.0

for fic in GRIBPFDEOD+0001h00m00s GRIBPFDEOD+0002h00m00s GRIBPFDEOD+0003h00m00s GRIBPFDEOD+0004h00m00s GRIBPFDEOD+0005h00m00s GRIBPFDEOD+0006h00m00s;do
ssh rm6@hpc-login "cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/CY48t3_AROME_nwp_ARDECHE_20241016/archive/2024/10/16/00/${fic} ."
scp rm6@hpc-login:/scratch/rm6/plot/${fic} .
extract_grib.py $fic rain${fic}.grib 139
epy_cartoplot.py -f'parameterNumber:65' -o png -O ${fic}.png rain${fic}.grib
done
