''' copy the whole directory to dpm
'''
# Standard imports
import os
# default locations
from StopsDilepton.samples.default_locations import default_locations

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")
#argParser.add_argument('--logLevel',    action='store',         nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
argParser.add_argument('--target_path',   action='store',         nargs='?',  type=str, default = 'Stops2l-postprocessed', help="Name of the directory the post-processed files will be saved" )
argParser.add_argument('--year',        action='store',                     type=int, default = 2016, choices = [2016, 2017, 2018], help="Which year?" )
args = argParser.parse_args()


if args.year == 2016:
    mc_source_path      = os.path.join( default_locations.mc_2016_data_directory, default_locations.mc_2016_postProcessing_directory)
    data_source_path    = os.path.join( default_locations.data_2016_data_directory, default_locations.data_2016_postProcessing_directory)
    mc_postProcessing_directory   = default_locations.mc_2016_postProcessing_directory
    data_postProcessing_directory = default_locations.data_2016_postProcessing_directory
    signal_2016_data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
    signal_2016_postProcessing_directory    = "stops_2016_nano_v0p16/dilep/"
elif args.year == 2017:
    mc_source_path      = os.path.join( default_locations.mc_2017_data_directory, default_locations.mc_2017_postProcessing_directory)
    data_source_path    = os.path.join( default_locations.data_2017_data_directory, default_locations.data_2017_postProcessing_directory)
    mc_postProcessing_directory   = default_locations.mc_2017_postProcessing_directory
    data_postProcessing_directory = default_locations.data_2017_postProcessing_directory
    signal_2017_data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
    signal_2017_postProcessing_directory    = "stops_2017_nano_v0p16/dilep/"
elif args.year == 2018:
    mc_source_path      = os.path.join( default_locations.mc_2018_data_directory, default_locations.mc_2018_postProcessing_directory)
    data_source_path    = os.path.join( default_locations.data_2018_data_directory, default_locations.data_2018_postProcessing_directory)
    mc_postProcessing_directory   = default_locations.mc_2018_postProcessing_directory
    data_postProcessing_directory = default_locations.data_2018_postProcessing_directory
    signal_2018_data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
    signal_2018_postProcessing_directory    = "stops_2018_nano_v0p16/dilep/"

data_target_path = '/dpm/oeaw.ac.at/home/cms/store/user/%s/%s/%s'%( os.environ['USER'], args.target_path, data_postProcessing_directory) 
mc_target_path   = '/dpm/oeaw.ac.at/home/cms/store/user/%s/%s/%s'%( os.environ['USER'], args.target_path, mc_postProcessing_directory) 

jobs=[]

for source, target in [ ( mc_source_path, mc_target_path), ( data_source_path, data_target_path)]:
    for obj in os.listdir(source):
        jobs.append( ( os.path.join( source, obj ), os.path.join(target)) )

#import subprocess
#def wrapper( job ):
#    cmd = ["dpmTools.py", "--fromLocal", "--cp", job[0], job[1]]
#    print " ".join(cmd)
#    subprocess.call(cmd)
#
#from multiprocessing import Pool
#pool = Pool(processes=2)
#results = pool.map(wrapper, jobs)
#pool.close()
#pool.join()
