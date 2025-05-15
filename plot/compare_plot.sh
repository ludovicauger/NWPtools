#!/usr/bin/bash
ulimit -s unlimited

XPAROME1=H04I
XPAROMEREF=H04U
XPNAME=LSI_NHEE

get_arome () {
ftp hendrix.meteo.fr<<EOF
cd vortex/arome/3dvarfr/$1/20241127T0000P/forecast/
get historic.arome.franmg-01km30+0036:00.fa
EOF
mv historic.arome.franmg-01km30+0036:00.fa $2.fa
}


rm *png

get_arome $XPAROME1 XP
get_arome $XPAROMEREF ref 
ficref=ref.fa
fic=XP.fa
for FIELD in S030TEMPERATURE S030WIND.U.PHYS S060TEMPERATURE S060WIND.U.PHYS S090TEMPERATURE S090WIND.U.PHYS SURFTEMPERATURE 'TOPRAYT DIR SOM' ATMONEBUL.CONVEC ATMONEBUL.HAUTE ATMONEBUL.MOYENN ATMONEBUL.BASSE;do
#for FIELD in SURFTEMPERATURE;do
epy_cartoplot.py -F $FIELD  $fic -O ${FIELD}.png
epy_cartoplot.py -F $FIELD  $ficref -O ${FIELD}ref.png
epy_cartoplot.py -F $FIELD -D $ficref $fic -O ${FIELD}diff.png
mv diff*png ${FIELD}zdiff.png
done
./plot/generate_html.py $XPNAME $XPNAME
