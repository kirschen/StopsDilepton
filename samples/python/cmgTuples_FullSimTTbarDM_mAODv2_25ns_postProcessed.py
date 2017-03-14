#Standard import 
import copy, os, sys
import ROOT

#user specific
from StopsDilepton.tools.user import data_directory

#RootTools
from RootTools.core.standard import *

signals_TTbarDM = []

# Data directory
try:
    data_directory = sys.modules['__main__'].data_directory
except:
    from StopsDilepton.tools.user import data_directory as user_data_directory
    data_directory = user_data_directory 

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_80X_v35/dilepTiny"

for f in os.listdir(os.path.join(data_directory, postProcessing_directory)):
    if f.startswith('TTbarDMJets_'):
        s = f.split('_')
        if s[1] == 'pseudoscalar':
            tp_ = "PS"
        elif s[1] == 'scalar':
            tp_ = "S"

        mChi = int(s[3])
        mPhi = int(s[5])

        tmp = Sample.fromDirectory(\
            name = f,
            directory = [os.path.join(os.path.join(data_directory,postProcessing_directory,f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "%s(m_{#chi}=%i, m_{#phi}=%i)"%(tp_, mChi, mPhi)
        )
        tmp.mChi = mChi
        tmp.mPhi = mPhi
        tmp.type = tp_

        exec("%s=tmp"%f)
        exec("signals_TTbarDM.append(%s)"%f)

print "Loaded %i TTDM signals: %s"%(len(signals_TTbarDM), ",".join([s.name for s in signals_TTbarDM]))
