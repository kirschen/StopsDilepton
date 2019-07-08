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
argParser.add_argument("--controlTT",      default = False, action = "store_true", help="Fits for TT CR (MT2ll<100)")
argParser.add_argument("--controlAll",     default = False, action = "store_true", help="Fits for all CRs")
argParser.add_argument("--fitAll",         default = False, action = "store_true", help="Fits SR and CR together")
argParser.add_argument("--aggregate",      default = False, action = "store_true", help="Use aggregated signal regions")
argParser.add_argument("--expected",       default = False, action = "store_true", help="Use sum of backgrounds instead of data.")
argParser.add_argument("--DMsync",         default = False, action = "store_true", help="Use two regions for MET+X syncing")
argParser.add_argument("--noSignal",       default = False, action = "store_true", help="Don't use any signal (force signal yield to 0)?")
argParser.add_argument("--useTxt",         default = False, action = "store_true", help="Use txt based cardFiles instead of root/shape based ones?")
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
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

# Load from DPM?
if args.dpm:
    data_directory      = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

from StopsDilepton.analysis.SetupHelpers    import channels, trilepChannels
from StopsDilepton.analysis.estimators      import *
from StopsDilepton.analysis.Setup           import Setup
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions         import regionsLegacy, noRegions, regionsAgg
#regionsLegacy, noRegions, regionsS, regionsAgg, regionsDM, regionsDM1, regionsDM2, regionsDM3, regionsDM4, regionsDM5, regionsDM6, regionsDM7
from StopsDilepton.analysis.Cache           import Cache
from copy import deepcopy

setup = Setup(year=year)

# Define CR
setupDYVV = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False,  'zWindow': 'onZ'})
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
setup.estimators     = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other']) # no data-driven estimation atm
setupDYVV.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ1.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ2.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ3.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ4.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ5.estimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTT.estimators   = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])

if args.fitAll:        setups = [setupTT, setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5, setupDYVV, setup]
elif args.controlDYVV: setups = [setupDYVV]
elif args.controlTTZ:  setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
elif args.controlTT:   setups = [setupTT]
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
elif args.controlDYVV:      subDir += 'controlDYVV'
elif args.controlTTZ:       subDir += 'controlTTZ'
elif args.controlTT:        subDir += 'controlTT'
elif args.controlAll:       subDir += 'controlAll'
elif args.significanceScan: subDir += 'significance'
else:                       subDir += 'signalOnly'

baseDir = os.path.join(setup.analysis_results, str(year), subDir)

limitDir    = os.path.join(baseDir, 'cardFiles', args.signal + args.extension, 'expected' if args.expected else 'observed')
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

if   args.signal == "T2tt":                         fastSim = True
elif args.signal == "T2bW":                         fastSim = True
elif args.signal == "T2bt":                         fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": fastSim = True
elif args.signal == "TTbarDM":                      fastSim = False
elif args.signal == "ttHinv":                       fastSim = False

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

    cardFileName = os.path.join(limitDir, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
        counter=0
        c.reset()
        c.setPrecision(3)
        shapeString = 'lnN' if args.useTxt else 'shape'
        # experimental
        c.addUncertainty('PU',         shapeString)
        c.addUncertainty('topPt',      shapeString)
        c.addUncertainty('JEC',        shapeString)
        c.addUncertainty('unclEn',     shapeString)
        c.addUncertainty('JER',        shapeString)
        c.addUncertainty('SFb',        shapeString)
        c.addUncertainty('SFl',        shapeString)
        c.addUncertainty('trigger',    shapeString)
        c.addUncertainty('leptonSF',   shapeString)
        # theory (PDF, scale, ISR)
        c.addUncertainty('scale',      shapeString)
        c.addUncertainty('scaleTT',    shapeString)
        c.addUncertainty('scaleTTZ',   shapeString)
        c.addUncertainty('PDF',        shapeString)
        c.addUncertainty('xsec_PDF',   shapeString)
        c.addUncertainty('xsec_QCD',   shapeString)
        c.addUncertainty('isr',        shapeString)
        # only in SRs
        c.addUncertainty('topGaus',    shapeString)
        c.addUncertainty('topNonGaus', shapeString)
        c.addUncertainty('topFakes',   shapeString)
        c.addUncertainty('DY_SR',      shapeString)
        c.addUncertainty('ttZ_SR',     shapeString)
        # all regions, lnN
        c.addUncertainty('topNorm',    'lnN')
        c.addUncertainty('multiBoson', 'lnN')
        c.addUncertainty('DY',         'lnN')
        c.addUncertainty('ttZ',        'lnN')
        c.addUncertainty('other',      'lnN')
        if fastSim:
            c.addUncertainty('btagFS',   shapeString)
            c.addUncertainty('leptonFS', shapeString)
            c.addUncertainty('FSmet',    shapeString)
            c.addUncertainty('PUFS',     shapeString)

        for setup in setups:
          eSignal     = MCBasedEstimate(name=s.name, sample=s, cacheDir=setup.defaultCacheDir()) # {channel:s for channel in channels+trilepChannels}
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
                if setup == setupTT:   niceName += "_controlTTBar"
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators][1:] + [ 'TTJetsG', 'TTJetsNG', 'TTJetsF' ], niceName)
#                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators], niceName)
                for e in setup.estimators:
                  name = e.name.split('-')[0]
                  expected = e.cachedEstimate(r, channel, setup)
                  expected = expected * args.scale
                  total_exp_bkg += expected.val
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
                    #logger.info("Splitting SRs into ttbar and ttZ dominated regions at signal region %s",divider)
                    if setup.regions == [regionsLegacy[0]]:
                        norm_G  = 0.98
                        norm_NG = 0.01
                        norm_F  = 0.01
                    elif (setup.regions != noRegions and (r in setup.regions[divider:])):
                        norm_G  = 0.25
                        norm_NG = 0.50
                        norm_F  = 0.25
                    else:
                        norm_G  = 0.55
                        norm_NG = 0.44
                        norm_F  = 0.01
                    TT_SF = 1
                    if TT_SF != 1: logger.warning("Scaling ttbar background by %s", TT_SF)
                    c.specifyExpectation(binname, 'TTJetsG',  norm_G  * expected.val * TT_SF)
                    c.specifyExpectation(binname, 'TTJetsNG', norm_NG * expected.val * TT_SF)
                    c.specifyExpectation(binname, 'TTJetsF',  norm_F  * expected.val * TT_SF)
                  elif e.name.count("DY"):
                    DY_SF = 1#.31 + 0.19*(-1)
                    c.specifyExpectation(binname, name, expected.val*DY_SF)
                    if DY_SF != 1: logger.warning("Scaling DY background by %s", DY_SF)
                  elif e.name.count("TTZ"):
                    TTZ_SF = 1
                    c.specifyExpectation(binname, name, expected.val*TTZ_SF)
                    if TTZ_SF != 1: logger.warning("Scaling ttZ background by %s", TTZ_SF)
                  else:
                    c.specifyExpectation(binname, name, expected.val)

                  if expected.val>0 or True:
                      if e.name.count('TTJets'):
                        names = [ 'TTJetsG', 'TTJetsNG', 'TTJetsF' ]
                      else:
                        names = [name]
                      for name in names:
                        if 'TTJets' in name: uncScale = 1./sqrt(norm_G**2 + norm_NG**2 + norm_F**2) # scaling of uncertainties for ttbar so that the total uncertainty remains unchanged
                        else: uncScale = 1
                        #print "Process", name, "uncertainty scale", uncScale
                        c.specifyUncertainty('PU',       binname, name, 1 + e.PUSystematic(         r, channel, setup).val * uncScale )
                        if not e.name.count("TTJets") and not niceName.count('controlTTBar'):
                        #if not niceName.count('controlTTBar'):
                            c.specifyUncertainty('JEC',      binname, name, 1 + e.JECSystematic(        r, channel, setup).val * uncScale )
                            c.specifyUncertainty('unclEn',   binname, name, 1 + e.unclusteredSystematic(r, channel, setup).val * uncScale ) # could remove uncertainties in ttbar CR
                            c.specifyUncertainty('JER',      binname, name, 1 + 0.03 )#e.JERSystematic(        r, channel, setup).val * uncScale )
                            c.specifyUncertainty('topPt',    binname, name, 1 + 0.02 )#e.topPtSystematic(      r, channel, setup).val * uncScale )
                            c.specifyUncertainty('SFb',      binname, name, 1 + e.btaggingSFbSystematic(r, channel, setup).val * uncScale )
                            c.specifyUncertainty('SFl',      binname, name, 1 + e.btaggingSFlSystematic(r, channel, setup).val * uncScale )
                            c.specifyUncertainty('trigger',  binname, name, 1 + e.triggerSystematic(    r, channel, setup).val * uncScale ) # could remove uncertainties in ttbar CR
                            c.specifyUncertainty('leptonSF', binname, name, 1 + e.leptonSFSystematic(   r, channel, setup).val * uncScale ) # could remove uncertainties in ttbar CR
                        
                        if e.name.count('TTJets'):
                            c.specifyUncertainty('scaleTT', binname, name, 1 + 0.02)#getScaleUncBkg('TTLep_pow', r, channel,'TTLep_pow'))
                            c.specifyUncertainty('PDF',     binname, name, 1 + 0.02)#getPDFUnc('TTLep_pow', r, channel,'TTLep_pow'))
                            #c.specifyUncertainty('top', binname, name, 2 if (setup.regions != noRegions and r == setup.regions[-1]) else 1.5)

                        if name == 'TTJetsG':
                            if not niceName.count('controlTTBar') and niceName.count("DYVV")==0 and niceName.count("TTZ")==0:
                                c.specifyUncertainty('topGaus',  binname, name, 1.15) # avoid constraining of uncertainties in the ttbar CR
                            c.specifyUncertainty('topNorm',  binname, name, 1.15)

                        if name == 'TTJetsNG':
                            if not niceName.count('controlTTBar') and niceName.count("DYVV")==0 and niceName.count("TTZ")==0:
                                c.specifyUncertainty('topNonGaus', binname, name, 1.30) # avoid constraining of uncertainties in the ttbar CR
                            c.specifyUncertainty('topNorm',  binname, name, 1.15)

                        if name == 'TTJetsF':
                            if not niceName.count('controlTTBar'):
                                c.specifyUncertainty('topFakes', binname, name, 1.50) # avoid constraining of uncertainties in the ttbar CR
                            c.specifyUncertainty('topNorm',  binname, name, 1.15)

                        if e.name.count('multiBoson'): c.specifyUncertainty('multiBoson', binname, name, 1.50)

                        if e.name.count('DY'):
                            c.specifyUncertainty('DY',         binname, name, 1.5)#1/(1+0.5))#1.5
                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0 and niceName.count("TTBar")==0:
                                c.specifyUncertainty("DY_SR", binname, name, 1.25)

                        if e.name.count('TTZ'):
                            c.specifyUncertainty('ttZ',        binname, name, 1.2)
                            c.specifyUncertainty('scaleTTZ',binname, name, 1 + 0.02) #getScaleUncBkg('TTZ', r, channel,'TTZ'))
                            c.specifyUncertainty('PDF',     binname, name, 1 + 0.02) #getPDFUnc('TTZ', r, channel,'TTZ'))

                            if r in setup.regions and niceName.count("DYVV")==0 and niceName.count("TTZ")==0 and niceName.count("TTBar")==0:
                                c.specifyUncertainty("ttZ_SR", binname, name, 1.20)

                        if e.name.count('other'):      c.specifyUncertainty('other',      binname, name, 1.25)

                        #MC bkg stat (some condition to neglect the smaller ones?)
                        uname = 'Stat_'+binname+'_'+name
                        c.addUncertainty(uname, 'lnN')
                        c.specifyUncertainty(uname, binname, name, 1 + (expected.sigma/expected.val) * uncScale if expected.val>0 else 1)

                if args.expected:
                    c.specifyObservation(binname, int(round(total_exp_bkg,0)))
                    logger.info("Expected observation: %s", int(round(total_exp_bkg,0)))
                else:
                    c.specifyObservation(binname, int(args.scale*observation.cachedObservation(r, channel, setup).val))
                    logger.info("Observation: %s", int(args.scale*observation.cachedObservation(r, channel, setup).val))

                #signal
                eSignal.isSignal = True
                e = eSignal
                #eSignal.isSignal = True
                if fastSim:
                    signalSetup = setup.sysClone(sys={'reweight':['reweight_nISR'], 'remove':[]}) # reweightLeptonFastSimSF
                    #signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})
                    signalSetup = setup.sysClone()
                    signal = e.cachedEstimate(r, channel, signalSetup)
                    #signal = 0.5 * (e.cachedEstimate(r, channel, signalSetup) + e.cachedEstimate(r, channel, signalSetup.sysClone({'selectionModifier':'genMet'}))) # genMET modifier -> what to do for legacy?
                else:
                    signalSetup = setup.sysClone()
                    signal = e.cachedEstimate(r, channel, signalSetup)

                signal = signal * args.scale

                #if args.noSignal:
                #    signal.val = 0
                #    signal.sigma = 1

                #signal.val, signal.sigma = 0.1, 1.0

                if niceName.count('controlTTZ'): signal.val = 0.001 # to avoid failing of the fit
                c.specifyExpectation(binname, 'signal', signal.val*xSecScale )


                if signal.val>0 or True:
                  if not fastSim:
                    c.specifyUncertainty('PU',       binname, 'signal', 1 + e.PUSystematic(         r, channel, signalSetup).val )
                    c.specifyUncertainty('PDF',      binname, 'signal', 1 + getPDFUncSignal(s.name, r, channel))
                    if args.signal == "ttHinv":
                        # x-sec uncertainties for ttH: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBSMAt13TeV#ttH_Process
                        c.specifyUncertainty('xsec_QCD',      binname, 'signal', 1.092)
                        c.specifyUncertainty('xsec_PDF',      binname, 'signal', 1.036)
                  c.specifyUncertainty('JEC',      binname, 'signal', 1 + e.JECSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('unclEn',   binname, 'signal', 1 + e.unclusteredSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('JER',      binname, 'signal', 1 + 0.02 )#e.JERSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('SFb',      binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('SFl',      binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('trigger',  binname, 'signal', 1 + e.triggerSystematic(    r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonSFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('scale',    binname, 'signal', 1 + 0.02 )#getScaleUnc(eSignal.name, r, channel)) #had 0.3 for tests
                  if not args.signal == "ttHinv": c.specifyUncertainty('isr',      binname, 'signal', 1 + 0.03 )#abs(getIsrUnc(  eSignal.name, r, channel)))

                  if fastSim: 
                    c.specifyUncertainty('leptonFS', binname, 'signal', 1 + 0.02 )#e.leptonFSSystematic(    r, channel, signalSetup).val )
                    c.specifyUncertainty('btagFS',   binname, 'signal', 1 + 0.02 )#e.btaggingSFFSSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('FSmet',    binname, 'signal', 1 + 0.02 )#e.fastSimMETSystematic(  r, channel, signalSetup).val )
                    c.specifyUncertainty('PUFS',     binname, 'signal', 1 + 0.02 )#e.fastSimPUSystematic(   r, channel, signalSetup).val )

                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 + signal.sigma/signal.val if signal.val>0 else 1 )
            
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
        
        print cardFileName
        combineWorkspace = cardFileName.replace('shapeCard.txt','shapeCard_FD.root')
        print "Extracting fit results from %s"%combineWorkspace
        
        postFitResults = getPrePostFitFromMLF(combineWorkspace)
        
        top_prefit  = postFitResults['results']['shapes_prefit']['Bin0']['TTJetsF'] + postFitResults['results']['shapes_prefit']['Bin0']['TTJetsG'] + postFitResults['results']['shapes_prefit']['Bin0']['TTJetsNG']
        top_postfit = postFitResults['results']['shapes_fit_b']['Bin0']['TTJetsF'] + postFitResults['results']['shapes_fit_b']['Bin0']['TTJetsG'] + postFitResults['results']['shapes_fit_b']['Bin0']['TTJetsNG']
        
        ttZ_prefit  = postFitResults['results']['shapes_prefit']['Bin0']['TTZ']
        ttZ_postfit = postFitResults['results']['shapes_fit_b']['Bin0']['TTZ']
        
        DY_prefit  = postFitResults['results']['shapes_prefit']['Bin0']['DY']
        DY_postfit = postFitResults['results']['shapes_fit_b']['Bin0']['DY']
        
        MB_prefit  = postFitResults['results']['shapes_prefit']['Bin0']['multiBoson']
        MB_postfit = postFitResults['results']['shapes_fit_b']['Bin0']['multiBoson']
        
        other_prefit  = postFitResults['results']['shapes_prefit']['Bin0']['other']
        other_postfit = postFitResults['results']['shapes_fit_b']['Bin0']['other']

        print
        print "## Scale Factors for backgrounds: ##"
        print "{:20}{:4.2f}{:3}{:4.2f}".format('top:',          (top_postfit/top_prefit).val, '+/-',  top_postfit.sigma/top_postfit.val)
        print "{:20}{:4.2f}{:3}{:4.2f}".format('ttZ:',          (ttZ_postfit/ttZ_prefit).val, '+/-',  ttZ_postfit.sigma/ttZ_postfit.val)
        print "{:20}{:4.2f}{:3}{:4.2f}".format('Drell-Yan:',    (DY_postfit/DY_prefit).val,   '+/-',  DY_postfit.sigma/DY_postfit.val)
        print "{:20}{:4.2f}{:3}{:4.2f}".format('multiBoson:',   (MB_postfit/MB_prefit).val,   '+/-',  MB_postfit.sigma/MB_postfit.val)
        print "{:20}{:4.2f}{:3}{:4.2f}".format('other:',        (other_postfit/other_prefit).val, '+/-',  other_postfit.sigma/other_postfit.val)


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
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2016_nano_v0p13/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt as jobs
    elif year == 2017:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2017_nano_v0p13/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt as jobs
    elif year == 2018:
        data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
        postProcessing_directory    = 'stops_2018_nano_v0p13/dilep/'
        from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt as jobs

if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        jobNames = [ x.name for x in jobs ]
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)

results = map(wrapper, jobs)
results = [r for r in results if r]


#########################################################################################
# Process the results. Make 2D hists for SUSY scans, or table for the DM interpretation #
#########################################################################################

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
