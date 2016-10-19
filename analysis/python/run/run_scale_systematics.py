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
import ROOT
import os
import sys
import pickle

# Analysis
from StopsDilepton.analysis.SetupHelpers import channels, allChannels
from StopsDilepton.analysis.estimators   import setup
from StopsDilepton.analysis.regions      import regions80X, superRegion, superRegion140, regions80X_2D
from StopsDilepton.analysis.u_float      import u_float 
from StopsDilepton.analysis.Region       import Region 

isFastSim         = True
#setup             = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']})
setup.sys['reweight'] = [] #Fall15 doesn't have the reweights. Not needed.
setup.verbose     = True

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

regions = regions80X + regions80X_2D #Use all the regions that are used in the limit setting

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate

from StopsDilepton.tools.user import analysis_results

ofile = os.path.join( analysis_results, "systematics", "scale_%s.pkl" % options.signal )
if not options.overwrite:
    if os.path.exists( ofile ):
        logger.warning( "Found file %s. Exiting. Use --overwrite if you want.", ofile ) 
        sys.exit(0)

##  Information on scale variations:
#p10 https://indico.cern.ch/event/459797/contributions/1961581/attachments/1181555/1800214/mcaod-Feb15-2016.pdf 
#Scale variations:
#0<weight id="1001"> muR=0.10000E+01 muF=0.10000E+01 </weight>
#1<weight id="1002"> muR=0.10000E+01 muF=0.20000E+01 </weight>
#2<weight id="1003"> muR=0.10000E+01 muF=0.50000E+00 </weight>
#3<weight id="1004"> muR=0.20000E+01 muF=0.10000E+01 </weight>
#4<weight id="1005"> muR=0.20000E+01 muF=0.20000E+01 </weight>
#5<weight id="1006"> muR=0.20000E+01 muF=0.50000E+00 </weight>
#6<weight id="1007"> muR=0.50000E+00 muF=0.10000E+01 </weight>
#7<weight id="1008"> muR=0.50000E+00 muF=0.20000E+01 </weight>
#8<weight id="1009"> muR=0.50000E+00 muF=0.50000E+00 </weight>
#n.b \1001" is index 0 in the weights() vector

if options.signal == "T2tt":
    #Loading Fall15 with PDF weights
    data_directory           = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
    postProcessing_directory = "postProcessed_Fall15_v3/dilepTiny" 
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
    for s in signals_T2tt:
        s.is76X = True
    signals = signals_T2tt

elif options.signal == "TTbarDM":
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
    signals = signals_TTbarDM
    for s in signals:
        s.isFastSim = False
        s.is76X     = False

nominal     = "LHEweight_original"
variations  = [ "LHEweight_wgt[%i]"%i for i in [0,1,2,3,4,6,8] ]
wgts        = [ nominal ] + variations

signalEstimators = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals ]

results = {}

scale_systematics = {}
for estimate in signalEstimators:
    logger.info("Calculating scale uncertainty for signal %s", estimate.name)
    estimate.initCache("/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/76X_for_Q2/")

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

    # Calculating scale systematics
    # Note: I apply the nominal and the scale variied weights and calculate the maximum unsigned relative variation
    # I can ignore the fact that the nominal weight is already applied by 'weight' (i.e. it is applied twice in the numbers below), because one factor cancels in the ratio

    total = {}
    for wgt in wgts:
        total[wgt] = sum([ estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[wgt]})) for r in regions for channel in channels ] )
    
    for r in regions:
        for c in channels + ['SF', 'all']:
            l = []
            for var in variations:
                if total[var]>0:
                    ref = estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[nominal]}) )
                    if ref>0:
                        scale = total[nominal]/total[var]
                        unc = abs( scale*estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[var]})) - ref ) / ref 
                        l.append( unc.val )

            scale_systematics[(estimate.name, r, c)] = max(l) if len(l)>0 else 0

if not os.path.exists(os.path.dirname(ofile)):
    os.makedirs(os.path.dirname(ofile))

pickle.dump( scale_systematics, file( ofile, 'w') )
logger.info( "Written output %s", ofile )
