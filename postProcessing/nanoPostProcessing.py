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
from StopsDilepton.tools.user import MVA_preprocessing_directory, MVA_model_directory

# Tools for systematics
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.helpers import closestOSDLMassToMZ, checkRootFile, writeObjToFile, m3, deltaR, bestDRMatchInCollection, deltaPhi
from StopsDilepton.tools.addJERScaling import addJERScaling
from StopsDilepton.tools.objectSelection import getMuons, getElectrons, muonSelector, eleSelector, getGoodMuons, getGoodElectrons,  getGoodJets, isBJet, jetId, isBJet, getGoodPhotons, getGenPartsAll
from StopsDilepton.tools.overlapRemovalTTG import getTTGJetsEventType
from StopsDilepton.tools.getGenBoson import getGenZ, getGenPhoton
from StopsDilepton.tools.polReweighting import getPolWeights
from StopsDilepton.tools.puProfileCache import puProfile

# For MVA discriminator
from StopsDilepton.MVA.KerasReader import KerasReader

from StopsDilepton.tools.triggerEfficiency import triggerEfficiency
triggerEff_withBackup = triggerEfficiency(with_backup_triggers = True)
triggerEff            = triggerEfficiency(with_backup_triggers = False)

from StopsDilepton.tools.leptonTrackingEfficiency import leptonTrackingEfficiency
leptonTrackingSF = leptonTrackingEfficiency()

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

    argParser.add_argument('--logLevel',    action='store',         nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],   default='INFO', help="Log level for logging" )
    argParser.add_argument('--samples',     action='store',         nargs='*',  type=str, default=['TTZToLLNuNu_ext'],                  help="List of samples to be post-processed, given as CMG component name" )
    argParser.add_argument('--eventsPerJob',action='store',         nargs='?',  type=int, default=30000000,                             help="Maximum number of events per job (Approximate!)." )
    argParser.add_argument('--nJobs',       action='store',         nargs='?',  type=int, default=1,                                    help="Maximum number of simultaneous jobs." )
    argParser.add_argument('--job',         action='store',                     type=int, default=0,                                    help="Run only jobs i" )
    argParser.add_argument('--minNJobs',    action='store',         nargs='?',  type=int, default=1,                                    help="Minimum number of simultaneous jobs." )
    argParser.add_argument('--dataDir',     action='store',         nargs='?',  type=str, default=user.cmg_directory,                   help="Name of the directory where the input data is stored (for samples read from Heppy)." )
    argParser.add_argument('--targetDir',   action='store',         nargs='?',  type=str, default=user.data_output_directory,           help="Name of the directory the post-processed files will be saved" )
    argParser.add_argument('--processingEra', action='store',       nargs='?',  type=str, default='postProcessed_80X_v22',              help="Name of the processing era" )
    argParser.add_argument('--skim',        action='store',         nargs='?',  type=str, default='dilepTiny',                          help="Skim conditions to be applied for post-processing" )
    argParser.add_argument('--LHEHTCut',    action='store',         nargs='?',  type=int, default=-1,                                   help="LHE cut." )
    argParser.add_argument('--year',        action='store',                     type=int,                                               help="Which year?" )
    argParser.add_argument('--overwrite',   action='store_true',                                                                        help="Overwrite existing output files, bool flag set to True  if used" )
    argParser.add_argument('--keepAllJets', action='store_true',                                                                        help="Keep also forward jets?" )
    argParser.add_argument('--small',       action='store_true',                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used" )
    argParser.add_argument('--susySignal',  action='store_true',                                                                        help="Is SUSY signal?" )
    argParser.add_argument('--TTDM',        action='store_true',                                                                        help="Is TTDM signal?" )
    argParser.add_argument('--fastSim',     action='store_true',                                                                        help="FastSim?" )
    argParser.add_argument('--triggerSelection',            action='store_true',                                                        help="Trigger selection?" ) 
    argParser.add_argument('--skipGenLepMatching',          action='store_true',                                                        help="skip matched genleps??" )
    argParser.add_argument('--keepLHEWeights',              action='store_true',                                                        help="Keep LHEWeights?" )
    argParser.add_argument('--checkTTGJetsOverlap',         action='store_true',                                                        help="Keep TTGJetsEventType which can be used to clean TTG events from TTJets samples" )
    argParser.add_argument('--skipSystematicVariations',    action='store_true',                                                        help="Don't calulcate BTag, JES and JER variations.")
    argParser.add_argument('--noTopPtReweighting',          action='store_true',                                                        help="Skip top pt reweighting.")
    argParser.add_argument('--fileBasedSplitting',          action='store_true',                                                        help="Split njobs according to files")
    argParser.add_argument('--forceProxy',                  action='store_true',                                                        help="Don't check certificate")

    return argParser

options = get_parser().parse_args()

# Logging
import StopsDilepton.tools.logger as _logger
logFile = '/tmp/%s_%s_%s_njob%s.txt'%(options.skim, '_'.join(options.samples), os.environ['USER'], str(0 if options.nJobs==1 else options.job))
logger  = _logger.get_logger(options.logLevel, logFile = logFile)

import RootTools.core.logger as _logger_rt
logger_rt = _logger_rt.get_logger(options.logLevel, logFile = None )

_logger.   add_fileHandler( user.data_output_directory + '/logs/%s_%s_debug.txt'%(options.samples[0], options.job), options.logLevel )

# Flags 
isDiLep     =   options.skim.lower().startswith('dilep')
isTriLep     =   options.skim.lower().startswith('trilep')
isSingleLep =   options.skim.lower().startswith('singlelep')
isTiny      =   options.skim.lower().count('tiny') 
isSmall      =   options.skim.lower().count('small')
isInclusive  = options.skim.lower().count('inclusive') 

writeToDPM = options.targetDir == '/dpm/'

fastSim = options.fastSim
if options.susySignal: fastSim = True

# Skim condition
skimConds = []
if isDiLep:
    skimConds.append( "Sum$(Electron_pt>20&&abs(Electron_eta)<2.5) + Sum$(Muon_pt>20&&abs(Muon_eta)<2.5)>=2" )
if isTriLep:
    skimConds.append( "Sum$(Electron_pt>20&&abs(Electron_eta)&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>20&&abs(Muon_eta)<2.5&&Muon_pfRelIso03_all<0.4)>=2 && Sum$(Electron_pt>10&&abs(Electron_eta)<2.5)+Sum$(Muon_pt>10&&abs(Muon_eta)<2.5)>=3" )
elif isSingleLep:
    skimConds.append( "Sum$(Electron_pt>20&&abs(Electron_eta)<2.5) + Sum$(Muon_pt>20&&abs(Muon_eta)<2.5)>=1" )

if isInclusive:
    skimConds = []

#Samples: Load samples
maxN = 2 if options.small else None

#from nanoMET.samples.helpers import fromNanoSample
if options.year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16          import allSamples as bkgSamples
    from StopsDilepton.samples.nanoTuples_FastSim_Spring16  import allSamples as signalSamples
    from StopsDilepton.samples.nanoTuples_Run2016_05Feb2018 import allSamples as dataSamples
    allSamples = bkgSamples + signalSamples + dataSamples
elif options.year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17 import allSamples as bkgSamples
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018 import allSamples as dataSamples
    allSamples = bkgSamples + dataSamples
else:
    raise NotImplementedError

samples = []
for selectedSamples in options.samples:
    for sample in allSamples:
        if selectedSamples == sample.name:
            samples.append(sample)

if len(samples)==0:
    logger.info( "No samples found. Was looking for %s. Exiting" % options.samples )
    sys.exit(-1)

isData = False not in [s.isData for s in samples]
isMC   =  True not in [s.isData for s in samples]


if options.susySignal:
    xSection = None
    ## special filet for bad jets in FastSim: https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSRecommendationsICHEP16#Cleaning_up_of_fastsim_jets_from
    #skimConds.append( "Sum$(JetFailId_pt>30&&abs(JetFailId_eta)<2.5&&JetFailId_mcPt==0&&JetFailId_chHEF<0.1)+Sum$(Jet_pt>30&&abs(Jet_eta)<2.5&&Jet_mcPt==0&&Jet_chHEF<0.1)==0" )
else:
    # Check that all samples which are concatenated have the same x-section.
    assert isData or len(set([s.xSection for s in samples]))==1, "Not all samples have the same xSection: %s !"%(",".join([s.name for s in samples]))
    assert isMC or len(samples)==1, "Don't concatenate data samples"

    xSection = samples[0].xSection if isMC else None

# Trigger selection
from StopsDilepton.tools.triggerSelector import triggerSelector
ts = triggerSelector(options.year)
triggerCond  = ts.getSelection(options.samples[0] if isData else "MC")
treeFormulas = {"triggerDecision": {'string':triggerCond} }
if isData and options.triggerSelection:
    logger.info("Sample will have the following trigger skim: %s"%triggerCond)
    skimConds.append( triggerCond )

sample_name_postFix = ""

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
    sample.name+=sample_name_postFix
else:
    raise ValueError( "Need at least one sample. Got %r",samples )

if options.fileBasedSplitting:
    len_orig = len(sample.files)
    sample = sample.split( n=options.nJobs, nSub=options.job)
    logger.info( "fileBasedSplitting: Run over %i/%i files for job %i/%i."%(len(sample.files), len_orig, options.job, options.nJobs))
    print sample.files
    logger.debug( "fileBasedSplitting: Files to be run over:\n%s", "\n".join(sample.files) )


if isMC:
    from StopsDilepton.tools.puReweighting import getReweightingFunction
    if options.year == 2016:
        nTrueInt36fb_puRW       = getReweightingFunction(data="PU_2016_36000_XSecCentral", mc="Summer16")
        nTrueInt36fb_puRWDown   = getReweightingFunction(data="PU_2016_36000_XSecDown",    mc="Summer16")
        nTrueInt36fb_puRWUp     = getReweightingFunction(data="PU_2016_36000_XSecUp",      mc="Summer16")
    elif options.year == 2017:
        # keep the weight name for now. Should we update to a more general one?
        puProfiles = puProfile( source_sample = samples[0] )
        mcHist = puProfiles.cachedTemplate( selection="( 1 )", weight='genWeight', overwrite=False ) # use genWeight for amc@NLO samples. No problems encountered so far
        nTrueInt36fb_puRW       = getReweightingFunction(data="PU_2017_42400_XSecCentral",  mc=mcHist)
        nTrueInt36fb_puRWDown   = getReweightingFunction(data="PU_2017_42400_XSecDown",     mc=mcHist)
        nTrueInt36fb_puRWUp     = getReweightingFunction(data="PU_2017_42400_XSecUp",       mc=mcHist)

options.skim = options.skim + '_small' if options.small else options.skim

# LHE cut (DY samples)
if options.LHEHTCut>0:
    sample.name+="_lheHT"+str(options.LHEHTCut)
    logger.info( "Adding upper LHE cut at %f", options.LHEHTCut )
    skimConds.append( "LHE_HTIncoming<%f"%options.LHEHTCut )

directory  = os.path.join(options.targetDir, options.processingEra)
output_directory = os.path.join( directory, options.skim, sample.name )

if options.susySignal:
    from StopsDilepton.samples.helpers import getT2ttSignalWeight
    logger.info( "SUSY signal samples to be processed: %s", ",".join(s.name for s in samples) )
    # FIXME I'm forcing ==1 signal sample because I don't have a good idea how to construct a sample name from the complicated T2tt_x_y_z_... names
    assert len(samples)==1, "Can only process one SUSY sample at a time."
    samples[0].files = samples[0].files[:maxN]
    logger.info( "Fetching signal weights..." )
    signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi, cacheDir = output_directory) #Can use same x-sec/weight for T8bbllnunu as for T2tt
    logger.info("Done fetching signal weights.")

# top pt reweighting
from StopsDilepton.tools.topPtReweighting import getUnscaledTopPairPtReweightungFunction, getTopPtDrawString, getTopPtsForReweighting
# Decision based on sample name -> whether TTJets or TTLep is in the sample name
isTT = sample.name.startswith("TTJets") or sample.name.startswith("TTLep") or sample.name.startswith("TT_pow")
doTopPtReweighting = isTT and not options.noTopPtReweighting
if doTopPtReweighting:
    logger.info( "Sample will have top pt reweighting." )
    topPtReweightingFunc = getUnscaledTopPairPtReweightungFunction(selection = "dilep")
    # Compute x-sec scale factor on unweighted events
    selectionString = "&&".join(skimConds)
    topScaleF = sample.getYieldFromDraw( selectionString = selectionString, weightString = getTopPtDrawString(selection = "dilep"))
    topScaleF = topScaleF['val']/float(sample.chain.GetEntries(selectionString))
    logger.info( "Found topScaleF %f", topScaleF )
else:
    topScaleF = 1
    logger.info( "Sample will NOT have top pt reweighting. topScaleF=%f",topScaleF )

if isTT:
    from StopsDilepton.analysis.daniel.isrWeight import *
    isr = ISRweight()
    logger.info("Sample will have ISR reweighting called reweight_nISR.")

if fastSim:
   from StopsDilepton.tools.leptonFastSimSF import leptonFastSimSF as leptonFastSimSF_
   leptonFastSimSF = leptonFastSimSF_()

from StopsDilepton.tools.leptonSF import leptonSF as leptonSF_
leptonSF = leptonSF_()


# systematic variations
addSystematicVariations = (not isData) and (not options.skipSystematicVariations)
if addSystematicVariations:
    # B tagging SF
    from StopsDilepton.tools.btagEfficiency import btagEfficiency
    btagEff = btagEfficiency( fastSim = fastSim )

# Directory for individual signal files
if options.susySignal:
    signalSubDir = options.samples[0].split('_')[1]
    signalDir = os.path.join(directory, options.skim, signalSubDir)
    logger.info("Separate files for each mass point will be located in %s"%signalDir)
    if not os.path.exists(signalDir): os.makedirs(signalDir)

if os.path.exists(output_directory) and options.overwrite:
    if options.nJobs > 1:
        logger.warning( "NOT removing directory %s because nJobs = %i", output_directory, options.nJobs )
    else:
        logger.info( "Output directory %s exists. Deleting.", output_directory )
        shutil.rmtree(output_directory)

try:    #Avoid trouble with race conditions in multithreading
    os.makedirs(output_directory)
    logger.info( "Created output directory %s.", output_directory )
except:
    pass

#branches to be kept for data and MC
branchKeepStrings_DATAMC = [\
    "run", "luminosityBlock", "event", "fixedGridRhoFastjetAll", "PV_npvs", "PV_npvsGood",
    "MET_pt", "MET_phi","MET_MetUnclustEnUpDeltaX", "MET_MetUnclustEnUpDeltaY", "MET_sumEt", "CaloMET_phi", "CaloMET_pt", "CaloMET_sumEt", "MET_covXX", "MET_covXY", "MET_covYY", "MET_significance",
    "RawMET_phi", "RawMET_pt", "RawMET_sumEt",
    "Flag_*","HLT_*",
    "nJet", "Jet_*",
    "nElectron", "Electron_*",
    "nMuon", "Muon_*",
    #"nTau", "Tau_*",
]

#branches to be kept for MC samples only
branchKeepStrings_MC = [\
    "Generator_*", "GenPart_*", "nGenPart", "genWeight", "Pileup_nTrueInt",
]

#branches to be kept for data only
branchKeepStrings_DATA = [ ]

# Jet variables to be read from chain
jetCorrInfo = []
jetMCInfo = []

#if not (isTiny or isSmall):
#    branchKeepStrings_DATAMC+=[
#        "nPhoton", "Photon_hoe", "Photon_r9", "Photon_sieie", "Photon_pfRelIso03_chg",
#        "Photon_pt", "Photon_eta", "Photon_phi", "Photon_mass",]
#    branchKeepStrings_DATAMC+= ["Photon_cutBased"] if (not options.year == 2017) else ["Photon_cutBasedBitmap"]

if sample.isData:
    lumiScaleFactor=None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_DATA
    from FWCore.PythonUtilities.LumiList import LumiList
    # Apply golden JSON
    if options.year == 2016:
        sample.json = '$CMSSW_BASE/src/StopsDilepton/tools/data/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
    elif options.year == 2017:
        sample.json = '$CMSSW_BASE/src/StopsDilepton/tools/data/json/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
    else:
        sample.json = '$CMSSW_BASE/src/StopsDilepton/tools/data/json/Cert_314472-318876_13TeV_PromptReco_Collisions18_JSON.txt'
    
    lumiList = LumiList(os.path.expandvars(sample.json))
    logger.info( "Loaded json %s", sample.json )
else:
    lumiScaleFactor = xSection*targetLumi/float(sample.normalization) if xSection is not None else None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC

jetVars = ['pt/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F', 'rawFactor/F', 'eta/F', 'phi/F', 'jetId/I', 'btagDeepB/F', 'btagCSVV2/F', 'area/F'] + jetCorrInfo + jetMCInfo
jetVarNames = [x.split('/')[0] for x in jetVars]
genLepVars      = ['pt/F', 'phi/F', 'eta/F', 'pdgId/I', 'genPartIdxMother/I', 'status/I', 'statusFlags/I'] # some might have different types
genLepVarNames  = [x.split('/')[0] for x in genLepVars]
lepVars     = ['pt/F','eta/F','phi/F','pdgId/I','cutBased/I','miniPFRelIso_all/F','pfRelIso03_all/F','sip3d/F','lostHits/b','convVeto/O','dxy/F','dz/F','charge/I','deltaEtaSC/F','mediumId/O']
lepVarNames = [x.split('/')[0] for x in lepVars]

read_variables = map(TreeVariable.fromString, ['MET_pt/F', 'MET_phi/F', 'run/I', 'luminosityBlock/I', 'event/l', 'PV_npvs/I', 'PV_npvsGood/I'] )
read_variables += [ TreeVariable.fromString('nPhoton/I'),
                    VectorTreeVariable.fromString('Photon[pt/F,eta/F,phi/F,mass/F,cutBased/I,pdgId/I]') if (not options.year == 2017) else VectorTreeVariable.fromString('Photon[pt/F,eta/F,phi/F,mass/F,cutBasedBitmap/I,pdgId/I]') ]

new_variables = [ 'weight/F']
if isMC:
    read_variables += [ TreeVariable.fromString('Pileup_nTrueInt/F') ]
    # reading gen particles for top pt reweighting
    read_variables.append( TreeVariable.fromString('nGenPart/I') )
    read_variables.append( VectorTreeVariable.fromString('GenPart[pt/F,mass/F,phi/F,eta/F,pdgId/I,genPartIdxMother/I,status/I,statusFlags/I]', nMax=200 )) # default nMax is 100, which would lead to corrupt values in this case
    read_variables.append( TreeVariable.fromString('genWeight/F') )

    new_variables.extend([ 'reweightTopPt/F', 'reweight_nISR/F', 'reweightPU/F','reweightPUUp/F','reweightPUDown/F', 'reweightPU12fb/F','reweightPU12fbUp/F','reweightPU12fbDown/F','reweightPU27fb/F','reweightPU27fbUp/F','reweightPU27fbDown/F', 'reweightPU36fb/F','reweightPU36fbUp/F','reweightPU36fbDown/F'])
    if not options.skipGenLepMatching:
        TreeVariable.fromString( 'nGenLep/I' ),
        new_variables.append( 'GenLep[%s]'% ( ','.join(genLepVars) ) )

read_variables += [\
    # now we don't have all IDs etc for both muons and electrons
    TreeVariable.fromString('nElectron/I'),
    VectorTreeVariable.fromString('Electron[pt/F,eta/F,phi/F,pdgId/I,cutBased/I,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,lostHits/b,convVeto/O,dxy/F,dz/F,charge/I,deltaEtaSC/F]'),
    TreeVariable.fromString('nMuon/I'),
    VectorTreeVariable.fromString('Muon[pt/F,eta/F,phi/F,pdgId/I,mediumId/O,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,dxy/F,dz/F,charge/I]'),
    TreeVariable.fromString('nJet/I'),
    VectorTreeVariable.fromString('Jet[%s]'% ( ','.join(jetVars) ) )
]

new_variables += [\
    'JetGood[%s]'% ( ','.join(jetVars) )
]

if isData: new_variables.extend( ['jsonPassed/I','isData/I'] )
new_variables.extend( ['nBTag/I', 'ht/F', 'metSig/F'] )
#new_variables.append( 'Lep[%s]'% ( ','.join(lepVars) ) )

if isSingleLep:
    new_variables.extend( ['m3/F', 'm3_ind1/I', 'm3_ind2/I', 'm3_ind3/I'] )
if isTriLep or isDiLep or isSingleLep:
    new_variables.extend( ['nGoodMuons/I', 'nGoodElectrons/I', 'nGoodLeptons/I' ] )
    new_variables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_pdgId/I', 'l1_index/I', 'l1_jetPtRelv2/F', 'l1_jetPtRatiov2/F', 'l1_miniRelIso/F', 'l1_relIso03/F', 'l1_dxy/F', 'l1_dz/F', 'l1_mIsoWP/I' ] )
    # new_variables.extend( ['mt/F', 'mlmZ_mass/F'] )
    new_variables.extend( ['mlmZ_mass/F'] )
    new_variables.extend( ['mt_photonEstimated/F'])
    if isMC: new_variables.extend(['reweightLeptonSF/F', 'reweightLeptonSFUp/F', 'reweightLeptonSFDown/F'])
if isTriLep or isDiLep:
    new_variables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_pdgId/I', 'l2_index/I', 'l2_jetPtRelv2/F', 'l2_jetPtRatiov2/F', 'l2_miniRelIso/F', 'l2_relIso03/F', 'l2_dxy/F', 'l2_dz/F', 'l2_mIsoWP/I' ] )
    new_variables.extend( ['isEE/I', 'isMuMu/I', 'isEMu/I', 'isOS/I' ] )
    new_variables.extend( ['dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_mass/F', 'MVA_T2tt_default/F', 'MVA_T2tt_lep_pt/F', 'MVA_T8bbllnunu_XCha0p5_XSlep0p09/F', 'MVA_T8bbllnunu_XCha0p5_XSlep0p5_800_1/F'] )
    new_variables.extend( ['dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F' ] )
    if isMC: new_variables.extend( \
        [   'zBoson_genPt/F', 'zBoson_genEta/F', 
            'reweightDilepTrigger/F', 'reweightDilepTriggerUp/F', 'reweightDilepTriggerDown/F', 'reweightDilepTriggerBackup/F', 'reweightDilepTriggerBackupUp/F', 'reweightDilepTriggerBackupDown/F',
            'reweightLeptonTrackingSF/F',
         ] )
    #if options.susySignal:
    #    new_variables.extend( ['dl_mt2ll_gen/F', 'dl_mt2bb_gen/F', 'dl_mt2blbl_gen/F' ] )
new_variables.extend( ['nPhotonGood/I','photon_pt/F','photon_eta/F','photon_phi/F','photon_idCutBased/I'] )
if isMC: new_variables.extend( ['photon_genPt/F', 'photon_genEta/F'] )
new_variables.extend( ['met_pt_photonEstimated/F','met_phi_photonEstimated/F','metSig_photonEstimated/F'] )
new_variables.extend( ['photonJetdR/F','photonLepdR/F'] )
if isTriLep or isDiLep:
  new_variables.extend( ['dlg_mass/F','dl_mt2ll_photonEstimated/F', 'dl_mt2bb_photonEstimated/F', 'dl_mt2blbl_photonEstimated/F' ] )

if options.checkTTGJetsOverlap:
    new_variables.extend( ['TTGJetsEventType/I'] )

if addSystematicVariations:

    for var in ['JECUp', 'JECDown', 'JERUp', 'JERDown', 'UnclusteredEnUp', 'UnclusteredEnDown']:
        if 'Unclustered' not in var: new_variables.extend( ['nJetGood_'+var+'/I', 'nBTag_'+var+'/I','ht_'+var+'/F'] )
        new_variables.extend( ['met_pt_'+var+'/F', 'met_phi_'+var+'/F', 'metSig_'+var+'/F'] )
        if isTriLep or isDiLep:
            new_variables.extend( ['dl_mt2ll_'+var+'/F', 'dl_mt2bb_'+var+'/F', 'dl_mt2blbl_'+var+'/F'] )
        new_variables.extend( ['met_pt_photonEstimated_'+var+'/F', 'met_phi_photonEstimated_'+var+'/F', 'metSig_photonEstimated_'+var+'/F'] )
        if isTriLep or isDiLep:
            new_variables.extend( ['dl_mt2ll_photonEstimated_'+var+'/F', 'dl_mt2bb_photonEstimated_'+var+'/F', 'dl_mt2blbl_photonEstimated_'+var+'/F'] )
    # Btag weights Method 1a
    for var in btagEff.btagWeightNames:
        if var!='MC':
            new_variables.append('reweightBTag_'+var+'/F')

#if options.susySignal or options.TTDM:
#    read_variables += map(TreeVariable.fromString, ['met_genPt/F', 'met_genPhi/F'] )
if options.susySignal:
    #read_variables += map(TreeVariable.fromString, ['GenSusyMStop/I', 'GenSusyMNeutralino/I'] )
    new_variables  += ['reweightXSecUp/F', 'reweightXSecDown/F', 'mStop/I', 'mNeu/I']
    if  'T8bbllnunu' in options.samples[0]:
        new_variables  += ['mCha/I', 'mSlep/I', 'sleptonPdg/I']
    if 'T2tt' in options.samples[0]:
        new_variables  += ['weight_pol_L/F', 'weight_pol_R/F']

if fastSim and (isTriLep or isDiLep):
    new_variables  += ['reweightLeptonFastSimSF/F', 'reweightLeptonFastSimSFUp/F', 'reweightLeptonFastSimSFDown/F']


## Initialize keras for different trainings
from StopsDilepton.MVA.default_classifier import training_variables_list as training_variables_list
from StopsDilepton.MVA.default_classifier_lep_pt import training_variables_list as training_variables_list_lep_pt

MVA_T2tt_default    = KerasReader( 'SMS_T2tt_mStop_400to1200-TTLep_pow/v1/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-08-20-1005', training_variables_list )
MVA_T2tt_lep_pt     = KerasReader( 'SMS_T2tt_mStop_400to1200-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-08-16-1253', training_variables_list_lep_pt )

MVA_T8bbllnunu_XCha0p5_XSlep0p09        = KerasReader( 'SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow/v1/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-07-25-1522', training_variables_list )
MVA_T8bbllnunu_XCha0p5_XSlep0p5_800_1   = KerasReader( 'T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/v1/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-07-25-1153', training_variables_list )

# Define a reader
reader = sample.treeReader( \
    variables = read_variables ,
    selectionString = "&&".join(skimConds)
    )

# Calculate photonEstimated met
def getMetPhotonEstimated(met_pt, met_phi, photon):
  met = ROOT.TLorentzVector()
  met.SetPtEtaPhiM(met_pt, 0, met_phi, 0 )
  gamma = ROOT.TLorentzVector()
  gamma.SetPtEtaPhiM(photon['pt'], photon['eta'], photon['phi'], photon['mass'] )
  metGamma = met + gamma
  return (metGamma.Pt(), metGamma.Phi())


## Calculate corrected met pt/phi using systematics for jets
def getMetJetCorrected(met_pt, met_phi, jets, var):
  met_corr_px  = met_pt*cos(met_phi) + sum([(j['pt']-j['pt_'+var])*cos(j['phi']) for j in jets])
  met_corr_py  = met_pt*sin(met_phi) + sum([(j['pt']-j['pt_'+var])*sin(j['phi']) for j in jets])
  met_corr_pt  = sqrt(met_corr_px**2 + met_corr_py**2)
  met_corr_phi = atan2(met_corr_py, met_corr_px)
  return (met_corr_pt, met_corr_phi)

def getMetCorrected(r, var, addPhoton = None):
    if var == "":
      if addPhoton is not None: return getMetPhotonEstimated(r.met_pt, r.met_phi, addPhoton)
      else:                     return (r.met_pt, r.met_phi)

    elif var in [ "JECUp", "JECDown", "UnclusteredEnUp", "UnclusteredEnDown" ]:
      var_ = var
      var_ = var_.replace("JEC", "JetEn")
      var_ = var_.replace("JER", "JetRes")
      met_pt  = getattr(r, "met_" + var_ + "_Pt")
      met_phi = getattr(r, "met_" + var_ + "_Phi")
      if addPhoton is not None: return getMetPhotonEstimated(met_pt, met_phi, addPhoton)
      else:                     return (met_pt, met_phi)

    else:
        raise ValueError

mothers = {"D":0, "B":0}
grannies_D = {}
grannies_B = {}

def filler( event ):
    # shortcut
    r = reader.event
    workaround  = (r.run, r.luminosityBlock, r.event) # some fastsim files seem to have issues, apparently solved by this.
    event.isData = s.isData
    if isMC: gPart = getGenPartsAll(r)

    # weight
    if options.susySignal:
        r.GenSusyMStop = max([p['mass']*(abs(p['pdgId']==1000006)) for p in gPart])
        r.GenSusyMNeutralino = max([p['mass']*(abs(p['pdgId']==1000022)) for p in gPart])
        if 'T8bbllnunu' in options.samples[0]:
            r.GenSusyMChargino = max([p['mass']*(abs(p['pdgId']==1000024)) for p in gPart])
            r.GenSusyMSlepton = max([p['mass']*(abs(p['pdgId']==1000011)) for p in gPart]) #FIXME check PDG ID of slepton in sample
            #logger.debug("Slepton is selectron with mass %i", r.GenSusyMSlepton)
            event.sleptonPdg = 1000011
            if not r.GenSusyMSlepton > 0:
                r.GenSusyMSlepton = max([p['mass']*(abs(p['pdgId']==1000013)) for p in gPart])
                #logger.debug("Slepton is smuon with mass %i", r.GenSusyMSlepton)
                event.sleptonPdg = 1000013
            if not r.GenSusyMSlepton > 0:
                r.GenSusyMSlepton = max([p['mass']*(abs(p['pdgId']==1000015)) for p in gPart])
                #logger.debug("Slepton is stau with mass %i", r.GenSusyMSlepton)
                event.sleptonPdg = 1000015
            event.mCha  = r.GenSusyMChargino
            event.mSlep = r.GenSusyMSlepton
        #if 'T2tt' in options.samples[0]:
        #    pol_weights = getPolWeights(r)
        #    event.weight_pol_L = pol_weights[0]
        #    event.weight_pol_R = pol_weights[1]

        event.weight=signalWeight[(int(r.GenSusyMStop), int(r.GenSusyMNeutralino))]['weight']
        event.mStop = int(r.GenSusyMStop)
        event.mNeu  = int(r.GenSusyMNeutralino)
        event.reweightXSecUp    = signalWeight[(r.GenSusyMStop, r.GenSusyMNeutralino)]['xSecFacUp']
        event.reweightXSecDown  = signalWeight[(r.GenSusyMStop, r.GenSusyMNeutralino)]['xSecFacDown']
    elif isMC:
        event.weight = lumiScaleFactor*r.genWeight if lumiScaleFactor is not None else 1
    elif isData:
        event.weight = 1
    else:
        raise NotImplementedError( "isMC %r isData %r susySignal? %r TTDM? %r" % (isMC, isData, options.susySignal, options.TTDM) )

    # lumi lists and vetos
    if isData:
        #event.vetoPassed  = vetoList.passesVeto(r.run, r.lumi, r.evt)
        event.jsonPassed  = lumiList.contains(r.run, r.luminosityBlock)
        # store decision to use after filler has been executed
        event.jsonPassed_ = event.jsonPassed

    if isMC:
        event.reweightPU36fb     = nTrueInt36fb_puRW       ( r.Pileup_nTrueInt ) # is this correct?
        event.reweightPU36fbDown = nTrueInt36fb_puRWDown   ( r.Pileup_nTrueInt )
        event.reweightPU36fbUp   = nTrueInt36fb_puRWUp     ( r.Pileup_nTrueInt )

    # top pt reweighting
    if isMC: event.reweightTopPt = topPtReweightingFunc(getTopPtsForReweighting(r))/topScaleF if doTopPtReweighting else 1.

    # jet/met related quantities, also load the leptons already
    if options.keepAllJets:
        jetAbsEtaCut = 99.
    else:
        jetAbsEtaCut = 2.4
#    print r.nJet
#    if r.nJet == -1:
#        print "Error"
#        sys.exit(-1)
#
#    print "Good"
#    sys.exit(0)
        
    allJets      = getGoodJets(r, ptCut=0, jetVars = jetVarNames, absEtaCut=jetAbsEtaCut)
    jets         = filter(lambda j:jetId(j, ptCut=30, absEtaCut=jetAbsEtaCut), allJets)
    soft_jets    = filter(lambda j:jetId(j, ptCut=0,  absEtaCut=jetAbsEtaCut) and j['pt']<30., allJets) if options.keepAllJets else []
    bJets        = filter(lambda j:isBJet(j, tagger="CSVv2", year=options.year) and abs(j['eta'])<=2.4    , jets)
    nonBJets     = filter(lambda j:not ( isBJet(j, tagger="CSVv2", year=options.year) and abs(j['eta'])<=2.4 ), jets)

    # using miniRelIso 0.2 as baseline 
    ele_selector = eleSelector( "tight", year = options.year )
    electrons_pt10 = getGoodElectrons(r, ele_selector = ele_selector)
    mu_selector = muonSelector( "tight", year = options.year )
    muons_pt10 = getGoodMuons(r, mu_selector = mu_selector )

    for e in electrons_pt10:
        e['pdgId'] = int( 11*e['charge'] )
    for m in muons_pt10:
        m['pdgId'] = int( 13*m['charge'] )

    leptons_pt10 = electrons_pt10+muons_pt10
    leptons_pt10.sort(key = lambda p:-p['pt'])

    leptons      = filter(lambda l:l['pt']>20, leptons_pt10)
    leptons.sort(key = lambda p:-p['pt'])
    
    event.met_pt  = r.MET_pt
    event.met_phi = r.MET_phi

    # Filling jets
    store_jets = jets if not options.keepAllJets else soft_jets + jets
    store_jets.sort( key = lambda j:-j['pt'])
    event.nJetGood   = len(store_jets)
    for iJet, jet in enumerate(store_jets):
        for b in jetVarNames:
            getattr(event, "JetGood_"+b)[iJet] = jet[b]

    if isSingleLep:
        # Compute M3 and the three indiced of the jets entering m3
        event.m3, event.m3_ind1, event.m3_ind2, event.m3_ind3 = m3( jets )

    event.ht         = sum([j['pt'] for j in jets])
    event.metSig     = event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan')
    event.nBTag      = len(bJets)

    jets_sys      = {}
    bjets_sys     = {}
    nonBjets_sys  = {}

    metVariants = [''] # default

    # Keep photons and estimate met including (leading pt) photon
    photons = getGoodPhotons(r, ptCut=20, idLevel="loose", isData=isData, year=options.year)
    event.nPhotonGood = len(photons)
    if event.nPhotonGood > 0:
      metVariants += ['_photonEstimated']  # do all met calculations also for the photonEstimated variant
      event.photon_pt         = photons[0]['pt']
      event.photon_eta        = photons[0]['eta']
      event.photon_phi        = photons[0]['phi']
      event.photon_idCutBased = photons[0]['cutBased'] if (not options.year == 2017) else photons[0]['cutBasedBitmap']
      if isMC:
        genPhoton       = getGenPhoton(gPart)
        event.photon_genPt  = genPhoton['pt']  if genPhoton is not None else float('nan')
        event.photon_genEta = genPhoton['eta'] if genPhoton is not None else float('nan')

      event.met_pt_photonEstimated, event.met_phi_photonEstimated = getMetPhotonEstimated(r.MET_pt, r.MET_phi, photons[0])
      event.metSig_photonEstimated = event.met_pt_photonEstimated/sqrt(event.ht) if event.ht>0 else float('nan')

      event.photonJetdR = min(deltaR(photons[0], j) for j in jets) if len(jets) > 0 else 999
      event.photonLepdR = min(deltaR(photons[0], l) for l in leptons_pt10) if len(leptons_pt10) > 0 else 999

    if options.checkTTGJetsOverlap and isMC:
       event.TTGJetsEventType = getTTGJetsEventType(r)

    if addSystematicVariations:
        for j in allJets:
            j['pt_JECUp']   =j['pt']/j['corr']*j['corr_JECUp']
            j['pt_JECDown'] =j['pt']/j['corr']*j['corr_JECDown']
            # JERUp, JERDown, JER
            addJERScaling(j)
        for var in ['JECUp', 'JECDown', 'JERUp', 'JERDown']:
            jets_sys[var]       = filter(lambda j:jetId(j, ptCut=30, absEtaCut=jetAbsEtaCut, ptVar='pt_'+var), allJets)
            bjets_sys[var]      = filter(lambda j: isBJet(j) and abs(j['eta'])<2.4, jets_sys[var])
            nonBjets_sys[var]   = filter(lambda j: not ( isBJet(j) and abs(j['eta'])<2.4), jets_sys[var])

            setattr(event, "nJetGood_"+var, len(jets_sys[var]))
            setattr(event, "ht_"+var,       sum([j['pt_'+var] for j in jets_sys[var]]))
            setattr(event, "nBTag_"+var,    len(bjets_sys[var]))

        for var in ['JECUp', 'JECDown', 'JERUp', 'JERDown', 'UnclusteredEnUp', 'UnclusteredEnDown']:
            for i in metVariants:
                # use cmg MET correction values ecept for JER where it is zero. There, propagate jet variations.
                if 'JER' in var or 'JECV' in var:
                  (met_corr_pt, met_corr_phi) = getMetJetCorrected(getattr(event, "met_pt" + i), getattr(event,"met_phi" + i), jets_sys[var], var)
                else:
                  (met_corr_pt, met_corr_phi) = getMetCorrected(r, var, photons[0] if i.count("photonEstimated") else None)

                setattr(event, "met_pt" +i+"_"+var, met_corr_pt)
                setattr(event, "met_phi"+i+"_"+var, met_corr_phi)
                ht = getattr(event, "ht_"+var) if 'Unclustered' not in var else event.ht 
                setattr(event, "metSig" +i+"_"+var, getattr(event, "met_pt"+i+"_"+var)/sqrt( ht ) if ht>0 else float('nan') )

    if isSingleLep or isTriLep or isDiLep:
        event.nGoodMuons      = len(filter( lambda l:abs(l['pdgId'])==13, leptons))
        event.nGoodElectrons  = len(filter( lambda l:abs(l['pdgId'])==11, leptons))
        event.nGoodLeptons    = len(leptons)

        if len(leptons)>=1:
            event.l1_pt     = leptons[0]['pt']
            event.l1_eta    = leptons[0]['eta']
            event.l1_phi    = leptons[0]['phi']
            event.l1_pdgId  = leptons[0]['pdgId']
            event.l1_index  = leptons[0]['index']
            event.l1_miniRelIso = leptons[0]['miniPFRelIso_all']
            event.l1_relIso03 = leptons[0]['pfRelIso03_all']
            event.l1_dxy = leptons[0]['dxy']
            event.l1_dz = leptons[0]['dz']


        # For TTZ studies: find Z boson candidate, and use third lepton to calculate mt
        (event.mlmZ_mass, zl1, zl2) = closestOSDLMassToMZ(leptons_pt10)
#        if len(leptons_pt10) >= 3:
#            thirdLepton = leptons_pt10[[x for x in range(len(leptons_pt10)) if x != zl1 and x != zl2][0]]
#            for i in metVariants:
#              setattr(event, "mt"+i, sqrt(2*thirdLepton['pt']*getattr(event, "met_pt"+i)*(1-cos(thirdLepton['phi']-getattr(event, "met_phi"+i)))))

        if fastSim:
            ## To check whether PV_npvsGood is the correct replacement for nVert
            event.reweightLeptonFastSimSF     = reduce(mul, [leptonFastSimSF.get2DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.Pileup_nTrueInt) for l in leptons], 1)
            event.reweightLeptonFastSimSFUp   = reduce(mul, [leptonFastSimSF.get2DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.Pileup_nTrueInt, sigma = +1) for l in leptons], 1)
            event.reweightLeptonFastSimSFDown = reduce(mul, [leptonFastSimSF.get2DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.Pileup_nTrueInt, sigma = -1) for l in leptons], 1)

        if isMC:
            event.reweightDilepTrigger       = 0 
            event.reweightDilepTriggerUp     = 0 
            event.reweightDilepTriggerDown   = 0 
            event.reweightDilepTriggerBackup       = 0 
            event.reweightDilepTriggerBackupUp     = 0 
            event.reweightDilepTriggerBackupDown   = 0 

            leptonsForSF = (leptons[:2] if isDiLep else (leptons[:3] if isTriLep else leptons[:1]))
            event.reweightLeptonSF           = reduce(mul, [leptonSF.getSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta']) for l in leptonsForSF], 1)
            event.reweightLeptonSFUp         = reduce(mul, [leptonSF.getSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , sigma = +1) for l in leptonsForSF], 1)
            event.reweightLeptonSFDown       = reduce(mul, [leptonSF.getSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , sigma = -1) for l in leptonsForSF], 1)

            event.reweightLeptonTrackingSF   = reduce(mul, [leptonTrackingSF.getSF( \
                pdgId = l['pdgId'],
                pt  =   l['pt'], 
                eta =   ((l['eta'] + l['deltaEtaSC']) if abs(l['pdgId'])==11 else l['eta'])
                )[0]  for l in leptonsForSF], 1)

    if isTriLep or isDiLep:
        if len(leptons)>=2:
            mt2Calc.reset()
            event.l2_pt     = leptons[1]['pt']
            event.l2_eta    = leptons[1]['eta']
            event.l2_phi    = leptons[1]['phi']
            event.l2_pdgId  = leptons[1]['pdgId']
            event.l2_index  = leptons[1]['index']
            event.l2_miniRelIso = leptons[1]['miniPFRelIso_all']
            event.l2_relIso03 = leptons[1]['pfRelIso03_all']
            event.l2_dxy = leptons[1]['dxy']
            event.l2_dz = leptons[1]['dz']
            

            l_pdgs = [abs(leptons[0]['pdgId']), abs(leptons[1]['pdgId'])]
            l_pdgs.sort()
            event.isMuMu = l_pdgs==[13,13]
            event.isEE   = l_pdgs==[11,11]
            event.isEMu  = l_pdgs==[11,13]
            event.isOS   = event.l1_pdgId*event.l2_pdgId<0

            l1 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(leptons[0]['pt'], leptons[0]['eta'], leptons[0]['phi'], 0 )
            l2 = ROOT.TLorentzVector()
            l2.SetPtEtaPhiM(leptons[1]['pt'], leptons[1]['eta'], leptons[1]['phi'], 0 )
            dl = l1+l2
            event.dl_pt   = dl.Pt()
            event.dl_eta  = dl.Eta()
            event.dl_phi  = dl.Phi()
            event.dl_mass = dl.M()
            mt2Calc.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)

            # need at least two jets for MVA
            if len(store_jets)>1:
                eventdict= {
                    'JetGood_eta[0]':   event.JetGood_eta[0],
                    'JetGood_pt[0]':    event.JetGood_pt[0],
                    'JetGood_eta[1]':   event.JetGood_eta[1],
                    'JetGood_pt[1]':    event.JetGood_pt[1],
                    'Jet_dphi':         deltaPhi( event.JetGood_phi[0], event.JetGood_phi[1] ),
                    'dl_eta':           event.dl_eta,
                    'dl_mass':          event.dl_mass,
                    'dl_pt':            event.dl_pt,
                    'ht':               event.ht,
                    'l1_eta':           event.l1_eta,
                    'l1_pt':            event.l1_pt,
                    'l2_eta':           event.l2_eta,
                    'l2_pt':            event.l2_pt,
                    'lep_dphi':         deltaPhi(event.l1_phi, event.l2_phi),
                    'metSig':           event.metSig,
                    'met_pt':           event.met_pt,
                    }

                event.MVA_T2tt_default      = MVA_T2tt_default.eval(eventdict)
                event.MVA_T2tt_lep_pt       = MVA_T2tt_lep_pt.eval(eventdict)
                event.MVA_T8bbllnunu_XCha0p5_XSlep0p09      = MVA_T8bbllnunu_XCha0p5_XSlep0p09.eval(eventdict)
                event.MVA_T8bbllnunu_XCha0p5_XSlep0p5_800_1 = MVA_T8bbllnunu_XCha0p5_XSlep0p5_800_1.eval(eventdict)


            # To check MC truth when looking at the TTZToLLNuNu sample
            if isMC:
              trig_eff, trig_eff_err =  triggerEff.getSF(event.l1_pt, event.l1_eta, event.l1_pdgId, event.l2_pt, event.l2_eta, event.l2_pdgId)
              event.reweightDilepTrigger       = trig_eff 
              event.reweightDilepTriggerUp     = trig_eff + trig_eff_err
              event.reweightDilepTriggerDown   = trig_eff - trig_eff_err
              trig_eff, trig_eff_err =  triggerEff_withBackup.getSF(event.l1_pt, event.l1_eta, event.l1_pdgId, event.l2_pt, event.l2_eta, event.l2_pdgId)
              event.reweightDilepTriggerBackup       = trig_eff 
              event.reweightDilepTriggerBackupUp     = trig_eff + trig_eff_err
              event.reweightDilepTriggerBackupDown   = trig_eff - trig_eff_err

              zBoson          = getGenZ(gPart)
              event.zBoson_genPt  = zBoson['pt']  if zBoson is not None else float('nan')
              event.zBoson_genEta = zBoson['eta'] if zBoson is not None else float('nan')

            if event.nPhotonGood > 0:
              gamma = ROOT.TLorentzVector()
              gamma.SetPtEtaPhiM(photons[0]['pt'], photons[0]['eta'], photons[0]['phi'], photons[0]['mass'] )
              dlg = dl + gamma
              event.dlg_mass = dlg.M()

            #if options.susySignal:
            #    mt2Calc.setMet(getattr(r, 'met_genPt'), getattr(r, 'met_genPhi'))
            #    setattr(event, "dl_mt2ll_gen", mt2Calc.mt2ll())
            #    if len(jets)>=2:
            #        bj0, bj1 = (bJets+nonBJets)[:2]
            #        mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
            #        setattr(event, "dl_mt2bb_gen",   mt2Calc.mt2bb())
            #        setattr(event, "dl_mt2blbl_gen", mt2Calc.mt2blbl())
                
            for i in metVariants:
                mt2Calc.setMet(getattr(event, 'met_pt'+i), getattr(event, 'met_phi'+i))
                setattr(event, "dl_mt2ll"+i, mt2Calc.mt2ll())

                bj0, bj1 = None, None
                if len(jets)>=2:
                    bj0, bj1 = (bJets+nonBJets)[:2]
                    mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
                    setattr(event, "dl_mt2bb"+i,   mt2Calc.mt2bb())
                    setattr(event, "dl_mt2blbl"+i, mt2Calc.mt2blbl())

                if addSystematicVariations:
                    for var in ['JECUp', 'JECDown', 'JERUp', 'JERDown', 'UnclusteredEnUp', 'UnclusteredEnDown']:
                        mt2Calc.setMet( getattr(event, "met_pt"+i+"_"+var), getattr(event, "met_phi"+i+"_"+var) )
                        setattr(event, "dl_mt2ll"+i+"_"+var,  mt2Calc.mt2ll())
                        if not 'Unclustered' in var:
                            if len(jets_sys[var])>=2:
                                bj0_, bj1_ = (bjets_sys[var]+nonBjets_sys[var])[:2]
                            else: 
                                bj0_, bj1_ = None, None
                        else:
                            bj0_, bj1_ = bj0, bj1
                        if bj0_ and bj1_:
                            mt2Calc.setBJets(bj0_['pt'], bj0_['eta'], bj0_['phi'], bj1_['pt'], bj1_['eta'], bj1_['phi'])
                            setattr(event, 'dl_mt2bb'  +i+'_'+var, mt2Calc.mt2bb())
                            setattr(event, 'dl_mt2blbl'+i+'_'+var, mt2Calc.mt2blbl())

    if addSystematicVariations:
        # B tagging weights method 1a
        for j in jets:
            btagEff.addBTagEffToJet(j)
        for var in btagEff.btagWeightNames:
            if var!='MC':
                setattr(event, 'reweightBTag_'+var, btagEff.getBTagSF_1a( var, bJets, filter( lambda j: abs(j['eta'])<2.4, nonBJets ) ) )
    # gen information on extra leptons
    if isMC and not options.skipGenLepMatching:
        genSearch.init( gPart )
        # Start with status 1 gen leptons in acceptance
        gLep = filter( lambda p:abs(p['pdgId']) in [11, 13] and p['status']==1 and p['pt']>20 and abs(p['eta'])<2.5, gPart )
        for l in gLep:
            ancestry = [ gPart[x]['pdgId'] for x in genSearch.ancestry( l ) ]
            l["n_D"]   =  sum([ancestry.count(p) for p in D_mesons])
            l["n_B"]   =  sum([ancestry.count(p) for p in B_mesons])
            l["n_W"]   =  sum([ancestry.count(p) for p in [24, -24]])
            l["n_t"]   =  sum([ancestry.count(p) for p in [6, -6]])
            l["n_tau"] =  sum([ancestry.count(p) for p in [15, -15]])
            matched_lep = bestDRMatchInCollection(l, leptons_pt10)
            if matched_lep:
                l["lepGoodMatchIndex"] = matched_lep['index']
                if isSingleLep:
                    l["matchesPromptGoodLepton"] = l["lepGoodMatchIndex"] in [event.l1_index]
                elif isTriLep or isDiLep:
                    l["matchesPromptGoodLepton"] = l["lepGoodMatchIndex"] in [event.l1_index, event.l2_index]
                else:
                    l["matchesPromptGoodLepton"] = 0
            else:
                l["lepGoodMatchIndex"] = -1
                l["matchesPromptGoodLepton"] = 0
#            if      l["n_t"]>0 and l["n_W"]>0 and l["n_B"]==0 and l["n_D"]==0 and l["n_tau"]==0:
#                print "t->W->l"
#            elif    l["n_t"]>0 and l["n_W"]==0 and l["n_B"]>0 and l["n_D"]==0 and l["n_tau"]==0:
#                print "t->b->B->l"
#            elif    l["n_t"]>0 and l["n_W"]==0 and l["n_B"]>0 and l["n_D"]>0 and l["n_tau"]==0:
#                print "t->b->B->D->l"
#            elif    l["n_t"]>0 and l["n_W"]>0 and l["n_B"]==0 and l["n_D"]==0 and l["n_tau"]>0 :
#                print "t->W->tau->l"
#            elif    l["n_t"]>0 and l["n_W"]>0 and l["n_B"]==0 and l["n_D"]>0 and l["n_tau"]==0:
#                print "t->W->c->D->l"
#            elif    l["n_t"]==0 and l["n_W"]==0 and l["n_B"]>0 and l["n_D"]>=0 and l["n_tau"]==0:
#                print l['pdgId'], l['pt'], l['phi'], l['eta'], ",".join(pdgToName( gPart[x]['pdgId']) for x in genSearch.ancestry(l) )
#                for p in genSearch.ancestry(l):
#                    print p, gPart[p]
#            else:
#                pass
                # print l['pdgId'], l['pt'], l['phi'], l['eta'], ",".join(pdgToName(gPart[x]['pdgId']) for x in genSearch.ancestry(l))
        event.nGenLep   = len(gLep)
        for iLep, lep in enumerate(gLep):
            for b in genLepVarNames:
                getattr(event, "GenLep_"+b)[iLep] = lep[b]

# Create a maker. Maker class will be compiled. This instance will be used as a parent in the loop
treeMaker_parent = TreeMaker(
    sequence  = [ filler ],
    variables = [ TreeVariable.fromString(x) for x in new_variables ],
    treeName = "Events"
    )

# Split input in ranges
if options.nJobs>1 and not options.fileBasedSplitting:
    eventRanges = reader.getEventRanges( nJobs = options.nJobs )
else:
    eventRanges = reader.getEventRanges( maxNEvents = options.eventsPerJob, minJobs = options.minNJobs )

logger.info( "Splitting into %i ranges of %i events on average. FileBasedSplitting: %s. Job number %s",  
        len(eventRanges), 
        (eventRanges[-1][1] - eventRanges[0][0])/len(eventRanges), 
        'Yes' if options.fileBasedSplitting else 'No',
        options.job)

#Define all jobs
jobs = [(i, eventRanges[i]) for i in range(len(eventRanges))]

filename, ext = os.path.splitext( os.path.join(output_directory, sample.name + '.root') )

if options.fileBasedSplitting and len(eventRanges)>1:
    raise RuntimeError("Using fileBasedSplitting but have more than one event range!")

clonedEvents = 0
convertedEvents = 0
outputLumiList = {}
for ievtRange, eventRange in enumerate( eventRanges ):

    
    if not options.fileBasedSplitting and options.nJobs>1:
        if ievtRange != options.job: continue

    logger.info( "Processing range %i/%i from %i to %i which are %i events.",  ievtRange, len(eventRanges), eventRange[0], eventRange[1], eventRange[1]-eventRange[0] )

    # Check whether file exists
    fileNumber = options.job if options.job is not None else 0
    outfilename = filename+'_'+str(fileNumber)+ext
    
    _logger.   add_fileHandler( outfilename.replace('.root', '.log'), options.logLevel )
    _logger_rt.add_fileHandler( outfilename.replace('.root', '_rt.log'), options.logLevel )
    
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

    if options.small: 
        logger.info("Running 'small'. Not more than 10000 events") 
        nMaxEvents = eventRange[1]-eventRange[0]
        eventRange = ( eventRange[0], eventRange[0] +  min( [nMaxEvents, 10000] ) )

    # Set the reader to the event range
    reader.setEventRange( eventRange )

    clonedTree = reader.cloneTree( branchKeepStrings, newTreename = "Events", rootfile = outputfile )
    clonedEvents += clonedTree.GetEntries()
    # Clone the empty maker in order to avoid recompilation at every loop iteration
    maker = treeMaker_parent.cloneWithoutCompile( externalTree = clonedTree )

    maker.start()
    # Do the thing
    reader.start()

    while reader.run():
        maker.run()
        if isData:
            if maker.event.jsonPassed_:
                if reader.event.run not in outputLumiList.keys():
                    outputLumiList[reader.event.run] = set([reader.event.luminosityBlock])
                else:
                    if reader.event.luminosityBlock not in outputLumiList[reader.event.run]:
                        outputLumiList[reader.event.run].add(reader.event.luminosityBlock)

    convertedEvents += maker.tree.GetEntries()
    maker.tree.Write()
    outputfile.Close()
    logger.info( "Written %s", outfilename)

  # Destroy the TTree
    maker.clear()


logger.info( "Converted %i events of %i, cloned %i",  convertedEvents, reader.nEvents , clonedEvents )

# Storing JSON file of processed events
if isData:
    jsonFile = filename+'_%s.json'%(0 if options.nJobs==1 else options.job)
    LumiList( runsAndLumis = outputLumiList ).writeJSON(jsonFile)
    logger.info( "Written JSON file %s", jsonFile )

# Write one file per mass point for SUSY signals
if options.nJobs == 1:
    if options.susySignal:
        signalModel = options.samples[0].split('_')[1]
        output = Sample.fromDirectory(signalModel+"_output", output_directory)
        print "Initialising chain, otherwise first mass point is empty"
        print output.chain
        if options.small: output.reduceFiles( to = 1 )
        for s in signalWeight.keys():
            #cut = "GenSusyMStop=="+str(s[0])+"&&GenSusyMNeutralino=="+str(s[1]) #FIXME
            logger.info("Going to write masspoint mStop %i mNeu %i", s[0], s[1])
            cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(s[0])+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(s[1])
            logger.debug("Using cut %s", cut)

            signal_prefix = signalModel + '_'
            if 'T8bbllnunu' in signalModel:
                T8bbllnunu_strings = options.samples[0].split('_')
                for st in T8bbllnunu_strings:
                    if 'XSlep' in st:
                        x_slep = st.replace('XSlep','')
                        logger.info("Factor x_slep in this sample is %s",x_slep)
                    if 'XCha' in st:
                        x_cha = st.replace('XCha','')
                        logger.info("Factor x_cha in this sample is %s",x_cha)
                assert x_cha, "Could not find X factor for chargino in T8bbllnunu model"
                assert x_slep, "Could not find X factor for slepton in T8bbllnunu model"
                signal_prefix = 'T8bbllnunu_XCha%s_XSlep%s_'%(x_cha,x_slep)

            signalFile = os.path.join(signalDir, signal_prefix + str(s[0]) + '_' + str(s[1]) + '.root' )
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

logger.info("Copying log file to %s", output_directory )
copyLog = subprocess.call(['cp', logFile, output_directory] )
if copyLog:
    logger.info( "Copying log from %s to %s failed", logFile, output_directory)
else:
    logger.info( "Successfully copied log file" )
    os.remove(logFile)
    logger.info( "Removed temporary log file" )

if writeToDPM:
    for dirname, subdirs, files in os.walk( directory ):
        logger.debug( 'Found directory: %s',  dirname )
        for fname in files:
            source = os.path.abspath(os.path.join(dirname, fname))
            postfix = '_small' if options.small else ''
            cmd = ['xrdcp', source, 'root://hephyse.oeaw.ac.at/%s' % os.path.join( user_dpm_directory, 'postprocessed',  options.processingEra+postfix, options.skim, sample.name, fname ) ]
            logger.info( "Issue copy command: %s", " ".join( cmd ) )
            subprocess.call( cmd )

    # Clean up.
    subprocess.call( [ 'rm', '-rf', directory ] ) # Let's risk it.
