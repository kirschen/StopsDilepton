#Standard import 
import copy, os, sys
import ROOT

#user specific
from StopsDilepton.tools.user import data_directory

#RootTools
from RootTools.core.standard import *

signals_T2tt=[]

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny"

for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T2tt')):
    if f.endswith('.root') and f.startswith('T2tt_'):
        name = f.replace('.root','')
        mStop, mNeu = name.replace('T2tt_','').split('_')

        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory, postProcessing_directory,'T2tt',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "T2tt("+mStop+","+mNeu+")"
        )
        tmp.mStop = int(mStop)
        tmp.mNeu = int(mNeu)

        exec("%s=tmp"%name)
        exec("signals_T2tt.append(%s)"%name)

print "Loaded %i T2tt signals: %s"%(len(signals_T2tt), ",".join([s.name for s in signals_T2tt]))
