#Standard import 
import copy, os, sys
import ROOT


#RootTools
from RootTools.core.standard import *

signals_T8bbllnunu_XCha0p5_XSlep0p05    = []
signals_T8bbllnunu_XCha0p5_XSlep0p5     = []

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_80X_v30/dilepTiny"

try:
    import sys
    data_directory = sys.modules['__main__'].data_directory
except:
    #user specific
    import StopsDilepton.tools.user as user
    data_directory = user.data_directory

for f in os.listdir(os.path.join(data_directory, postProcessing_directory, 'T8bbllnunu')):
    if f.endswith('.root') and f.startswith('T8bbllnunu_'):
        name = f.replace('.root','')
        xChaStr, xSlepStr, mStop, mNeu = name.replace('T8bbllnunu_','').split('_')
        
        bcha    = "b#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{#pm}}"
        nuslep  = "#nu#tilde{l}"
        lneu    = "l#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}}"
        ra      = " #rightarrow "
        
        xCha = xChaStr.replace('XCha','').replace('p','.')
        xSlep = xSlepStr.replace('XSlep','').replace('p','.')
        
        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory, postProcessing_directory,'T8bbllnunu',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "#tilde{t} #rightarrow b#nu l#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+","+xCha+","+xSlep+")"
            #texName = "#tilde{t}" + ra + bcha + ra + nuslep + ra + lneu + "("+mStop+","+mNeu+","+xCha+","+xSlep+")"
        )

        tmp.mStop   = int(mStop)
        tmp.mNeu    = int(mNeu)
        tmp.xCha    = float(xCha)
        tmp.xSlep   = float(xSlep)
        tmp.mCha    = int( tmp.xCha * ( tmp.mStop - tmp.mNeu ) + tmp.mNeu )
        tmp.mSlep   = int( tmp.xSlep * ( tmp.mCha - tmp.mNeu ) + tmp.mNeu )
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        if f.startswith('T8bbllnunu_XCha0p5_XSlep0p05'):
            exec("signals_T8bbllnunu_XCha0p5_XSlep0p05.append(%s)"%name)
        elif f.startswith('T8bbllnunu_XCha0p5_XSlep0p5'):
            exec("signals_T8bbllnunu_XCha0p5_XSlep0p5.append(%s)"%name)

print "Loaded %i T8bbllnunu signals: %s"%(len(signals_T8bbllnunu_XCha0p5_XSlep0p05)+len(signals_T8bbllnunu_XCha0p5_XSlep0p5), ",".join([s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05+signals_T8bbllnunu_XCha0p5_XSlep0p5]))
