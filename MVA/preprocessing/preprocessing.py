#!/usr/bin/env python
'''
preprocessing.py reads Events using an Eventloop and saves them in pandas DataFrame format.

Loads Signal and Background Sample specified by arguments, applies selection string and saves Samples.
Both samples are saved as 
one feature matrix X (columns defined by read_variables, in each row is an event) and 
one target vector y ( 0/1 labelged for Background/Signal event, in each row is an event)

eg. python preprocessing.py --signal SMS_T8bbllnunu_XCha0p5_XSlep0p09 --selection njet2p-blabel1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 --small
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

# How many jets do we record from event loop:
dict_nrJets = 4

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

# MVA configuration
from StopsDilepton.MVA.default_classifier import training_variables, spectator_variables, read_variables, selection_cutstring, selection, mode

output_dir = os.path.join( MVA_preprocessing_directory, args.signal + '-' + args.background, args.version, selection, mode ) 

if not os.path.exists( output_dir ):
    os.makedirs( os.path.join( output_dir ) ) 

# Read variables and sequences
# (same list as in plotanalysis)


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


# keys for dict

#read_variables_vector = []
#dict_keys = []
#
#for variable in read_variables:
#    if '[' not in variable:
#        read_variables_vector.append(variable.split('/')[0])
#        dict_keys.append(variable.split('/')[0])
#    else:
#        [mainvariable, sublist ] = variable.split(']')[0].split('[')
#        sublist = sublist.split(',')
#        tmpnr = 0
#        while tmpnr < dict_nrJets:
#            for subvariable in sublist:
#                subvariable = subvariable.split('/')[0] 
#                if tmpnr == 0:
#                    read_variables_vector.append( mainvariable + '_' + subvariable) 
#                dict_keys.append( mainvariable + '_' + subvariable + '[' + str(tmpnr) + ']') 
#            tmpnr +=1 

# initialize dictionary with empty lists
datadict = {key : [] for key in ['label'] + training_variables.keys() + spectator_variables.keys() }

# event loop
for sample in [signal, background] :
    if sample == signal:
        label = 1
    else:
        label = 0
    r = sample.treeReader(variables = map( TreeVariable.fromString, read_variables) )
    r.start()
    while r.run():
        datadict['label'].append( label )
        for dictionary in training_variables, spectator_variables:
            for key, lambda_function in dictionary.iteritems():
                datadict[key].append( lambda_function(r.event) )
             
#            if '[' not in key:
#                datadict[key].append( getattr(r.event, key))
#            else:
#                [var, nr] = key.split('[')
#                datadict[key].append( getattr(r.event, var)[int(nr.strip(']'))]) 

# convert dict to DataFrame
df = pd.DataFrame(datadict)

#save in Dataframe in .h5 file as feature matrix X and target vector y
df.drop(['label'], axis=1).to_hdf( os.path.join( output_dir,  'data_X.h5'), key='df', mode='w')
df['label'].to_hdf(  os.path.join( output_dir, 'data_y.h5'), key='df', mode='w')

logger.info( "Written directory %s", output_dir )
