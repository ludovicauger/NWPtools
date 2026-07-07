#!/bin/bash


###################################################################
# Script permettant de faire une requete d'extraire antilope de la BDAP
#
###################################################################

#export PGDATABASE=${PGDATABASE:-bdu}
#export PGHOST=${PGHOST:-bdu-zd}
#export PGUSER=${PGUSER:-olive}
#export PGPASSWORD=${PGPASSWORD:-olive}





liste_parametres="PRECIP"
type_niveau="SOL"
niveau=0
modele_BDAP=ANTILOPEJP1
grille_BDAP=FRANXL1S100



##### REQUETE BDAP ######
cat << fin > questionRequeteDap3
#RQST
#NFIC anti_RR1_FRANXL1S100.grib
#MOD $modele_BDAP
#PARAM $liste_parametres
#Z_REF $grille_BDAP
#Z_EXTR GRILLE
#T_LST 60
#D_STP 20250502110000 20250502120000 010000
#L_TYP $type_niveau
#L_LST $niveau
#FORM GRIB2_C_MAX
fin

# Lance de la requete
/usr/local/sopra/bin/dap3_dev_date_ech questionRequeteDap3
#dap3_date_ech questionRequeteDap3
