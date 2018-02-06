#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--selectWeight",       dest="selectWeight",       default=None,                action="store",      help="select weight?")
parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option("--sample",               dest='sample',  action='store', default='TTZ',    choices=["TTLep_pow","TTZ","DY","multiboson"], help="which sample?")
parser.add_option("--small",  action='store_true', help="small?")
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
from StopsDilepton.analysis.regions      import regionsO, noRegions, regionsS, regionsAgg
from StopsDilepton.analysis.u_float      import u_float 
from StopsDilepton.analysis.Region       import Region 

#RootTools
from RootTools.core.standard import *
from StopsDilepton.tools.user import data_directory as user_data_directory
data_directory = user_data_directory
postProcessing_directory = "postProcessed_80X_v36/dilep/"
from StopsDilepton.samples.color import color
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed_PDFsamples import *

sample = TTZ
if options.sample == "TTLep_pow":
    sample = TTLep_pow
    sample.reduceFiles( to = 10 )
elif options.sample == "DY":
    sample = DY_HT_LO
elif options.sample == "multiboson":
    sample = multiBoson

if options.small:
    sample.reduceFiles( to = 1 )

setupIncl = setup.sysClone(parameters={'triLep': False, 'zWindow' : 'allZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(0,-1),  'nBTags':(0,-1), 'dPhi': False, 'dPhiInv': False})
setup.verbose     = True



# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

#normRegions = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2bb", (0, -1)) + Region("met_pt", (0, -1))] # could add this for normalizing. Then, there's no difference between normalizing to <100 and inclusive since bulk is <100 anyway
regions = regionsO + noRegions# + regionsAgg #Use all the regions that are used in the limit setting



from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.tools.user import analysis_results


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

# Divide the LHEweight by genWeight to get the pure reweight - otherwise problematic for (NLO) samples with neg. weights
if not options.selectWeight:
    variations  = [ "(LHEweight_wgt[%i]/genWeight)"%i for i in [1,2,3,4,6,8] ]
else:
    variations  = [ "(LHEweight_wgt[%s]/genWeight)"%options.selectWeight ]

results = {}

scale_systematics = {}
estimate = MCBasedEstimate(name=sample.name, sample={channel:sample for channel in allChannels})
estimate.initCache("/afs/hephy.at/data/dspitzbart02/StopsDilepton/results/80X_for_scaleV3/")

def wrapper(args):
        r,channel,setup = args
        res = estimate.cachedEstimate(r, channel, setup, save=True)
        return (estimate.uniqueKey(r, channel, setup), res )

jobs=[]

for channel in allChannels:
    jobs.append((noRegions[0], channel, setupIncl.sysClone(sys={'reweight':["LHEweight_wgt[0]/genWeight"]})))
    jobs.append((noRegions[0], channel, setupIncl))
    for var in variations:
        jobs.append((noRegions[0], channel, setupIncl.sysClone(sys={'reweight':[var]})))

for channel in allChannels:
    for region in regions:
        jobs.append((region, channel, setup))
        jobs.append((region, channel, setup.sysClone(sys={'reweight':["LHEweight_wgt[0]/genWeight"]})))
        for var in variations:
            jobs.append((region, channel, setup.sysClone(sys={'reweight':[var]})))

if options.noMultiThreading: 
    results = map(wrapper, jobs)
else:
    from multiprocessing import Pool
    pool = Pool(processes=8)
    results = pool.map(wrapper, jobs)
    pool.close()
    pool.join()


if not options.selectWeight:
    ofile = os.path.join( analysis_results, "systematicsTest_v2", "scale_%s.pkl" % options.sample )
    if not options.overwrite:
        if os.path.exists( ofile ):
            logger.warning( "Found file %s. Exiting. Use --overwrite if you want.", ofile )
            sys.exit(0)

    scale_systematics = {}
    
    for channel in allChannels:
        for region in regions:
            if channel in ["SF","all"]:
                print
                print channel
                print region
            env = ROOT.TH1F("envelope","",100, 0., 2.)
            for var in variations:
                var_bin     = estimate.cachedEstimate(region, channel, setup.sysClone(sys={'reweight':[var]}))
                ref_bin     = estimate.cachedEstimate(region, channel, setup.sysClone(sys={'reweight':["LHEweight_wgt[0]/genWeight"]}))
                var_incl    = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
                ref_incl    = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':["LHEweight_wgt[0]/genWeight"]}))
                #var_incl_ch = estimate.cachedEstimate(noRegions[0], channel, setupIncl.sysClone(sys={'reweight':[var]}))
                #ref_incl_ch = estimate.cachedEstimate(noRegions[0], channel, setupIncl.sysClone(sys={'reweight':["(LHEweight_wgt[0]/genWeight)"]}))
                norm = ref_incl/var_incl
                #norm2 = ref_incl_ch/var_incl_ch
                if ref_bin>0:
                    if channel in ["SF","all"]:
                        print (norm * var_bin/ref_bin)
                    scaleU = abs((norm * var_bin/ref_bin).val)
                    env.Fill(scaleU)
            
            stdDev = env.GetStdDev()
            meanH = env.GetMean()
            if channel in ["SF","all"]:
                print "Assigned uncertainty:", stdDev
            if stdDev>0:
                scale_systematics[(estimate.name, region, channel)] = stdDev
            else:
                scale_systematics[(estimate.name, region, channel)] = 0.01
                logger.info("Scale uncertainty set to 0.01 for this region")
            del env


    if not os.path.exists(os.path.dirname(ofile)):
        os.makedirs(os.path.dirname(ofile))
    
    pickle.dump( scale_systematics, file( ofile, 'w') )
    logger.info( "Written output %s", ofile )
