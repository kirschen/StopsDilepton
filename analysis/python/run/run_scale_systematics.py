#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
#parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
#parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
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
from StopsDilepton.analysis.regions      import regions80X, superRegion, superRegion140

isFastSim         = True
#setup             = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']})
setup.sys['reweight'] = [] #Fall15 doesn't have the reweights. Not needed.
setup.verbose     = True

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

regions = regions80X #Use all the regions that are used in the limit setting

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate

from StopsDilepton.tools.user import analysis_results

ofile = os.path.join( analysis_results, "systematics", "scale.pkl" )
if not options.overwrite:
    if os.path.exists( ofile ):
        logger.warning( "Found file %s. Exiting. Use --overwrite if you want.", ofile ) 
        sys.exit(0)

#Loading Fall15 with PDF weights
data_directory           = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
postProcessing_directory = "postProcessed_Fall15_v3/dilepTiny" 
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
signals = signals_T2tt

## Temporary:
#from RootTools.core.standard import *
#T2tt_425_325 = Sample.fromFiles(name="T2tt_425_325", treeName="Events", isData=False, color=ROOT.kBlack, texName="T2tt(425,325)", \
#    files=['/afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v12/dilepTiny/T2tt/T2tt_425_325.root'], maxN = -1)
#signals = [T2tt_425_325]

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

nominal     = "LHEweight_original"
variations  = [ "LHEweight_wgt[%i]"%i for i in [0,1,2,3,4,6,8] ]
wgts        = [ nominal ] + variations

signalEstimators = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals ]

results = {}

scale_systematics = {}
for estimate in signalEstimators:
    logger.info("Calculating scale uncertainty for signal %s", estimate.name)
    estimate.initCache(setup.defaultCacheDir())

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
        for c in channels:
            l = []
            for var in variations:
                if total[var]>0:
                    ref = estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[nominal]}) )
                    if ref>0:
                        scale = total[nominal]/total[var] 
                        l.append( abs( scale*estimate.cachedEstimate(r, channel, setup.sysClone(sys={'reweight':[var]})) - ref ) / ref )
            scale_systematics[(estimate.name, r, c)] = max(l) if len(l)>0 else 0

if not os.path.exists(os.path.dirname(ofile)):
    os.makedirs(os.path.dirname(ofile))

pickle.dump( scale_systematics, file( ofile, 'w') )
logger.info( "Written output %s", ofile )
