#!/opt/softs/anaconda3/bin/python
import epygram
epygram.init_env()



def rms(fielda,fieldb):
   return sum(sum((fieldb.data-fielda.data)**2))


def extract(file,field):
  a=epygram.formats.resource(file,'r')
  fielda=a.readfield(field)
  fielda.sp2gp()
  return fielda



#a=epygram.formats.resource('ICMSHFCST+0001_hydro','r')
#b=epygram.formats.resource('ICMSHFCST+0001_nh','r')
#field='S060TEMPERATURE'
#fielda=a.readfield(field)
#fielda.sp2gp()
#fieldb=b.readfield(field)
#fieldb.sp2gp()
#field='S090TEMPERATURE'
field='S080WIND.U.PHYS'
for i in range(1,16):
   print(f'{i:02d}')
   fieldcur=extract(f'ICMSHFCST+00{i:02d}',field)
   j=i+1
   #fieldcurp1=extract(f'ICMSHFCST+00{j:02d}',field)
   j=i-1
   #fieldcurm1=extract(f'ICMSHFCST+00{j:02d}',field)
   fieldh1=extract(f'ICMSHFCST+00{i:02d}.h1',field)
   fieldh0=extract(f'ICMSHFCST+00{i:02d}.h0',field)
   fieldnh1=extract(f'ICMSHFCST+00{i:02d}.nh1',field)
   fieldnh0=extract(f'ICMSHFCST+00{i:02d}.nh0',field)
   print(rms(fieldh0,fieldh1))
   print(rms(fieldnh0,fieldnh1))
   print(rms(fieldh0,fieldnh0))
   print(rms(fieldh1,fieldnh1))
   print(rms(fieldcur,fieldh1))
   #print(rms(fieldcurp1,fieldh1))
   #print(rms(fieldcurm1,fieldh1))
   print(rms(fieldcur,fieldnh1))



