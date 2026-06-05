#!/usr/bin/bash
module load python/3.12.12
module load epygram
ulimit -s unlimited

LOCDIR=`pwd`
WORKDIR=/scratch/work/auger/plotdeode

get_deode () {
scp rm6@hpc-login:/scratch/rm6/deode/CY49t2_AROME_DAN_1500x1500_500m_2025_07_v5/20250729_1200/mbr000/Failed_task_Forecast_ac1-2012.bullx3076316/ICMSHDEOD+0000:00:40 ./fica
scp rm6@hpc-login:/scratch/rm6/deode/CY49t2_AROME_DAN_1500x1500_500m_2025_07_v5/20250729_1200/mbr000/Failed_task_Forecast_ac1-2012.bullx3076316/ICMSHDEODINIT ./ficb

}

cd $WORKDIR

rm $WORKDIR/*png

get_deode 
for FIELD in SURFTEMPERATURE;do
#for FIELD in SURFTEMPERATURE;do
#epy_cartoplot.py -F $FIELD  -D ficb -O ${FIELD}.png fica
epy_cartoplot.py -F $FIELD  -d ficb -O ${FIELD}.png fica
done
cd $LOCDIR
#./plot/generate_html.py $XPNAME $XPNAME
