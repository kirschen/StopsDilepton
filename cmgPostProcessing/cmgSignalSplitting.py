#!/usr/bin/env python

# standard imports
import ROOT
import sys
import os
import copy
import random
import subprocess
import datetime
import shutil

from array import array
from operator import mul
from math import sqrt, atan2, sin, cos

# RootTools
from RootTools.core.standard import *

# User specific
import StopsDilepton.tools.user as user

# Tools for systematics
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.helpers import closestOSDLMassToMZ, checkRootFile, writeObjToFile, m3, deltaR, bestDRMatchInCollection
from StopsDilepton.tools.addJERScaling import addJERScaling
from StopsDilepton.tools.objectSelection import getMuons, getElectrons, muonSelector, eleSelector, getGoodLeptons, getGoodAndOtherLeptons,  getGoodBJets, getGoodJets, isBJet, jetId, isBJet, getGoodPhotons, getGenPartsAll, multiIsoWPInt
from StopsDilepton.tools.overlapRemovalTTG import getTTGJetsEventType
from StopsDilepton.tools.getGenBoson import getGenZ, getGenPhoton

from StopsDilepton.tools.triggerEfficiency import triggerEfficiency
triggerEff_withBackup = triggerEfficiency(with_backup_triggers = True)
triggerEff            = triggerEfficiency(with_backup_triggers = False)

from StopsDilepton.tools.leptonHIPEfficiency import leptonHIPEfficiency
leptonHIPSF = leptonHIPEfficiency()

#MC tools
from StopsDilepton.tools.mcTools import pdgToName, GenSearch, B_mesons, D_mesons, B_mesons_abs, D_mesons_abs
genSearch = GenSearch()

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
#        default=['MuonEG_Run2015D_16Dec'],
        default=['TTJets'],
        help="List of samples to be post-processed, given as CMG component name"
        )

    argParser.add_argument('--triggerSelection',
        action='store',
        nargs='?',
        type=str,
        default=None,
        choices=['mumu', 'ee', 'mue', 'mu_for_mumu', 'e_for_ee', 'mu_for_mue', 'e_for_mue'],
        help="Trigger selection?"
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
        default='postProcessed_80X_v21',
        help="Name of the processing era"
        )

    argParser.add_argument('--skim',
        action='store',
        nargs='?',
        type=str,
        default='dilepTiny',
        help="Skim conditions to be applied for post-processing"
        )

    argParser.add_argument('--LHEHTCut',
        action='store',
        nargs='?',
        type=int,
        default=-1,
        help="LHE cut."
        )

    argParser.add_argument('--keepForwardJets',
        action='store_true',
        help="Is T2tt signal?"
        )

    argParser.add_argument('--small',
        action='store_true',
        help="Run the file on a small sample (for test purpose), bool flag set to True if used",
        #default = True
        )

    argParser.add_argument('--T2tt',
        action='store_true',
        help="Is T2tt signal?"
        )
    
    argParser.add_argument('--T8bbllnunu',
        action='store_true',
        help="Is T8bbllnunu signal?"
        )

    argParser.add_argument('--TTDM',
        action='store_true',
        help="Is TTDM signal?"
        )

    argParser.add_argument('--fastSim',
        action='store_true',
        help="FastSim?"
        )

    argParser.add_argument('--skipGenLepMatching',
        action='store_true',
        help="skip matched genleps??"
        )

    argParser.add_argument('--keepLHEWeights',
        action='store_true',
        help="Keep LHEWeights?"
        )

    argParser.add_argument('--checkTTGJetsOverlap',
        action='store_true',
        default=True,
        help="Keep TTGJetsEventType which can be used to clean TTG events from TTJets samples"
        )

    argParser.add_argument('--skipSystematicVariations',
        action='store_true',
        help="Don't calulcate BTag, JES and JER variations."
        )

    argParser.add_argument('--noTopPtReweighting',
        action='store_true',
        help="Skip top pt reweighting.")

    return argParser

options = get_parser().parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile ='/tmp/%s_%s.txt'%(options.skim, '_'.join(options.samples) ) )
logFileLocation = '/tmp/%s_%s.txt'%(options.skim, '_'.join(options.samples) )

import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

# flags (I think string searching is slow, so let's not do it in the filler function)
isDiLep     =   options.skim.lower().startswith('dilep')
isTriLep     =   options.skim.lower().startswith('trilep')
isSingleLep =   options.skim.lower().startswith('singlelep')
isTiny      =   options.skim.lower().count('tiny') 
isSmall      =   options.skim.lower().count('small')
isInclusive  = options.skim.lower().count('inclusive') 
isVeryLoose =  'veryloose' in options.skim.lower()
isVeryLoosePt10 =  'veryloosept10' in options.skim.lower()
isLoose     =  'loose' in options.skim.lower() and not isVeryLoose
isJet250    = 'jet250' in options.skim.lower()

# Skim condition
skimConds = []
if isDiLep:
    skimConds.append( "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5) + Sum$(LepOther_pt>20&&abs(LepOther_eta)<2.5)>=2" )
if isTriLep:
    raise NotImplementedError
    # skimConds.append( "Sum$(LepGood_pt>20&&abs(LepGood_eta)&&LepGood_miniRelIso<0.4) + Sum$(LepOther_pt>20&&abs(LepOther_eta)<2.5&&LepGood_miniRelIso<0.4)>=2 && Sum$(LepOther_pt>10&&abs(LepOther_eta)<2.5)+Sum$(LepGood_pt>10&&abs(LepGood_eta)<2.5)>=3" )
elif isSingleLep:
    skimConds.append( "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5) + Sum$(LepOther_pt>20&&abs(LepOther_eta)<2.5)>=1" )
elif isJet250:
    skimConds.append( "Sum$(Jet_pt>250) +  Sum$(DiscJet_pt>250) + Sum$(JetFailId_pt>250) + Sum$(gamma_pt>250) > 0" )

if isInclusive:
    skimConds = []

#Samples: Load samples
maxN = 2 if options.small else None
from StopsDilepton.samples.helpers import fromHeppySample
if options.T2tt or options.T8bbllnunu:
    samples = [ fromHeppySample(s, data_path = options.dataDir, maxN = maxN) for s in options.samples ]
    from StopsDilepton.samples.helpers import getT2ttSignalWeight
    logger.info( "SUSY signal samples to be processed: %s", ",".join(s.name for s in samples) )
    # FIXME I'm forcing ==1 signal sample because I don't have a good idea how to construct a sample name from the complicated T2tt_x_y_z_... names
    assert len(samples)==1, "Can only process one SUSY sample at a time."
    samples[0].files = samples[0].files[:maxN]
    logger.debug( "Fetching signal weights..." )
    signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi )
    logger.debug("Done fetching signal weights.")
#elif options.TTDM:
#    samples = [ fromHeppySample(s, data_path = "/scratch/rschoefbeck/cmgTuples/80X_0l_TTDM/", \
#                    module = "CMGTools.StopsDilepton.TTbarDMJets_signals_RunIISpring16MiniAODv2",  
#                    maxN = maxN)\
#                for s in options.samples ]
else:
    samples = [ fromHeppySample(s, data_path = options.dataDir, maxN = maxN) for s in options.samples ]

if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(-1)

isData = False not in [s.isData for s in samples]
isMC   =  True not in [s.isData for s in samples]

sample_name_postFix = ""

#Samples: combine if more than one
if len(samples)>1:
    sample_name =  samples[0].name+"_comb"
    logger.info( "Combining samples %s to %s.", ",".join(s.name for s in samples), sample_name )
    sample = Sample.combine(sample_name, samples, maxN = maxN)
    if options.small: sample.reduceFiles( to=1 )
    # Clean up
    for s in samples:
        sample.clear()
elif len(samples)==1:
    sample = samples[0]
    sample.name+=sample_name_postFix
    if options.small: sample.reduceFiles( to = 1 )
else:
    raise ValueError( "Need at least one sample. Got %r",samples )


outDir = os.path.join(options.targetDir, options.processingEra, options.skim, sample.name)

if options.T2tt or options.T8bbllnunu:
    xSection = None
    # special filet for bad jets in FastSim: https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSRecommendationsICHEP16#Cleaning_up_of_fastsim_jets_from
    skimConds.append( "Sum$(JetFailId_pt>30&&abs(JetFailId_eta)<2.5&&JetFailId_mcPt==0&&JetFailId_chHEF<0.1)+Sum$(Jet_pt>30&&abs(Jet_eta)<2.5&&Jet_mcPt==0&&Jet_chHEF<0.1)==0" )
else:
    # Check that all samples which are concatenated have the same x-section.
    assert isData or len(set([s.heppy.xSection for s in samples]))==1, "Not all samples have the same xSection: %s !"%(",".join([s.name for s in samples]))
    assert isMC or len(samples)==1, "Don't concatenate data samples"

    xSection = samples[0].heppy.xSection if isMC else None


# Directory for individual signal files
if options.T2tt:
    signalDir = os.path.join(options.targetDir, options.processingEra, options.skim, "T2tt")
    if not os.path.exists(signalDir): os.makedirs(signalDir)

if options.T8bbllnunu:
    T8bbllnunu_strings = options.samples[0].split('_')
    for st in T8bbllnunu_strings:
        if 'XSlep' in st:
            x_slep = st.replace('XSlep','')
            logger.info("Factor x_slep in this sample is %s",x_slep)
        if 'XCha' in st:
            x_cha = st.replace('XCha','')
            logger.info("Factor x_cha in this sample is %s",x_cha)
    signalSubDir = options.samples[0].replace('SMS_','')

    signalDir = os.path.join(options.targetDir, options.processingEra, options.skim, "T8bbllnunu")
    if not os.path.exists(signalDir): os.makedirs(signalDir) #FIXME

try:    #Avoid trouble with race conditions in multithreading
    os.makedirs(outDir)
    logger.info( "Created output directory %s.", outDir )
except:
    pass


# Write one file per mass point for T2tt
if options.T2tt or options.T8bbllnunu:
    if options.T2tt: output = Sample.fromDirectory("T2tt_output", outDir)
    else: output = Sample.fromDirectory("T8bbllnunu_output", outDir) #FIXME
    print "Initialising chain, otherwise first mass point is empty"
    print output.chain
    if options.small: output.reduceFiles( to = 1 )
    for s in signalWeight.keys():
        #cut = "GenSusyMStop=="+str(s[0])+"&&GenSusyMNeutralino=="+str(s[1]) #FIXME
        logger.info("Going to write masspoint mStop %i mNeu %i", s[0], s[1])
        cut = "Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000006))=="+str(s[0])+"&&Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000022))=="+str(s[1])
        logger.debug("Using cut %s", cut)
        if options.T2tt: signal_prefix = 'T2tt_'
        else: signal_prefix = 'T8bbllnunu_XCha%s_XSlep%s_'%(x_cha,x_slep)
        signalFile = os.path.join(signalDir, signal_prefix + str(s[0]) + '_' + str(s[1]) + '.root' )
        #signalFile = os.path.join(signalDir, 'T2tt_'+str(s[0])+'_'+str(s[1])+'.root' )
        logger.debug("Ouput file will be %s", signalFile)
        if not os.path.exists(signalFile) or options.overwrite:
            outF = ROOT.TFile.Open(signalFile, "RECREATE")
            t = output.chain.CopyTree(cut)
            nEvents = t.GetEntries()
            outF.Write()
            outF.Close()
            logger.info( "Number of events %i", nEvents)
            inF = ROOT.TFile.Open(signalFile, "READ")
            u = inF.Get("Events")
            nnEvents = u.GetEntries()
            logger.debug("Number of events in tree %i and in file %i", nEvents, nnEvents)
            if nEvents == nnEvents: logger.debug("All events written")
            else: logger.debug("Something went wrong, discrepancy between file and tree")
            inF.Close()
            logger.info( "Written signal file for masses mStop %i mNeu %i to %s", s[0], s[1], signalFile)
        else:
            logger.info( "Found file %s -> Skipping"%(signalFile) )

    output.clear()

logger.info("Copying log file to %s"%outDir)
copyLog = subprocess.call(['cp',logFileLocation,outDir])
if copyLog: print "Copying log from %s to %s failed"%(logFileLocation,outDir)
else: print "Successfully copied log file"
