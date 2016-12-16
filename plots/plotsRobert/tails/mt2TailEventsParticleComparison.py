''' FWLiteReader example: Loop over a sample and write some data to a histogram.
'''
# Standard imports
import os
import logging
import ROOT
from math import cos, sin, atan2, sqrt

#RootTools
from RootTools.core.standard import *

#StopsDilepton
from StopsDilepton.tools.mcTools import pdgToName
from StopsDilepton.tools.helpers import deltaR


# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='CRITICAL',
      help="Log level for logging"
)

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)

def toDict(p):
    return {'pt':p.pt(), 'eta':p.eta(), 'phi':p.phi(), 'pdgId':p.pdgId()}

def bold(s):
    return '\033[1m'+s+'\033[0m'

## 8X mAOD, assumes eos mount in home directory 
## from Directory
dirname = "/data/rschoefbeck/pickEvents/StopsDilepton/" 


prompt = FWLiteSample.fromFiles("prompt", files = [ \
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016B-PromptReco-v2-MINIAOD.root",
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016C-PromptReco-v2-MINIAOD.root",
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016D-PromptReco-v2-MINIAOD.root",
    ])

rereco = FWLiteSample.fromFiles("rereco", files = [ \
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016B-23Sep2016-v3-MINIAOD.root",
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016C-23Sep2016-v1-MINIAOD.root",
    "/data/rschoefbeck/pickEvents/StopsDilepton/data_rereco/DoubleMuon-Run2016D-23Sep2016-v1-MINIAOD.root",
    ])


products = {
    'pfCand':{'type':'vector<pat::PackedCandidate>', 'label': ("packedPFCandidates")},
    'muons':{'type':'vector<pat::Muon>', 'label':("slimmedMuons") },
}
r_prompt = prompt.fwliteReader( products = products )
r_prompt.start()

p_prompt = {}
while r_prompt.run():
    p_prompt[ r_prompt.evt ] = r_prompt.position - 1    

r_rereco = rereco.fwliteReader( products = products )
r_rereco.start()

p_rereco = {}
while r_rereco.run():
    p_rereco[ r_rereco.evt ] = r_rereco.position - 1    

evt_common = [pos for pos in p_rereco.keys() if pos in p_prompt.keys()]
evt_common.sort()


#evt_break = -1
evt_break = 85068029
#evt_break = 265511308 fails dPhi in rereco
#evt_break = 999589926 passes dPhi in rereco
#evt_break = 1125693285

for i_evt, evt in enumerate(evt_common):
    # if evt not in rereco_outliers: continue

    if evt_break>0 and not evt_break in evt: continue

    r_prompt.goToPosition( p_prompt[ evt ] )
    r_rereco.goToPosition( p_rereco[ evt ] )

    print     
    print "Event %2i   %i:%i:%i"%((i_evt,) + evt )
    #print "  mAOD: MET rereco %3.2f prompt %3.2f"%( r_rereco.products['pfMet'][0].pt(), r_prompt.products['pfMet'][0].pt())

#    evt_str = "%i:%i:%i"%evt
#    if evt in prompt_outliers: 
#        print "    in prompt!"
#    else:
#        print "NOT in prompt!"
#    if evt in rereco_outliers: 
#        print "    in rereco!"
#    else:
#        print "NOT in rereco!"

    pf_prompt_mu = filter( lambda p: abs(p.pdgId()) == 13, r_prompt.products["pfCand"])
    pf_rereco_mu = filter( lambda p: abs(p.pdgId()) == 13, r_rereco.products["pfCand"])
    prompt_mu = filter( lambda p: abs(p.pdgId()) == 13, r_prompt.products["muons"])
    rereco_mu = filter( lambda p: abs(p.pdgId()) == 13, r_rereco.products["muons"])
