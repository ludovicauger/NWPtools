export DR_HOOK=0
export DR_HOOK_IGNORE_SIGNALS=-1
export DR_HACK=0
export DR_HOOK=1

module purge
module load cmake/3.24.1 1> /dev/null
#module load intel/oneapi/2023.2 1> /dev/null
module load intel/2018.5.274_mkl_nightly_2019u2
#module load compiler/2023.2.0 1> /dev/null
#module load mkl/2023.2.0 1> /dev/null
#module load mpi/2021.10.0 1> /dev/null
#module load gcc/9.2.0 1> /dev/null
module load python/3.10.12 1> /dev/null
module load perl/5.40.1 1> /dev/null
module load openmpi/gnu/ilp64/4.0.5.1
module load hdf5/1.10.5_recom
module load eccodes



#export ECCODES_DEFINITION_PATH=/scratch/mtool/auger/arome/test/extra_grib_defs:/opt/softs/libraries/ICC_2018.5.274/eccodes-2.14.1/share/eccodes/definitions
export ECCODES_DEFINITION_PATH=extra_grib_defs:/opt/softs/libraries/ICC_2018.5.274/eccodes-2.14.1/share/eccodes/definitions
export ECCODES_SAMPLES_PATH=/opt/softs/libraries/ICC_2018.5.274/eccodes-2.14.1/share/eccodes/ifs_samples/grib1
export OMP_NUM_THREADS=1
ulimit -s unlimited
rm ICMSHFCST+00??
rm PFFCSTFRANGP0025+0000
#while ! [[ -f /home/gmap/mrpa/auger/pack/cy46t1_gp_thomas_dev/bin/MASTERODB ]]; do
#echo "pas la"
#sleep 5
#done
#rm -rf ICMSHFCST+0015 ICMSHFCST+0002 ICMSHFCST+0001 output
#for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
#do
#echo "test" $i>>output
ls -H getf
while [ $? -ne 0 ]
do
  sleep 10
  ls -H getf
done
/home/mf/dp/marp/verolive/public/mpi-tools/mpiauto/mpiauto --wrap --wrap-stdeo --wrap-stdeo-pack --verbose --init-timeout-restart 1 -nn 1 -nnp 1 ./getf
#./getf
#grep NaN stdeo.0>>output
#mv stdeo.0 stdeo.0.$i
#done
