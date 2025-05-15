#!/opt/softs/anaconda3/bin/python3
import subprocess
import sys
import re

#usage
# plotlist <fichier.grib> <list_from_listgrib>


myargs=sys.argv
if '-h' in myargs:
  print('plotlist <fichier.grib> <list_from_listgrib>\n')
print(myargs)
#subprocess.run("module load eccodes; grib_dump -O "+sys.argv[1]+" > _out.txt",shell=True)
#file_cmd=open('plotcmd.txt','w')
file_name=sys.argv[1]
prefix='module load eccodes4epygram/2.38.0;/home/gmap/mrpe/mary/public/EPyGrAM/1.4.20-ecc2.38.0/apptools/epy_cartoplot.py   -f'
editionNumber=1
myopts=''
with open(sys.argv[2],'r') as f:
    for line in f:
     if line[0] != "#":
      if 'option' in line:
         myopts=' '+line[:-1].replace('options','').replace('option','')+' '
      if 'parameterCategory' in line:
         field=line.split('|')[0]
         fieldname=line.split('|')[1].replace(" ","").replace("'","").replace("(grib2/tables/15/4.1.0.table)","").replace("(2octets)","").replace("(grib2/tables/15/4.2.0.2.table)","").replace("(","").replace(")","").replace("/","")[:-1]
         fieldname = re.sub("\(.*\)","",fieldname)
         print(field)
         fieldsplit=re.split(',| ',field)
         print(fieldsplit)
         level=fieldsplit[fieldsplit.index('scaledValueOfFirstFixedSurface')+2].replace("'","")
         #subprocess.run(prefix+' '+line.split('|')[0]+' -O '+file_name+f'l{level}'+fieldname+'.png '+file_name,shell=True)
         print(fieldname)
         print(prefix+' '+line.split('|')[0]+myopts+' -O '+file_name+f'l{level}'+fieldname+'.png '+file_name)
         subprocess.run(prefix+' '+line.split('|')[0]+myopts+' -O '+file_name+f'l{level}'+fieldname+'.png '+file_name,shell=True)
      if 'indicatorOfParameter' in line:
         field=line.split('|')[0]
         fieldname=line.split('|')[1].replace(" ","").replace("'","").replace("(grib1/2.0.1.table)","").replace("(2octets)","").replace("(grib1/3.table)","").replace("/","")[:-1]
         fieldname = re.sub("\(.*\)","",fieldname)
         print(field)
         fieldsplit=re.split(',| ',field)
         print(fieldsplit)
         level=fieldsplit[fieldsplit.index('level')+2].replace("'","")
         #subprocess.run(prefix+' '+line.split('|')[0]+' -O '+file_name+f'l{level}'+fieldname+'.png '+file_name,shell=True)
         print(fieldname)
         subprocess.run(prefix+' '+line.split('|')[0]+myopts+' -O '+file_name+f'l{level}'+fieldname+'.png '+file_name,shell=True)
      

      
