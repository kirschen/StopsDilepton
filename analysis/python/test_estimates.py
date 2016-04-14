from StopsDilepton.analysis.SetupHelpers import channels
from StopsDilepton.analysis.mcAnalysis import setup, regions, bkgEstimators
from StopsDilepton.analysis.defaultAnalysis import setup, regions, bkgEstimators

from MCBasedEstimate import MCBasedEstimate
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_2l_postProcessed import *

setup.analysis_results='/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test5'
setup.verbose=True

#signal = T2tt_450_0
#signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']}, parameters={'useTriggers':False})

signal = TTbarDMJets_pseudoscalar_Mchi1_Mphi50
signalSetup = setup.sysClone(sys={'reweight':[]}, parameters={'useTriggers':False})

#from StopsDilepton.tools.objectSelection import multiIsoLepString
#wp = 'VL'
#setup.externalCuts.append(multiIsoLepString(wp, ('l1_index','l2_index')))
#setup.prefixes.append('multiIso'+wp)

signalEstimators = [ MCBasedEstimate(name=s.name,    sample={channel:s for channel in channels}, cacheDir=None ) for s in [signal] ]

#channel = 'MuMu'
channel = 'all'
sigEstimate = signalEstimators[0]
from StopsDilepton.analysis.Region import Region
region=Region('dl_mt2ll', (140,-1))


sigExampleTrig = sigEstimate.cachedEstimate(region, channel, setup)
sigExample     = sigEstimate.cachedEstimate(region, channel, setup.sysClone(parameters={'useTriggers':False}))
sigExampleFSim = sigEstimate.cachedEstimate(region, channel, signalSetup)
print "Region %s Channel %s sig (trig) %s sig (no trig) %s (FSim) %s"%(region, channel, sigExampleTrig, sigExample, sigExampleFSim)
