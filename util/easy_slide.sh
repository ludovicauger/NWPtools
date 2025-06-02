#!/bin/bash
dat=2025051900
ech=48
yyyy=${dat:0:4}
mm=${dat:4:2}
dd=${dat:6:2}
hh=${dat:8:2}

module load intel
module unload eccodes
module load eccodes4epygram/2.38.0
ulimit -s unlimited

zoom='lonmin=3,lonmax=8,latmin=42,latmax=45'
get_arome_oper.sh $dat $ech
get_arome_ifs.sh $dat $ech
antilope.py 2025051900 2025052024 $zoom
set -x
epy_cartoplot.py --zoom  ${zoom}  --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs$dat.png aromeifs$dat$ech.fa
epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
ssh rm6@hpc-login 'cd /scratch/rm6 ;ecp ec:/aut6432/DE_NWP/deode/2025/05/19/00/convection/4/AROME_500m/ICMSHDEOD+0048h00m00s .'
scp rm6@hpc-login:/scratch/rm6/ICMSHDEOD+0048h00m00s .
epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodeoper$dat.png ICMSHDEOD+0048h00m00s
dat=2025051903
ech=45
get_arome_oper.sh $dat $ech
epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
dat=2025051906
ech=42
get_arome_oper.sh $dat $ech
get_arome_ifs $dat $ech
epy_cartoplot.py --zoom $zoom  --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs$dat.png aromeifs$dat$ech.fa
epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
generate_html cas20mai2025 cas20mai2025




