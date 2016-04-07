# standard imports
import ROOT

# RootTools
from RootTools.core.standard import *

# User specific
import StopsDilepton.tools.user as user

def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse 
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")
 
    argParser.add_argument('--logLevel', 
        action='store',
        nargs='?',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
        default='INFO',
        help="Log level for logging"
        )

    return argParser

# Logging
options = get_parser().parse_args()

import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )
    

def checkT2tt():
    try:
        from StopsDilepton.samples.cmgTuples_Signals_Spring15_mAODv2_25ns_0l import T2tt
    except:
        logger.info( "Problem in loading T2tt signal" )
        return

    logger.info( "T2tt signal samples found: " )
    for s in T2tt:
        logger.info( "Sample %s number of files: %i", s.name, len(s.files) )

def checkBackgrounds():
    logger.info( "Checking backgrounds." )
    from StopsDilepton.samples.helpers import fromHeppySample
    from CMGTools.RootTools.samples.samples_13TeV_RunIIFall15MiniAODv2 import samples 
    from StopsDilepton.tools.user import cmg_directory
    for s in samples:
        try:
            sample = fromHeppySample(s.name, data_path = cmg_directory)
            logger.info( "Background sample %s found with %i files", sample.name, len(sample.files)  )
        except helpers.EmptySampleError:
            logger.info( "Background sample %s empty.", s.name)
        except:
            logger.info( "Could not load sample %s.", s.name )
            
        
def checkData():
    logger.info( "Checking Data: Not implemented yet" )
    return

if __name__ == "__main__":
    checkBackgrounds()
    checkData()
    checkT2tt()
