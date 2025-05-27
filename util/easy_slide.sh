#!/usr/bin/bash
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

./get_arome_oper.sh $dat $ech
./get_arome_ifs.sh $dat $ech
./antilope.py 2025051900 2025052024 'lonmin=3, lonmax=8, latmin=42, latmax=45'
set -x
#source /home/gmap/mrpa/auger/.epygram/profile
epy_cartoplot.py --zoom 'lonmin=3, lonmax=8, latmin=42, latmax=45' --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs.png aromeifs$dat$ech.fa
epy_cartoplot.py --zoom 'lonmin=3, lonmax=8, latmin=42, latmax=45' --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper.png aromeoper$dat$ech.fa
generate_html cas20mai2025 cas20mai2025




