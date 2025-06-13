#!/opt/softs/anaconda3/bin/python
import epygram
import numpy
epygram.init_env()



def rms(fielda,fieldb):
   return numpy.sqrt(sum(sum((fieldb.data-fielda.data)**2)))

def moyq(fielda):
   return numpy.sqrt(sum(sum((fielda.data)**2)))

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
   field1=extract(f'ICMSHFCST+00{i:02d}.ref',field)
   field2=extract(f'ICMSHFCST+00{i:02d}.ref1',field)
   print(rms(fieldcur,field1))
   print(rms(fieldcur,field2))
   print(moyq(field1))



