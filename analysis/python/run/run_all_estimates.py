#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--skipIfCachefileExists", dest="skipIfCachefileExists", default = False,             action="store_true", help="skipIfCachefileExists?")
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--metSigMin",             dest="metSigMin",             default=5,    type="int",    action="store",      help="metSigMin?")
parser.add_option("--metMin",                dest="metMin",                default=80,   type="int",    action="store",      help="metMin?")
parser.add_option("--multiIsoWP",            dest="multiIsoWP",            default="",   type="string", action="store",      help="wpMu,wpEle")
parser.add_option("--relIso04",              dest="relIso04",              default=-1,   type=float,    action="store",      help="relIso04 cut?")
parser.add_option("--signal",                dest="signal",                default=None,                action="store",      help="which signal estimators?", choices=[None,"DM","T2tt","allT2tt"])
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.estimators import setup, allEstimators
from StopsDilepton.analysis.regions import defaultRegions, reducedRegionsA, reducedRegionsB, reducedRegionsAB, reducedRegionsNew, reducedRegionsC

setup.parameters['metMin']    = options.metMin
setup.parameters['metSigMin'] = options.metSigMin

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

allRegions = set(defaultRegions + reducedRegionsA + reducedRegionsB + reducedRegionsAB + reducedRegionsNew + reducedRegionsC)
if options.multiIsoWP!="":
    multiIsoWPs = ['VL', 'L', 'M', 'T', 'VT']
    wpMu, wpEle=options.multiIsoWP.split(',')
    from StopsDilepton.tools.objectSelection import multiIsoLepString
    setup.externalCuts.append(multiIsoLepString(wpMu, wpEle, ('l1_index','l2_index')))
    setup.prefixes.append('multiIso'+options.multiIsoWP.replace(',',''))

if options.relIso04>0:
    setup.externalCuts.append("&&".join(["LepGood_relIso04["+ist+"]<"+str(options.relIso04) for ist in ('l1_index','l2_index')]))
    setup.prefixes.append('relIso04sm'+str(int(100*options.relIso04)))

for e in allEstimators:
    e.initCache(setup.defaultCacheDir())

setup.verbose=True
#from multi_estimate import multi_estimate
from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *

if options.signal is None:
  signalEstimators = []
  isFastSim = False
elif options.signal == "DM":
  signalEstimators = [ MCBasedEstimate(name=s.name,    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in signals_TTDM ]
  isFastSim = False
elif options.signal == "T2tt":
  signalEstimators = [ MCBasedEstimate(name=s.name,    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in [T2tt_450_0] ]
  isFastSim = True
elif options.signal == "allT2tt":
  signalEstimators = [ MCBasedEstimate(name=s.name,    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in signals_T2tt ]
  isFastSim = True
else:
  raise Exception("Unknown signal estimator choice")

signalSetup = setup.sysClone(parameters={'useTriggers':False})

def wrapper(args):
        r,channel,setup = args
        res = estimate.cachedEstimate(r, channel, setup, save=False)
        return (estimate.uniqueKey(r, channel, setup), res )


for isSignal, estimators_ in [ [ True, signalEstimators ], [ False, allEstimators ] ]:
    for estimate in estimators_:
        setup_ = signalSetup if isSignal else setup
        if options.skipIfCachefileExists and estimate.cache.cacheFileLoaded:
            print "Cache file %s was loaded -> Skipping."%estimate.cache.filename
            continue
        jobs=[]
        for channel in ['MuMu' ,'EE', 'EMu']:
            for r in allRegions:
                jobs.append((r, channel, setup_))
                if isSignal:
                    jobs.extend(estimate.getSigSysJobs(r, channel, setup_, isFastSim))
                else:
                    jobs.extend(estimate.getBkgSysJobs(r, channel, setup_))

        if options.noMultiThreading: 
            results = map(wrapper, jobs)
        else:
            from multiprocessing import Pool
            pool = Pool(processes=6)
            results = pool.map(wrapper, jobs)
            pool.close()
            pool.join()

        for r in results:
            estimate.cache.add(*r, save=False)

        for channel in ['all']:
            for r in allRegions:
                estimate.cachedEstimate(r, channel, setup_, save=False)
                map(lambda args:estimate.cachedEstimate(*args, save=False), estimate.getBkgSysJobs(r, channel, setup_))
                if isSignal:
                    map(lambda args:estimate.cachedEstimate(*args, save=False), estimate.getSigSysJobs(r, channel, setup_, isFastSim))

        estimate.cache.save()
