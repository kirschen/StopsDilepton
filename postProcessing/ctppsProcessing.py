#!/usr/bin/env python

# standard imports

# RootTools
from RootTools.core.standard import *

# User specific
import StopsDilepton.tools.user as user

# Standard imports
import imp
import os

# StopsDilepton
from StopsDilepton.tools.ctppsFileProcessor import ctppsFileProcessor

def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")

    argParser.add_argument('--logLevel',    action='store',         nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
    argParser.add_argument('--sample',      action='store',         nargs='?',  type=str, default='FSQJet1_Run2017H_17Nov2017',         help="miniAOD sample" )
    argParser.add_argument('--sampleFile',  action='store',         nargs='*',  type=str, default='Run2017_17Nov2017',                  help="Which sample file in Samples/miniAOD/python?" )
    argParser.add_argument('--nJobs',       action='store',         nargs='?',  type=int, default=1,                                    help="Maximum number of simultaneous jobs." )
    argParser.add_argument('--job',         action='store',                     type=int, default=0,                                    help="Run only jobs i" )
    argParser.add_argument('--targetDir',   action='store',         nargs='?',  type=str, default=user.data_output_directory,           help="Name of the directory the post-processed files will be saved" )
    argParser.add_argument('--year',        action='store',                     type=int, default = 2017, choices = [2016, 2017, 2018], help="Which year?" )
    argParser.add_argument('--overwrite',   action='store_true',                                                                        help="Overwrite existing output files, bool flag set to True  if used" )
    argParser.add_argument('--maxEvents',   action='store',                     type=int, default = -1,                                 help="maxEvents" )

    return argParser

options = get_parser().parse_args()

# Logging
import StopsDilepton.tools.logger as _logger
logFile = '/tmp/%s_%s_njob%s.txt'%(options.sample, os.environ['USER'], str(0 if options.nJobs==1 else options.job))
logger  = _logger.get_logger(options.logLevel, logFile = logFile)

import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(options.logLevel, logFile = None )

#from nanoMET.samples.helpers import fromNanoSample
if options.year != 2017:
    raise NotImplementedError

s = __import__('Samples.miniAOD.%s' % options.sampleFile) # Yes.
sample  = getattr(getattr(s.miniAOD, options.sampleFile), options.sample) # And I do that too. 

output_directory = os.path.join( options.targetDir, 'ctpps', sample.name )

len_orig = len( sample.files )
sample = sample.split( n=options.nJobs, nSub=options.job)
logger.info( "fileBasedSplitting: Run over %i/%i files for job %i/%i."%(len(sample.files), len_orig, options.job, options.nJobs))
logger.debug( "fileBasedSplitting: Files to be run over:\n%s", "\n".join(sample.files) )

if os.path.exists(output_directory) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", output_directory, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", output_directory )
        shutil.rmtree(output_directory)

try:    #Avoid trouble with race conditions in multithreading
    os.makedirs(output_directory)
    logger.info( "Created output directory %s.", output_directory )
except:
    pass

ctppsFileProcessor( 
    sample.files, 
    outfile = os.path.join( output_directory, 'ctpps_%i.root'%options.job ),
    year = 2017,
    isMC = False, #not sample.isData,
    overwrite = options.overwrite,
    maxEvents = options.maxEvents,
    json = "$CMSSW_BASE/src/Samples/Tools/data/json/Cert_306896-307082_13TeV_PromptReco_Collisions17_JSON_LowPU.txt"
 )
