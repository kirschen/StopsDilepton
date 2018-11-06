#!/usr/bin/env python
import ROOT
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store', default='T2tt',          nargs='?', choices=["T2tt"], help="which signal?")
argParser.add_argument("--only",           action='store', default=None,            nargs='?',                                                                                           help="pick only one masspoint?")
argParser.add_argument("--scale",          action='store', default=1.0, type=float, nargs='?',                                                                                           help="scaling all yields")
argParser.add_argument("--selectRegions",  action='store', default="regionsO", help="Which set of signal regions?")
argParser.add_argument("--overwrite",      default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--keepCard",       default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--controlDYVV",    default = False, action = "store_true", help="Fits for DY/VV CR")
argParser.add_argument("--controlTTZ",     default = False, action = "store_true", help="Fits for TTZ CR")
argParser.add_argument("--fitAll",         default = False, action = "store_true", help="Fits SR and CR together")
argParser.add_argument("--aggregate",      default = False, action = "store_true", help="Use aggregated signal regions")
argParser.add_argument("--expected",       default = False, action = "store_true", help="Use sum of backgrounds instead of data.")
argParser.add_argument("--DMsync",         default = False, action = "store_true", help="Use two regions for MET+X syncing")
argParser.add_argument("--significanceScan",         default = False, action = "store_true", help="Calculate significance instead?")
argParser.add_argument("--removeSR",      default = False, action = "store", help="Remove one signal region?")
argParser.add_argument("--extension",      default = '', action = "store", help="Extension to dir name?")
argParser.add_argument("--showSyst",      default = '', action = "store", help="Print the systematic uncertainties?")

args = argParser.parse_args()


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

from StopsDilepton.analysis.SetupHelpers    import channels, trilepChannels
from StopsDilepton.analysis.estimators      import *
from StopsDilepton.analysis.Setup           import Setup
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions         import *
from StopsDilepton.analysis.Cache           import Cache
from StopsDilepton.tools.resultsDB          import resultsDB
from copy import deepcopy

#define samples
#data_directory = '/afs/hephy.at/data/dspitzbart02/cmgTuples/'
#postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
#from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
#
#data_directory = '/afs/hephy.at/data/dspitzbart01/nanoTuples/'
#postProcessing_directory = 'stops_2016_nano_v2/dilep'
#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

data_directory = '/afs/hephy.at/data/dspitzbart02/nanoTuples/'
postProcessing_directory = 'stops_2016_nano_v2/dilep'
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

oSetup = Setup()
# This needs to be adjusted #FIXME
setup = oSetup.sysClone(parameters={"metMin":80., "metSigMin":0.})


# Define CR
setupDYVV = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False,  'zWindow': 'onZ'})
setupTTZ1 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(2,2),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ2 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ3 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ4 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ5 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})

# Define channels for CR
if args.aggregate:
    setup.channels = ['all']
elif args.DMsync:
    setup.channels = ['EE','MuMu', 'EMu']
else:
    setup.channels     = ['SF','EMu']
setupDYVV.channels = ['SF']
setupTTZ1.channels = ['all']
setupTTZ2.channels = ['all']
setupTTZ3.channels = ['all']
setupTTZ4.channels = ['all']
setupTTZ5.channels = ['all']

# Dirty signal region set selection
if args.selectRegions == "regionsO": signalRegions = regionsO[1:]
# FIXME add more!


# Define regions for CR
if args.aggregate:
    if args.removeSR:
        tmpRegion = deepcopy(regionsAgg[1:])
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
    else:
        setup.regions     = regionsAgg[1:]
    setupDYVV.regions = signalRegions
elif args.DMsync:
    setup.regions     = regionsDM[1:]
    setupDYVV.regions = signalRegions
else:
    if args.removeSR:
        tmpRegion = deepcopy(signalRegions)
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
    else:
        setup.regions   = signalRegions
    setupDYVV.regions = signalRegions
setupTTZ1.regions = noRegions
setupTTZ2.regions = noRegions
setupTTZ3.regions = noRegions
setupTTZ4.regions = noRegions
setupTTZ5.regions = noRegions

# Define estimators for CR
estimators           = estimatorList(setup)
#setup.estimators     = estimators.constructEstimatorList(["TTJets-DD","TTZ","DY", 'multiBoson', 'other'])
setup.estimators     = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other']) # no data-driven estimation atm
setupDYVV.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ1.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ2.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ3.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ4.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ5.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])

if args.fitAll:        setups = [setup, setupDYVV, setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
elif args.controlDYVV: setups = [setupDYVV]
elif args.controlTTZ:  setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
else:                  setups = [setup]

from StopsDilepton.analysis.u_float                                              import u_float
from math                                                                        import sqrt

##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.user           import combineReleaseLocation
from StopsDilepton.tools.cardFileWriter import cardFileWriter

if args.aggregate:          subDir = 'aggregated/'
elif args.DMsync:           subDir = 'DMsync/'
else:                       subDir = ''

if args.fitAll:             subDir += 'fitAll' 
elif args.controlDYVV:      subDir += 'controlDYVV'
elif args.controlTTZ:       subDir += 'controlTTZ'
elif args.significanceScan: subDir += 'significance'
else:                       subDir += 'signalOnly'


baseDir = os.path.join(setup.analysis_results, subDir)

limitDir    = os.path.join(baseDir, 'cardFiles', args.selectRegions, args.signal + args.extension)
overWrite   = (args.only is not None) or args.overwrite
if args.keepCard:
    overWrite = False
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits.pkl')
resDB = resultsDB(limitDir+'/results.sq', "results", ['mStop', 'mNeu', 'exp', 'obs', 'exp1up', 'exp2up', 'exp1down', 'exp2down'])
#limitCache    = Cache(cacheFileName, verbosity=2)

if   args.signal == "T2tt":                         fastSim = False ## Careful!

if   args.signal == "T2tt":
    # no MET Sig in fastsim
    postProcessing_directory = 'stops_2016_nano_v2/dilep'
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import T2tt_mStop_850_mLSP_100, T2tt_mStop_500_mLSP_325
    T2tt_mStop_850_mLSP_100.mStop, T2tt_mStop_850_mLSP_100.mNeu  = 850, 100
    T2tt_mStop_500_mLSP_325.mStop, T2tt_mStop_500_mLSP_325.mNeu  = 500, 325

    jobs = [T2tt_mStop_850_mLSP_100,T2tt_mStop_500_mLSP_325]


def wrapper(s):
    xSecScale = 1
    if "T8bb" in s.name:
        if s.mStop<10:#810
                xSecScale = 0.01
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    cardFileName = os.path.join(limitDir, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
        counter=0
        c.reset()
        c.setPrecision(3)
        c.addUncertainty('PU',         'lnN')
        c.addUncertainty('topPt',      'lnN')
        c.addUncertainty('JEC',        'lnN')
        c.addUncertainty('unclEn',     'lnN')
        c.addUncertainty('JER',        'lnN')
        c.addUncertainty('SFb',        'lnN')
        c.addUncertainty('SFl',        'lnN')
        c.addUncertainty('trigger',    'lnN')
        c.addUncertainty('leptonSF',   'lnN')
        c.addUncertainty('scale',      'lnN')
        c.addUncertainty('scaleTT',    'lnN')
        c.addUncertainty('scaleTTZ',   'lnN')
        c.addUncertainty('PDF',        'lnN')
        c.addUncertainty('xsec_PDF',   'lnN')
        c.addUncertainty('xsec_QCD',   'lnN')
        c.addUncertainty('isr',        'lnN')
        c.addUncertainty('topGaus',    'lnN')
        c.addUncertainty('topNonGaus', 'lnN')
        c.addUncertainty('topFakes',   'lnN')
        c.addUncertainty('multiBoson', 'lnN')
        c.addUncertainty('DY',         'lnN')
        c.addUncertainty('DY_SR',      'lnN')
        c.addUncertainty('ttZ_SR',     'lnN')
        c.addUncertainty('ttZ',        'lnN')
        c.addUncertainty('other',      'lnN')
        if fastSim:
            c.addUncertainty('btagFS',   'lnN')
            c.addUncertainty('leptonFS', 'lnN')
            c.addUncertainty('FSmet',    'lnN')
            c.addUncertainty('PUFS',     'lnN')

        for setup in setups:
          eSignal     = MCBasedEstimate(name=s.name, sample={channel:s for channel in channels+trilepChannels}, cacheDir=setup.defaultCacheDir())
          observation = DataObservation(name='Data', sample=setup.samples['Data'], cacheDir=setup.defaultCacheDir())
          for e in setup.estimators: e.initCache(setup.defaultCacheDir())

          for r in setup.regions:
            for channel in setup.channels:
                niceName = ' '.join([channel, r.__str__()])
                if setup == setupDYVV: niceName += "_controlDYVV"
                if setup == setupTTZ1: niceName += "_controlTTZ1"
                if setup == setupTTZ2: niceName += "_controlTTZ2"
                if setup == setupTTZ3: niceName += "_controlTTZ3"
                if setup == setupTTZ4: niceName += "_controlTTZ4"
                if setup == setupTTZ5: niceName += "_controlTTZ5"
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators][1:] + [ 'TTJetsG', 'TTJetsNG', 'TTJetsF' ], niceName)
                for e in setup.estimators:
                  name = e.name.split('-')[0]
                  expected = e.cachedEstimate(r, channel, setup)
                  total_exp_bkg += expected.val
                  if e.name.count('TTJets'):
                    if len(setup.regions) == len(signalRegions):     divider = 6
                    elif len(setup.regions) == len(signalRegions)-1:
                        if int(args.removeSR) < 6: divider = 5
                        else: divider = 6
                    elif len(setup.regions) == len(regionsAgg[1:]): divider = 1
                    elif len(setup.regions) == len(regionsAgg[1:])-1:
                        if int(args.removeSR) < 1 and args.removeSR is not False: divider = 0
                        else: divider = 1 # back to 1!!
                    elif len(setup.regions) == len(regionsDM1[1:]): divider = 3
                    elif len(setup.regions) == len(regionsDM5[1:]): divider = 2
                    else:                                           divider = 0 # Was 0, think about changing to 1 for ttZ sideband
                    logger.info("Splitting SRs into ttbar and ttZ dominated regions at signal region %s",divider)
                    if (setup.regions != noRegions and (r in setup.regions[divider:])):
                        norm_G  = 0.25
                        norm_NG = 0.50
                        norm_F  = 0.25
                    else:
                        norm_G  = 0.55
                        norm_NG = 0.44
                        norm_F  = 0.01
                    TT_SF = 1
                    if TT_SF != 1: logger.warning("Scaling ttbar background by %s", TT_SF)
                    c.specifyExpectation(binname, 'TTJetsG',  norm_G  * expected.val*args.scale * TT_SF)
                    c.specifyExpectation(binname, 'TTJetsNG', norm_NG * expected.val*args.scale * TT_SF)
                    c.specifyExpectation(binname, 'TTJetsF',  norm_F  * expected.val*args.scale * TT_SF)
                  elif e.name.count("DY"):
                    DY_SF = 1#.31 + 0.19*(-1)
                    c.specifyExpectation(binname, name, expected.val*args.scale*DY_SF)
                    if DY_SF != 1: logger.warning("Scaling DY background by %s", DY_SF)
                  elif e.name.count("TTZ"):
                    TTZ_SF = 1
                    c.specifyExpectation(binname, name, expected.val*args.scale*TTZ_SF)
                    if TTZ_SF != 1: logger.warning("Scaling ttZ background by %s", TTZ_SF)
                  else:
                    c.specifyExpectation(binname, name, expected.val*args.scale)

                  if expected.val>0:
                      if e.name.count('TTJets'):
                        names = [ 'TTJetsG', 'TTJetsNG', 'TTJetsF' ]
                      else:
                        names = [name]
                      for name in names:
                        if 'TTJets' in name: uncScale = 1#./sqrt(norm_G**2 + norm_NG**2 + norm_F**2) # scaling of uncertainties to be used in the future
                        else: uncScale = 1
                        #print "Process", name, "uncertainty scale", uncScale
                        c.specifyUncertainty('PU',       binname, name, 1 + 0.05 )#e.PUSystematic(         r, channel, setup).val * uncScale )
                        c.specifyUncertainty('JEC',      binname, name, 1 + 0.03 )#e.JECSystematic(        r, channel, setup).val * uncScale )
                        c.specifyUncertainty('unclEn',   binname, name, 1 + 0.05 )#e.unclusteredSystematic(r, channel, setup).val * uncScale )
                        c.specifyUncertainty('JER',      binname, name, 1 + 0.03 )#e.JERSystematic(        r, channel, setup).val * uncScale )
                        c.specifyUncertainty('topPt',    binname, name, 1 + 0.02 )#e.topPtSystematic(      r, channel, setup).val * uncScale )
                        c.specifyUncertainty('SFb',      binname, name, 1 + 0.02 )#e.btaggingSFbSystematic(r, channel, setup).val * uncScale )
                        c.specifyUncertainty('SFl',      binname, name, 1 + 0.01 )#e.btaggingSFlSystematic(r, channel, setup).val * uncScale )
                        c.specifyUncertainty('trigger',  binname, name, 1 + 0.02 )#e.triggerSystematic(    r, channel, setup).val * uncScale )
                        c.specifyUncertainty('leptonSF', binname, name, 1 + 0.04 )#e.leptonSFSystematic(   r, channel, setup).val * uncScale )
                        
                        if e.name.count('TTJets'):
                            c.specifyUncertainty('scaleTT', binname, name, 1 + 0.02)#getScaleUncBkg('TTLep_pow', r, channel,'TTLep_pow'))
                            c.specifyUncertainty('PDF',     binname, name, 1 + 0.02)#getPDFUnc('TTLep_pow', r, channel,'TTLep_pow'))
                            #c.specifyUncertainty('top', binname, name, 2 if (setup.regions != noRegions and r == setup.regions[-1]) else 1.5)

                        if name == 'TTJetsG':
                            c.specifyUncertainty('topGaus',  binname, name, 1.15)#1.15

                        if name == 'TTJetsNG':
                            c.specifyUncertainty('topNonGaus', binname, name, 1.30)#1.3

                        if name == 'TTJetsF':
                            c.specifyUncertainty('topFakes', binname, name, 1.50)#1.5

                        if e.name.count('multiBoson'): c.specifyUncertainty('multiBoson', binname, name, 1.5)

                        if e.name.count('DY'):
                            c.specifyUncertainty('DY',         binname, name, 1/(1+0.5))#1.5
                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0:
                                c.specifyUncertainty("DY_SR", binname, name, 1.25)

                        if e.name.count('TTZ'):
                            c.specifyUncertainty('ttZ',        binname, name, 1.2)
                            c.specifyUncertainty('scaleTTZ',binname, name, 1 + 0.02) #getScaleUncBkg('TTZ', r, channel,'TTZ'))
                            c.specifyUncertainty('PDF',     binname, name, 1 + 0.02) #getPDFUnc('TTZ', r, channel,'TTZ'))

                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0:
                                c.specifyUncertainty("ttZ_SR", binname, name, 1.20)

                        if e.name.count('other'):      c.specifyUncertainty('other',      binname, name, 1.25)

                        #MC bkg stat (some condition to neglect the smaller ones?)
                        uname = 'Stat_'+binname+'_'+name
                        c.addUncertainty(uname, 'lnN')
                        c.specifyUncertainty(uname, binname, name, 1 + (expected.sigma/expected.val) * uncScale)

                if args.expected:
                    c.specifyObservation(binname, int(round(total_exp_bkg,0)))
                else:
                    c.specifyObservation(binname, int(args.scale*observation.cachedObservation(r, channel, setup).val))

                #signal
                e = eSignal
                eSignal.isSignal = True
                if fastSim:
                    #signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF', 'weight_pol_L'], 'remove':['reweightPU36fb']})
                    #signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})
                    signalSetup = setup.sysClone()
                    signal = e.cachedEstimate(r, channel, signalSetup)
                    #signal = 0.5 * (e.cachedEstimate(r, channel, signalSetup) + e.cachedEstimate(r, channel, signalSetup.sysClone({'selectionModifier':'genMet'}))) # genMET modifier -> what to do for legacy?
                else:
                    signalSetup = setup.sysClone()
                    signal = e.cachedEstimate(r, channel, signalSetup)

                c.specifyExpectation(binname, 'signal', args.scale*signal.val*xSecScale )

                if signal.val>0:
                  if not fastSim:
                    c.specifyUncertainty('PU',       binname, 'signal', 1 + 0.05)#e.PUSystematic(         r, channel, signalSetup).val )
                    c.specifyUncertainty('PDF',      binname, 'signal', 1 + 0.02)#getPDFUncSignal(s.name, r, channel))
                  c.specifyUncertainty('JEC',      binname, 'signal', 1 + 0.02 )#e.JECSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('unclEn',   binname, 'signal', 1 + 0.02 )#e.unclusteredSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('JER',      binname, 'signal', 1 + 0.02 )#e.JERSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('SFb',      binname, 'signal', 1 + 0.02 )#e.btaggingSFbSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('SFl',      binname, 'signal', 1 + 0.02 )#e.btaggingSFlSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('trigger',  binname, 'signal', 1 + 0.02 )#e.triggerSystematic(    r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonSF', binname, 'signal', 1 + 0.02 )#e.leptonSFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('scale',    binname, 'signal', 1 + 0.02 )#getScaleUnc(eSignal.name, r, channel)) #had 0.3 for tests
                  if not args.signal == "ttHinv": c.specifyUncertainty('isr',      binname, 'signal', 1 + 0.03 )#abs(getIsrUnc(  eSignal.name, r, channel)))

                  if fastSim: 
                    c.specifyUncertainty('leptonFS', binname, 'signal', 1 + 0.02 )#e.leptonFSSystematic(    r, channel, signalSetup).val )
                    c.specifyUncertainty('btagFS',   binname, 'signal', 1 + 0.02 )#e.btaggingSFFSSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('FSmet',    binname, 'signal', 1 + 0.02 )#e.fastSimMETSystematic(  r, channel, signalSetup).val )
                    c.specifyUncertainty('PUFS',     binname, 'signal', 1 + 0.02 )#e.fastSimPUSystematic(   r, channel, signalSetup).val )

                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 + signal.sigma/signal.val )
            
                    
                else:
                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 )
                
                if not args.controlDYVV and (signal.val<=0.01 and total_exp_bkg<=0.01 or total_exp_bkg<=0):# or (total_exp_bkg>300 and signal.val<0.05):
                  if verbose: print "Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
                  c.muted[binname] = True
                else:
                  if verbose: print "NOT Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)

        c.addUncertainty('Lumi', 'lnN')
        c.specifyFlatUncertainty('Lumi', 1.026)
        cardFileName = c.writeToFile(cardFileName)
    else:
        print "File %s found. Reusing."%cardFileName
    
    if args.signal == "T2tt": sConfig = {'mStop':s.mStop, 'mNeu':s.mNeu}

    if useCache and not overWrite and resDB.contains(sConfig):
      res = limitCache.get(sConfig)
    else:
      res = c.calcLimit(cardFileName)#, options="--run blind")
      #c.calcNuisances(cardFileName)
      sConfig.update({'obs':res['-1.000'], 'exp':res['0.500'], 'exp1up':res['0.840'], 'exp2up':res['0.975'], 'exp1down':res['0.160'], 'exp2down':res['0.025']})
      resDB.add(sConfig, res['-1.000'], overwrite=True)

    #print xSecScale
    if xSecScale != 1:
        for k in res:
            res[k] *= xSecScale
    
    if res: 
      if args.signal == "T2tt": sString = "mStop %i mNeu %i" %(sConfig['mStop'], sConfig['mNeu'])
      try:
          print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
          return sConfig, res
      except:
          print "Problem with limit: %r"%str(res)
          return None


if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        jobNames = [ x.name for x in jobs ]
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)

results = map(wrapper, jobs)
results = [r for r in results if r]

