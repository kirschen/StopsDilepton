#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
#parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--noSystematics",         dest="noSystematics",         default = False,             action="store_true", help="no systematics?")
parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option("--year",                  dest="year",                  default=2016, type="int",    action="store",      help="Which year?")
#parser.add_option("--nThreads",              dest="nThreads",              default=8, type="int",       action="store",      help="How many threads?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option("--control",               dest="control",               default=None,                action='store',      choices=[None, "DY", "VV", "DYVV", "TTZ1", "TTZ2", "TTZ3", "TTZ4", "TTZ5"], help="For CR region?")
parser.add_option("--useGenMet",             dest="useGenMet",             default=False,               action='store_true', help="use genMET instead of recoMET, used for signal studies")
parser.add_option("--overwrite",             dest="overwrite",             default=False,               action='store_true', help="overwrite existing results?")
parser.add_option("--aggregate",             dest="aggregate",             default=False,               action='store_true', help="run over aggregated signal regions")
parser.add_option("--all",                   dest="all",                   default=False,               action='store_true', help="Run over all SR and CR?")
parser.add_option('--dpm',                   dest='dpm',                   default=False,               action='store_true', help='Use dpm?')

(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import channels, allChannels, trilepChannels
from StopsDilepton.analysis.estimators   import *
from StopsDilepton.analysis.regions      import regionsLegacy, noRegions, regions2016

if options.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

# Logging
import Analysis.Tools.logger as logger
logger  = logger.get_logger(options.logLevel, logFile = None)

import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import Analysis.Tools.logger as logger_an
logger_an = logger_an.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger('INFO', logFile = None )


from StopsDilepton.analysis.Setup import Setup

setup = Setup(year=options.year)

allRegions = noRegions if (options.control and options.control.count('TTZ')) else regionsLegacy #regions2016
if options.aggregate: allRegions = regionsAgg

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation

# signals, so far only T2tt
signals_T2tt = []
#postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
#from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed    import signals_T2tt
#from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed    import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5, signals_T8bbllnunu_XCha0p5_XSlep0p95
#from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
#allEstimators += [ MCBasedEstimate(name=s.name, sample={channel:s for channel in channels + trilepChannels}) for s in signals_TTbarDM + signals_T2tt + signals_T8bbllnunu_XCha0p5_XSlep0p5 + signals_T8bbllnunu_XCha0p5_XSlep0p05 + signals_T8bbllnunu_XCha0p5_XSlep0p95]

estimators = estimatorList(setup)
allEstimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TZX', 'TTXNoZ', 'triBoson', 'diBoson', 'WW', 'ZZ']) # replaced other
allEstimators += [ MCBasedEstimate(name=s.name, sample={channel:s for channel in channels + trilepChannels}) for s in signals_T2tt ]


# Select estimate
if not options.selectEstimator == 'Data':
    estimate = next((e for e in allEstimators if e.name == options.selectEstimator), None)
    estimate.isData = False
else:
    estimate = DataObservation(name='Data', sample=setup.samples['Data'], cacheDir=setup.defaultCacheDir())
    estimate.isSignal = False
    estimate.isData   = True

if not estimate:
  logger.warn(options.selectEstimator + " not known")
  exit(0)


if estimate.name.count('T2tt') or estimate.name.count('TTbarDM') or estimate.name.count('T8bbllnunu'): estimate.isSignal = True

isFastSim = estimate.name.count('T2tt')
isFastSim = estimate.name.count('T8bbllnunu')
if isFastSim:
  setup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})


if options.control:
  if   options.control == "DY":   setup = setup.sysClone(parameters={'zWindow' : 'onZ', 'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': True})
  elif options.control == "VV":   setup = setup.sysClone(parameters={'zWindow' : 'onZ', 'nBTags':(0,0 ), 'dPhi': True,  'dPhiInv': False})
  elif options.control == "DYVV": setup = setup.sysClone(parameters={'zWindow' : 'onZ', 'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False, 'metSigMin' : 12})
  elif options.control == "TTZ1": setup = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(2,2),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
  elif options.control == "TTZ2": setup = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
  elif options.control == "TTZ3": setup = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
  elif options.control == "TTZ4": setup = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
  elif options.control == "TTZ5": setup = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})


setup.verbose=True

def wrapper(args):
        r,channel,setup = args
        res = estimate.cachedEstimate(r, channel, setup, save=True, overwrite=options.overwrite)
        return (estimate.uniqueKey(r, channel, setup), res )

estimate.initCache(setup.defaultCacheDir())

jobs=[]
for channel in (trilepChannels if (options.control and options.control.count('TTZ')) else channels):
    for (i, r) in enumerate(allRegions):
        if options.selectRegion is not None and options.selectRegion != i: continue
        jobs.append((r, channel, setup))
        if not estimate.isData and not options.noSystematics:
            if estimate.isSignal: jobs.extend(estimate.getSigSysJobs(r, channel, setup, isFastSim))
            else:                 jobs.extend(estimate.getBkgSysJobs(r, channel, setup))


#if options.noMultiThreading: 
results = map(wrapper, jobs)
#else:
#    from multiprocessing import Pool
#    pool = Pool(processes=options.nThreads)
#    results = pool.map(wrapper, jobs)
#    pool.close()
#    pool.join()

for channel in (['all'] if ((options.control and options.control.count('TTZ')) or options.aggregate) else ['SF','all']):
    for (i, r) in enumerate(allRegions):
        if options.selectRegion is not None and options.selectRegion != i: continue
        if options.useGenMet: estimate.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'genMet'}), save=True)
        else: estimate.cachedEstimate(r, channel, setup, save=True, overwrite=options.overwrite)
        if not estimate.isData and not options.noSystematics:
            if estimate.isSignal: map(lambda args:estimate.cachedEstimate(*args, save=True, overwrite=options.overwrite), estimate.getSigSysJobs(r, channel, setup, isFastSim))
            else:                 map(lambda args:estimate.cachedEstimate(*args, save=True, overwrite=options.overwrite), estimate.getBkgSysJobs(r, channel, setup))
        logger.info('Done with region: %s', r)
    logger.info('Done with channel: %s', channel)
logger.info('Done.')
