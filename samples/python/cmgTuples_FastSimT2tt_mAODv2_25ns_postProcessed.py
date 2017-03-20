#Standard import 
import copy, os, sys
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

#RootTools
from RootTools.core.standard import *

signals_T2tt=[]

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_80X_v35/dilepTiny"

try:
    import sys
    data_directory = sys.modules['__main__'].data_directory
except:
    #user specific
    import StopsDilepton.tools.user as user
    data_directory = user.data_directory

logger.info("Loading T2tt samples from directory %s", os.path.join(data_directory, postProcessing_directory))

#for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T2tt')):
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
            texName = "#tilde{t} #rightarrow t#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+")"
        )

        tmp.mStop = int(mStop)
        tmp.mNeu = int(mNeu)
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        exec("signals_T2tt.append(%s)"%name)

logger.info("Loaded %i T2tt signals", len(signals_T2tt))
logger.debug("Loaded T2tt signals: %s", ",".join([s.name for s in signals_T2tt]))

