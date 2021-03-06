class default_locations:
    mc_2016_data_directory              = "/afs/hephy.at/data/cms06/nanoTuples/" 
    mc_2016_postProcessing_directory    = "stops_2016_nano_v0p23/dilep/" 
    data_2016_data_directory            = "/afs/hephy.at/data/cms07/nanoTuples/" 
    data_2016_postProcessing_directory  = "stops_2016_nano_v0p19/dilep/" 
 
    mc_2017_data_directory              = "/afs/hephy.at/data/cms06/nanoTuples/" 
    mc_2017_postProcessing_directory    = "stops_2017_nano_v0p23/dilep/" 
    data_2017_data_directory            = "/afs/hephy.at/data/cms07/nanoTuples/" 
    data_2017_postProcessing_directory  = "stops_2017_nano_v0p19/dilep/" 
 
    mc_2018_data_directory              = "/afs/hephy.at/data/cms06/nanoTuples/" 
    mc_2018_postProcessing_directory    = "stops_2018_nano_v0p23/dilep/" 
    data_2018_data_directory            = "/afs/hephy.at/data/cms07/nanoTuples/" 
    data_2018_postProcessing_directory  = "stops_2018_nano_v0p19/dilep/"

import os
if os.environ['HOSTNAME'].startswith('clip'):
    default_locations.mc_2016_data_directory   =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
    default_locations.data_2016_data_directory =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
    default_locations.mc_2017_data_directory   =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
    default_locations.data_2017_data_directory =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
    default_locations.mc_2018_data_directory   =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
    default_locations.data_2018_data_directory =  "/mnt/hephy/cms/robert.schoefbeck/StopsDileptonLegacy/nanoTuples/"
