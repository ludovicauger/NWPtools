#!/usr/bin/bash
dat=$1
yyyy=${dat:0:4}
mm=${dat:4:2}
dd=${dat:6:2}
hh=${dat:8:2}
ech=$2
ftp hendrix.meteo.fr<<EOF
cd /home/m/mxpt/mxpt001/vortex/arome/3dvarfr/OPER/$yyyy/$mm/$dd/T${hh}00P/forecast
get historic.arome.franmg-01km30+00${ech}:00.fa aromeoper$yyyy$mm$dd${hh}${ech}.fa
get grid.arome-forecast.eurw1s40+00${ech}:00.grib aromeoper$yyyy$mm$dd${hh}${ech}1s40.grib
get grid.arome-forecast.eurw1s100+00${ech}:00.grib aromeoper$yyyy$mm$dd${hh}${ech}1s100.grib
EOF

