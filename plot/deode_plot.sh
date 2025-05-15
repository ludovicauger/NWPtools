#!/usr/bin/bash
ulimit -s unlimited

LOCDIR=`pwd`
WORKDIR=/scratch/work/auger/plotdeode

get_deode () {
scp rm6@hpc-login:/scratch/rm6/deode/CY49t2_AROME_nwp_large_SW_500m_20250209/archive/2025/02/09/00/ICMSHDEOD+0006h00m00s .
}

cd $WORKDIR

rm $WORKDIR/*png

get_deode 
fic=ICMSHDEOD+0006h00m00s
for FIELD in S030TEMPERATURE S030WIND.U.PHYS S060TEMPERATURE S060WIND.U.PHYS S090TEMPERATURE S090WIND.U.PHYS SURFTEMPERATURE 'TOPRAYT DIR SOM' ATMONEBUL.CONVEC ATMONEBUL.HAUTE ATMONEBUL.MOYENN ATMONEBUL.BASSE;do
#for FIELD in SURFTEMPERATURE;do
epy_cartoplot.py -F $FIELD  $fic -O ${FIELD}.png
done
cd $LOCDIR
#./plot/generate_html.py $XPNAME $XPNAME
