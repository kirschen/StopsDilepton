import ROOT
import os

from StopsDilepton.analysis.u_float         import u_float
from StopsDilepton.analysis.SetupHelpers    import channels, trilepChannels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList, MCBasedEstimate, DataDrivenTTJetsEstimate
from StopsDilepton.analysis.regions         import regionsO, noRegions, regionsS, regionsAgg, regionsDM, regionsDM1, regionsDM2, regionsDM3, regionsDM4, regionsDM5, regionsDM6, regionsDM7

from copy import deepcopy

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Higgs_mAODv2_25ns_postProcessed import *

ttH_HToInvisible_M125.isFastSim = False

aggregate = False

setup.channels     = ['SF','EMu']
#setup.channels     = ['all']

if aggregate:
    setup.regions   = regionsAgg[1:]
    SRname_prefix = "A"
    setup.channels     = ['all']
else:
    setup.regions   = regionsO[1:]
    SRname_prefix = "SR"
    setup.channels     = ['SF','EMu']

setups = [setup]

TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10.isFastSim = False
TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10.isFastSim = False

signals = [ T2tt_750_1, T2tt_600_300, TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10, ttH_HToInvisible_M125 ]

texdir  = os.path.join(setup.analysis_results, setup.prefix(), 'tables_agg')
print texdir

allSignals = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in channels+trilepChannels}, cacheDir=setup.defaultCacheDir()) for s in signals ]

for s in signals:
    total = u_float(0)
    total_CF = u_float(0)
    eSignal     = MCBasedEstimate(name=s.name, sample={channel:s for channel in channels+trilepChannels}, cacheDir=setup.defaultCacheDir())
    print s.name
    print "{:10}{:15}{:15}{:15}{:>10} +/- {:10}{:15}".format("","MT2(ll)", "MT2(lblb)", "MET","count","stat", "signal region")    
    for i,r in enumerate(setup.regions):
        for c in setup.channels:
            if s.isFastSim:
                signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})
                signal = 0.5 * (eSignal.cachedEstimate(r, c, signalSetup) + eSignal.cachedEstimate(r, c, signalSetup.sysClone({'selectionModifier':'genMet'})))
            else:
                signalSetup = setup.sysClone()
                signal = eSignal.cachedEstimate(r, c, signalSetup)
            
            print "{:10}{:15}{:15}{:15}{:10.2f} +/- {:<10.2f}{:15}".format(c, r.vals[r.variables()[2]], r.vals[r.variables()[1]], r.vals[r.variables()[0]], signal.val, signal.sigma, SRname_prefix+"%i"%i)
            if r.vals[r.variables()[2]][0] >= 140: total_CF += signal
            total += signal
    print "{:10}{:15}{:15}{:15}{:10.2f} +/- {:<10.2f}".format("total", "", "", "", total.val, total.sigma)
    print "{:10}{:15}{:15}{:15}{:10.2f} +/- {:<10.2f}".format("total cutflow", "", "", "", total_CF.val, total_CF.sigma)

