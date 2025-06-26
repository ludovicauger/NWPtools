#!/opt/softs/anaconda3/bin/python3
import epygram
epygram.init_env()
a=epygram.formats.resource('pluie_1h_ardeche.grib','r')
b=a.readfield('parameterCategory : 1, parameterNumber : 65')
c=b.as_lists()
lon=c['longitudes']
lat=c['latitudes']
#for i in range(0,2211840):
for i in range(0,2217121):
    print(f'{lon[i]:10.10},{lat[i]:10.10}')
