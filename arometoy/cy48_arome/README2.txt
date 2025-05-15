export DR_HOOK=0
export DR_HOOK_IGNORE_SIGNALS=-1
#export GRIB_SAMPLES_PATH=/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/ifs_samples/grib1
#export GRIB_DEFINITION_PATH=/home/auger/exp/arpege/extra_grib_defs/:/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/definitions/grib2/:/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/definitions/grib1/
export ECCODES_DEFINITION_PATH=/scratch/mtool/auger/spool/spool_087648_B8PT_frc/extra_grib_defs:/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/definitions
export ECCODES_SAMPLES_PATH=/opt/softs/libraries/ICC16.1.150/eccodes-2.7.0-b80884e7ca77a8f8ead5b4b1a2bd9011448b961e/share/eccodes/ifs_samples/grib1
ulimit -s unlimited
/home/mf/dp/marp/verolive/SAVE/public/mtool-2.2.8/public/mpi-tools/mpiauto/mpiauto --wrap --wrap-stdeo --wrap-stdeo-pack --verbose --init-timeout-restart 1 -nn 1 -nnp 1 ./ARPEGE.EX
 il faut récupérer le bon mpiauto depuis un step.02.out....
pourquoi je n'ai pas eu besoin de positionner les variables grib ?????
mystere, bon ca marche.
il faudrait positionner les variables grib
il faut effacer les output sinon pour certain on ecrit à la fin du fichier sans l effacer
les variables GRIB_XXX ne sont pas a positionner obligatoirement mais si c'est fait la premiere valeur de GRIB_DEFINIT... doit etre correctement mise
