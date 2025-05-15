#!/bin/bash
#SBATCH --export=NONE
#SBATCH --job-name=frc@7J5F
#SBATCH --mem=62000
#SBATCH --nodes=1
#SBATCH --partition=huge256
#SBATCH --time=3-00:00:00
#SBATCH --exclusive
#SBATCH --verbose
#SBATCH --no-requeue

#export DR_HOOK=0
export DR_HOOK_IGNORE_SIGNALS=-1
export ECCODES_DEFINITION_PATH=/scratch/mtool/auger/spool/spool_087648_B8PT_frc/extra_grib_defs:/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/definitions
export ECCODES_SAMPLES_PATH=/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/ifs_samples/grib1
ulimit -s unlimited
ulimit -l unlimited
export OMP_NUM_THREADS=1
export OMP_STACKSIZE=4G
export KMP_STACKSIZE=4G
export KMP_MONITOR_STACKSIZE=1G
export DR_HOOK=1
export DR_HOOK_IGNORE_SIGNALS=-1
export DR_HOOK_OPT=prof
export EC_PROFILE_HEAP=0
export EC_MPI_ATEXIT=0
STG=1
ENDSTEP=216
ICMSATM=ICMSHFCST+00$ENDSTEP
ICMSSURF=ICMSHFCST+00${ENDSTEP}.sfx
set -x
LOCDIR=`pwd`
echo $LOCDIR
cd /scratch/work/auger/exp/AROMErefday1
unlink ELSCFFCSTALBC000
unlink ELSCFFCSTALBC001
unlink ELSCFFCSTALBC002
unlink ELSCFFCSTALBC003
CP1=`expr $STG - 1 | xargs printf "%4.4d"`
CP2=`expr $STG  | xargs printf "%4.4d"`
CP3=`expr $STG + 1 | xargs printf "%4.4d"`
CP4=`expr $STG + 2 | xargs printf "%4.4d"`
ln -s ELSCFFCSTALBC$CP1 ELSCFFCSTALBC000 
ln -s ELSCFFCSTALBC$CP2 ELSCFFCSTALBC001 
ln -s ELSCFFCSTALBC$CP3 ELSCFFCSTALBC002 
ln -s ELSCFFCSTALBC$CP4 ELSCFFCSTALBC003 
#rm -f ICMSHFCST+00${ENDSTEP}* ICMSHFCST+0018.sfx*
unlink ICMSHFCSTINIT
unlink ICMSHFCSTINIT.sfx
if [ $STG == 1 ];
then
ln -s ICMSHFCSTINIT.ini ICMSHFCSTINIT
ln -s ICMSHFCSTINIT.sfx.ini ICMSHFCSTINIT.sfx
else
STGM1=`expr STG - 1`
ln -s ICMSHFCST+0216.$STGM1 ICMSHFCSTINIT
ln -s ICMSHFCST+0216.sfx.$STGM1 ICMSHFCSTINIT.sfx
fi
/home/mf/dp/marp/verolive/SAVE/public/mtool-2.2.8/public/mpi-tools/mpiauto/mpiauto --wrap --wrap-stdeo --wrap-stdeo-pack --verbose --init-timeout-restart 1 -nn 1 -nnp 1 --openmp 1 -- ./AROME.EX -eFCST -c001 -maladin -vmeteo -asli -t50 -ft${ENDSTEP}
mv stdeo.0 stdeo.0.$STG
mv ICMSHFCST+0036 ICMSHFCST+0036.$STG
mv ICMSHFCST+0036.sfx ICMSHFCST+0036.sfx.$STG
mv ICMSHFCST+0072 ICMSHFCST+0072.$STG
mv ICMSHFCST+0072.sfx ICMSHFCST+0072.sfx.$STG
mv ICMSHFCST+0108 ICMSHFCST+0108.$STG
mv ICMSHFCST+0108.sfx ICMSHFCST+0108.sfx.$STG
mv ICMSHFCST+0144 ICMSHFCST+0144.$STG
mv ICMSHFCST+0144.sfx ICMSHFCST+0144.sfx.$STG
mv ICMSHFCST+0180 ICMSHFCST+0180.$STG
mv ICMSHFCST+0180.sfx ICMSHFCST+0180.sfx.$STG
mv ICMSHFCST+0216 ICMSHFCST+0216.$STG
mv ICMSHFCST+0216.sfx ICMSHFCST+0216.sfx.$STG

