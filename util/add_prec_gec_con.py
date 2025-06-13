#!/opt/softs/anaconda3/bin/python3
import epygram
import sys

nbarg=len(sys.argv)                                                                                                                                                                           

if (nbarg==2) and (sys.argv[1] == '-h'):
   print("add_prec_gec_con.py accumulate SURFPREC.EAU.GEC and SURFPREC.EAU.CON into SURFPREC.EAU.GEC")
   print("usage : add_prec_gec_con.py <file.fa>")
   exit()

epygram.init_env()
a=epygram.formats.resource(sys.argv[1],'a')
b=a.readfield('SURFPREC.EAU.GEC')
d=a.readfield('SURFPREC.EAU.CON')
#b.operation_with_other('+',d)
b.operation('+',d)
a.writefield(b)
a.close()
#aa=epygram.formats.resource('FILEM.fa','a')
#bb=aa.readfield('SURFPREC.EAU.GEC')
#dd=aa.readfield('SURFPREC.EAU.CON')
##bb.operation_with_other('+',dd)
#bb.operation('+',dd)
#aa.writefield(bb)
#aa.close()
