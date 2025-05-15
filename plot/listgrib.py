#!/opt/softs/anaconda3/bin/python3
import subprocess
import sys
import re 



myargs=sys.argv
if '-h' in myargs:
   print('usage listgrib <grib_file>')
print(myargs)
subprocess.run("module load eccodes; grib_dump -O "+sys.argv[1]+" > _out.txt",shell=True)
file_cmd=open('plotcmd.txt','w')
file_cmd.write("#options --depts  -c 'rr6h' --zoom 'latmin=41,latmax=45,lonmin=0,lonmax=5'\n")
file_cmd.write("#options --depts  -c 'jet' --zoom 'latmin=41,latmax=45,lonmin=0,lonmax=5'\n")
editionNumber=1
with open('_out.txt','r') as f:
    for line in f:
     if 'editionNumber = 2' in line :
         editionNumber=2
     if editionNumber == 1:
        if 'indicatorOfParameter' in line :
            outline=f"'indicatorOfParameter : {line.split()[3]}"
            comment=f" {' '.join(line.split()[4:])}"
        if 'indicatorOfTypeOfLevel' in line :
            outline+=f", indicatorOfTypeOfLevel : {line.split()[3]}"
            comment+=f" {' '.join(line.split()[4:])}"
        if 'level' in line :
            outline+=f", level : {line.split()[3]}'"
            comment=re.sub("\(.*\)","",comment)
            file_cmd.write(outline+' | '+comment+'\n')
     if editionNumber == 2:
        if 'parameterCategory' in line :
            outline=f"'parameterCategory : {line.split()[3]}"
#            comment=f" {' '.join(line.split()[4:])}"
        if 'parameterNumber' in line :
            outline+=f", parameterNumber : {line.split()[3]}"
            comment=f" {' '.join(line.split()[4:])}"
        if 'typeOfFirstFixedSurface' in line :
            outline+=f", typeOfFirstFixedSurface : {line.split()[3]}"
        if 'scaledValueOfFirstFixedSurface' in line :
            outline+=f", scaledValueOfFirstFixedSurface : {line.split()[3]}'"
            comment=re.sub("\(.*\)","",comment)
            file_cmd.write(outline+' | '+comment+'\n')

subprocess.run("rm -f _out.txt",shell=True)
