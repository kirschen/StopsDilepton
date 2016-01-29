import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
import ROOT

signals_ttbarDM=[]

for d in os.listdir(dataDir):
  if d.startswith('TTbarDMJets'):
    name = d
#    TTbarDMJets_scalar_Mchi10_Mphi10 
    mode, mchistr, mphistr = d.split('_')[-3:]
    mChi=int(mchistr.replace('Mchi',''))
    mPhi=int(mphistr.replace('Mphi',''))
    tmp={\
    "name" : name,
    'dir' : dataDir,
    'isData':False,
    'color': 8,
    'mChi':mChi,
    'mPhi':mPhi,
    'texName':"t#overline{t}+Jets + DM(m_{#chi}="+str(mChi)+",m_{#phi}="+str(mPhi)+")"
    }
    exec("%s=copy.deepcopy(tmp)"%name)
    exec("signals_ttbarDM.append(%s)"%name)

print "Loaded %i ttbarDM signals: %s"%(len(signals_ttbarDM), ",".join([s['name'] for s in signals_ttbarDM]))

