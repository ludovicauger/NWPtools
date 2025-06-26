#!/bin/bash
dat=2025051900
ech=45
yyyy=${dat:0:4}
mm=${dat:4:2}
dd=${dat:6:2}
hh=${dat:8:2}

module load intel
module unload eccodes
#module load eccodes4epygram/2.38.0
module load eccodes4epygram
ulimit -s unlimited


zoom='lonmin=3,lonmax=8,latmin=42,latmax=45'






get_arome_oper.sh $dat $ech
get_arome_ifs.sh $dat $ech
antilope.py 2025051900 2025052024 $zoom
set -x
#epy_cartoplot.py --zoom  ${zoom}  --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs$dat.png aromeifs$dat$ech.fa
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/alaroCY48t3_ALARO_nwp_FRA_20250519_20250519/archive/2025/05/19/00/ICMSHDEOD+0045h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0045h00m00s .
#add_prec_gec_con.py ICMSHDEOD+0045h00m00s
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFPREC.EAU.GEC -c 'rr24h' -o png -O deodecy48alaro$dat.png ICMSHDEOD+0045h00m00s 
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/CY48t3_AROME_nwp_FRA_20250519_20250519/archive/2025/05/19/00/ICMSHDEOD+0045h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0045h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodecy48arome$dat.png ICMSHDEOD+0045h00m00s 
#	
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/har_aromeCY49t2_HARMONIE_AROME_nwp_FRA_20250519_20250519/archive/2025/05/19/00/ICMSHDEOD+0045h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0045h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodecy49har_arome$dat.png ICMSHDEOD+0045h00m00s 
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/CY49t2_AROME_nwp_FRA_20250519_20250519/archive/2025/05/19/00/ICMSHDEOD+0045h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0045h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodecy49arome$dat.png ICMSHDEOD+0045h00m00s 
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/rm6/deode/CY49t2_ALARO_nwp_FRA_20250519_20250519/archive/2025/05/19/00/ICMSHDEOD+0045h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0045h00m00s .
#add_prec_gec_con.py ICMSHDEOD+0045h00m00s 
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFPREC.EAU.GEC -c 'rr24h' -o png -O deodecy49alaro$dat.png ICMSHDEOD+0045h00m00s 


generate_html cas20mai2025 cas20mai2025

#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/aut6432/DE_NWP/deode/2025/05/19/00/convection/4/AROME_500m/ICMSHDEOD+0047h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0047h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodeoper$dat.png ICMSHDEOD+0047h00m00s
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/fra6312/deode/FRA_20250520_flood_1_csc_lt1_bis/archive/2025/05/20/00/ICMSHDEOD+0047h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0047h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodebis20$dat.png ICMSHDEOD+0047h00m00s
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/fra6312/deode/FRA_20250520_flood_1_csc_lt1_centered_bis/archive/2025/05/20/00/ICMSHDEOD+0047h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0047h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodecentered20$dat.png ICMSHDEOD+0047h00m00s
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/fra6312/deode/FRA_20250519_flood_1_csc_lt1_verif_bis/archive/2025/05/19/00/ICMSHDEOD+0047h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0047h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodebisverif19$dat.png ICMSHDEOD+0047h00m00s
#
#ssh rm6@hpc-login 'cd /scratch/rm6/plot;rm /scratch/rm6/plot/* ;ecp ec:/fra6312/deode/FRA_20250519_flood_1_csc_lt1_centered_bis/archive/2025/05/19/00/ICMSHDEOD+0047h00m00s .'
#scp rm6@hpc-login:/scratch/rm6/plot/ICMSHDEOD+0047h00m00s .
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O deodecentered19$dat.png ICMSHDEOD+0047h00m00s
#
#dat=2025051903
#ech=45
#get_arome_oper.sh $dat $ech
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
#dat=2025051906
#ech=42
#get_arome_oper.sh $dat $ech
#get_arome_ifs.sh $dat $ech
#epy_cartoplot.py --zoom $zoom  --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs$dat.png aromeifs$dat$ech.fa
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
#
#
#dat=2025052000
#ech=24
#get_arome_oper.sh $dat $ech
#get_arome_ifs.sh $dat $ech
#epy_cartoplot.py --zoom $zoom  --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeifs$dat.png aromeifs$dat$ech.fa
#epy_cartoplot.py --zoom $zoom --pm contourf --depts  -f SURFACCPLUIE -c 'rr24h' -o png -O aromeoper$dat.png aromeoper$dat$ech.fa
#
#generate_html cas20mai2025 cas20mai2025




