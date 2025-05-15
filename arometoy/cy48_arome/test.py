#!/opt/softs/python/2.7.5/bin/python
import epygram
from matplotlib import pyplot as plt
fic1='ICMSHFCST+0015'

def pdiff(field,fic2):
 epygram.init_env()
 a=epygram.formats.resource(fic1,'r')
 ca=a.readfield(field)
 b=epygram.formats.resource(fic2,'r')
 cb=b.readfield(field)
 ca.operation('-',cb)
 ca.sp2gp()
 c=ca.getdata()
 print('comparaison to '+fic2)
 print('max min difference '+field)
 d=abs(c)
 msum=0.
 mmax=0.
 for i in range(20,40):
   for j in range(20,40):
     msum=msum+d[i][j]
     if mmax < d[i][j]:
         mmax=d[i][j]
 print(msum/20.0/20.0)
 print(mmax)
#ca.plotfield()
#plt.savefig('out.pdf',dpi=150)
pdiff('S080WIND.U.PHYS','ICMSHFCST+0015_spec2trans')
pdiff('S080TEMPERATURE','ICMSHFCST+0015_spec2trans')
pdiff('S080WIND.U.PHYS','ICMSHFCST+0015.ini.pdg')
pdiff('S080TEMPERATURE','ICMSHFCST+0015.ini.pdg')
pdiff('S080WIND.U.PHYS','ICMSHFCST+0015.SIGAMPDG')
pdiff('S080TEMPERATURE','ICMSHFCST+0015.SIGAMPDG')
pdiff('S080WIND.U.PHYS','ICMSHFCST+0015.PDGNOTOR')
pdiff('S080TEMPERATURE','ICMSHFCST+0015.PDGNOTOR')
pdiff('S080TEMPERATURE','ICMSHFCST+0015.NEWSP2PDG')
