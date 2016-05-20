#!/usr/bin/env python


#
# genPostProcessing.py:
# creates a small tree with only the leptons, bjets and Z-boson or photon for the purpose of TTG vs. TTZ studies
# might be incorporated in the larger cmgPostProcessing, but I don't want to mess it up
#


# standard imports
import ROOT
import sys
import os
import copy
import random
import subprocess
import datetime
import shutil

from math import sqrt, atan2, sin, cos

# RootTools
from RootTools.core.standard import *

# User specific
import StopsDilepton.tools.user as user

from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.objectSelection import getGenPartsAll
from StopsDilepton.tools.getGenBoson import getGenZ, getGenPhoton

# central configuration
targetLumi = 1000 #pb-1 Which lumi to normalize to

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

    argParser.add_argument('--overwrite',
        action='store_true',
        help="Overwrite existing output files, bool flag set to True  if used")

    argParser.add_argument('--samples',
        action='store',
        nargs='*',
        type=str,
        default=['TTZToLLNuNu'],
        help="List of samples to be post-processed, given as CMG component name"
        )

    argParser.add_argument('--eventsPerJob',
        action='store',
        nargs='?',
        type=int,
        default=300000,
        help="Maximum number of events per job (Approximate!)."
        )

    argParser.add_argument('--nJobs',
        action='store',
        nargs='?',
        type=int,
        default=1,
        help="Maximum number of simultaneous jobs."
        )
    argParser.add_argument('--job',
        action='store',
        nargs='*',
        type=int,
        default=[],
        help="Run only jobs i"
        )

    argParser.add_argument('--minNJobs',
        action='store',
        nargs='?',
        type=int,
        default=1,
        help="Minimum number of simultaneous jobs."
        )

    argParser.add_argument('--dataDir',
        action='store',
        nargs='?',
        type=str,
        default=user.cmg_directory,
        help="Name of the directory where the input data is stored (for samples read from Heppy)."
        )

    argParser.add_argument('--targetDir',
        action='store',
        nargs='?',
        type=str,
        default=user.data_output_directory,
        help="Name of the directory the post-processed files will be saved"
        )

    argParser.add_argument('--processingEra',
        action='store',
        nargs='?',
        type=str,
        default='postProcessed_Fall15_mAODv2',
        help="Name of the processing era"
        )

    return argParser

options = get_parser().parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

#Samples: Load samples
from StopsDilepton.samples.helpers import fromHeppySample
samples = [ fromHeppySample(s, data_path = options.dataDir, maxN = None) for s in options.samples ]

xSection = samples[0].heppy.xSection

#Samples: combine if more than one
if len(samples)>1:
    sample_name =  samples[0].name+"_comb"
    logger.info( "Combining samples %s to %s.", ",".join(s.name for s in samples), sample_name )
    sample = Sample.combine(sample_name, samples, maxN = maxN)
    # Clean up
    for s in samples:
        sample.clear()
elif len(samples)==1:
    sample = samples[0]
else:
    raise ValueError( "Need at least one sample. Got %r",samples )

lumiScaleFactor = xSection*targetLumi/float(sample.normalization) if xSection is not None else None

from StopsDilepton.tools.puReweighting import getReweightingFunction
puRW        = getReweightingFunction(data="PU_2100_XSecCentral", mc="Fall15")
puRWDown    = getReweightingFunction(data="PU_2100_XSecDown", mc="Fall15")
puRWUp      = getReweightingFunction(data="PU_2100_XSecUp", mc="Fall15")


# output directory
outDir = os.path.join(options.targetDir, options.processingEra, "gen", sample.name)

if os.path.exists(outDir) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", outDir, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", outDir )
        shutil.rmtree(outDir)

try:    #Avoid trouble with race conditions in multithreading
    os.makedirs(outDir)
    logger.info( "Created output directory %s.", outDir )
except:
    pass

new_variables = [ 'weight/F']
read_variables = [] 
read_variables+= [Variable.fromString('nTrueInt/F')]
# reading gen particles for top pt reweighting
read_variables.append( Variable.fromString('ngenPartAll/I') )
read_variables.append( VectorType.fromString('genPartAll[pt/F,eta/F,phi/F,pdgId/I,status/I,charge/I,motherId/I,grandmotherId/I,nMothers/I,motherIndex1/I,motherIndex2/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I]', nMax=200 )) # default nMax is 100, which would lead to corrupt values in this case
read_variables.append( Variable.fromString('genWeight/F') )
read_variables.append( Variable.fromString('met_genPt/F') )
read_variables.append( Variable.fromString('met_genPhi/F') )

new_variables.extend( ['met_pt/F', 'met_pt_photon/F'] )
new_variables.extend( ['met_phi/F', 'met_phi_photon/F'] )
new_variables.extend( ['zBoson_genPt/F', 'zBoson_genEta/F', 'zBoson_genPhi/F', 'zBoson_isNeutrinoDecay/O'] )
new_variables.extend( ['photon_genPt/F', 'photon_genEta/F', 'photon_genPhi/F'] )
new_variables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_pdgId/I'] )
new_variables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_pdgId/I'] )
new_variables.extend( ['nu1_pt/F', 'nu1_eta/F', 'nu1_phi/F', 'nu1_pdgId/I'] )
new_variables.extend( ['nu2_pt/F', 'nu2_eta/F', 'nu2_phi/F', 'nu2_pdgId/I'] )
new_variables.extend( ['bJet1_pt/F', 'bJet1_eta/F', 'bJet1_phi/F', 'bJet1_pdgId/I'] )
new_variables.extend( ['bJet2_pt/F', 'bJet2_eta/F', 'bJet2_phi/F', 'bJet2_pdgId/I'] )
new_variables.extend( ['t1_pt/F', 't1_eta/F', 't1_phi/F', 't1_pdgId/I'] )
new_variables.extend( ['t2_pt/F', 't2_eta/F', 't2_phi/F', 't2_pdgId/I'] )
new_variables.extend( ['leptonicDecays/I', 'mt2ll/F', 'mt2ll_photon/F'] )
new_variables.extend( ['mt1/F','mt2/F'] )
new_variables.extend( ['nunu_pt/F','nunu_eta/F','nunu_phi/F'] )



# Define a reader
reader = sample.treeReader( \
    variables = read_variables ,
    selectionString = ""
    )

# Calculate corrected met pt/phi using systematics for jets
def getMetCorrected(met_pt, met_phi, jets, var):
  met_corr_px  = met_pt*cos(met_phi) + sum([(j['pt']-j['pt_'+var])*cos(j['phi']) for j in jets])
  met_corr_py  = met_pt*sin(met_phi) + sum([(j['pt']-j['pt_'+var])*sin(j['phi']) for j in jets])
  met_corr_pt  = sqrt(met_corr_px**2 + met_corr_py**2)
  met_corr_phi = atan2(met_corr_py, met_corr_px)
  return (met_corr_pt, met_corr_phi)

def filler(s):
    # shortcut
    r = reader.data
    s.reweightPU = puRW(r.nTrueInt)
    s.weight = lumiScaleFactor*r.genWeight if lumiScaleFactor is not None else 1

    s.met_pt  = r.met_genPt
    s.met_phi = r.met_genPhi

    genParts = getGenPartsAll(r)

    s.leptonicDecays = 0
    for g in genParts:
      if abs(g['pdgId']) == 6 and g['nDaughters'] == 2:
        try:
	  # Look for top decay to W boson and (b-)jet
	  if abs(genParts[g['daughterIndex1']]['pdgId']) != 24 and abs(genParts[g['daughterIndex2']]['pdgId']) != 24: continue
	  if abs(genParts[g['daughterIndex1']]['pdgId']) == 24:
	    wBoson = genParts[g['daughterIndex1']]
	    bJet   = genParts[g['daughterIndex2']]
	  elif abs(genParts[g['daughterIndex2']]['pdgId']) == 24:
	    wBoson = genParts[g['daughterIndex2']]
	    bJet   = genParts[g['daughterIndex1']]
	  else:
	    raise Exception('Logic is wrong')

	  # Go down through the W-boson radiations until we find the W decay
	  while abs(genParts[wBoson['daughterIndex1']]['pdgId']) == 24 or abs(genParts[wBoson['daughterIndex2']]['pdgId']) == 24:
	    if   abs(genParts[wBoson['daughterIndex1']]['pdgId']) == 24: wBoson = genParts[wBoson['daughterIndex1']] 
	    elif abs(genParts[wBoson['daughterIndex2']]['pdgId']) == 24: wBoson = genParts[wBoson['daughterIndex2']] 
	    else:
	      raise Exception('Logic is wrong')

	  if g['pdgId'] == 6:
	    s.t1_pt         = g['pt']
	    s.t1_eta        = g['eta']
	    s.t1_phi        = g['phi']
	    s.t1_pdgId      = g['pdgId']
	    s.bJet1_pt      = bJet['pt']
	    s.bJet1_eta     = bJet['eta']
	    s.bJet1_phi     = bJet['phi']
	    s.bJet1_pdgId   = bJet['pdgId']
	  elif g['pdgId'] == -6:
	    s.t2_pt         = g['pt']
	    s.t2_eta        = g['eta']
	    s.t2_phi        = g['phi']
	    s.t2_pdgId      = g['pdgId']
	    s.bJet2_pt      = bJet['pt']
	    s.bJet2_eta     = bJet['eta']
	    s.bJet2_phi     = bJet['phi']
	    s.bJet2_pdgId   = bJet['pdgId']
	  else:
	    raise Exception('Logic is wrong')

	  # Check for leptonic decay
	  if abs(genParts[wBoson['daughterIndex1']]['pdgId']) in (11,12,13,14,15,16):
	    s.leptonicDecays += 1
	    if abs(genParts[wBoson['daughterIndex1']]['pdgId']) in (11,13,15):
	      l  = genParts[wBoson['daughterIndex1']]
	      nu = genParts[wBoson['daughterIndex2']]
	    elif abs(genParts[wBoson['daughterIndex2']]['pdgId']) in (11,13,15):
	      l  = genParts[wBoson['daughterIndex2']]
	      nu = genParts[wBoson['daughterIndex1']]
	    else:
	      raise Exception('Logic is wrong')

	    if g['pdgId'] == 6:
	      s.l1_pt     = l['pt']
	      s.l1_eta    = l['eta']
	      s.l1_phi    = l['phi']
	      s.l1_pdgId  = l['pdgId']
	      s.nu1_pt    = nu['pt']
	      s.nu1_eta   = nu['eta']
	      s.nu1_phi   = nu['phi']
	      s.nu1_pdgId = nu['pdgId']
              s.mt1       = sqrt(2*s.l1_pt*s.nu1_pt*(1-cos(s.l1_phi-s.nu1_phi)))
	    elif g['pdgId'] == -6:
	      s.l2_pt     = l['pt']
	      s.l2_eta    = l['eta']
	      s.l2_phi    = l['phi']
	      s.l2_pdgId  = l['pdgId']
	      s.nu2_pt    = nu['pt']
	      s.nu2_eta   = nu['eta']
	      s.nu2_phi   = nu['phi']
	      s.nu2_pdgId = nu['pdgId']
              s.mt2       = sqrt(2*s.l2_pt*s.nu2_pt*(1-cos(s.l2_phi-s.nu2_phi)))
	    else:
	      raise Exception('Logic is wrong')

        except Exception, e:
           print str(e)

    zBoson = getGenZ(genParts)
    if zBoson is not None:
      s.zBoson_isNeutrinoDecay = abs(genParts[zBoson['daughterIndex1']]['pdgId']) in (12, 14, 16)
      s.zBoson_genPt           = zBoson['pt']
      s.zBoson_genEta          = zBoson['eta']
      s.zBoson_genPhi          = zBoson['phi']

    genPhoton = getGenPhoton(genParts)
    if genPhoton is not None:
      s.photon_genPt     = genPhoton['pt']
      s.photon_genEta    = genPhoton['eta']
      s.photon_genPhi    = genPhoton['phi']

    if s.leptonicDecays == 2:      
      nu1 = ROOT.TLorentzVector()
      nu2 = ROOT.TLorentzVector()
      nu1.SetPtEtaPhiM(s.nu1_pt, s.nu1_eta, s.nu1_phi, 0 )
      nu2.SetPtEtaPhiM(s.nu2_pt, s.nu2_eta, s.nu2_phi, 0 )

      nunu = nu1 + nu2
      s.nunu_pt  = nunu.Pt()
      s.nunu_eta = nunu.Eta()
      s.nunu_phi = nunu.Phi()

      mt2Calc.reset()
      mt2Calc.setLeptons(s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi)
      mt2Calc.setMet(s.met_pt, s.met_phi)
      s.mt2ll = mt2Calc.mt2ll()

      if genPhoton is not None:
        met   = ROOT.TLorentzVector()
        gamma = ROOT.TLorentzVector()
        met.SetPtEtaPhiM(s.met_pt, 0, s.met_phi, 0 )
        gamma.SetPtEtaPhiM(s.photon_genPt, s.photon_genEta, s.photon_genPhi, 0)
        metGamma = met + gamma

	s.met_pt_photon  = metGamma.Pt()
	s.met_phi_photon = metGamma.Phi()

	mt2Calc.setMet(metGamma.Pt(), metGamma.Phi())
	s.mt2ll_photon = mt2Calc.mt2ll()


# Create a maker. Maker class will be compiled. This instance will be used as a parent in the loop
treeMaker_parent = TreeMaker(
    filler = filler,
    variables = [ Variable.fromString(x) for x in new_variables ],
    treeName = "Events"
    )

# Split input in ranges
if options.nJobs>1:
    eventRanges = reader.getEventRanges( nJobs = options.nJobs )
else:
    eventRanges = reader.getEventRanges( maxNEvents = options.eventsPerJob, minJobs = options.minNJobs )

logger.info( "Splitting into %i ranges of %i events on average.",  len(eventRanges), (eventRanges[-1][1] - eventRanges[0][0])/len(eventRanges) )

#Define all jobs
jobs = [(i, eventRanges[i]) for i in range(len(eventRanges))]

filename, ext = os.path.splitext( os.path.join(outDir, sample.name + '.root') )

clonedEvents = 0
convertedEvents = 0
outputLumiList = {}
for ievtRange, eventRange in enumerate( eventRanges ):

    if len(options.job)>0 and not ievtRange in options.job: continue

    logger.info( "Processing range %i/%i from %i to %i which are %i events.",  ievtRange, len(eventRanges), eventRange[0], eventRange[1], eventRange[1]-eventRange[0] )

    # Check whether file exists
    outfilename = filename+'_'+str(ievtRange)+ext
    if os.path.isfile(outfilename):
        logger.info( "Output file %s found.", outfilename)
        if not checkRootFile(outfilename, checkForObjects=["Events"]):
            logger.info( "File %s is broken. Overwriting.", outfilename)
        elif not options.overwrite:
            logger.info( "Skipping.")
            continue
        else:
            logger.info( "Overwriting.")

    tmp_directory = ROOT.gDirectory
    outputfile = ROOT.TFile.Open(outfilename, 'recreate')
    tmp_directory.cd()

    # Set the reader to the event range
    reader.setEventRange( eventRange )
    clonedTree = reader.cloneTree( [], newTreename = "Events", rootfile = outputfile )
    clonedEvents += clonedTree.GetEntries()

    # Clone the empty maker in order to avoid recompilation at every loop iteration
    maker = treeMaker_parent.cloneWithoutCompile( externalTree = clonedTree )

    maker.start()
    # Do the thing
    reader.start()

    while reader.run():
        maker.run()

    convertedEvents += maker.tree.GetEntries()
    maker.tree.Write()
    outputfile.Close()
    logger.info( "Written %s", outfilename)

  # Destroy the TTree
    maker.clear()


logger.info( "Converted %i events of %i, cloned %i",  convertedEvents, reader.nEvents , clonedEvents )
