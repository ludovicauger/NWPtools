export DR_HOOK=0
export DR_HOOK_IGNORE_SIGNALS=-1
ECCODES_DEFINITION_PATH=/home/gmap/mrpm/marguina/install/I185274INTELMPI185274_bull/eccodes-2.14.0/share/eccodes/definitions
ECCODES_SAMPLES_PATH=/home/gmap/mrpm/marguina/install/I185274INTELMPI185274_bull/eccodes-2.14.0/share/eccodes/ifs_samples/grib1
ulimit -s unlimited
/home/mf/dp/marp/verolive/public/mpi-tools/mpiauto/mpiauto --wrap --wrap-stdeo --wrap-stdeo-pack --verbose --init-timeout-restart 1 -nn 1 -nnp 1 ./ARPEGE.EX
 il faut récupérer le bon mpiauto depuis un step.02.out....
pourquoi je n'ai pas eu besoin de positionner les variables grib ?????
mystere, bon ca marche.
il faudrait positionner les variables grib
il faut effacer les output sinon pour certain on ecrit à la fin du fichier sans l effacer
les variables GRIB_XXX ne sont pas a positionner obligatoirement mais si c'est fait la premiere valeur de GRIB_DEFINIT... doit etre correctement mise
les variables d'environnements doivent etre positionnées en copie paste directement dans le shell ça ne semble par fonctionner systematiquement en lancant le script
