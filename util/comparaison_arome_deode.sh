#!/usr/bin/bash
#dat=20260304;event=storm;number=00
dat=20260312;event=flooding;number=00
#dat=20260330;event=nwp;number=00
datp1=$(date -d "${dat} +1 day" +"%Y%m%d")
echo $datp1
rm -f ICMSHDEOD*
rm -f historic*
ssh sotrtm37-sidev "/home/mrpa/auger/EXTRACT_BD/lance_antilope.sh ${datp1}"
/scratch/work/auger/NWPtools/util/plot_antilope_24h.sh ${datp1} -5 10 40 53
/home/gmap/mrpa/auger/bin/lgetmf
ssh hpc-login "/home/rm6/dev/get_deode.sh ${dat} $event $number"
/home/gmap/mrpa/auger/bin/lgetec
module load intel
module load eccodes
module load python/3.12.12
module load epygram
epy_cartoplot.py --pm contourf --depts  -D ICMSHDEOD+0024h00m00s -f SURFACCPLUIE -C 'rr24h' -o png -O deode.png ICMSHDEOD+0048h00m00s
mv diff* deode${datp1}.png
ftp hendrix.meteo.Fr<<EOF
cd /home/m/mxpt/mxpt001/vortex/arome/3dvarfr/OPER/${dat:0:4}/${dat:4:2}/${dat:6:2}/T1200P/forecast
get historic.arome.franmg-01km30+0036:00.fa
get historic.arome.franmg-01km30+0012:00.fa
EOF
epy_cartoplot.py --pm contourf --depts  -D 'historic.arome.franmg-01km30+0012:00.fa' -f SURFACCPLUIE -C 'rr24h' -o png -O arome.png 'historic.arome.franmg-01km30+0036:00.fa'
mv diff* arome${datp1}.png
