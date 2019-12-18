#!/usr/bin/env python
#regionsLegacytest1
import ROOT
import os
import math
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store', default='T2tt',          nargs='?', choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95", "T2bt","T2bW", "T8bbllnunu_XCha0p5_XSlep0p09", "ttHinv"], help="which signal?")
argParser.add_argument("--only",           action='store', default=None,            nargs='?',                                                                                           help="pick only one masspoint?")
argParser.add_argument("--scale",          action='store', default=1.0, type=float, nargs='?',                                                                                           help="scaling all yields")
argParser.add_argument("--overwrite",      default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--keepCard",       default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--control2016",    default = False, action = "store_true", help="Fits for DY/VV/TTZ CR")
argParser.add_argument("--controlDYVV",    default = False, action = "store_true", help="Fits for DY/VV CR")
argParser.add_argument("--controlTTZ",     default = False, action = "store_true", help="Fits for TTZ CR")
argParser.add_argument("--controlTT",      default = False, action = "store_true", help="Fits for TT CR (MT2ll<100)")
argParser.add_argument("--controlAll",     default = False, action = "store_true", help="Fits for all CRs")
argParser.add_argument("--fitAll",         default = False, action = "store_true", help="Fits SR and CR together")
argParser.add_argument("--fitAllNoTT",     default = False, action = "store_true", help="Fits SR and CR together")
argParser.add_argument("--aggregate",      default = False, action = "store_true", help="Use aggregated signal regions")
argParser.add_argument("--expected",       default = False, action = "store_true", help="Use sum of backgrounds instead of data.")
argParser.add_argument("--unblind",        default = False, action = "store_true", help="Use real data in the signal regions.")
argParser.add_argument("--DMsync",         default = False, action = "store_true", help="Use two regions for MET+X syncing")
argParser.add_argument("--noSignal",       default = False, action = "store_true", help="Don't use any signal (force signal yield to 0)?")
argParser.add_argument("--useTxt",         default = False, action = "store_true", help="Use txt based cardFiles instead of root/shape based ones?")
argParser.add_argument("--fullSim",        default = False, action = "store_true", help="Use FullSim signals")
argParser.add_argument("--signalInjection",default = False, action = "store_true", help="Inject signal?")
argParser.add_argument("--significanceScan",         default = False, action = "store_true", help="Calculate significance instead?")
argParser.add_argument("--removeSR",       default = False, action = "store", help="Remove one signal region?")
argParser.add_argument("--skipFitDiagnostics", default = False, action = "store_true", help="Don't do the fitDiagnostics (this is necessary for pre/postfit plots, but not 2D scans)?")
argParser.add_argument("--extension",      default = '', action = "store", help="Extension to dir name?")
argParser.add_argument("--year",           default=2016,     action="store",      help="Which year?")
argParser.add_argument("--dpm",            default= False,   action="store_true",help="Use dpm?",)
args = argParser.parse_args()

year = int(args.year)

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger('INFO', logFile = None )
import Analysis.Tools.logger as logger_an
logger_an = logger_an.get_logger(args.logLevel, logFile = None )

# Load from DPM?
if args.dpm:
    data_directory      = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

from StopsDilepton.analysis.SetupHelpers    import channels, trilepChannels
from StopsDilepton.analysis.estimators      import *
from StopsDilepton.analysis.Setup           import Setup
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions         import regionsLegacy, noRegions, regionsAgg, highMT2blblregions
#regionsLegacy, noRegions, regionsS, regionsAgg, regionsDM, regionsDM1, regionsDM2, regionsDM3, regionsDM4, regionsDM5, regionsDM6, regionsDM7
from StopsDilepton.analysis.Cache           import Cache
from copy import deepcopy

setup = Setup(year=year)

# Define CR
setupDYVV = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False,  'zWindow': 'onZ', 'metSigMin' : 12})
setupTTZ1 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(2,2),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ2 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ3 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ4 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ5 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTT   = setup.sysClone()

# Define channels for CR
if args.aggregate:
    setup.channels = ['all']
elif args.DMsync:
    setup.channels = ['EE','MuMu', 'EMu']
else:
    setup.channels     = ['SF','EMu']
#setupDYVV.channels = ['EE']
setupDYVV.channels = ['SF']
setupTTZ1.channels = ['all']
setupTTZ2.channels = ['all']
setupTTZ3.channels = ['all']
setupTTZ4.channels = ['all']
setupTTZ5.channels = ['all']
setupTT.channels = ['SF','EMu']

# Define regions for CR
if args.aggregate:
    if args.removeSR:
        tmpRegion = deepcopy(regionsAgg[1:])
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
    else:
        setup.regions     = regionsAgg[1:]
    setupDYVV.regions = regionsLegacy[1:]
elif args.DMsync:
    setup.regions     = regionsDM[1:]
    setupDYVV.regions = regionsLegacy[1:]
else:
    if args.removeSR:
        tmpRegion = deepcopy(regionsLegacy[1:])
        tmpRegion.pop(int(args.removeSR))
        setup.regions   = tmpRegion
        setupDYVV.regions = tmpRegion
    else:
        setup.regions   = regionsLegacy[1:]
        #setup.regions   = regionsDM7[1:]
        setupDYVV.regions = regionsLegacy[1:]
setupTTZ1.regions = noRegions
setupTTZ2.regions = noRegions
setupTTZ3.regions = noRegions
setupTTZ4.regions = noRegions
setupTTZ5.regions = noRegions

setupTT.regions = [regionsLegacy[0]]

# Define estimators for CR
estimators           = estimatorList(setup)
#setup.estimators     = estimators.constructEstimatorList(["TTJets-DD","TTZ","DY", 'multiBoson', 'other'])
setup.estimators     = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX']) # no data-driven estimation atm
setupDYVV.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTTZ1.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTTZ2.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTTZ3.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTTZ4.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTTZ5.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])
setupTT.estimators   = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ', 'TZX'])

if args.fitAll:        setups = [setupTT, setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5, setupDYVV, setup]
elif args.fitAllNoTT:  setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5, setupDYVV, setup]
elif args.controlDYVV: setups = [setupDYVV]
elif args.controlTTZ:  setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
elif args.controlTT:   setups = [setupTT]
elif args.control2016: setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5, setupDYVV]
elif args.controlAll:  setups = [setupTT, setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5, setupDYVV]
else:                  setups = [setup]

from StopsDilepton.tools.u_float    import u_float
from math                           import sqrt

#signals_T8bbllnunu_XCha0p5_XSlep0p5 = [s for s in signals_T8bbllnunu_XCha0p5_XSlep0p5 if not s.mStop==851]

##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.cardFileWriter import cardFileWriter

if args.aggregate:          subDir = 'aggregated/'
elif args.DMsync:           subDir = 'DMsync/'
else:                       subDir = ''

if args.fitAll:             subDir += 'fitAll' 
elif args.fitAllNoTT:       subDir += 'fitAllNoTT' 
elif args.controlDYVV:      subDir += 'controlDYVV'
elif args.controlTTZ:       subDir += 'controlTTZ'
elif args.controlTT:        subDir += 'controlTT'
elif args.controlAll:       subDir += 'controlAll'
elif args.control2016:       subDir += 'control2016'
elif args.significanceScan: subDir += 'significance'
else:                       subDir += 'signalOnly'

baseDir = os.path.join(setup.analysis_results, str(year), subDir)

sSubDir = 'expected' if args.expected else 'observed'
if args.signalInjection: sSubDir += '_signalInjected'

limitDir    = os.path.join(baseDir, 'cardFiles', args.signal + args.extension, sSubDir)
overWrite   = (args.only is not None) or args.overwrite
if args.keepCard:
    overWrite = False
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits')
limitCache    = Cache(cacheFileName, verbosity=2)

cacheFileNameS  = os.path.join(limitDir, 'calculatedSignifs')
signifCache     = Cache(cacheFileNameS, verbosity=2)

fastSim = False # default value
if   args.signal == "T2tt" and not args.fullSim:    fastSim = True
elif args.signal == "T2bW":                         fastSim = True
elif args.signal == "T2bt":                         fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": fastSim = True
elif args.signal == "TTbarDM":                      fastSim = False
elif args.signal == "ttHinv":                       fastSim = False

if fastSim:
    logger.info("Assuming the signal sample is FastSim!")
else:
    logger.info("Assuming the signal sample is FullSim!")

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


def wrapper(s):
    xSecScale = 1
    if "T8bb" in s.name:
        if s.mStop<10:#810
                xSecScale = 0.01
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = os.path.abspath('.') # now run directly in the run directory

    logger.info("Running over signal: %s", s.name)

    cardFileName = os.path.join(limitDir, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
        counter=0
        c.reset()
        c.setPrecision(3)
        shapeString = 'lnN' if args.useTxt else 'shape'
        # experimental
        SFb     = 'SFb_%s'%year
        SFl     = 'SFl_%s'%year
        trigger = 'trigger_%s'%year
        JEC     = 'JEC_%s'%year
        unclEn  = 'unclEn'
        JER     = 'JER_%s'%year
        PU      = 'PU_%s'%year
        Lumi    = 'Lumi_%s'%year
        c.addUncertainty(PU,           shapeString)
        c.addUncertainty('topPt',      shapeString)
        c.addUncertainty(JEC,          shapeString)
        c.addUncertainty(unclEn,       shapeString)
        c.addUncertainty(JER,          shapeString)
        c.addUncertainty(SFb,          shapeString)
        c.addUncertainty(SFl,          shapeString)
        c.addUncertainty(trigger,      shapeString)
        c.addUncertainty('leptonSF',   shapeString)
        c.addUncertainty('leptonHit0SF',   shapeString)
        c.addUncertainty('leptonSIP3DSF',   shapeString)
        c.addUncertainty('L1prefire',  shapeString)
        # theory (PDF, scale, ISR)
        c.addUncertainty('scale',      shapeString)
        c.addUncertainty('scaleTT',    shapeString)
        c.addUncertainty('scaleTTZ',   shapeString)
        c.addUncertainty('PDF',        shapeString)
        c.addUncertainty('xsec_PDF',   shapeString)
        c.addUncertainty('xsec_QCD',   shapeString)
        c.addUncertainty('isr',        shapeString)
        # only in SRs
        DY_add = 'DY_hMT2blbl'
        c.addUncertainty('topXSec',    shapeString)
        c.addUncertainty('topNonGauss', shapeString)
        c.addUncertainty('topFakes',   shapeString)
        c.addUncertainty('DY_SR',      shapeString)
        c.addUncertainty('MB_SR',      shapeString)
        c.addUncertainty(DY_add,       shapeString) # only in high mt2blbl
        c.addUncertainty('ttZ_SR',     shapeString)
        # all regions, lnN
        c.addUncertainty('other',      'lnN')
        c.addUncertainty(Lumi,         'lnN')
        if fastSim:
            c.addUncertainty('btagFS',   shapeString)
            c.addUncertainty('leptonFS', shapeString)
            c.addUncertainty('FSmet',    shapeString)
            c.addUncertainty('PUFS',     shapeString)

        c.addRateParameter('DY',            1, '[0,10]') #0.5, 1.5
        c.addRateParameter('multiBoson',    1, '[0.6,1.4]') #0.6, 1.4
        c.addRateParameter('TTZ',           1, '[0,10]')
        c.addRateParameter('TTJets',        1, '[0,10]') #[0.85,1.15]

        for setup in setups:
          eSignal     = MCBasedEstimate(name=s.name, sample=s, cacheDir=setup.defaultCacheDir()) # {channel:s for channel in channels+trilepChannels}
          observation = DataObservation(name='Data', sample=setup.samples['Data'], cacheDir=setup.defaultCacheDir())
          for e in setup.estimators: e.initCache(setup.defaultCacheDir())

          for r in setup.regions:
            print r
            for channel in setup.channels:
                niceName = ' '.join([channel, r.__str__()])
                if setup == setupDYVV: niceName += "_controlDYVV"
                if setup == setupTTZ1: niceName += "_controlTTZ1"
                if setup == setupTTZ2: niceName += "_controlTTZ2"
                if setup == setupTTZ3: niceName += "_controlTTZ3"
                if setup == setupTTZ4: niceName += "_controlTTZ4"
                if setup == setupTTZ5: niceName += "_controlTTZ5"
                if setup == setupTT:   niceName += "_controlTTBar"
                logger.info("Bin name: %s", niceName)
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
#                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators][1:] + [ 'TTJetsG', 'TTJetsNG', 'TTJetsF' ], niceName)
                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators if not 'TZX' in e.name ], niceName)
                for e in setup.estimators:
                  name = e.name.split('-')[0]
                  expected = e.cachedEstimate(r, channel, setup)
                  expected = expected * args.scale
                  total_exp_bkg += expected.val
                  if e.name.count("TZX"): continue
                  logger.info("Expectation for process %s: %s", e.name, expected.val)
                  if e.name.count('TTJets'):
                    if len(setup.regions) == len(regionsLegacy[1:]):     divider = 6
                    elif len(setup.regions) == len(regionsLegacy[1:])-1:
                        if int(args.removeSR) < 6: divider = 5
                        else: divider = 6
                    elif len(setup.regions) == len(regionsAgg[1:]): divider = 1
                    elif len(setup.regions) == len(regionsAgg[1:])-1:
                        if int(args.removeSR) < 1 and args.removeSR is not False: divider = 0
                        else: divider = 1 # back to 1!!
                    elif len(setup.regions) == len(regionsDM1[1:]): divider = 3
                    elif len(setup.regions) == len(regionsDM5[1:]): divider = 2
                    else:                                           divider = 0 # Was 0, think about changing to 1 for ttZ sideband
                    if setup.regions == [regionsLegacy[0]]:
                        fakeUncertainty     = 1.02 # 1.002
                        nonGaussUncertainty = 1.02 # 1.002
                        normUncertainty = 1.06
                    elif niceName.count("controlDYVV") or niceName.count("controlTTZ"):
                        fakeUncertainty     = 1.02 # 1.02
                        nonGaussUncertainty = 1.02 # 1.02
                        normUncertainty = 1.08
                    elif (setup.regions != noRegions and (r in setup.regions[divider:])):
                        fakeUncertainty     = 1.20
                        nonGaussUncertainty = 1.25
                        normUncertainty = 1.10
                    else:
                        fakeUncertainty     = 1.05 # 1.03
                        nonGaussUncertainty = 1.10
                        normUncertainty = 1.10
                    TT_SF = 1
                    if TT_SF != 1: logger.warning("Scaling ttbar background by %s", TT_SF)
                    logger.info("Fake and non-gauss uncertainty are %s and  %s", fakeUncertainty, nonGaussUncertainty)
                    c.specifyExpectation(binname, 'TTJets',  expected.val * TT_SF)
                    #c.specifyUncertainty("Top", binname, name, 1.10)
                  elif e.name.count("DY"):
                    DY_SF = 1
                    c.specifyExpectation(binname, name, expected.val*DY_SF)
                    if DY_SF != 1: logger.warning("Scaling DY background by %s", DY_SF)
                    #c.specifyUncertainty("DY", binname, name, 1.20)
                  elif e.name.count("multiBoson"):
                    c.specifyExpectation(binname, name, expected.val)
                    #c.specifyUncertainty("MB", binname, name, 1.20)
                  elif e.name.count("TTZ"):
                    TTZ_SF = 1
                    for tmp_e in setup.estimators:
                        if tmp_e.name.count("TZX"): TZX_e = tmp_e
                    TZX_expected = TZX_e.cachedEstimate(r, channel, setup)
                    logger.info("Pure ttZ expected %s", expected.val)
                    expected = expected+TZX_expected
                    logger.info("ttZ+tZX expected %s", expected.val)
                    c.specifyExpectation(binname, name, expected.val*TTZ_SF)
                    if TTZ_SF != 1: logger.warning("Scaling ttZ background by %s", TTZ_SF)
                    #c.specifyUncertainty("TTZ", binname, name, 1.10)
                  elif e.name.count("TZX"):
                    logger.info("TZX has been added to TTZ")
                  elif e.name.count("TTXNoZ") or e.name.count("other"):
                    c.specifyExpectation(binname, name, expected.val)

                  if expected.val>0 or True:
                      names = [name]
                      for name in names:
                        sysChannel = 'all' # could be channel as well
                        uncScale = 1
                        c.specifyUncertainty(PU,       binname, name, 1 + e.PUSystematic(         r, sysChannel, setup).val * uncScale )
                        if not e.name.count("TTJets") and not niceName.count('controlTTBar'):
                            #c.specifyUncertainty(JEC,        binname, name, 1 + e.JECSystematic(        r, channel, setup).val * uncScale )
                            c.specifyUncertainty(JEC,        binname, name, e.JECSystematicAsym(        r, sysChannel, setup) )
                            #c.specifyUncertainty(unclEn,     binname, name, 1 + e.unclusteredSystematic(r, channel, setup).val * uncScale ) # could remove uncertainties in ttbar CR
                            c.specifyUncertainty(unclEn,     binname, name, e.unclusteredSystematicAsym(r, sysChannel, setup) ) # could remove uncertainties in ttbar CR
                            #c.specifyUncertainty(JER,        binname, name, 1 + e.JERSystematic(        r, channel, setup).val * uncScale )#0.03 )
                            c.specifyUncertainty(JER,        binname, name, e.JERSystematicAsym(        r, sysChannel, setup) )
                        c.specifyUncertainty('topPt',    binname, name, 1 + e.topPtSystematic(      r, channel, setup).val * uncScale )#0.02 )
                        c.specifyUncertainty(SFb,        binname, name, 1 + e.btaggingSFbSystematic(r, channel, setup).val * uncScale )
                        c.specifyUncertainty(SFl,        binname, name, 1 + e.btaggingSFlSystematic(r, channel, setup).val * uncScale )
                        c.specifyUncertainty('leptonSF', binname, name, 1 + e.leptonSFSystematic(   r, channel, setup).val * uncScale ) 
                        c.specifyUncertainty('leptonSIP3DSF', binname, name, 1 + e.leptonSIP3DSFSystematic(   r, channel, setup).val * uncScale ) 
                        c.specifyUncertainty('leptonHit0SF', binname, name, 1 + e.leptonHit0SFSystematic(   r, channel, setup).val * uncScale ) 
                        c.specifyUncertainty('L1prefire', binname, name, 1 + e.L1PrefireSystematic(   r, channel, setup).val * uncScale ) 
                        if not e.name.count("TTJets") and not niceName.count('controlTTBar'):
                            c.specifyUncertainty(trigger,    binname, name, 1 + e.triggerSystematic(    r, channel, setup).val * uncScale ) # could remove uncertainties in ttbar CR

                        #if e.name.count('TTJets'):
                        #    c.specifyUncertainty('scaleTT', binname, name, 1 + 0.02)#getScaleUncBkg('TTLep_pow', r, channel,'TTLep_pow'))
                        #    c.specifyUncertainty('PDF',     binname, name, 1 + 0.02)#getPDFUnc('TTLep_pow', r, channel,'TTLep_pow'))

                        if name == 'TTJets':
                            c.specifyUncertainty('topFakes',  binname, name, fakeUncertainty)
                            c.specifyUncertainty('topNonGauss',  binname, name, nonGaussUncertainty)
                            c.specifyUncertainty('topXSec',  binname, name, normUncertainty)

                        if e.name.count('multiBoson'):
                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0 and niceName.count("TTBar")==0:
                                    c.specifyUncertainty("MB_SR", binname, name, 1.25)

                        if e.name.count('DY'):
                            if niceName.count("controlTT")==0:
                                #if r in highMT2blblregions:
                                #    c.specifyUncertainty(DY_add,         binname, name, 1.5)
                                if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0 and niceName.count("TTBar")==0:
                                    c.specifyUncertainty("DY_SR", binname, name, 1.25)

                        if e.name.count('TTZ') and niceName.count('DYVV')==0 and niceName.count('TTBar')==0:
                            #c.specifyUncertainty('scaleTTZ',binname, name, 1 + 0.02) #getScaleUncBkg('TTZ', r, channel,'TTZ'))
                            #c.specifyUncertainty('PDF',     binname, name, 1 + 0.02) #getPDFUnc('TTZ', r, channel,'TTZ'))

                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0 and niceName.count("TTBar")==0:
                                c.specifyUncertainty("ttZ_SR", binname, name, 1.20)

                        if e.name.count('TTXNoZ'):      c.specifyUncertainty('other',      binname, name, 1.25)
                        #if e.name.count('TZX'):      c.specifyUncertainty('TZX',      binname, name, 1.25)

                        #MC bkg stat (some condition to neglect the smaller ones?)
                        uname = 'Stat_'+binname+'_'+name
                        c.addUncertainty(uname, 'lnN')
                        c.specifyUncertainty(uname, binname, name, 1 + (expected.sigma/expected.val) * uncScale if expected.val>0 else 1)


                #signal
                eSignal.isSignal = True
                e = eSignal
                
                if fastSim:
                    if args.signal == 'T2tt': 
                        signalSetup = setup.sysClone(sys={'reweight':['reweight_nISR', 'reweightLeptonFastSimSF']}) # added reweightLeptonFastSimSF in the tuples?
                    else:
                        signalSetup = setup.sysClone(sys={'reweight':[ 'reweightLeptonFastSimSF'], 'remove':[]}) # added reweightLeptonFastSimSF in the tuples?
                    signal = e.cachedEstimate(r, channel, signalSetup)
                    # need MET Significance with gen MET for this
                    #signal = 0.5 * (e.cachedEstimate(r, channel, signalSetup) + e.cachedEstimate(r, channel, signalSetup.sysClone({'selectionModifier':'GenMET'}))) # genMET modifier -> what to do for legacy?
                else:
                    signalSetup = setup.sysClone(sys={'reweight':['reweight_nISR'], 'remove':[]}) 
                    signal = e.cachedEstimate(r, channel, signalSetup)

                signal = signal * args.scale

                #if niceName.count('controlTTZ') and signal.val<0.01: signal.val = 0.001 # to avoid failing of the fit
                #if niceName.count('controlDY') and signal.val<0.01: signal.val = 0.001 # to avoid failing of the fit
                c.specifyExpectation(binname, 'signal', signal.val*xSecScale )

                logger.info("Signal expectation: %s", signal.val*xSecScale)

                if signal.val>0:
                  if not fastSim:
                    c.specifyUncertainty('PDF',      binname, 'signal', 1 + getPDFUncSignal(s.name, r, channel))
                    if args.signal == "ttHinv":
                        # x-sec uncertainties for ttH: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBSMAt13TeV#ttH_Process
                        c.specifyUncertainty('xsec_QCD',      binname, 'signal', 1.092)
                        c.specifyUncertainty('xsec_PDF',      binname, 'signal', 1.036)
                  c.specifyUncertainty(PU,         binname, 'signal', 1 + e.PUSystematic(         r, channel, signalSetup).val )
                  c.specifyUncertainty(JEC,        binname, 'signal', e.JECSystematicAsym(        r, channel, signalSetup) )
                  c.specifyUncertainty(unclEn,     binname, 'signal', e.unclusteredSystematicAsym(r, channel, signalSetup) )
                  c.specifyUncertainty(JER,        binname, 'signal', e.JERSystematicAsym(        r, channel, signalSetup) ) #0.02 )
                  c.specifyUncertainty(SFb,        binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty(SFl,        binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty(trigger,    binname, 'signal', 1 + e.triggerSystematic(    r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonSFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonSIP3DSF', binname, 'signal', 1 + e.leptonSIP3DSFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonHit0SF', binname, 'signal', 1 + e.leptonHit0SFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('scale',    binname, 'signal', 1 + 0.02 )#getScaleUnc(eSignal.name, r, channel)) #had 0.3 for tests
                  c.specifyUncertainty('L1prefire', binname, 'signal', 1 + e.L1PrefireSystematic(   r, channel, setup).val * uncScale )

                  if fastSim: 
                    c.specifyUncertainty('leptonFS', binname, 'signal', 1 + e.leptonFSSystematic(    r, channel, signalSetup).val )
                    c.specifyUncertainty('btagFS',   binname, 'signal', 1 + e.btaggingSFFSSystematic(r, channel, signalSetup).val )
                    #c.specifyUncertainty('FSmet',    binname, 'signal', 1 + e.fastSimMETSystematic(  r, channel, signalSetup).val )
                    c.specifyUncertainty('FSmet',    binname, 'signal', 1 + 0.02)
                    #print "FS MET", e.fastSimMETSystematic(  r, channel, signalSetup).val
                    if args.signal == 'T2tt':
                        c.specifyUncertainty('isr',      binname, 'signal', 1 + e.nISRSystematic( r, channel, signalSetup).val)

                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 + signal.sigma/signal.val if signal.val>0 else 1 )
            
                else:
                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 )
                
                logger.info("Done with MC. Now working on observation.")
                ## Observation ##
                # expected
                if (args.expected or (not args.unblind and not niceName.count('control'))) and not args.signalInjection:
                    c.specifyObservation(binname, int(round(total_exp_bkg,0)))
                    logger.info("Expected observation: %s", int(round(total_exp_bkg,0)))
                # expected with signal injected
                elif args.signalInjection:
                    pseudoObservation = int(round(total_exp_bkg+signal.val,0))
                    c.specifyObservation(binname, pseudoObservation)
                    logger.info("Expected observation (signal is injected!): %s", pseudoObservation)
                # real observation (can be scaled for studies)
                else:
                    c.specifyObservation(binname, int(args.scale*observation.cachedObservation(r, channel, setup).val))
                    logger.info("Observation: %s", int(args.scale*observation.cachedObservation(r, channel, setup).val))
                
                # Muting (maybe obsolete??)
                if not args.controlDYVV and (signal.val<=0.01 and total_exp_bkg<=0.01 or total_exp_bkg<=0):# or (total_exp_bkg>300 and signal.val<0.05):
                  if verbose: print "Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
                  c.muted[binname] = True
                else:
                  if verbose: print "NOT Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)

        if year == 2016:
            lumiUncertainty = 1.025
        elif year == 2017:
            lumiUncertainty = 1.023
        elif year == 2018:
            lumiUncertainty = 1.025
        
        c.specifyFlatUncertainty(Lumi, lumiUncertainty)
        cardFileNameTxt     = c.writeToFile(cardFileName)
        cardFileNameShape   = c.writeToShapeFile(cardFileName.replace('.txt', '_shape.root'))
        cardFileName = cardFileNameTxt if args.useTxt else cardFileNameShape
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

    if not args.significanceScan:
        if useCache and not overWrite and limitCache.contains(sConfig):
          res = limitCache.get(sConfig)
        else:
          res = c.calcLimit(cardFileName)#, options="--run blind")
          if not args.skipFitDiagnostics:
              c.calcNuisances(cardFileName)
          limitCache.add(sConfig, res)
    else:
        if useCache and not overWrite and signifCache.contains(sConfig):
            res = signifCache.get(sConfig)
        else:
            res = c.calcSignif(cardFileName)
            signifCache.add(sConfig,res)
    

    ###################
    # extract the SFs #
    ###################
    if not args.useTxt and args.only and not args.skipFitDiagnostics:
        # Would be a bit more complicated with the classical txt files, so only automatically extract the SF when using shape based datacards
        from StopsDilepton.tools.getPostFit import getPrePostFitFromMLF
        
        # get the most signal region like bins
        if args.controlDYVV:
            iBinDYLow, iBinDYHigh       = 1,13
            iBinTTZLow, iBinTTZHigh     = 1,13
            iBinTTLow, iBinTTHigh       = 1,13
            iBinOtherLow, iBinOtherHigh = 1,13
        elif args.controlTTZ:
            iBinDYLow, iBinDYHigh       = 1,5
            iBinTTZLow, iBinTTZHigh     = 1,5
            iBinTTLow, iBinTTHigh       = 1,5
            iBinOtherLow, iBinOtherHigh = 1,5
        elif args.controlTT:
            iBinDYLow, iBinDYHigh       = 1,2
            iBinTTZLow, iBinTTZHigh     = 1,2
            iBinTTLow, iBinTTHigh       = 1,2
            iBinOtherLow, iBinOtherHigh = 1,2
        elif args.control2016:
            iBinDYLow, iBinDYHigh       = 6,18
            iBinTTZLow, iBinTTZHigh     = 1,5
            iBinTTLow, iBinTTHigh       = 1,18
            iBinOtherLow, iBinOtherHigh = 1,18
        elif args.controlAll:
            iBinDYLow, iBinDYHigh       = 8,20
            iBinTTZLow, iBinTTZHigh     = 3,7
            iBinTTLow, iBinTTHigh       = 1,2
            iBinOtherLow, iBinOtherHigh = 1,20
        elif args.fitAll:
            iBinDYLow, iBinDYHigh       = 21,46
            iBinTTZLow, iBinTTZHigh     = 21,46
            iBinTTLow, iBinTTHigh       = 21,46
            iBinOtherLow, iBinOtherHigh = 21,46
        else:
            iBinDYLow, iBinDYHigh       = 1,26
            iBinTTZLow, iBinTTZHigh     = 1,26
            iBinTTLow, iBinTTHigh       = 1,26
            iBinOtherLow, iBinOtherHigh = 1,26


        print cardFileName
        combineWorkspace = cardFileName.replace('shapeCard.txt','shapeCard_FD.root')
        print "Extracting fit results from %s"%combineWorkspace
        
        try:
            fitResults      = getPrePostFitFromMLF(combineWorkspace)
        except:
            fitResults = False

        if fitResults:
            preFitResults   = fitResults['results']['shapes_prefit']['Bin0']
            preFitShapes    = fitResults['hists']['shapes_prefit']['Bin0']
            postFitResults  = fitResults['results']['shapes_fit_b']['Bin0']
            postFitShapes   = fitResults['hists']['shapes_fit_b']['Bin0']
            

            top_prefit  = preFitResults['TTJets']
            top_postfit = postFitResults['TTJets']

            top_prefit_SR_err   = ROOT.Double()
            top_postfit_SR_err  = ROOT.Double()
            top_prefit_SR  =  preFitShapes['TTJets'].IntegralAndError(iBinTTLow, iBinTTHigh, top_prefit_SR_err)
            top_postfit_SR = postFitShapes['TTJets'].IntegralAndError(iBinTTLow, iBinTTHigh, top_postfit_SR_err)
            
            ttZ_prefit  = preFitResults['TTZ']
            ttZ_postfit = postFitResults['TTZ']

            ttZ_prefit_SR_err   = ROOT.Double()
            ttZ_postfit_SR_err  = ROOT.Double()
            ttZ_prefit_SR  = preFitShapes['TTZ'].IntegralAndError(iBinTTZLow, iBinTTZHigh, ttZ_prefit_SR_err)
            ttZ_postfit_SR = postFitShapes['TTZ'].IntegralAndError(iBinTTZLow, iBinTTZHigh, ttZ_postfit_SR_err)
            
            DY_prefit  = preFitResults['DY']
            DY_postfit = postFitResults['DY']

            DY_prefit_SR_err   = ROOT.Double()
            DY_postfit_SR_err  = ROOT.Double()
            DY_prefit_SR  = preFitShapes['DY'].IntegralAndError(iBinDYLow, iBinDYHigh, DY_prefit_SR_err)
            DY_postfit_SR = postFitShapes['DY'].IntegralAndError(iBinDYLow, iBinDYHigh, DY_postfit_SR_err)
            
            MB_prefit  = preFitResults['multiBoson']
            MB_postfit = postFitResults['multiBoson']
            
            MB_prefit_SR_err   = ROOT.Double()
            MB_postfit_SR_err  = ROOT.Double()
            MB_prefit_SR  = preFitShapes['multiBoson'].IntegralAndError(iBinDYLow, iBinDYHigh, MB_prefit_SR_err)
            MB_postfit_SR = postFitShapes['multiBoson'].IntegralAndError(iBinDYLow, iBinDYHigh, MB_postfit_SR_err)

            #other_prefit  = preFitResults['other']
            #other_postfit = postFitResults['other']

            #other_prefit_SR_err   = ROOT.Double()
            #other_postfit_SR_err  = ROOT.Double()
            #other_prefit_SR  = preFitShapes['other'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_prefit_SR_err)
            #other_postfit_SR = postFitShapes['other'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_postfit_SR_err)

            other_prefit  = preFitResults['TTXNoZ']
            other_postfit = postFitResults['TTXNoZ']

            other_prefit_SR_err   = ROOT.Double()
            other_postfit_SR_err  = ROOT.Double()
            other_prefit_SR  = preFitShapes['TTXNoZ'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_prefit_SR_err)
            other_postfit_SR = postFitShapes['TTXNoZ'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_postfit_SR_err)

            #TZX_prefit  = preFitResults['TZX']
            #TZX_postfit = postFitResults['TZX']

            #TZX_prefit_SR_err   = ROOT.Double()
            #TZX_postfit_SR_err  = ROOT.Double()
            #TZX_prefit_SR  = preFitShapes['TZX'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_prefit_SR_err)
            #TZX_postfit_SR = postFitShapes['TZX'].IntegralAndError(iBinOtherLow, iBinOtherHigh, other_postfit_SR_err)

            print
            print "## Scale Factors for backgrounds, integrated over ALL regions: ##"
            print "{:20}{:4.2f}{:3}{:4.2f}".format('top:',          (top_postfit/top_prefit).val, '+/-',  top_postfit.sigma/top_postfit.val)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('ttZ:',          (ttZ_postfit/ttZ_prefit).val, '+/-',  ttZ_postfit.sigma/ttZ_postfit.val)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('Drell-Yan:',    (DY_postfit/DY_prefit).val,   '+/-',  DY_postfit.sigma/DY_postfit.val)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('multiBoson:',   (MB_postfit/MB_prefit).val,   '+/-',  MB_postfit.sigma/MB_postfit.val)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('other:',        (other_postfit/other_prefit).val, '+/-',  other_postfit.sigma/other_postfit.val)
            #print "{:20}{:4.2f}{:3}{:4.2f}".format('TZX:',          (TZX_postfit/TZX_prefit).val, '+/-',  TZX_postfit.sigma/TZX_postfit.val)

            print
            print "## Scale Factors for backgrounds, integrated over dedicated control regions: ##" if not args.fitAll else "## Scale Factors for backgrounds, integrated over the signal regions: ##"
            print "{:20}{:4.2f}{:3}{:4.2f}".format('top:',          (top_postfit_SR/top_prefit_SR), '+/-',  top_postfit_SR_err/top_postfit_SR)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('ttZ:',          (ttZ_postfit_SR/ttZ_prefit_SR), '+/-',  ttZ_postfit_SR_err/ttZ_postfit_SR)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('Drell-Yan:',    (DY_postfit_SR/DY_prefit_SR),   '+/-',  DY_postfit_SR_err/DY_postfit_SR)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('multiBoson:',   (MB_postfit_SR/MB_prefit_SR),   '+/-',  MB_postfit_SR_err/MB_postfit_SR)
            print "{:20}{:4.2f}{:3}{:4.2f}".format('other:',        (other_postfit_SR/other_prefit_SR), '+/-',  other_postfit_SR_err/other_postfit_SR)
            #print "{:20}{:4.2f}{:3}{:4.2f}".format('TZX:',          (TZX_postfit_SR/TZX_prefit_SR), '+/-',  TZX_postfit_SR_err/TZX_postfit_SR)

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


######################################
# Load the signals and run the code! #
######################################

if args.signal == "T2tt":
    if year == 2016:
        if args.fullSim:
             from StopsDilepton.samples.nanoTuples_Summer16_FullSimSignal_postProcessed import signals_T2tt as jobs
        else:
            data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
            postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
            from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt as jobs
    elif year == 2017:
        if args.fullSim:
             from StopsDilepton.samples.nanoTuples_Fall17_FullSimSignal_postProcessed import signals_T2tt as jobs
        else:
            data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
            postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
            from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt as jobs
    elif year == 2018:
        if args.fullSim:
             from StopsDilepton.samples.nanoTuples_Autumn18_FullSimSignal_postProcessed import signals_T2tt as jobs
        else:
            data_directory              = '/afs/hephy.at/data/cms07/nanoTuples/'
            postProcessing_directory    = 'stops_2018_nano_v0p21/dilep/'
            from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt as jobs

if args.signal == "T2bW":
    if year == 2016:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW as jobs
    elif year == 2017:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2bW as jobs
    elif year == 2018:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2bW as jobs

if args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":
    if year == 2016:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
    elif year == 2017:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
    elif year == 2018:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs


if args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":
    if year == 2016:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
    elif year == 2017:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
    elif year == 2018:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs


if args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
    if year == 2016:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs
    elif year == 2017:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs
    elif year == 2018:
        data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
        postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs

#for j, job in enumerate(jobs):
#    print j, job.name

if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        
        jobNames = [ x.name for x in jobs ]
        #print jobNames
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)

# FIXME: removing 1052_0 from list
for i, j in enumerate(jobs):
    if j.name == "T8bbllnunu_XCha0p5_XSlep0p05_1052_0":
        print "~removing ", j.name
        del jobs[i]

results = map(wrapper, jobs)
results = [r for r in results if r]


#########################################################################################
# Process the results. Make 2D hists for SUSY scans, or table for the DM interpretation #
#########################################################################################

limitPrefix = args.signal
if args.significanceScan:
  limitResultsFilename = os.path.join(baseDir, 'limits', args.signal, limitPrefix,'signifResults.root')
else:
  limitResultsFilename = os.path.join(baseDir, 'limits', args.signal, limitPrefix,'limitResults.root')

## new try, other thing is buggy
def toGraph2D(name,title,length,x,y,z):
    result = ROOT.TGraph2D(length)
    result.SetName(name)
    result.SetTitle(title)
    for i in range(length):
        result.SetPoint(i,x[i],y[i],z[i])
    h = result.GetHistogram()
    h.SetMinimum(min(z))
    h.SetMaximum(max(z))
    c = ROOT.TCanvas()
    result.Draw()
    del c
    #res = ROOT.TGraphDelaunay(result)
    return result

mStop_list = []
mLSP_list  = []
exp_list   = []
obs_list   = []
exp_up_list   = []
exp_down_list   = []

for r in results:
    s, res = r
    mStop, mNeu = s
    #if mStop%50>0: continue
    #if mNeu%50>0 and not mNeu>(mStop-125): continue
    mStop_list.append(mStop)
    mLSP_list.append(mNeu)
    exp_list.append(res['0.500'])
    exp_up_list.append(res['0.160'])
    exp_down_list.append(res['0.840'])
    obs_list.append(res['-1.000'])

scatter         = ROOT.TGraph(len(mStop_list))
scatter.SetName('scatter')
for i in range(len(mStop_list)):
    scatter.SetPoint(i,mStop_list[i],mLSP_list[i])

exp_graph       = toGraph2D('exp','exp',len(mStop_list),mStop_list,mLSP_list,exp_list)
exp_up_graph    = toGraph2D('exp_up','exp_up',len(mStop_list),mStop_list,mLSP_list,exp_up_list)
exp_down_graph  = toGraph2D('exp_down','exp_down',len(mStop_list),mStop_list,mLSP_list,exp_down_list)
obs_graph       = toGraph2D('obs','obs',len(mStop_list),mStop_list,mLSP_list,obs_list)

outfile = ROOT.TFile(limitResultsFilename, "recreate")
scatter        .Write()
exp_graph      .Write()
exp_down_graph .Write()
exp_up_graph   .Write()
obs_graph      .Write()
outfile.Close()

print limitResultsFilename

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
