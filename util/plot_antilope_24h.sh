#!/usr/bin/bash
export MODULEPATH=/home/gmap/mrpe/mary/public/modulefiles:/opt/softs/libraries/modulefiles/ICC_2018.5.274:/opt/softs/modulefiles

module () 
{ 
    eval `/usr/bin/modulecmd bash $*`
}

module load intel
module load eccodes

dat=$1
#for dat in 20241016 20241017 20241018;do
WORKDIR=/scratch/work/auger/antilope/$dat
cd $WORKDIR
source /home/gmap/mrpa/auger/.epygram_profile
/home/gmap/mrpa/auger/bin/epysum.py ${dat}00.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}01.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}02.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}03.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}04.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}05.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}06.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}07.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}08.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}09.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}10.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}11.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}12.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}13.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}14.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}15.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}16.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}17.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}18.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}19.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}20.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}21.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}22.anti_RR1_FRANXL1S100.grib 'parameterNumber:5' ${dat}23.anti_RR1_FRANXL1S100.grib 'parameterNumber:5'
epy_cartoplot.py --zoom "lonmin=${2}, lonmax=${3}, latmin=${4}, latmax=${5}" --pm contourf --depts  -f 'parameterNumber:5' -c 'rr24h' -o png -O pluie$dat.png sum.grib
/home/gmap/mrpa/auger/bin/lput pluie$dat.png
