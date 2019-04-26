''' Make veto list 
'''
# Standard imports
import ROOT
import os
import pickle

# RootTools
from RootTools.core.standard import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',    action='store', default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
#argParser.add_argument('--sample',       action='store',) 
argParser.add_argument('--directory',    action='store',) 
argParser.add_argument('--nJobs',       action='store', nargs='?',  type=int, default=1,                                    help="Maximum number of simultaneous jobs." )
argParser.add_argument('--job',         action='store',             type=int, default=0,                                    help="Run only jobs i" )
args = argParser.parse_args()

# Logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


from Samples.miniAOD.Run2018_promptReco import *

sample = DoubleMuon_Run2018D_promptReco_v2
sample = sample.split( n=options.nJobs, nSub=options.job)

#logger.info( "Analyzing %s", filename ) 
#products = {
#    'muons':{'type':'vector<pat::Muon>', 'label':("slimmedMuons") },
#}
#fwlite_sample = FWLiteSample.fromFiles( "tail", [filename] )
#
#r = fwlite_sample.fwliteReader( products = products )
#r.start()
#while r.run():
#    muons = filter( lambda m: m.pt()>10, r.event.muons )
#    if len(muons)==2:
#        logger.info( "%i:%i:%i nMuons>10 %i", r.event.run, r.event.lumi, r.event.evt, len(muons) )
#    elif len(muons)>=3:
#        logger.info( "%i:%i:%i nMuons>10 %i pt: %s eta: %s phi %s", r.event.run, r.event.lumi, r.event.evt, len(muons), "/".join(["%3.2f"%m.pt() for m in muons]),  "/".join(["%3.2f"%m.eta() for m in muons]),  "/".join(["%3.2f"%m.phi() for m in muons]) )
#    else:
#        logger.warning("Too few leptons: %i", len(muons) )
#    mindR = min( [ deltaR({'phi':m1.phi(),'eta':m1.eta()},{'phi':m2.phi(),'eta':m2.eta()}) for m1, m2 in itertools.combinations(muons, 2) ] +[99] )
#    if mindR<0.1: logger.warning( "Close!" )
#
