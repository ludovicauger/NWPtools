export DR_HOOK=0
export DR_HOOK_IGNORE_SIGNALS=-1
export DR_HACK=0
export DR_HOOK=0

export ECCODES_DEFINITION_PATH=/scratch/mtool/auger/arome/test/extra_grib_defs:/opt/softs/libraries/ICC_2018.5.274/eccodes-2.14.1/share/eccodes/definitions
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
#mpirun -np  1 ./getf
#./getf
#grep NaN stdeo.0>>output
#mv stdeo.0 stdeo.0.$i
#done
