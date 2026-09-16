#!/opt/softs/anaconda3/bin/python3
import subprocess
import os
from random import randint
from datetime import datetime, timedelta
import sys
#Time is in UTC
date1_str = '2026082414'
date2_str = '2026082416'
myzoom='lonmin=1, lonmax=4, latmin=42, latmax=44'
nbarg=len(sys.argv)

subprocess.run([f"module load eccodes"],shell=True)

if (nbarg==2) and (sys.argv[1] == '-h'):
   print("Extract antilope rain accumulation between date1 and date2. The period ends at date2 not date2 + 1 hour")
   print("Time is in UTC")
   print("usage : antilope <beginning date1 YYYYMMDDHH> <date2 format YYYYMMDDHH> ['lonmin=-1, lonmax=3, latmin=42, latmax=45']")
   exit()
if nbarg>2:
   date1_str = sys.argv[1]
   date2_str = sys.argv[2]
if nbarg==4:
   myzoom = sys.argv[3]

def  parse_date(date_str):
    return datetime.strptime(date_str, "%Y%m%d%H")

date1 = parse_date(date1_str)

if date2_str[8:10] == '24':
   date2_str=date2_str[0:8]+'23'
   date2 = parse_date(date2_str)
else:
   date2 = parse_date(date2_str)
   date2 -= timedelta(hours=1)

date_debut=date1.strftime("%Y%m%d%H")+"0000"
date_fin=date2.strftime("%Y%m%d%H")+"0000"
nomfic='anti_RR1_FRANXL1S100.grib'
import epygram
with open('cmd.ksh','w') as f:
  f.write(f'''#!/bin/bash


###################################################################
# Script permettant de faire une requete d'extraire antilope de la BDAP
#
###################################################################

#export PGDATABASE=${{PGDATABASE:-bdu}}
#export PGHOST=${{PGHOST:-bdu-zd}}
#export PGUSER=${{PGUSER:-olive}}
#export PGPASSWORD=${{PGPASSWORD:-olive}}

export LOGNAME=auger
export DB_NAMES_PG=/usr/local/sopra/etc/pgnames.conf
export DB_FILE_BDCP=/usr/local/sopra/neons_db_bdcp
export ORACLE_HOME=/home/oracle/11g/client
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/sopra/lib/:/usr/local/sopra/grib_api/lib/
export EXTRACTION_BDAP_JOURNAL_AGT_tar_cbd=/tmp/journal_extraction_tar_cbd
export DB_FILE_BDAPARP=/usr/local/sopra/neons_db_bdaparp
export DB_FILE_BDAPARCH=/usr/local/sopra/neons_db_bdaparch
export BDAP_IAA="-lAgtArch -lAgtStruct -lArchBdap -lDesarchBdap -lBIDAP_IAA -lbdap_lecture -ldmt $(GRIB)"
export BDAP_IAA_FTN=-lBIB $(BDAP_IAA)
export DB_FILE_BDAPARO=/usr/local/sopra/neons_db_bdaparo
export JOURNAL_EXTRACTION_BDAP_ARCHIVE=/tmp/journal_extraction
export DB_FILE_BDAP=/usr/local/sopra/neons_db_bdap
export DB_FILE_BDAPPROD=/usr/local/sopra/neons_db_bdapprod
export DB_FILE_BDAPARP=/usr/local/sopra/neons_db_bdaparp
export DB_PROFIL=/usr/local/sopra/etc/CONF_DB/db_profil
export DB_FILE_BDAPARCH=/usr/local/sopra/neons_db_bdaparch
export DB_FILE_BDEPI=/usr/local/sopra/neons_db_bdepi
export DB_FILE_BDPE=/usr/local/sopra/neons_db_bdpe
export DB_FILE_BDAPARO=/usr/local/sopra/neons_db_bdaparo
export DB_FILE_CDP=/usr/local/sopra/neons_db_cdp
export DB_FILE_BDE=/usr/local/sopra/neons_db_bde
export DB_CONF_PATH=/usr/local/sopra/etc/CONF_DB
export DB_FILE_BDM=/usr/local/sopra/neons_db_bdm
export DB_FILE_BDI=/usr/local/sopra/neons_db_bdi
export DB_FILE_BDAP=/usr/local/sopra/neons_db_bdap
export DB_FILE_BDAPPROD=/usr/local/sopra/neons_db_bdapprod
export DB_NAMES_PG=/usr/local/sopra/etc/pgnames.conf
export DB_FILE_BDCP=/usr/local/sopra/neons_db_bdcp

source /usr/local/sopra/etc/config_taches.soprano-dev
source /opt/metwork-mfext-2.2/share/profile




liste_parametres="PRECIP"
type_niveau="SOL"
niveau=0
modele_BDAP=ANTILOPEJP1
grille_BDAP=FRANXL1S100



##### REQUETE BDAP ######
cat << fin > questionRequeteDap3
#RQST
#NFIC {nomfic}
#MOD $modele_BDAP
#PARAM $liste_parametres
#Z_REF $grille_BDAP
#Z_EXTR GRILLE
#T_LST 60
#D_STP {date_debut} {date_fin} 010000
#L_TYP $type_niveau
#L_LST $niveau
#FORM GRIB2_C_MAX
fin

# Lance de la requete
/usr/local/sopra/bin/dap3_dev_date_ech questionRequeteDap3
#dap3_date_ech questionRequeteDap3
''')
subprocess.run(["scp cmd.ksh auger@sotrtm37-sidev:cmd.ksh"],shell=True)
subprocess.run(["ssh auger@sotrtm37-sidev 'chmod 744 cmd.ksh'"],shell=True)
subprocess.run(["ssh auger@sotrtm37-sidev './cmd.ksh'"],shell=True)
subprocess.run([f"scp auger@sotrtm37-sidev:{nomfic} {nomfic}"],shell=True)
epygram.init_env()

a=epygram.formats.resource(nomfic,'r')


def main():
    # Entrées
    #date1_str = input("Entrez la première date (format YYYYMMDDHH) : ")
    #date2_str = input("Entrez la deuxième date (format YYYYMMDDHH) : ")


    # Boucles imbriquées
    for year in range(date1.year, date2.year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                for hour in range(0, 24):
                    try:
                        current_date = datetime(year, month, day, hour)
                        if date1 <= current_date <= date2:
#                            print(current_date.strftime("%Y-%m-%d %H:00"))
#                            print(current_date.strftime("%Y%m%d%H:00"))
                            fielda=f'parameterNumber:5,year:{current_date.strftime("%Y")},month:{current_date.strftime("%m")},day:{current_date.strftime("%d")},hour:{current_date.strftime("%H")}'
#                            print(fielda)
                            champ=a.readfield(fielda)
                            try:
                              acc_champ.operation('+',champ)
                            except:
                              acc_champ=a.readfield(fielda)
                    except ValueError:
                        # Ignorer les dates invalides (par exemple, 31 février)
                        pass
    nf=epygram.formats.resource(f'antilope_{date1_str}_{date2_str}.grib','w',fmt='GRIB')
    nf.writefield(acc_champ)
    nf.close()


if __name__ == "__main__":
    main()
    subprocess.run(f"epy_cartoplot.py --zoom '{myzoom}' --pm contourf --depts  -f 'parameterNumber:5' -c 'rr24h' -o png -O pluie{date1_str}_{date2_str}.png antilope_{date1_str}_{date2_str}.grib",shell=True)
    subprocess.run(f"rm -f cmd.ksh",shell=True)
    subprocess.run(f"rm -f anti_RR1_FRANXL1S100.grib",shell=True)

#myrep=f'_tmpwork/{randint(1000,9999)}'
#print(myrep)

#print("apres")
#os.system("ssh auger@sotrtm31-sidev 'ls -lrt'")
