#!/usr/bin/env python
import ROOT
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store', default='T2tt',          nargs='?', choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95", "T2bt","T2bW", "T8bbllnunu_XCha0p5_XSlep0p09", "ttHinv"], help="which signal?")
argParser.add_argument("--only",           action='store', default=None,            nargs='?',                                                                                           help="pick only one masspoint?")
argParser.add_argument("--scale",          action='store', default=1.0, type=float, nargs='?',                                                                                           help="scaling all yields")
argParser.add_argument("--overwrite",      default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--keepCard",       default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--controlDYVV",    default = False, action = "store_true", help="Fits for DY/VV CR")
argParser.add_argument("--controlTTZ",     default = False, action = "store_true", help="Fits for TTZ CR")
argParser.add_argument("--fitAll",         default = False, action = "store_true", help="Fits SR and CR together")
argParser.add_argument("--aggregate",      default = False, action = "store_true", help="Use aggregated signal regions")
argParser.add_argument("--expected",       default = False, action = "store_true", help="Use sum of backgrounds instead of data.")
argParser.add_argument("--DMsync",         default = False, action = "store_true", help="Use two regions for MET+X syncing")
argParser.add_argument("--significanceScan",         default = False, action = "store_true", help="Calculate significance instead?")
argParser.add_argument("--removeSR",       default = False, action = "store", help="Remove one signal region?")
argParser.add_argument("--extension",      default = '', action = "store", help="Extension to dir name?")
argParser.add_argument("--showSyst",       default = '', action = "store", help="Print the systematic uncertainties?")
argParser.add_argument("--year",           default=2016, type="int",    action="store",      help="Which year?")

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
from StopsDilepton.analysis.regions         import regionsO, noRegions, regionsS, regionsAgg, regionsDM, regionsDM1, regionsDM2, regionsDM3, regionsDM4, regionsDM5, regionsDM6, regionsDM7
from StopsDilepton.analysis.Cache           import Cache
from copy import deepcopy

#define samples
#data_directory = '/afs/hephy.at/data/dspitzbart02/cmgTuples/'
#postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
#from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
#
#data_directory = '/afs/hephy.at/data/dspitzbart01/nanoTuples/'
#postProcessing_directory = 'stops_2016_nano_v2/dilep'
#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

data_directory = '/afs/hephy.at/data/rschoefbeck02/cmgTuples/'
postProcessing_directory = 'stops_2016_nano_v3/dilep'
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

setup = Setup(year=args.year)


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

# Define regions for CR
if args.aggregate:
    if args.removeSR:
        tmpRegion = deepcopy(regionsAgg[1:])
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
    else:
        setup.regions     = regionsAgg[1:]
    setupDYVV.regions = regionsO[1:]
elif args.DMsync:
    setup.regions     = regionsDM[1:]
    setupDYVV.regions = regionsO[1:]
else:
    if args.removeSR:
        tmpRegion = deepcopy(regionsO[1:])
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
    else:
        setup.regions   = regionsO[1:]
        #setup.regions   = regionsDM7[1:]
    setupDYVV.regions = regionsO[1:]
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

#signals_T8bbllnunu_XCha0p5_XSlep0p5 = [s for s in signals_T8bbllnunu_XCha0p5_XSlep0p5 if not s.mStop==851]

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

limitDir    = os.path.join(baseDir, 'cardFiles', args.signal + args.extension)
overWrite   = (args.only is not None) or args.overwrite
if args.keepCard:
    overWrite = False
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits.pkl')
limitCache    = Cache(cacheFileName, verbosity=2)

cacheFileNameS  = os.path.join(limitDir, 'calculatedSignifs.pkl')
signifCache     = Cache(cacheFileNameS, verbosity=2)

if   args.signal == "T2tt":                         fastSim = True
elif args.signal == "T2bW":                         fastSim = True
elif args.signal == "T2bt":                         fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": fastSim = True
elif args.signal == "TTbarDM":                      fastSim = False
elif args.signal == "ttHinv":                       fastSim = False

if   args.signal == "T2tt":
    #postProcessing_directory = 'stops_2016_nano_v2/dilep'
    postProcessing_directory = 'stops_2016_nano_v3/dilep'
    from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import signals_T2tt as jobs
#elif args.signal == "T2bt":
#    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#    from StopsDilepton.samples.cmgTuples_FastSimT2bX_mAODv2_25ns_postProcessed import signals_T2bt as jobs
#elif args.signal == "T2bW":
#    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#    from StopsDilepton.samples.cmgTuples_FastSimT2bX_mAODv2_25ns_postProcessed import signals_T2bW as jobs
elif 'T8bb' in args.signal:
    #postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
    postProcessing_directory = 'stops_2016_nano_v3/dilep'
    if args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p09 as jobs
#elif args.signal == "TTbarDM":
#    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM as jobs
#elif args.signal == "ttHinv":
#    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#    from StopsDilepton.samples.cmgTuples_Higgs_mAODv2_25ns_postProcessed import *
#    jobs = [ttH_HToInvisible_M125]

scaleUncCache = Cache(setup.analysis_results+'/systematics/scale_%s.pkl' % args.signal, verbosity=2)
isrUncCache   = Cache(setup.analysis_results+'/systematics/isr_%s.pkl'   % args.signal, verbosity=2)
PDF = ['TTLep_pow', 'DY', 'multiboson', 'TTZ'] 
PDFUncCaches   = {p:Cache(setup.analysis_results+'/systematicsTest_v2/PDF_%s.pkl' %p, verbosity=2) for p in PDF}
#PDFUncCacheSignal = Cache(setup.analysis_results+'/systematicsTest_v2/PDF_%s_acceptance.pkl'   % args.signal, verbosity=2)
if args.signal == "TTbarDM":
    PDFUncCacheSignal = Cache(setup.analysis_results+'/systematicsTest_v2/PDF_DM_signal_acceptance.pkl', verbosity=2) #should be one cache in the future. Kept like this for now
else:
    PDFUncCacheSignal = Cache(setup.analysis_results+'/systematicsTest_v2/PDF_ttH_signal_acceptance.pkl', verbosity=2)
scales = ['TTLep_pow', 'TTZ']
scaleUncCaches   = {p:Cache(setup.analysis_results+'/systematicsTest_v2/scale_%s.pkl' %p, verbosity=2) for p in scales}


def getScaleUnc(name, r, channel):
  if scaleUncCache.contains((name, r, channel)):    return max(0.01, scaleUncCache.get((name, r, channel)))
  else:                                             return 0.01

def getPDFUnc(name, r, channel, process):
    if PDFUncCaches[process].contains((name, r, channel)):  return max(0.01, PDFUncCaches[process].get((name, r, channel)))
    else:                                                   return 0.02

def getPDFUncSignal(name, r, channel):
    if PDFUncCacheSignal.contains((name, r, channel)):  return max(0.01, PDFUncCacheSignal.get((name, r, channel)))
    else:                                               return 0.01

def getScaleUncBkg(name, r, channel, process):
    if scaleUncCaches[process].contains((name, r, channel)):    return max(0.01, scaleUncCaches[process].get((name, r, channel)))
    else:                                                       return 0.01

def getIsrUnc(name, r, channel):
  if isrUncCache.contains((name,r,channel)):    return abs(isrUncCache.get((name, r, channel)))
  else:                                         return 0.02

systList = ["PU", "PDF", "xsec_QCD", "xsec_PDF", "JEC", "unclEn", "JER", "SFb", "SFl", "trigger", "leptonSF", "scale", "MCstat"]
systematicUncertainties = {x:[] for x in systList}


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
#        c.addUncertainty('top',   'lnN') #REMOVE AGAIN
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
#                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators], niceName)
                for e in setup.estimators:
                  name = e.name.split('-')[0]
                  expected = e.cachedEstimate(r, channel, setup)
                  total_exp_bkg += expected.val
                  if e.name.count('TTJets'):
                    if len(setup.regions) == len(regionsO[1:]):     divider = 6
                    elif len(setup.regions) == len(regionsO[1:])-1:
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
                        c.specifyUncertainty('PU',       binname, name, 1 + e.PUSystematic(         r, channel, setup).val * uncScale )
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
                    c.specifyUncertainty('PU',       binname, 'signal', 1 + e.PUSystematic(         r, channel, signalSetup).val )
                    c.specifyUncertainty('PDF',      binname, 'signal', 1 + getPDFUncSignal(s.name, r, channel))
                    if args.signal == "ttHinv":
                        # x-sec uncertainties for ttH: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBSMAt13TeV#ttH_Process
                        c.specifyUncertainty('xsec_QCD',      binname, 'signal', 1.092)
                        c.specifyUncertainty('xsec_PDF',      binname, 'signal', 1.036)
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
            
                  # add all signal uncertainties to print out max
                  #if counter < 26:
                  #  systematicUncertainties["PU"].append(e.PUSystematic(r, channel, signalSetup).val)
                  #  systematicUncertainties["PDF"].append(getPDFUncSignal(s.name, r, channel))
                  #  systematicUncertainties["xsec_QCD"].append(1.092)
                  #  systematicUncertainties["xsec_PDF"].append(1.036)
                  #  systematicUncertainties["JEC"].append(e.JECSystematic(        r, channel, signalSetup).val)
                  #  systematicUncertainties["unclEn"].append(e.unclusteredSystematic(r, channel, signalSetup).val)
                  #  systematicUncertainties["JER"].append(e.JERSystematic(        r, channel, signalSetup).val)
                  #  systematicUncertainties["SFb"].append(e.btaggingSFbSystematic(r, channel, signalSetup).val)
                  #  systematicUncertainties["SFl"].append(e.btaggingSFlSystematic(r, channel, signalSetup).val)
                  #  systematicUncertainties["trigger"].append(e.triggerSystematic(    r, channel, signalSetup).val)
                  #  systematicUncertainties["leptonSF"].append(e.leptonSFSystematic(   r, channel, signalSetup).val)
                  #  systematicUncertainties["scale"].append(getScaleUnc(eSignal.name, r, channel))
                  #  systematicUncertainties["MCstat"].append(signal.sigma/signal.val)
                  #  #systematicUncertainties[""].append()
                    
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
    
    if   args.signal == "TTbarDM":                      sConfig = s.mChi, s.mPhi, s.type
    elif args.signal == "T2tt":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T2bt":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T2bW":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": sConfig = s.mStop, s.mNeu
    elif args.signal == "ttHinv":                       sConfig = ("ttHinv", "2l")

    ## Print the systematic uncertainties
    #print
    #print "Systematic uncertainties"
    #print "{:10}{:10}{:10}".format("name", "min", "max")
    #for syst in systematicUncertainties.keys():
    #    print "{:10}{:10.2f}{:10.2f}".format(syst, min(systematicUncertainties[syst])*100, max(systematicUncertainties[syst])*100)

    if not args.significanceScan:
        if useCache and not overWrite and limitCache.contains(sConfig):
          res = limitCache.get(sConfig)
        else:
          res = c.calcLimit(cardFileName)#, options="--run blind")
          c.calcNuisances(cardFileName)
          limitCache.add(sConfig, res, save=True)
    else:
        if useCache and not overWrite and signifCache.contains(sConfig):
            res = signifCache.get(sConfig)
        else:
            res = c.calcSignif(cardFileName)
            signifCache.add(sConfig,res,save=True)
    
    #print xSecScale
    if xSecScale != 1:
        for k in res:
            res[k] *= xSecScale
    
    if res: 
      if   args.signal == "TTbarDM":                        sString = "mChi %i mPhi %i type %s" % sConfig
      elif args.signal == "T2tt":                           sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T2bt":                           sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T2bW":                           sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":   sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09":   sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":    sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":   sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "ttHinv":                         sString = "ttH->inv"
      if args.significanceScan:
        try:   
            print "Result: %r significance %5.3f"%(sString, res['-1.000'])
            return sConfig, res
        except:
            print "Problem with limit: %r" + str(res)
            return None
      else:
        try:
            print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
            return sConfig, res
        except:
            print "Problem with limit: %r"%str(res)
            return None


#postProcessing_directory = "postProcessed_80X_v40/dilepTiny"
#if   args.signal == "T2tt":                         from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt as jobs
#elif args.signal == "T2bt":                         from StopsDilepton.samples.cmgTuples_FastSimT2bX_mAODv2_25ns_postProcessed import signals_T2bt as jobs
#elif args.signal == "T2bW":                         from StopsDilepton.samples.cmgTuples_FastSimT2bX_mAODv2_25ns_postProcessed import signals_T2bW as jobs
#elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
#elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
#elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs
#elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p09 as jobs
#elif args.signal == "TTbarDM":
#    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM as jobs

if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        jobNames = [ x.name for x in jobs ]
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)

results = map(wrapper, jobs)
results = [r for r in results if r]

# Make histograms for T2tt
if "T2" in args.signal or  "T8bb" in args.signal:
  binSize = 25
  shift = binSize/2.*(-1)
  exp      = ROOT.TH2F("exp", "exp", 1600/25, shift, 1600+shift, 1500/25, shift, 1500+shift)
#  exp      = ROOT.TH2F("exp", "exp", 128, 0, 1600, 120, 0, 1500)
  exp_down = exp.Clone("exp_down")
  exp_up   = exp.Clone("exp_up")
  obs      = exp.Clone("obs")
  limitPrefix = args.signal
  for r in results:
    s, res = r
    mStop, mNeu = s
    if args.significanceScan:
        resultList = [(obs, '-1.000')]
    else:
        resultList = [(exp, '0.500'), (exp_up, '0.160'), (exp_down, '0.840'), (obs, '-1.000')]

    for hist, qE in resultList:
      #print hist, qE, res[qE]
      if qE=='0.500':
        print "Masspoint m_gl %5.3f m_neu %5.3f, expected limit %5.3f"%(mStop,mNeu,res[qE])
      if qE=='-1.000':
        print "Observed limit %5.3f"%(res[qE])
      hist.GetXaxis().FindBin(mStop)
      hist.GetYaxis().FindBin(mNeu)
      #print hist.GetName(), mStop, mNeu, res[qE]
      hist.Fill(mStop, mNeu, res[qE])

  if args.significanceScan:
    limitResultsFilename = os.path.join(baseDir, 'limits', args.signal, limitPrefix,'signifResults.root')
  else:
    limitResultsFilename = os.path.join(baseDir, 'limits', args.signal, limitPrefix,'limitResults.root')

  if not os.path.exists(os.path.dirname(limitResultsFilename)):
      os.makedirs(os.path.dirname(limitResultsFilename))

  outfile = ROOT.TFile(limitResultsFilename, "recreate")
  exp      .Write()
  exp_down .Write()
  exp_up   .Write()
  obs      .Write()
  outfile.Close()
  print "Written %s"%limitResultsFilename

# Make table for DM
if args.signal == "TTbarDM":
  limitPrefix = args.signal
  # Create table
  texdir = os.path.join(baseDir, 'limits', args.signal, limitPrefix)
  if not os.path.exists(texdir): os.makedirs(texdir)

  for type in sorted(set([type_ for ((mChi, mPhi, type_), res) in results])):
    for lim, key in [['exp','0.500'], ['obs', '-1.000']]:
        chiList = sorted(set([mChi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
        phiList = sorted(set([mPhi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
        ofilename = texdir + "/%s_%s.tex"%(type, lim)
        print "Writing to ", ofilename 
        with open(ofilename, "w") as f:
          f.write("\\begin{tabular}{cc|" + "c"*len(phiList) + "} \n")
          f.write(" & & \multicolumn{" + str(len(phiList)) + "}{c}{$m_\\phi$ (GeV)} \\\\ \n")
          f.write("& &" + " & ".join(str(x) for x in phiList) + "\\\\ \n \\hline \\hline \n")
          for chi in chiList:
            resultList = []
            for phi in phiList:
              result = ''
              try:
                for ((c, p, t), r) in results:
                  if c == chi and p == phi and t == type:
                      result = "%.2f" % r[key]
              except:
                pass
              resultList.append(result)
            if chi == chiList[0]: f.write("\\multirow{" + str(len(chiList)) + "}{*}{$m_\\chi$ (GeV)}")
            f.write(" & " + str(chi) + " & " + " & ".join(resultList) + "\\\\ \n")
          f.write(" \\end{tabular}")
