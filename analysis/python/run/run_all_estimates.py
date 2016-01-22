from optparse import OptionParser
parser = OptionParser()
parser.add_option("--dontSkipIfCachefileExists", dest="dontSkipIfCachefileExists", default = False, action="store_true", help="dontSkipIfCachefileExists?")
parser.add_option("--metSigMin", dest="metSigMin", default=5, type="int", action="store", help="metSigMin?")
parser.add_option("--metMin", dest="metMin", default=80, type="int", action="store", help="metMin?")
parser.add_option("--multiIsoWP", dest="multiIsoWP", default="", type="string", action="store", help="wpMu,wpEle")
parser.add_option("--relIso04", dest="relIso04", default=-1, type=float, action="store", help="relIso04 cut?")
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.defaultAnalysis import setup, regions, bkgEstimators
setup.analysisOutputDir='/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test5'
setup.parameters['metMin'] = options.metMin
setup.parameters['metSigMin'] = options.metSigMin

if options.multiIsoWP!="":
  multiIsoWPs = ['VL', 'L', 'M', 'T', 'VT']
  wpMu, wpEle=options.multiIsoWP.split(',')
  from StopsDilepton.tools.objectSelection import multiIsoLepString
  setup.externalCuts.append(multiIsoLepString(wpMu, wpEle, ('l1_index','l2_index')))
  setup.prefixes.append('multiIso'+options.multiIsoWP.replace(',',''))

if options.relIso04>0:
  setup.externalCuts.append("&&".join(["LepGood_relIso04["+ist+"]<"+str(options.relIso04) for ist in ('l1_index','l2_index')]))
  setup.prefixes.append('relIso04sm'+str(int(100*options.relIso04)))

for e in bkgEstimators:
  e.initCache(setup.defaultCacheDir())

setup.verbose=True
#from multi_estimate import multi_estimate
from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_1l_postProcessed import *
#signalEstimators = [ MCBasedEstimate(name=s['name'],    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in [T2tt_450_0] ] #signals_T2tt ]
signalEstimators = [ MCBasedEstimate(name=s['name'],    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in signals_T2tt ]
signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']}, parameters={'useTriggers':False})

#estimate = signals_T2tt[0]['estimator']
#isSignal=True
#regions=regions[:1]
#bkgEstimators=[]
#signalEstimators = signalEstimators[:1]
#regions=regions[:1]

def wrapper(args):
    r,channel,setup = args
    res = estimate.cachedEstimate(r, channel, setup, save=False)
#    res = estimate._estimate(r, channel, setup)
    return (estimate.uniqueKey(r, channel, setup), res )

for isSignal, estimators_ in [ [ True, signalEstimators ], [ False, bkgEstimators ] ]:
  for estimate in estimators_:
    setup_ = signalSetup if isSignal else setup
    if not options.dontSkipIfCachefileExists and estimate.cache.cacheFileLoaded: 
      print "Cache file %s was loaded -> Skipping."%estimate.cache.filename
      continue
    jobs=[]
    for channel in ['MuMu' ,'EE', 'EMu']:
      for r in regions:
        jobs.append((r, channel, setup_))
        jobs.extend(estimate.getBkgSysJobs(r, channel, setup_))
        if isSignal:
          jobs.extend(estimate.getSigSysJobs(r, channel, setup_))

    from multiprocessing import Pool
    pool = Pool(processes=20)

    results = pool.map(wrapper, jobs)
    pool.close()
    pool.join()

    for r in results:
      estimate.cache.add(*r, save=False)

    for channel in ['all']:
      for r in regions:
        estimate.cachedEstimate(r, channel, setup_, save=False)
        map(lambda args:estimate.cachedEstimate(*args, save=False), estimate.getBkgSysJobs(r, channel, setup_))
        if isSignal:
          map(lambda args:estimate.cachedEstimate(*args, save=False), estimate.getSigSysJobs(r, channel, setup_))
    estimate.cache.save()
