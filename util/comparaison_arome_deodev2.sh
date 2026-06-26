#!/usr/bin/bash
latmin=42
latmax=45
lonmin=2
lonmax=5
process() {
dat=$1;event=$2;ref=$3
latmin=$4;latmax=$5;lonmin=$6,lonmax=$7
datp1=$(date -d "${dat} +1 day" +"%Y%m%d")
echo $datp1
#rm -f ICMSHDEOD*
rm -f historic*
ssh sotrtm37-sidev "/home/mrpa/auger/EXTRACT_BD/lance_antilope.sh ${datp1}"
/scratch/work/auger/NWPtools/util/plot_antilope_24h.sh ${datp1} $lonmin $lonmax $latmin $latmax
/home/gmap/mrpa/auger/bin/lgetmf
mv pluie${datp1}.png ${datp1}pluie.png
ssh hpc-login "/home/rm6/dev/get_deode.sh ${dat} $event $ref"
/home/gmap/mrpa/auger/bin/lgetec
module load intel
module load eccodes
module load python/3.12.12
module load epygram
epy_cartoplot.py --title "" --difftitle "" --pm contourf --depts  -D ICMSHDEOD+0024h00m00s -f SURFACCPLUIE -C 'rr24h' --zoom "lonmin=$lonmin, lonmax=$lonmax, latmin=$latmin, latmax=$latmax" -o png -O deode.png ICMSHDEOD+0048h00m00s
mv diff* ${datp1}deode.png
mv ICMSHDEOD+0048h00m00s ICMSHDEOD+0048h00m00s${dat}
mv ICMSHDEOD+0024h00m00s ICMSHDEOD+0024h00m00s${dat}
ftp hendrix.meteo.Fr<<EOF
cd /home/m/mxpt/mxpt001/vortex/arome/3dvarfr/OPER/${dat:0:4}/${dat:4:2}/${dat:6:2}/T1200P/forecast
get historic.arome.franmg-01km30+0036:00.fa
get historic.arome.franmg-01km30+0012:00.fa
EOF
epy_cartoplot.py --title "" --difftitle "" --pm contourf --depts  --zoom "lonmin=$lonmin, lonmax=$lonmax, latmin=$latmin, latmax=$latmax" -D 'historic.arome.franmg-01km30+0012:00.fa' -f SURFACCPLUIE -C 'rr24h' -o png -O arome.png 'historic.arome.franmg-01km30+0036:00.fa'
mv diff* ${datp1}arome.png
}

#process 20260108 flooding u0cwwq 48 52 -2 7 
#process 20260116 flooding gbtggt 45.5 51 -6 2 # 0
#process 20251217 flooding gbt3uu 46 50 -6 0 # + / bonne localisation dans les 2 cas mais meilleurs maximas pour deode
#dat=20260218;event=flooding;ref=gbxdwn;process
process 20260217 flooding u086sy 46 51 -2 5 # 0
process 20260216 flooding gbq698 43 50 5 2 # + / légère meilleur localisation
process 20260212 flooding u00r3s 43 49 -2 5 # + / pluie peu intense deode ameliore un peut la localisation
process 20260214 flooding u01jn7 43 49 -2 5 # - / bonne localisatin mais un peu trop intense
process 20260411 flooding u04qxy 43 49 0 7 # 0 
#dat=20250827;event=flooding;ref=u0hmuu;process
#dat=20260211;event=flooding;ref=u0hz3x;process # 0
#dat=20260210;event=flooding;ref=u01gkz;process #- / bonne localisation masi trop intense
#dat=20260218;event=flooding;ref=u0h73x;process
#dat=20250826;event=flooding;ref=u013zu;process
#dat=20250831;event=flooding;ref=spgr3w;process
#dat=20260115;event=flooding;ref=spfvcs;process # 0
#dat=20260209;event=flooding;ref=spbkrc;process # 0
#dat=20260220;event=flooding;ref=spbkku;process # 0 
#dat=20251105;event=flooding;ref=spc9yk;process
#dat=20260308;event=flooding;ref=spdzsb;process # + / meilleur localisation et meilleur maximum (cas vigilance)
#dat=20251219;event=flooding;ref=spf2kc;process # - / bonne localisation mais trop intense
#dat=20260117;event=flooding;ref=spdxw2;process # - / bonne localisation mas trop intense
#dat=20260219;event=flooding;ref=sp8qsy;process
#dat=20260118;event=flooding;ref=spdmuu;process # - / moins bien localisé dans le departement a côte, (mais maximum un tout petit peut plus proche)
