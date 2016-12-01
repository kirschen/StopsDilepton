'''
Extract cmg samples from dpm'''

maxN = -1

## cache file
#cache_file = '/afs/hephy.at/work/r/rschoefbeck/StopsDilepton/dpm_sample_caches/80X_1l_21.pkl'
## MC
#def_robert = '/dpm/oeaw.ac.at/home/cms/store/user/schoef/cmgTuples/80X_1l_21'
#def_daniel = '/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/cmgTuples/80X_1l_21'
#mc_dpm_directories = [ def_robert, def_daniel ]
#from CMGTools.RootTools.samples.samples_13TeV_RunIISpring16MiniAODv2 import mcSamples as heppy_samples

cache_file = '/afs/hephy.at/work/r/rschoefbeck/StopsDilepton/dpm_sample_caches/test_data.pkl'
test_daniel = "/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/cmgTuples/80X_stopsDilep/MuonEG"
mc_dpm_directories = [test_daniel]
from CMGTools.RootTools.samples.samples_13TeV_DATA2016 import dataSamples as heppy_samples


def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")
    argParser.add_argument('--logLevel', action='store', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], default='INFO', help="Log level for logging" )
    argParser.add_argument('--overwrite', action='store_true', default=False, help="Overwrite cache?" )

    return argParser

options = get_parser().parse_args()


# Logging
import StopsDilepton.tools.logger as logger_
logger = logger_.get_logger(options.logLevel, logFile = None )

# Walk all subdirectories
from StopsDilepton.samples.walk_dpm import walk_dpm

import os
import pickle

# Read cache file, if exists
if os.path.exists( cache_file ) and not options.overwrite:
    sample_map = pickle.load( file(cache_file) )
else:


    # Proxy certificate
    from StopsDilepton.tools.helpers import renewCredentials
    proxy = renewCredentials()
    logger.info( "Using proxy %s"%proxy )

    # Read dpm directories
    cmg_directories = {}
    for data_path in mc_dpm_directories:
        walker = walk_dpm( data_path )
        cmg_directories[ data_path ] = walker.walk_dpm_cmgdirectories('.',  maxN = maxN )
        #del walker

    for heppy_sample in heppy_samples:
        heppy_sample.candidate_directories = []
        pd, era = heppy_sample.dataset.split('/')[1:3]
        for data_path in cmg_directories.keys():
            for dpm_directory in cmg_directories[data_path].keys():
                if ('/%s/'%pd in dpm_directory) and ('/'+era in dpm_directory):
                    heppy_sample.candidate_directories.append([data_path, dpm_directory])
                    logger.debug("heppy sample %s in %s", heppy_sample.name, dpm_directory)

    # Merge
    from RootTools.core.Sample import Sample
    sample_map = {}
    for heppy_sample in heppy_samples:
        if len(heppy_sample.candidate_directories)==0:
            logger.info("No directory found for %s", heppy_sample.name)
        else:
            normalization, files = walker.combine_cmg_directories( {dpm_directory:cmg_directories[data_path][dpm_directory] for data_path, dpm_directory in heppy_sample.candidate_directories } )
            logger.info( "Sample %s: Found a total of %i files with normalization %3.2f", heppy_sample.name, len(files), normalization)
            sample_map[heppy_sample] = Sample.fromFiles(
                heppy_sample.name, 
                files = ['root://hephyse.oeaw.ac.at/'+f for f in files],
                normalization = normalization, 
                treeName = 'tree', isData = heppy_sample.isData, maxN = maxN)
            
            logger.info("Combined %i directories for sample %s to a total of %i files with normalization %3.2f", len(heppy_sample.candidate_directories), heppy_sample.name, len(files), normalization)

    # Store cache file
    dir_name = os.path.dirname( cache_file ) 
    if not os.path.exists( dir_name ): os.makedirs( dir_name )
    pickle.dump( sample_map, file( cache_file, 'w') )
    logger.info( "Created MC sample cache %s", cache_file )
