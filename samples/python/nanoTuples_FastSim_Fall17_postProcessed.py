#Standard import 
import copy, os, sys
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

#RootTools
from RootTools.core.standard import *

signals_T2tt=[]
signals_T2bW=[]
signals_T8bbllnunu_XCha0p5_XSlep0p05 = []
signals_T8bbllnunu_XCha0p5_XSlep0p09 = []
signals_T8bbllnunu_XCha0p5_XSlep0p5  = []
signals_T8bbllnunu_XCha0p5_XSlep0p95 = []
signals_T8bbstausnu_XCha0p5_XStau0p5 = []
# Data directory
#try:
#    data_directory_ = sys.modules['__main__'].data_directory
#except:
#    from StopsDilepton.samples.default_locations import default_locations
#    data_directory_ = default_locations.mc_2017_data_directory 
#
## Take post processing directory if defined in main module
#try:
#  import sys
#  postProcessing_directory_ = sys.modules['__main__'].postProcessing_directory
#except:
#  from StopsDilepton.samples.default_locations import default_locations
#  postProcessing_directory_ = default_locations.mc_2017_postProcessing_directory 
data_directory_              = '/afs/hephy.at/data/cms05/nanoTuples/'
postProcessing_directory_    = 'stops_2017_nano_v0p16/dilep/'


logger.info("Loading Signal samples from directory %s", os.path.join(data_directory_, postProcessing_directory_))

for f in os.listdir(os.path.join(data_directory_, postProcessing_directory_, 'T2tt')):
    if f.endswith('.root') and f.startswith('T2tt_'):
        name = f.replace('.root','')
        mStop, mNeu = name.replace('T2tt_','').split('_')

        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory_, postProcessing_directory_,'T2tt',f))],
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

for f in os.listdir(os.path.join(data_directory_, postProcessing_directory_, 'T2bW')):
    if f.endswith('.root') and f.startswith('T2bW_'):
        name = f.replace('.root','')
        mStop, mNeu = name.replace('T2bW_','').split('_')

        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory_, postProcessing_directory_,'T2bW',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "#tilde{t} #rightarrow t#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+")"
        )

        tmp.mStop = int(mStop)
        tmp.mNeu = int(mNeu)
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        exec("signals_T2bW.append(%s)"%name)

logger.info("Loaded %i T2bW signals", len(signals_T2bW))
logger.debug("Loaded T2bW signals: %s", ",".join([s.name for s in signals_T2bW]))


for f in os.listdir(os.path.join(data_directory_, postProcessing_directory_, 'T8bbllnunu')):

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
            files = [os.path.join(os.path.join(data_directory_, postProcessing_directory_,'T8bbllnunu',f))],
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
        elif f.startswith('T8bbllnunu_XCha0p5_XSlep0p95'):
            exec("signals_T8bbllnunu_XCha0p5_XSlep0p95.append(%s)"%name)
        elif f.startswith('T8bbllnunu_XCha0p5_XSlep0p09'):
            exec("signals_T8bbllnunu_XCha0p5_XSlep0p09.append(%s)"%name)
        
logger.info("Loaded %i T8bbllnunu signals", len(signals_T8bbllnunu_XCha0p5_XSlep0p05) + len(signals_T8bbllnunu_XCha0p5_XSlep0p5) + len(signals_T8bbllnunu_XCha0p5_XSlep0p95))
logger.debug("Loaded T8bbllnunu signals: %s", ",".join([s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05 + signals_T8bbllnunu_XCha0p5_XSlep0p5 + signals_T8bbllnunu_XCha0p5_XSlep0p95]))

for f in os.listdir(os.path.join(data_directory_, postProcessing_directory_, 'T8bbstausnu')):

    if f.endswith('.root') and f.startswith('T8bbstausnu_'):
        name = f.replace('.root','')
        xChaStr, xStauStr, mStop, mNeu = name.replace('T8bbstausnu_','').split('_')
        bcha    = "b#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{#pm}}"
        nuslep  = "#nu#tilde{tau}"
        lneu    = "l#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}}"
        ra      = " #rightarrow "
        
        xCha = xChaStr.replace('XCha','').replace('p','.')
        xStau = xStauStr.replace('XStau','').replace('p','.')
        
        tmp = Sample.fromFiles(\
            name = name,
            files = [os.path.join(os.path.join(data_directory_, postProcessing_directory_,'T8bbstausnu',f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "#tilde{t} #rightarrow b#nu l#tilde{#chi}_{#lower[-0.3]{1}}^{#lower[0.4]{0}} ("+mStop+","+mNeu+","+xCha+","+xStau+")"
            #texName = "#tilde{t}" + ra + bcha + ra + nuslep + ra + lneu + "("+mStop+","+mNeu+","+xCha+","+xSlep+")"
        )

        tmp.mStop   = int(mStop)
        tmp.mNeu    = int(mNeu)
        tmp.xCha    = float(xCha)
        tmp.xStau   = float(xStau)
        tmp.mCha    = int( tmp.xCha * ( tmp.mStop - tmp.mNeu ) + tmp.mNeu )
        tmp.mStau   = int( tmp.xStau * ( tmp.mCha - tmp.mNeu ) + tmp.mNeu )
        tmp.isFastSim = True

        exec("%s=tmp"%name)
        if f.startswith('T8bbstausnu_XCha0p5_XStau0p5'):
            exec("signals_T8bbstausnu_XCha0p5_XStau0p5.append(%s)"%name)

