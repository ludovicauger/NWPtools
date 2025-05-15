#!/opt/softs/anaconda3/bin/python3
import glob
import pdb
import sys

target_string = 'TYPE DIAG_t'
lalloc=True

# itereate over files


if lalloc : print('SUBROUTINE ALLOCATE_SURFEX_T(YSC,RHSYSC)')
if not lalloc : print('SUBROUTINE COPY_SURFEX_T(YSC,RHSYSC,EXYSC)')
print('USE MODD_SURFEX_N, ONLY : SURFEX_t')  
print('IMPLICIT NONE')
if lalloc:
  print('TYPE(SURFEX_t),INTENT(INOUT) :: YSC,RHSYSC')
else:
  print('TYPE(SURFEX_t),INTENT(INOUT) :: YSC,RHSYSC,EXYSC')
print('INTEGER(8) :: JIZZ')

      

def dimension(line):
    #a=line.split()  
    #for i in range(0,len(a)):
    #  if a[i][0:9]=='DIMENSION':
    #       print(a[i].count(':'))
    a=line.split('!')[0]
    if a.count('(:)')>0 or a.count('(:,:)')>0 or a.count('(:,:,:)'):
       return a[a.find('(:'):a.find(':)')+2]
    else: 
       return ''
def gettype(line):
    a=line.split()  
    if len(a)>0 and a[0][0:5]=='TYPE(' :
       s=a[0]
    if len(a)>1 and a[0][0:4]=='TYPE' and a[1][0:1]=='(':
       s=a[1]
    return s[s.find("(")+1:s.find(")")]
def istype(line):
    a=line.split()  
    test=False
    if len(a)>0 and a[0][0:5]=='TYPE(' :
       test= True
    if len(a)>1 and a[0][0:4]=='TYPE' and a[1][0:1]=='(':
       test= True
    return test
def isnewtype(line,newtype):
    a=line.split()  
    if len(a)>1 and a[0]=='TYPE' and a[1]==newtype :
       return True
    else :
       return False
def endtype(line):
    a=line.split()  
    test=False
    if len(a) > 1 and a[0]=='END' and a[1]=='TYPE' :
       test= True
    if len(a) > 0 and a[0]=='ENDTYPE' :
       test= True
    return test
def returnvar(mypath,line):
    line=line.rstrip()
 #   a=line.split()  
 #   for i in range(0,len(a)-1) :
 #      if a[i]=='::' : 
 #        s=a[i+1]
 #        if s.count('=')>0:
 #         return(mypath+'%'+s[0:s.find('=')])
 #        else:
 #         return(mypath+'%'+s)
    a=line.split('::')  
#    if len(a)>1 :
#      s=a[1].split('!')[0].split(',')
#      return [mypath+'%'+s[i].split()[0].split('=')[0].split('!')[0].split('(')[0] for i in range(0,len(s)) ] 
    try :
      s=a[1].split('!')[0].split(',')
      return [mypath+'%'+s[i].split()[0].split('=')[0].split('!')[0].split('(')[0] for i in range(0,len(s)) ] 
    except IndexError:
     sys.exit()
lread=False
def printtype(mypath,mytype):
    if mytype=='PRONOSVAR_T':
       #print(returnvar(mypath,line)+'%NEXT'+"=RHS"+returnvar(mypath,line))
       if not lalloc : print(mypath+'%NEXT=RHS'+mypath)
       return
    files = glob.glob('/home/gmap/mrpa/auger/pack/cy48t1_op1_dyn.v2.hydro/src/main/surfex/SURFEX/*F90', recursive=True)
    lread=False
#    print("search",mytype)
    for file in files:
     # print(file,mypath,mytype)
      try:
          # open file for reading
          with open(file, 'r') as f:
               lines=f.readlines()
               for line in lines:
                   if isnewtype(line,mytype):
                      lread=True
                   if endtype(line):
                      lread = False
                   if lread :
                      if istype(line) :
                            q=returnvar(mypath,line)
                            for i in range(0,len(q)):
                               if dimension(line)=='(:)' and not mypath.count('JIZZ') :
                                   print('IF (ASSOCIATED(RHS'+q[i]+')) THEN')
                                   if lalloc : print('ALLOCATE('+q[i]+'(SIZE(RHS'+q[i]+',1)))')
                                   if lalloc : 
                                       print('DO JIZZ=1,SIZE(RHS'+q[i]+',1)') 
                                   else:
                                       print('DO JIZZ=1,SIZE(EX'+q[i]+',1)') 
                                   printtype('    '+returnvar(mypath,line)[i]+'(JIZZ)',gettype(line))
                                   print('END DO') 
                                   print('END IF') 
                               else: 
                                   printtype(returnvar(mypath,line)[i]+dimension(line),gettype(line))
                      else :
                        if line.count('::')>0 :
                            #print(returnvar(mypath,line)+"=RHS"+returnvar(mypath,line))
                            q=returnvar(mypath,line)
                            for i in range(0,len(q)):
                               if dimension(line)=='(:)' and lalloc:
                                  sini='    ' if mypath.count(' ')>1 else ''
                                  stripmypath=mypath.strip()
                                  print(sini+'IF (ASSOCIATED(RHS'+returnvar(stripmypath,line)[i]+')) ALLOCATE('+returnvar(stripmypath,line)[i]+'(SIZE(RHS'+returnvar(stripmypath,line)[i]+',1)))')
                               if dimension(line)=='(:,:)' and lalloc:
                                  sini='    ' if mypath.count(' ')>1 else ''
                                  stripmypath=mypath.strip()
                                  print(sini+'IF (ASSOCIATED(RHS'+returnvar(stripmypath,line)[i]+')) ALLOCATE('+returnvar(stripmypath,line)[i]+'(SIZE(RHS'+returnvar(stripmypath,line)[i]+',1),SIZE(RHS'+returnvar(stripmypath,line)[i]+',2)))')
                               if dimension(line)=='(:,:,:)' and lalloc:
                                  sini='    ' if mypath.count(' ')>1 else ''
                                  stripmypath=mypath.strip()
                                  print(sini+'IF (ASSOCIATED(RHS'+returnvar(stripmypath,line)[i]+')) ALLOCATE('+returnvar(stripmypath,line)[i]+'(SIZE(RHS'+returnvar(stripmypath,line)[i]+',1),SIZE(RHS'+returnvar(stripmypath,line)[i]+',2),SIZE(RHS'+returnvar(stripmypath,line)[i]+',3)))')
                               if not lalloc : 
                                  sini='    ' if mypath.count(' ')>1 else ''
                                  stripmypath=mypath.strip()
                                  if dimension(line)=='(:)' or  dimension(line)=='(:,:)' or  dimension(line)=='(:,:,:)':
                                        print(sini+'IF ((ASSOCIATED(EX'+returnvar(stripmypath,line)[i]+')) .AND. (SIZE(EX'+returnvar(stripmypath,line)[i]+')>0)) '+returnvar(stripmypath,line)[i]+dimension(line)+'=RHS'+returnvar(stripmypath,line)[i]+dimension(line))
                                  else:
                                        print(sini+returnvar(stripmypath,line)[i]+dimension(line)+'=RHS'+returnvar(stripmypath,line)[i]+dimension(line))

                            #print(dimension(line))
      except:
          pass

printtype('YSC','SURFEX_t')
#printtype('YSC','CH_EMIS_FIELD_t')
if lalloc : print('END SUBROUTINE ALLOCATE_SURFEX_T')
if not lalloc  : print('END SUBROUTINE COPY_SURFEX_T')
#printtype('YSC','DATE_TIME')
