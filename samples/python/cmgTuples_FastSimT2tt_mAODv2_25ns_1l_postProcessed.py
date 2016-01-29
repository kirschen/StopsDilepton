import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
import ROOT
dir = dataDir 

signals_T2tt=[]

for f in os.listdir(os.path.join(dataDir,'T2tt')):
  if f.endswith('.root') and f.startswith('T2tt_'):
    name = f.replace('.root','')
    mStop, mNeu = name.replace('T2tt_','').split('_') 
    tmp={\
    "name" : name,
    "file" : os.path.join(os.path.join(dataDir,'T2tt',f)),
    'dir' : os.path.join(os.path.join(dataDir,'T2tt')),
    'isData':False,
    'color': 8,
    'mStop':int(mStop),
    'mNeu':int(mNeu),
    'texName':"T2tt("+mStop+","+mNeu+")"
    }
    exec("%s=copy.deepcopy(tmp)"%name)
    exec("signals_T2tt.append(%s)"%name)

print "Loaded %i T2tt signals: %s"%(len(signals_T2tt), ",".join([s['name'] for s in signals_T2tt]))

