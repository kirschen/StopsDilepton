#!/usr/bin/env python
'''
EventsToH5.py reads Events using an Eventloop and saves them in pandas DataFrame format.

Loads Signal and Background Sample specified by arguments, applies selection string and saves Samples.
Both samples are saved as 
one feature matrix X (columns defined by read_variables, in each row is an event) and 
one target vector y ( 0/1 tagged for Background/Signal event, in each row is an event)
in SINGAL-BACKGROUND/SELECTIONSTRING_MODE(_small)/

eg. python preprocessing.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 --small
'''

# Standard imports and batch mode
import ROOT, os
ROOT.gROOT.SetBatch(True)
import pandas as pd
import h5py
import imp

#from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.helpers         import deltaPhi
from StopsDilepton.tools.user import     MVA_preprocessing_directory
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default="T8bbllnunu_XCha0p5_XSlep0p5_800_1",  nargs='?', help="signal sample")
argParser.add_argument('--mode',               action='store',      default="all",  nargs='?', choices = ['all', 'mumu', 'emu', 'ee'], help="dilepton mode")
argParser.add_argument('--background',         action='store',      default="TTLep_pow",     nargs='?', help="background sample")
argParser.add_argument('--small',              action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--version',            action='store',      default='v1')
argParser.add_argument('--selection',          action='store',      default='njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1')
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

output_dir = os.path.join( MVA_preprocessing_directory, args.version, args.selection, args.mode ) 

if not os.path.exists( output_dir ):
    os.makedirs( os.path.join( output_dir ) ) 

# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="all":  return "nGoodMuons+nGoodElectrons==2&&isOS&&( " + "(isEE||isMuMu)" + offZ + "|| isEMu)"

samples = imp.load_source( "samples", os.path.expandvars( "$CMSSW_BASE/src/StopsDilepton/MVA/python/samples.py" ) )

signal = getattr(samples, args.signal)
signal.setSelectionString([getFilterCut(isData=False, badMuonFilters = "Summer16"), getLeptonSelection(args.mode)])
signal.addSelectionString( cutInterpreter.cutString(args.selection) )
signal.name           = "signal"

background = getattr(samples, args.background)
background.setSelectionString([getFilterCut(isData=False, badMuonFilters = "Summer16"), getLeptonSelection(args.mode)])
background.addSelectionString( cutInterpreter.cutString(args.selection) )
background.name           = "background"

for sample in [signal, background]:
  if args.small:
        sample.reduceFiles( to = 1 )

# keys for dict
dict_nrJets = 4
tmpnr = 1
dict_keys = []
for i in read_variables:
    if not i.startswith("JetGood"):
        dict_keys.append(i)
    else:
        i = i.replace(']','')
        tmp_var = i.split('[')
        tmptmp_var = tmp_var[1].split(',')
        while tmpnr <= dict_nrJets:
            for j in tmptmp_var:
                dict_keys.append('Jet' + str(tmpnr) +  "_" + j)
            tmpnr += 1 

# initialize dictionary with empty lists
datadict = {}
for i in ['label'] + dict_keys:
    datadict[i.split('/')[0]] = []

for sample in [signal, background] :
    r = sample.treeReader(variables = map( TreeVariable.fromString, read_variables) )
    r.start()
    while r.run():
        datadict['label'].append(1)
        tmpdict = { 'btagCSV' : [ x for x in r.event.JetGood_btagCSV],
                    'eta' : [ x for x in r.event.JetGood_eta],
                    'phi' : [ x for x in r.event.JetGood_phi],
                    'pt' : [ x for x in r.event.JetGood_pt] }
        for key in datadict:
            if key.startswith('Jet'):
                number = int( key.replace('Jet','')[0] )
                datadict[key].append( tmpdict[ key.replace('Jet','')[2:]][number-1] )
            else:
                if key !='label':
                    datadict[key].append( getattr(r.event, key) )

#convert dict to DataFrame
df = pd.DataFrame(datadict)

#save in Dataframe in .h5 file as feature matrix X and target vector y
df.drop(['label'], axis=1).to_hdf( os.path.join( output_dir,  'data_X.h5'), key='df', mode='w')
df['label'].to_hdf(  os.path.join( output_dir, 'data_y.h5'), key='df', mode='w')

logger.info( "Written directory %s", output_dir )
