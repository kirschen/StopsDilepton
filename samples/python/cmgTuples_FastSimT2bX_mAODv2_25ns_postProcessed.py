#Standard import 
import copy, os, sys
import ROOT


#RootTools
from RootTools.core.standard import *

signals_T2bW=[]
signals_T2bt=[]


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

#for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T2tt')):
for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T2bW')):
    if f.endswith('.root') and f.startswith('T2bW_'):
        name = f.replace('.root','')
        mStop, mNeu = name.replace('T2bW_','').split('_')

        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory, postProcessing_directory,'T2bW',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "#tilde{t} #rightarrow bW#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+")"
        )

        tmp.mStop = int(mStop)
        tmp.mNeu = int(mNeu)
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        exec("signals_T2bW.append(%s)"%name)

print "Loaded %i T2bW signals: %s"%(len(signals_T2bW), ",".join([s.name for s in signals_T2bW]))


for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T2bt')):
    if f.endswith('.root') and f.startswith('T2bt_'):
        name = f.replace('.root','')
        mStop, mNeu = name.replace('T2bt_','').split('_')

        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory, postProcessing_directory,'T2bt',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "#tilde{t} #rightarrow bW#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}}, #tilde{t} #rightarrow t#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+")"
        )

        tmp.mStop = int(mStop)
        tmp.mNeu = int(mNeu)
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        exec("signals_T2bt.append(%s)"%name)

print "Loaded %i T2bt signals: %s"%(len(signals_T2bt), ",".join([s.name for s in signals_T2bt]))

