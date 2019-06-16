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
from StopsDilepton.tools.helpers import closestOSDLMassToMZ, writeObjToFile, m3, deltaR, bestDRMatchInCollection
from StopsDilepton.tools.overlapRemovalTTG import getTTGJetsEventType
from StopsDilepton.tools.getGenBoson import getGenZ, getGenPhoton

from Analysis.Tools.helpers import deepCheckRootFile

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
        nargs='?',
        type=int,
        default=0,
        help="Run only job i"
        )

    argParser.add_argument('--minNJobs',
        action='store',
        nargs='?',
        type=int,
        default=1,
        help="Minimum number of simultaneous jobs."
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
    argParser.add_argument('--T2bW',
        action='store_true',
        help="Is T2tt signal?"
        )
    argParser.add_argument('--T2bt',
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

    argParser.add_argument('--year',
        action='store',
        type=int,
        help="Which year?"
        )


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


if options.year == 2016:
    from Samples.nanoAOD.Summer16_private_legacy_v1 import allSamples as bkgSamples
    from Samples.nanoAOD.Summer16_private_legacy_v1 import SUSY as signalSamples
    from Samples.nanoAOD.Run2016_17Jul2018_private  import allSamples as dataSamples
    allSamples = bkgSamples + dataSamples + signalSamples
elif options.year == 2017:
    from Samples.nanoAOD.Fall17_private_legacy_v1   import allSamples as bkgSamples
    from Samples.nanoAOD.Fall17_private_legacy_v1   import SUSY as signalSamples
    from Samples.nanoAOD.Run2017_31Mar2018_private  import allSamples as dataSamples
    allSamples = bkgSamples + dataSamples
elif options.year == 2018:
    from Samples.nanoAOD.Spring18_private           import allSamples as HEMSamples
    from Samples.nanoAOD.Run2018_26Sep2018_private  import allSamples as HEMDataSamples
    from Samples.nanoAOD.Autumn18_private_legacy_v1 import allSamples as bkgSamples
    from Samples.nanoAOD.Run2018_17Sep2018_private  import allSamples as dataSamples
    allSamples = HEMSamples + HEMDataSamples + bkgSamples + dataSamples
else:
    raise NotImplementedError

samples = []
for selectedSamples in options.samples:
    for sample in allSamples:
        if selectedSamples == sample.name:
            samples.append(sample)

print [ s.name for s in samples ]
directory  = os.path.join(options.targetDir, options.processingEra)
output_directory = os.path.join( directory, options.skim, samples[0].name )
print output_directory

#Samples: Load samples
maxN = 2 if options.small else None
if options.T2tt or options.T8bbllnunu or options.T2bW or options.T2bt:
    from StopsDilepton.samples.helpers import getT2ttSignalWeight
    logger.info( "SUSY signal samples to be processed: %s", ",".join(s.name for s in samples) )
    # FIXME I'm forcing ==1 signal sample because I don't have a good idea how to construct a sample name from the complicated T2tt_x_y_z_... names
    assert len(samples)==1, "Can only process one SUSY sample at a time."
    samples[0].files = samples[0].files[:maxN]
    logger.debug( "Fetching signal weights..." )
    signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi, cacheDir = '/afs/hephy.at/data/cms01/stopsDilepton/signals/caches/%s/'%(options.year)) #Can use same x-sec/weight for T8bbllnunu as for T2tt
    logger.debug("Done fetching signal weights.")

if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(-1)

isData = False not in [s.isData for s in samples]
isMC   =  True not in [s.isData for s in samples]

sample_name_postFix = ""

outDir = os.path.join(options.targetDir, options.processingEra, options.skim, samples[0].name)

print outDir

if options.T2tt or options.T8bbllnunu or options.T2bW or options.T2bt:
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

if options.T2bt:
    signalDir = os.path.join(options.targetDir, options.processingEra, options.skim, "T2bt")
    if not os.path.exists(signalDir): os.makedirs(signalDir)

if options.T2bW:
    signalDir = os.path.join(options.targetDir, options.processingEra, options.skim, "T2bW")
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

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


nJobs = options.nJobs
chunkSize = len(signalWeight.keys())/nJobs
if not len(signalWeight.keys())%nJobs == 0: chunkSize += 1

masspoints = list(chunks(signalWeight.keys(), chunkSize))

job = options.job

print "All masspoints:"
print masspoints

print "Running over:"
print masspoints[job]

# Write one file per mass point for T2tt
if options.T2tt or options.T8bbllnunu  or options.T2bW or options.T2bt:
    if options.T2tt: output = Sample.fromDirectory("T2tt_output", outDir)
    elif options.T2bW: output = Sample.fromDirectory("T2bW_output", outDir)
    elif options.T2bt: output = Sample.fromDirectory("T2bt_output", outDir)
    else: output = Sample.fromDirectory("T8bbllnunu_output", outDir) #FIXME
    print "Initialising chain, otherwise first mass point is empty"
    print output.chain
    if options.small: output.reduceFiles( to = 1 )
    for i,s in enumerate(masspoints[job]):
        #cut = "GenSusyMStop=="+str(s[0])+"&&GenSusyMNeutralino=="+str(s[1]) #FIXME
        logger.info("Going to write masspoint mStop %i mNeu %i", s[0], s[1])
        cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(s[0])+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(s[1])
        logger.debug("Using cut %s", cut)
        if options.T2tt: signal_prefix = 'T2tt_'
        elif options.T2bW: signal_prefix = 'T2bW_'
        elif options.T2bt: signal_prefix = 'T2bt_'
        else: signal_prefix = 'T8bbllnunu_XCha%s_XSlep%s_'%(x_cha,x_slep)
        signalFile = os.path.join(signalDir, signal_prefix + str(s[0]) + '_' + str(s[1]) + '.root' )
        #signalFile = os.path.join(signalDir, 'T2tt_'+str(s[0])+'_'+str(s[1])+'.root' )
        logger.debug("Ouput file will be %s", signalFile)
        if not (os.path.exists(signalFile) and deepCheckRootFile(signalFile)) or options.overwrite:
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
        logger.info("Done with %s/%s", i+1, len(masspoints[job])) 

    output.clear()

#logger.info("Copying log file to %s"%outDir)
#copyLog = subprocess.call(['cp',logFileLocation,outDir])
#if copyLog: print "Copying log from %s to %s failed"%(logFileLocation,outDir)
#else: print "Successfully copied log file"
