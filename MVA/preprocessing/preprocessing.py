#!/usr/bin/env python
'''
preprocessing.py reads Events using an Eventloop and saves them in pandas DataFrame format.
Saving format ( Note: First events are signals then background, they are not random)
one feature matrix X (columns defined by read_variables, in each row is an event) and 
one target vector y ( 0/1 labelged for Background/Signal event, in each row is an event)

Available sample signals are specified in samples.py
selection and mode in default_classifier.py

eg. python preprocessing.py --signal SMS_T2tt_mStop_400to1200 --background TTLep_pow --version v1_lep_pt --small

Note: There also a direct solution to this: Root to numpy!
'''

# Standard imports and batch mode
import ROOT, os
ROOT.gROOT.SetBatch(True)
import pandas as pd
import numpy as np
import imp

#from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.helpers         import deltaPhi
from StopsDilepton.tools.user import     MVA_preprocessing_directory

# MVA and sample configuration
from StopsDilepton.MVA.default_classifier import training_variables, spectator_variables, read_variables, selection_cutstring, selection, mode

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default="T8bbllnunu_XCha0p5_XSlep0p5_800_1",  nargs='?', help="signal sample")
argParser.add_argument('--background',         action='store',      default="TTLep_pow",     nargs='?', help="background sample")
argParser.add_argument('--small',              action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--version',            action='store',      default='v1')
argParser.add_argument('--chunksize',          action='store',      default='100000',       type=int)
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#
# Define Storage location for .h5 files
#
if args.small:
    args.version += '_small'

output_dir = os.path.join( MVA_preprocessing_directory, args.signal + '-' + args.background, args.version, selection, mode ) 

if not os.path.exists( output_dir ):
    os.makedirs( os.path.join( output_dir ) ) 

# Read variables and sequences
samples = imp.load_source( "samples", os.path.expandvars( "$CMSSW_BASE/src/StopsDilepton/MVA/python/samples.py" ) )

signal = getattr(samples, args.signal)
signal.setSelectionString(selection_cutstring)
signal.name           = "signal"

background = getattr(samples, args.background)
background.setSelectionString(selection_cutstring)
background.name           = "background"

for sample in [signal, background]:
  if args.small:
        sample.reduceFiles( to = 1 )

# initialize dictionary 
datadict = {key : [] for key in ['label'] + training_variables.keys() + spectator_variables.keys() }
# create .h5 file
df = pd.DataFrame(datadict)
df.drop(['label'], axis=1).to_hdf( os.path.join( output_dir,  'data_X.h5'), key='df', format='table', mode='w')
df['label'].to_hdf(  os.path.join( output_dir, 'data_y.h5'), key='df', format='table', mode='w')
 
# event loop
i = 0
lastsavedindex = 0
for sample in [signal, background] :
    if sample == signal:
        label = 1
    else:
        label = 0
    r = sample.treeReader(variables = map( TreeVariable.fromString, read_variables) )
    r.start()
    while r.run():
        # write data to dictionary
        datadict['label'].append( label )
        for dictionary in training_variables, spectator_variables:
            for key, lambda_function in dictionary.iteritems():
                datadict[key].append( lambda_function(r.event) )
        
        i += 1 
        # in chunks, convert dictionary to dataframe and append to .h5 file 
        if not i % args.chunksize:
            df = pd.DataFrame(datadict)
            df.index = pd.RangeIndex(start=lastsavedindex,stop=i, step=1)
            df.drop(['label'], axis=1).to_hdf( os.path.join( output_dir,  'data_X.h5'), key='df', format='table', append=True, mode='a')
            df['label'].to_hdf(  os.path.join( output_dir, 'data_y.h5'), key='df', format='table', append=True, mode='a')
            # clear dictionary and dataframe
            datadict = {key : [] for key in ['label'] + training_variables.keys() + spectator_variables.keys() }
            #df.iloc[0:0]
            lastsavedindex = i
        
    df = pd.DataFrame(datadict)
    df.index = pd.RangeIndex(start=lastsavedindex,stop=i, step=1)
    # append to file
    df.drop(['label'], axis=1).to_hdf( os.path.join( output_dir,  'data_X.h5') , key='df', format='table', append=True, mode='a')
    df['label'].to_hdf(  os.path.join( output_dir, 'data_y.h5'), key='df', format='table', append=True, mode='a')
    # clear Dataframe
    datadict = {key : [] for key in ['label'] + training_variables.keys() + spectator_variables.keys() }
    #df.iloc[0:0]
    lastsavedindex = i
logger.info( "Written directory %s", output_dir )
