'''
Get all the needed weights and norms for SUSY signals. Usage like
python getWeightsForSignals.py --year 2017 --sample SMS_T2tt_mStop_250to350 --ppSamplePath /afs/hephy.at/data/cms01/nanoTuples/stops_2017_nano_v0p12/dilep/

/afs/hephy.at/data/dspitzbart03/nanoTuples/stops_2017_nano_v0p7/inclusive/SMS_T2tt_mStop_400to1200/
'''

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys
import os
import copy
import random
import subprocess
import datetime
import shutil
import uuid

from array import array
from operator import mul
from math import sqrt, atan2, sin, cos

# RootTools
from RootTools.core.standard import *

# User specific
import StopsDilepton.tools.user as user

# top pt reweighting
from StopsDilepton.tools.topPtReweighting import getUnscaledTopPairPtReweightungFunction, getTopPtDrawString, getTopPtsForReweighting

# use a cacheDir that's read/writable for all of us
cacheDir = "/afs/hephy.at/data/cms01/stopsDilepton/signals/caches/"

def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")

    argParser.add_argument('--logLevel',        action='store',         nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
    argParser.add_argument('--samples',         action='store',         nargs='*',  type=str, default=['TTZToLLNuNu_ext'],                  help="List of samples to be post-processed, given as CMG component name" )
    argParser.add_argument('--ppSamplePath',    action='store',         nargs='*',  type=str, default=None,                  help="List of samples to be post-processed, given as CMG component name" )
    argParser.add_argument('--year',            action='store',                     type=int,                                               help="Which year?" )

    return argParser

options = get_parser().parse_args()

# Logging
import StopsDilepton.tools.logger as _logger
logFile = None
logger  = _logger.get_logger(options.logLevel, logFile = logFile)

import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(options.logLevel, logFile = None )

cacheDir += "%s/"%options.year

## First, get the normalization per masspoint (done on nanoAOD tuples)

if options.year == 2016:
    from Samples.nanoAOD.Summer16_private_legacy_v1 import allSamples as bkgSamples
    from Samples.nanoAOD.Summer16_private_legacy_v1 import SUSY as signalSamples
    from Samples.nanoAOD.Run2016_17Jul2018_private  import allSamples as dataSamples
    allSamples = bkgSamples + dataSamples + signalSamples
elif options.year == 2017:
    from Samples.nanoAOD.Fall17_private_legacy_v1   import allSamples as bkgSamples
    from Samples.nanoAOD.Fall17_private_legacy_v1   import SUSY as signalSamples
    from Samples.nanoAOD.Run2017_31Mar2018_private  import allSamples as dataSamples
    allSamples = bkgSamples + dataSamples
elif options.year == 2018:
    from Samples.nanoAOD.Spring18_private           import allSamples as HEMSamples
    from Samples.nanoAOD.Run2018_26Sep2018_private  import allSamples as HEMDataSamples
    from Samples.nanoAOD.Autumn18_private_legacy_v1 import allSamples as bkgSamples
    from Samples.nanoAOD.Run2018_17Sep2018_private  import allSamples as dataSamples
    allSamples = HEMSamples + HEMDataSamples + bkgSamples + dataSamples
else:
    raise NotImplementedError

samples = []
for selectedSamples in options.samples:
    for sample in allSamples:
        if selectedSamples == sample.name:
            samples.append(sample)

if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(-1)

targetLumi = 1000 #pb-1 Which lumi to normalize to

from StopsDilepton.samples.helpers import getT2ttSignalWeight

logger.info("Getting the signal weights for sample %s", options.samples[0])

signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi, cacheDir = cacheDir)
masspoints = signalWeight.keys()

## now, if we already have it, also get the ISR norm for each masspoint

if options.ppSamplePath:
    import glob
    files = '%s/%s/*.root'%(options.ppSamplePath[0], options.samples[0])
    fileList = [ f for f in  glob.glob(files) if not f.count('signalCounts') ]
    
    sample = Sample.fromFiles(samples[0].name, fileList)

    logger.info("Now extracting the ISR normalization factors.")

    from StopsDilepton.samples.helpers import getT2ttISRNorm

    norm = getT2ttISRNorm(sample, masspoints[0][0], masspoints[0][1], masspoints, options.year, signal=sample.name, cacheDir=cacheDir, fillCache=True)
    
    logger.info("Got the following norm for dummy masspoint mStop %s, mLSP %s : %s", masspoints[0][0], masspoints[0][1], norm)
    logger.info("Done.")



#targetLumi = 1000
#output_directory = '/afs/hephy.at/data/dspitzbart03/nanoTuples/stops_2017_nano_v0p7/inclusive/SMS_T2tt_mStop_400to1200/'
#
#from StopsDilepton.samples.helpers import getT2ttSignalWeight
#logger.info( "SUSY signal samples to be processed: %s", ",".join(s.name for s in samples) )
## FIXME I'm forcing ==1 signal sample because I don't have a good idea how to construct a sample name from the complicated T2tt_x_y_z_... names
#assert len(samples)==1, "Can only process one SUSY sample at a time."
#logger.debug( "Fetching signal weights..." )
#signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi, cacheDir = output_directory)
#logger.debug("Done fetching signal weights.")
#
#mMax = 1550
#bStr = str(mMax)+','+str(mMax)
#
#from Analysis.Tools.isrWeight import ISRweight
#isr = ISRweight()
#
#isrWeightString = isr.getWeightString()
#
#sample.chain.Draw("Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022)):Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))>>hNEvents("+','.join([bStr, bStr])+")", isrWeightString+'*(1)',"goff")
#hNEvents = ROOT.gDirectory.Get("hNEvents")
#
##for masspoint in signalWeight.keys():
##    s = masspoint
##    cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(s[0])+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(s[1])
##    
##    num = sample.getYieldFromDraw(cut, "weight")
##    denom = sample.getYieldFromDraw(cut, "weight*reweight_nISR")
##
##    print masspoint, num/denom
#
