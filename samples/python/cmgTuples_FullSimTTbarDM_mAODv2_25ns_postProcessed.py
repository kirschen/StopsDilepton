#Standard import 
import copy, os, sys
import ROOT

#user specific
from StopsDilepton.tools.user import data_directory

#RootTools
from RootTools.core.standard import *

signals_TTDM=[]

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny"

for f in os.listdir(os.path.join(data_directory, postProcessing_directory)):
    if f.startswith('TTbarDMJets_'):
        s = f.split('_')
        type = s[1]
        mChi = int(s[2].replace('Mchi',''))
        mPhi = int(s[3].replace('Mphi',''))

        tmp = Sample.fromDirectory(\
            name = f,
            directory = [os.path.join(os.path.join(data_directory,postProcessing_directory,f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "%s(m_{#chi}=%i, m_{#phi}=%i)"%(type, mChi, mPhi)
        )
        tmp.mChi = mChi
        tmp.mPhi = mPhi
        tmp.type = type

        exec("%s=tmp"%f)
        exec("signals_TTDM.append(%s)"%f)

print "Loaded %i TTDM signals: %s"%(len(signals_TTDM), ",".join([s.name for s in signals_TTDM]))
