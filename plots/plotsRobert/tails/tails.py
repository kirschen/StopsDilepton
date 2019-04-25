''' Tail scan
'''
# Standard imports
import ROOT
import os
import pickle
import subprocess
from distutils.spawn import find_executable

# StopsDilepton/Analysis
from StopsDilepton.tools.cutInterpreter import cutInterpreter
from Samples.Tools.metFilters           import getFilterCut

# RootTools
from RootTools.core.standard import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--selection',          action='store',      default='lepSel-njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1')
argParser.add_argument('--mode',               action='store',      default='mumu', choices = ['mumu','mue','ee'])
argParser.add_argument('--year',               action='store',      default=2018, type=int)
argParser.add_argument('--mt2ll',              action='store',      default=140, type=int)
args = argParser.parse_args()

# Logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# Datasets
if args.year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    if args.mode=='mumu':
        data_sample = DoubleMuon_Run2016
    elif args.mode == 'mue':
        data_sample = MuonEG_Run2016 
    elif args.mode == 'ee':
        data_sample = DoubleEG_Run2016
elif args.year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    if args.mode=='mumu':
        data_sample = DoubleMuon_Run2017
    elif args.mode == 'mue':
        data_sample = MuonEG_Run2017 
    elif args.mode == 'ee':
        data_sample = DoubleEG_Run2017
elif args.year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    if args.mode=='mumu':
        data_sample = DoubleMuon_Run2018
    elif args.mode == 'mue':
        data_sample = MuonEG_Run2018 
    elif args.mode == 'ee':
        data_sample = DoubleEG_Run2018

# work directory
directory = "%i_%s_%s" % ( args.year, args.mode, args.selection )
if not os.path.exists( directory):
    os.makedirs( directory )

# selection
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)&&" + offZ+")||isEMu)"

selectionString = "&&".join( [ 'dl_mt2ll>%i'%args.mt2ll, cutInterpreter.cutString(args.selection), getLeptonSelection( args.mode ), getFilterCut(isData=True,year=args.year) ] )

# postprocessed files
postprocessed_files_pkl = os.path.join( directory, 'filenames_postprocessed.pkl')
if not os.path.exists(postprocessed_files_pkl):
    logger.info( "Obtain list of postprocessed files." )
    files = []
    for i_sub_sample, sub_sample in enumerate(data_sample.split( len( data_sample.files ) )):
        n = sub_sample.chain.GetEntries(selectionString)
        logger.info( "File %i/%i: Found %i events", i_sub_sample, len( data_sample.files ), n)
        if n>0:
            files.extend( sub_sample.files )
    pickle.dump( files, file( postprocessed_files_pkl, 'w' ))
    logger.info( "Written postprocessed files to %s", postprocessed_files_pkl)
else:
    files = pickle.load(file( postprocessed_files_pkl ))
    logger.info( "Loaded postprocessed files from %s", postprocessed_files_pkl)

#make small sample
sample = Sample.fromFiles( "tail", files )
sample.setSelectionString( selectionString )

# retrieve miniAOD
patterns_miniAOD = {
2016: { 
    'mue': ["/MuonEG/Run2016*-17Jul2018_*/MINIAOD"],
    'mumu':["/DoubleMuon/Run2016*-17Jul2018_*/MINIAOD"],
    'ee': ["/DoubleEG/Run2016*-17Jul2018_*/MINIAOD"],
    },
2017: {
    'mue':  ["/MuonEG/Run2017*-31Mar2018-v*/MINIAOD"],
    'mumu': ["/DoubleMuon/Run2017*-31Mar2018-v*/MINIAOD"],
    'ee':   ["/DoubleEG/Run2017*-31Mar2018-v*/MINIAOD"],
    },
2018: {
    'mumu': ["/DoubleMuon/Run2018*-17Sep2018-v*/MINIAOD", "/DoubleMuon/Run2018D-PromptReco-v2/MINIAOD"],
    'mue':  ["/MuonEG/Run2018*-17Sep2018-v*/MINIAOD", "/MuonEG/Run2018D-PromptReco-v2/MINIAOD"],
    'ee':   ["/EGamma/Run2018*-17Sep2018-v*/MINIAOD", "/EGamma/Run2018D-PromptReco-v2/MINIAOD"],
    }
}

def _dasPopen(dbs):
    logger.info('DAS query\t: %s',  dbs)
    return os.popen(dbs)

# runlumievent files
runlumievent_pkl = os.path.join( directory, 'filenames_runlumievent.pkl')
if not os.path.exists(runlumievent_pkl):
    logger.info( "Obtain run:lumi:event." )
    run_lumi_evt = []
    r = sample.treeReader( variables = map( TreeVariable.fromString, [ "event/l", "luminosityBlock/I", "run/I" ] ) )
    r.start()
    while r.run():
        erl = ( r.event.run, r.event.luminosityBlock, r.event.event )
        if erl not in run_lumi_evt:
            run_lumi_evt.append( erl )
    logger.info( "Found %i:%i:%i", *erl) 
    pickle.dump( run_lumi_evt, file( runlumievent_pkl, 'w' ))
    logger.info( "Written run:lumi:evt to %s", runlumievent_pkl)
else:
    run_lumi_evt = pickle.load(file( runlumievent_pkl ))
    logger.info( "Loaded run:lumi:evt from %s", runlumievent_pkl)

# datasets
datasets_pkl = os.path.join( directory, 'filenames_datasets.pkl')
if not os.path.exists(datasets_pkl):
    logger.info( "Search for miniAOD datasets")
    datasets = {}
    for run, lumi, event in run_lumi_evt:
        found = False
        for pattern in patterns_miniAOD[args.year][args.mode]:
            dbs='dasgoclient -query="dataset dataset=%s run=%i"'%(pattern, run)
            dbsOut = _dasPopen(dbs).readlines()
            if len(dbsOut)==1:
                dataset = dbsOut[0].rstrip()
                if datasets.has_key(dataset):
                    datasets[dataset].append((run, lumi, event))
                else:
                    datasets[dataset] = [(run, lumi, event)]
                found = True
                break
            elif len(dbsOut)>1:
                logger.error( "Error in dasgoclient output: %r", dbsOut )
                raise RuntimeError
        if not found:
            logger.warning( "Didn't find %i:%i:%i in either of %s", run, lumi, event, ", ".join( patterns_miniAOD[args.year][args.mode] ) )
    pickle.dump( datasets, file( datasets_pkl, 'w' ))
    logger.info( "Written miniAOD datasets per event to: %s", datasets_pkl)
else:
    datasets = pickle.load(file( datasets_pkl ))
    logger.info( "Loaded miniAOD datasets from %s", datasets_pkl)

for dataset, events in datasets.iteritems():
    logger.info( "Look for %i events in %s", len(events), dataset)
    filename = os.path.join(directory, dataset[1:].replace('/','_'))
    txt_file = file( filename+'.txt', 'w')
    for event in events:
        txt_file.write(":".join(map(str, event)))
        txt_file.write("\n")
    txt_file.close()
    logger.info( "Written %s", filename+'.txt' ) 

    if not os.path.exists( filename +'.root' ):
        cmd = ["python", find_executable("edmPickEvents.py"), dataset, filename+'.txt', '--output=%s'%filename, '--maxEventsInteractive=%i'%len(events)]
        logger.info( "Running: %s", " ".join( cmd ) )
        edmCopyPickMerge = subprocess.check_output(cmd)

        edmCopyPickMerge_cmd = edmCopyPickMerge.rstrip().lstrip().replace('\\\n','').split()
        logger.info( "Running %s", " ".join( edmCopyPickMerge_cmd ) )
        subprocess.call( edmCopyPickMerge_cmd )
    else:
        logger.info( "Found tail root file %s. Skip.", filename +'.root' ) 
