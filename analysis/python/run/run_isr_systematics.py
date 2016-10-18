#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
#parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
#parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option("--signal",               dest='signal',  action='store', default='T2tt',    choices=["T2tt","TTbarDM"],                                                                                 help="which signal?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option('--overwrite',            dest="overwrite", default = False, action = "store_true", help="Overwrite existing output files, bool flag set to True  if used")
(options, args) = parser.parse_args()

# Standard imports
import pickle
import ROOT
import os
import sys

# Analysis
from StopsDilepton.analysis.SetupHelpers import channels, allChannels
from StopsDilepton.analysis.estimators   import setup
from StopsDilepton.analysis.regions      import regions80X, superRegion, superRegion140, regions80X_2D
from StopsDilepton.analysis.u_float import u_float

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

if options.signal=='T2tt':
    isFastSim         = True
    setup             = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']})
    setup.verbose     = True
elif options.signal == 'TTbarDM':
    isFastSim         = False
    setup.verbose     = True

regions = regions80X + regions80X_2D + superRegion140 #Use all the regions that are used in the limit setting

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate

from StopsDilepton.tools.user import analysis_results

ofile = os.path.join( analysis_results, "systematics", "isr_%s.pkl"%options.signal )
if not options.overwrite:
    if os.path.exists( ofile ):
        logger.warning( "Found file %s. Exiting. Use --overwrite if you want.", ofile ) 
        sys.exit(0)

norm_file = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/80X_v12/systematics/isrSignalSysNormalization_%s.pkl"%options.signal
normalization_corrections = pickle.load(file( norm_file ))
logger.info( "Loaded ISR normalization file %s", norm_file )

if options.signal == "T2tt":
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
    signals = signals_T2tt
    for s in signals:
        s.isFastSim = True
        s.is76X     = False

elif options.signal == "TTbarDM":
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
    signals = signals_TTbarDM
    for s in signals:
        s.isFastSim = False
        s.is76X     = False

nominal     = "(1)"
from StopsDilepton.analysis.robert.helpers import isrWeight
wgts        = [ nominal, isrWeight ]

signalEstimators = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals ]

results = {}

isr_systematics = {}
for estimate in signalEstimators:
    logger.info("Calculating ISR  uncertainty for signal %s", estimate.name)
    estimate.initCache("/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/80X_for_ISR/")

    def wrapper(args):
            r,channel,setup = args
            res = estimate.cachedEstimate(r, channel, setup, save=True)
            return (estimate.uniqueKey(r, channel, setup), res )

    jobs=[]
    for channel in channels:
        for region in regions:
            #if options.selectRegion is not None and options.selectRegion != i: continue
            for wgt in wgts:
                jobs.append((region, channel, setup.sysClone(sys={'reweight':[wgt]})))

    if options.noMultiThreading: 
        results = map(wrapper, jobs)
    else:
        from multiprocessing import Pool
        pool = Pool(processes=8)
        results = pool.map(wrapper, jobs)
        pool.close()
        pool.join()

    # Make a dictionary from the results
    rd = {x[0]:x[1] for x in results} 

    s_ = estimate.sample.values()[0] # 
    if options.signal == "T2tt":
        masses = ( s_.mStop, s_.mNeu )
    elif options.signal == "TTbarDM":
        masses = ( s_.mChi, s_.mPhi )

    for r in regions:
        for c in channels+['SF', 'all']:
            l = []
            ref = estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[nominal]}) )
            if ref>0:
                var = normalization_corrections[masses]*estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[isrWeight]}) )
                
            isr_systematics[(estimate.name, r, c)] =  (var/ref).val - 1. if ref>0 else 0. 

if not os.path.exists(os.path.dirname(ofile)):
    os.makedirs(os.path.dirname(ofile))

pickle.dump( isr_systematics, file( ofile, 'w') )
logger.info( "Written output %s", ofile )
