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
from StopsDilepton.tools.helpers import closestOSDLMassToMZ, checkRootFile, writeObjToFile, m3, deltaR
from StopsDilepton.tools.addJERScaling import addJERScaling
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons, getJets, getGoodBJets, getGoodJets, isBJet, jetId, isBJet, getGoodPhotons
from StopsDilepton.tools.overlapRemovalTTG import getTTGJetsEventType
from StopsDilepton.tools.genPtZ import getGenPtZ

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
        default=['MuonEG_Run2015D_16Dec'],
#        default=['WZZ'],
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

    argParser.add_argument('--runSmallSample',
        action='store_true',
        help="Run the file on a small sample (for test purpose), bool flag set to True if used"
        )

    argParser.add_argument('--T2tt',
        action='store_true',
        help="Is T2tt signal?"
        )

    argParser.add_argument('--TTDM',
        action='store_true',
        help="Is TTDM signal?"
        )

    argParser.add_argument('--fastSim',
        action='store_true',
        help="FastSim?"
        )

    argParser.add_argument('--keepPhotons',
        action='store_true',
        help="Keep photons?"
        )

    argParser.add_argument('--keepLHEWeights',
        action='store_true',
        help="Keep LHEWeights?"
        )

    argParser.add_argument('--checkTTGJetsOverlap',
        action='store_true',
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
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

# Skim condition
skimConds = []
if options.skim.lower().startswith('dilep'):
    skimConds.append( "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5)>=2" )
if options.skim.lower().startswith('singlelep'):
    skimConds.append( "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5)>=1" )

#Samples: Load samples
maxN = 2 if options.runSmallSample else None
if options.T2tt:
    from StopsDilepton.samples.cmgTuples_Signals_Spring15_mAODv2_25ns_0l import T2tt
    from StopsDilepton.samples.helpers import getT2ttSignalWeight
    samples = filter( lambda s:s.name in options.samples, T2tt)
    logger.info( "T2tt signal samples to be processed: %s", ",".join(s.name for s in samples) )
    # FIXME I'm forcing ==1 signal sample because I don't have a good idea how to construct a sample name from the complicated T2tt_x_y_z_... names
    assert len(samples)==1, "Can only process one T2tt sample at a time."
    samples[0].files = samples[0].files[:maxN] 
    logger.debug( "Fetching signal weights..." )
    signalWeight = getT2ttSignalWeight( samples[0], lumi = targetLumi )
    logger.debug("Done fetching signal weights.")
elif options.TTDM:
    from StopsDilepton.samples.helpers import fromHeppySample
    samples = [ fromHeppySample(s, data_path = "/data/rschoefbeck/cmgTuples/TTBar_DM/", \
                    module = "CMGTools.StopsDilepton.TTbarDMJets_signals_RunIISpring15MiniAODv2",  maxN = maxN)\
                for s in options.samples ]
else:
    from StopsDilepton.samples.helpers import fromHeppySample
    samples = [ fromHeppySample(s, data_path = options.dataDir, maxN = maxN) for s in options.samples ]

isData = False not in [s.isData for s in samples]
isMC   =  True not in [s.isData for s in samples]

if options.T2tt:
    xSection = None
else:
    # Check that all samples which are concatenated have the same x-section.
    assert isData or len(set([s.heppy.xSection for s in samples]))==1, "Not all samples have the same xSection: %s !"%(",".join([s.name for s in samples]))
    assert isMC or len(samples)==1, "Don't concatenate data samples"

    xSection = samples[0].heppy.xSection if isMC else None

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

if isMC:
    from StopsDilepton.tools.puReweighting import getReweightingFunction
    if options.T2tt or options.TTDM:
        # T2tt signal is 74X with Spring15 profile!
        puRW        = getReweightingFunction(data="PU_2100_XSecCentral", mc="Spring15")
        puRWDown    = getReweightingFunction(data="PU_2100_XSecDown", mc="Spring15")
        puRWUp      = getReweightingFunction(data="PU_2100_XSecUp", mc="Spring15")
    else:
        puRW        = getReweightingFunction(data="PU_2100_XSecCentral", mc="Fall15")
        puRWDown    = getReweightingFunction(data="PU_2100_XSecDown", mc="Fall15")
        puRWUp      = getReweightingFunction(data="PU_2100_XSecUp", mc="Fall15")

# top pt reweighting
from StopsDilepton.tools.topPtReweighting import getUnscaledTopPairPtReweightungFunction, getTopPtDrawString, getTopPtsForReweighting
# Decision based on sample name -> whether TTJets or TTLep is in the sample name
doTopPtReweighting = (sample.name.startswith("TTJets") or sample.name.startswith("TTLep")) and not options.noTopPtReweighting
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

if options.fastSim:
   from StopsDilepton.tools.leptonFastSimSF import leptonFastSimSF as leptonFastSimSF_
   leptonFastSimSF = leptonFastSimSF_()

# systematic variations
addSystematicVariations = (not isData) and (not options.skipSystematicVariations)
if addSystematicVariations:
    # B tagging SF
    from StopsDilepton.tools.btagEfficiency import btagEfficiency
    btagEff = btagEfficiency( fastSim = options.fastSim )

# LHE cut (DY samples)
if options.LHEHTCut>0:
    sample.name+="_lheHT"+str(options.LHEHTCut)
    logger.info( "Adding upper LHE cut at %f", options.LHEHTCut )
    skimConds.append( "lheHTIncoming<%f"%options.LHEHTCut )

# MET group veto list
if sample.isData:
    import StopsDilepton.tools.vetoList as vetoList_
    # MET group veto lists from 74X
    fileNames  = ['Run2015D/csc2015_Dec01.txt.gz', 'Run2015D/ecalscn1043093_Dec01.txt.gz']
    vetoList = vetoList_.vetoList( [os.path.join(user.veto_lists, f) for f in fileNames] )

# output directory
outDir = os.path.join(options.targetDir, options.processingEra, options.skim, sample.name)

# Directory for individual signal files
if options.T2tt:
    signalDir = os.path.join(options.targetDir, options.processingEra, options.skim, "T2tt")
    if not os.path.exists(signalDir): os.makedirs(signalDir)

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

if options.skim.lower().count('tiny'):
    #branches to be kept for data and MC
    branchKeepStrings_DATAMC = \
       ["run", "lumi", "evt", "isData", "nVert",
        "met_pt", "met_phi",
#        "puppiMet_pt","puppiMet_phi",
        "Flag_*",
        "HLT_mumuIso", "HLT_ee_DZ", "HLT_mue",
        "HLT_3mu", "HLT_3e", "HLT_2e1mu", "HLT_2mu1e",
        "LepGood_eta","LepGood_pt","LepGood_phi", "LepGood_dxy", "LepGood_dz","LepGood_tightId", "LepGood_pdgId", 
        "LepGood_mediumMuonId", "LepGood_miniRelIso", "LepGood_sip3d", "LepGood_mvaIdSpring15", "LepGood_convVeto", "LepGood_lostHits",
        ]

    #branches to be kept for MC samples only
    branchKeepStrings_MC = [ \
        "nTrueInt", "genWeight", "xsec", "met_genPt", "met_genPhi", "lheHTIncoming"
    ]

    #branches to be kept for data only
    branchKeepStrings_DATA = [ ]

else:
    #branches to be kept for data and MC
    branchKeepStrings_DATAMC = [\
        "run", "lumi", "evt", "isData", "rho", "nVert",
        "met_pt", "met_phi","met_Jet*", "met_Unclustered*", "met_sumEt", "met_rawPt","met_rawPhi", "met_rawSumEt",
#        "metNoHF_pt", "metNoHF_phi",
#        "puppiMet_pt","puppiMet_phi","puppiMet_sumEt","puppiMet_rawPt","puppiMet_rawPhi","puppiMet_rawSumEt",
        "Flag_*","HLT_*",
        "nDiscJet", "DiscJet_*",
        "nJetFailId", "JetFailId_*",
        "nLepGood", "LepGood_*",
        "nTauGood", "TauGood_*",
    ]

    #branches to be kept for MC samples only
    branchKeepStrings_MC = [\
        "nTrueInt", "genWeight", "xsec", "met_gen*", "lheHTIncoming",
        "ngenPartAll","genPartAll_*","ngenLep","genLep_*"
    ]

    #branches to be kept for data only
    branchKeepStrings_DATA = [ ]

if options.skim.lower().startswith('singlelep'):
    branchKeepStrings_DATAMC += ['HLT_SingleMu', 'HLT_IsoMu27', 'HLT_IsoMu20', 'HLT_Mu45eta2p1', 'HLT_Mu50', 'HLT_MuHT350', 'HLT_MuHTMET', 'HLT_MuMET120', 'HLT_IsoEle32', 'HLT_IsoEle23', 'HLT_IsoEle22']

if options.T2tt: branchKeepStrings_MC += ['GenSusyMScan1', 'GenSusyMScan2']

# Jet variables to be read from chain 
jetCorrInfo = ['corr/F', 'corr_JECUp/F', 'corr_JECDown/F'] if addSystematicVariations else []
if isMC:
    if options.skim.lower().count('tiny'):
        jetMCInfo = ['mcPt/F', 'hadronFlavour/I']
    else:
        jetMCInfo = ['mcMatchFlav/I', 'partonId/I', 'partonMotherId/I', 'mcPt/F', 'mcFlavour/I', 'hadronFlavour/I', 'mcMatchId/I']
        if not options.T2tt: 
            jetMCInfo.append('partonFlavour/I')
else: 
    jetMCInfo = []

jetVars = ['pt/F', 'rawPt/F', 'eta/F', 'phi/F', 'id/I', 'btagCSV/F'] + jetCorrInfo + jetMCInfo
# for convinience: List of jet variables to be read in the filler
jetVarNames = [x.split('/')[0] for x in jetVars]

if options.keepPhotons and not options.skim.lower().count('tiny'):
    branchKeepStrings_DATAMC+=[
        "ngamma", "gamma_idCutBased", "gamma_hOverE", "gamma_r9", "gamma_sigmaIetaIeta", "gamma_chHadIso04", "gamma_chHadIso", "gamma_phIso", 
        "gamma_neuHadIso", "gamma_relIso", "gamma_pdgId", "gamma_pt", "gamma_eta", "gamma_phi", "gamma_mass", 
        "gamma_chHadIsoRC04", "gamma_chHadIsoRC"]
    if isMC: branchKeepStrings_DATAMC+=[ "gamma_mcMatchId", "gamma_mcPt", "gamma_genIso04", "gamma_genIso03", "gamma_drMinParton"]

#if options.keepLHEWeights:
#        branchKeepStrings_MC+=["nLHEweight", "LHEweight_id", "LHEweight_wgt", "LHEweight_original"]

if sample.isData:
    lumiScaleFactor=None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_DATA
    from FWCore.PythonUtilities.LumiList import LumiList
    # Apply golden JSON
    sample.heppy.json = '$CMSSW_BASE/src/CMGTools/TTHAnalysis/data/json/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt'
    lumiList = LumiList(os.path.expandvars(sample.heppy.json))
    logger.info( "Loaded json %s", sample.heppy.json )
else:
    lumiScaleFactor = xSection*targetLumi/float(sample.normalization) if xSection is not None else None
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC


read_variables = map(Variable.fromString, ['met_pt/F', 'met_phi/F', 'run/I', 'lumi/I', 'evt/l', 'nVert/I'] )
if options.keepPhotons:
  read_variables += [Variable.fromString('ngamma/I'),
                     VectorType.fromString('gamma[pt/F,eta/F,phi/F,mass/F,idCutBased/I,pdgId/I]')]

new_variables = [ 'weight/F']
if isMC: 
    read_variables+= [Variable.fromString('nTrueInt/F')]
    # reading gen particles for top pt reweighting
    read_variables.append( Variable.fromString('ngenPartAll/I') ) 
    read_variables.append( VectorType.fromString('genPartAll[pt/F,eta/F,phi/F,pdgId/I,status/I,charge/I,motherId/I,grandmotherId/I,nMothers/I,motherIndex1/I,motherIndex2/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I]', nMax=200 )) # default nMax is 100, which would lead to corrupt values in this case
    read_variables.append( Variable.fromString('genWeight/F') ) 
    read_variables.append( VectorType.fromString('gamma[mcPt/F]') )

    new_variables.extend([ 'reweightTopPt/F', 'reweightPU/F','reweightPUUp/F','reweightPUDown/F'])

read_variables += [\
    Variable.fromString('nLepGood/I'), 
    VectorType.fromString('LepGood[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F]'),
    Variable.fromString('nJet/I'), 
    VectorType.fromString('Jet[%s]'% ( ','.join(jetVars) ) )
]
new_variables += [\
    'JetGood[%s]'% ( ','.join(jetVars) ) 
]

if isData: new_variables.extend( ['vetoPassed/I', 'jsonPassed/I'] )
new_variables.extend( ['nJetGood/I','nBTag/I', 'ht/F', 'metSig/F'] )

if options.skim.lower().startswith('singlelep'):
    new_variables.extend( ['m3/F', 'm3_ind1/I', 'm3_ind2/I', 'm3_ind3/I'] )
if options.skim.lower().startswith('dilep') or options.skim.lower().startswith('singlelep'):
    new_variables.extend( ['nGoodMuons/I', 'nGoodElectrons/I' ] )
    new_variables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_pdgId/I', 'l1_index/I' ] )
    new_variables.extend( ['mt/F', 'mlmZ_mass/F'] )
    if options.keepPhotons:
      new_variables.extend( ['mt_photonEstimated/F'] )
if options.skim.lower().startswith('dilep'):
    new_variables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_pdgId/I', 'l2_index/I' ] )
    new_variables.extend( ['isEE/I', 'isMuMu/I', 'isEMu/I', 'isOS/I' ] )
    new_variables.extend( ['dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_mass/F'] )
    new_variables.extend( ['dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F' ] )
    if isMC: new_variables.extend( ['zBoson_genPt/F'] )

if options.keepPhotons:
    new_variables.extend( ['nPhotonGood/I','photon_pt/F','photon_eta/F','photon_phi/F','photon_idCutBased/I'] )
    if isMC: new_variables.extend( ['photon_genPt/F'] )
    new_variables.extend( ['met_pt_photonEstimated/F','met_phi_photonEstimated/F','metSig_photonEstimated/F'] )
    new_variables.extend( ['photonJetdR/F','photonLepdR/F'] )
    if options.skim.lower().startswith('dilep'):
      new_variables.extend( ['dlg_mass/F','dl_mt2ll_photonEstimated/F', 'dl_mt2bb_photonEstimated/F', 'dl_mt2blbl_photonEstimated/F' ] )

if options.checkTTGJetsOverlap:
    new_variables.extend( ['TTGJetsEventType/I'] )

if addSystematicVariations:
    for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
        new_variables.extend( ['nJetGood_'+var+'/I', 'nBTag_'+var+'/I','ht_'+var+'/F', 'metSig_'+var+'/F'] )
        new_variables.extend( ['met_pt_'+var+'/F', 'met_phi_'+var+'/F'] )
        if options.skim.lower().startswith('dilep'):
            new_variables.extend( ['dl_mt2ll_'+var+'/F', 'dl_mt2bb_'+var+'/F', 'dl_mt2blbl_'+var+'/F'] )
        if options.keepPhotons:
            new_variables.extend( ['met_pt_photonEstimated_'+var+'/F', 'met_phi_photonEstimated_'+var+'/F', 'metSig_photonEstimated_'+var+'/F'] )
            if options.skim.lower().startswith('dilep'):
                new_variables.extend( ['dl_mt2ll_photonEstimated_'+var+'/F', 'dl_mt2bb_photonEstimated_'+var+'/F', 'dl_mt2blbl_photonEstimated_'+var+'/F'] )
    # Btag weights Method 1a
    for var in btagEff.btagWeightNames:
        if var!='MC':
            new_variables.append('reweightBTag_'+var+'/F')

if options.T2tt:
    read_variables += map(Variable.fromString, ['GenSusyMScan1/I', 'GenSusyMScan2/I'] )
    new_variables  += ['reweightXSecUp/F', 'reweightXSecDown/F', 'mStop/I', 'mNeu/I']

if options.fastSim and options.skim.lower().startswith('dilep'):
    new_variables  += ['reweightLeptonFastSimSF/F', 'reweightLeptonFastSimSFUp/F', 'reweightLeptonFastSimSFDown/F']

# Define a reader
reader = sample.treeReader( \
    variables = read_variables , 
    selectionString = "&&".join(skimConds)
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

    # weight
    if options.T2tt:
        s.weight=signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['weight']
        s.mStop = r.GenSusyMScan1
        s.mNeu  = r.GenSusyMScan2
        s.reweightXSecUp    = signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['xSecFacUp']
        s.reweightXSecDown  = signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['xSecFacDown']
    elif isMC: 
        s.weight = lumiScaleFactor*r.genWeight if lumiScaleFactor is not None else 1
    elif isData:
        s.weight = 1
    else:
        raise NotImplementedError( "isMC %r isData %r T2tt? %r TTDM?" % (isMC, isData, options.T2tt, options.TTDM) )

    # lumi lists and vetos
    if isData:
        s.vetoPassed  = vetoList.passesVeto(r.run, r.lumi, r.evt)
        s.jsonPassed  = lumiList.contains(r.run, r.lumi)
        # store decision to use after filler has been executed
        s.jsonPassed_ = s.jsonPassed 

    if isMC:
        s.reweightPU     = puRW(r.nTrueInt)
        s.reweightPUDown = puRWDown(r.nTrueInt)
        s.reweightPUUp   = puRWUp(r.nTrueInt)

    # top pt reweighting
    if isMC: s.reweightTopPt = topPtReweightingFunc(getTopPtsForReweighting(r))/topScaleF if doTopPtReweighting else 1.

    # jet/met related quantities, also load the leptons already
    allJets      = getGoodJets(r, ptCut=0, jetVars = jetVarNames )
    jets         = filter(lambda j:jetId(j, ptCut=30, absEtaCut=2.4), allJets)
    bJets        = filter(lambda j:isBJet(j), jets)
    nonBJets     = filter(lambda j:not isBJet(j), jets)
    leptons_pt10 = getGoodLeptons(r, ptCut=10)
    leptons      = filter(lambda l:l['pt']>20, leptons_pt10)

    s.met_pt  = r.met_pt
    s.met_phi = r.met_phi

    # Filling jets
    s.nJetGood   = len(jets)
    if options.skim.lower().startswith('singlelep'):
        # Compute M3 and the three indiced of the jets entering m3
        s.m3, s.m3_ind1, s.m3_ind2, s.m3_ind3 = m3( jets )
    for iJet, jet in enumerate(jets):
        for b in jetVarNames:
            getattr(s, "JetGood_"+b)[iJet] = jet[b]

    s.ht         = sum([j['pt'] for j in jets])
    s.metSig     = s.met_pt/sqrt(s.ht) if s.ht>0 else float('nan')
    s.nBTag      = len(bJets)

    jets_sys      = {}
    bjets_sys     = {}
    nonBjets_sys  = {}

    metVariants = [''] # default

    # Keep photons and estimate met including (leading pt) photon
    if options.keepPhotons:
       photons = getGoodPhotons(r, ptCut=20, idLevel="loose", isData=isData)
       s.nPhotonGood = len(photons)
       if s.nPhotonGood > 0:
         metVariants += ['_photonEstimated']  # do all met calculations also for the photonEstimated variant
         s.photon_pt         = photons[0]['pt']
         s.photon_genPt      = photons[0]['mcPt']
         s.photon_eta        = photons[0]['eta']
         s.photon_phi        = photons[0]['phi']
         s.photon_idCutBased = photons[0]['idCutBased']

         met = ROOT.TLorentzVector()
         met.SetPtEtaPhiM(r.met_pt, 0, r.met_phi, 0 )
         gamma = ROOT.TLorentzVector()
         gamma.SetPtEtaPhiM(photons[0]['pt'], photons[0]['eta'], photons[0]['phi'], photons[0]['mass'] )
         metGamma = met + gamma
         s.met_pt_photonEstimated  = metGamma.Pt()
         s.met_phi_photonEstimated = metGamma.Phi()
         s.metSig_photonEstimated  = s.met_pt_photonEstimated/sqrt(s.ht) if s.ht>0 else float('nan')

         s.photonJetdR = min(deltaR(photons[0], j) for j in jets) if len(jets) > 0 else 999
         s.photonLepdR = min(deltaR(photons[0], l) for l in leptons_pt10) if len(leptons_pt10) > 0 else 999

    if options.checkTTGJetsOverlap and isMC:
       s.TTGJetsEventType = getTTGJetsEventType(r)

    if addSystematicVariations:
        for j in allJets:
            j['pt_JECUp']   =j['pt']/j['corr']*j['corr_JECUp']
            j['pt_JECDown'] =j['pt']/j['corr']*j['corr_JECDown']
            addJERScaling(j)
        for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
            jets_sys[var]       = filter(lambda j:jetId(j, ptCut=30, absEtaCut=2.4, ptVar='pt_'+var), allJets)
            bjets_sys[var]      = filter(isBJet, jets_sys[var])
            nonBjets_sys[var]   = filter(lambda j: not isBJet(j), jets_sys[var])

            setattr(s, "nJetGood_"+var, len(jets_sys[var]))
            setattr(s, "ht_"+var,       sum([j['pt_'+var] for j in jets_sys[var]]))
            setattr(s, "nBTag_"+var,    len(bjets_sys[var]))

            for i in metVariants:
              (met_corr_pt, met_corr_phi) = getMetCorrected(getattr(s, "met_pt" + i), getattr(s,"met_phi" + i), jets_sys[var], var)

              setattr(s, "met_pt" +i+"_"+var, met_corr_pt)
              setattr(s, "met_phi"+i+"_"+var, met_corr_phi)
              setattr(s, "metSig" +i+"_"+var, getattr(s, "met_pt"+i+"_"+var)/sqrt( getattr(s, "ht_"+var) ) ) if getattr(s, "ht_"+var) else float ('nan')


    if options.skim.lower().startswith('singlelep') or options.skim.lower().startswith('dilep'):
        s.nGoodMuons      = len(filter( lambda l:abs(l['pdgId'])==13, leptons))
        s.nGoodElectrons  = len(filter( lambda l:abs(l['pdgId'])==11, leptons))
        if len(leptons)>=1:
            s.l1_pt     = leptons[0]['pt']
            s.l1_eta    = leptons[0]['eta']
            s.l1_phi    = leptons[0]['phi']
            s.l1_pdgId  = leptons[0]['pdgId']
            s.l1_index  = leptons[0]['index']

        # For TTZ studies: find Z boson candidate, and use third lepton to calculate mt
        (s.mlmZ_mass, zl1, zl2) = closestOSDLMassToMZ(leptons_pt10)
        if len(leptons_pt10) >= 3:
            thirdLepton = leptons_pt10[[x for x in range(len(leptons_pt10)) if x != zl1 and x != zl2][0]]
            for i in metVariants:
              setattr(s, "mt"+i, sqrt(2*thirdLepton['pt']*getattr(s, "met_pt"+i)*(1-cos(thirdLepton['phi']-getattr(s, "met_phi"+i)))))

    if options.skim.lower().startswith('dilep'):
        if options.fastSim:
            s.reweightLeptonFastSimSF     = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert) for l in leptons], 1)
            s.reweightLeptonFastSimSFUp   = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert, sigma = +1) for l in leptons], 1)
            s.reweightLeptonFastSimSFDown = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert, sigma = -1) for l in leptons], 1)

        if len(leptons)>=2:# and leptons[0]['pdgId']*leptons[1]['pdgId']<0 and abs(leptons[0]['pdgId'])==abs(leptons[1]['pdgId']): #OSSF choice
            mt2Calc.reset()
            s.l2_pt     = leptons[1]['pt']
            s.l2_eta    = leptons[1]['eta']
            s.l2_phi    = leptons[1]['phi']
            s.l2_pdgId  = leptons[1]['pdgId']
            s.l2_index  = leptons[1]['index']

            l_pdgs = [abs(leptons[0]['pdgId']), abs(leptons[1]['pdgId'])]
            l_pdgs.sort()
            s.isMuMu = l_pdgs==[13,13]
            s.isEE   = l_pdgs==[11,11]
            s.isEMu  = l_pdgs==[11,13]
            s.isOS   = s.l1_pdgId*s.l2_pdgId<0

            l1 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(leptons[0]['pt'], leptons[0]['eta'], leptons[0]['phi'], 0 )
            l2 = ROOT.TLorentzVector()
            l2.SetPtEtaPhiM(leptons[1]['pt'], leptons[1]['eta'], leptons[1]['phi'], 0 )
            dl = l1+l2
            s.dl_pt   = dl.Pt()
            s.dl_eta  = dl.Eta()
            s.dl_phi  = dl.Phi()
            s.dl_mass = dl.M()
            mt2Calc.setLeptons(s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi)

            if isMC: s.zBoson_genPt  = getGenPtZ(r)

            if options.keepPhotons and s.nPhotonGood > 0:
              dlg = dl + gamma
              s.dlg_mass = dlg.M()

            for i in metVariants:
                mt2Calc.setMet(getattr(s, 'met_pt'+i), getattr(s, 'met_phi', i))
                setattr(s, "dl_mt2ll"+i, mt2Calc.mt2ll())

                if len(jets)>=2:
                    bj0, bj1 = (bJets+nonBJets)[:2]
                    mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
                    setattr(s, "dl_mt2bb"+i,   mt2Calc.mt2bb())
                    setattr(s, "dl_mt2blbl"+i, mt2Calc.mt2blbl())

                if addSystematicVariations:
                    for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
                        mt2Calc.setMet( getattr(s, "met_pt"+i+"_"+var), getattr(s, "met_phi"+i+"_"+var) )
                        setattr(s, "dl_mt2ll"+i+"_"+var,  mt2Calc.mt2ll())
                        if len(jets_sys[var])>=2:
                            bj0, bj1 = (bjets_sys[var]+nonBjets_sys[var])[:2]
                            mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
                            setattr(s, 'dl_mt2bb'  +i+'_'+var, mt2Calc.mt2bb())
                            setattr(s, 'dl_mt2blbl'+i+'_'+var, mt2Calc.mt2blbl())

    if addSystematicVariations:
        # B tagging weights method 1a
        for j in jets:
            btagEff.addBTagEffToJet(j)
        for var in btagEff.btagWeightNames:
            if var!='MC':
                setattr(s, 'reweightBTag_'+var, btagEff.getBTagSF_1a( var, bJets, nonBJets ) )
    
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
            if maker.data.jsonPassed_:
                if reader.data.run not in outputLumiList.keys():
                    outputLumiList[reader.data.run] = {reader.data.lumi}
                else:
                    if reader.data.lumi not in outputLumiList[reader.data.run]:
                        outputLumiList[reader.data.run].add(reader.data.lumi)

    convertedEvents += maker.tree.GetEntries()
    maker.tree.Write()
    outputfile.Close()
    logger.info( "Written %s", outfilename)

  # Destroy the TTree
    maker.clear()


logger.info( "Converted %i events of %i, cloned %i",  convertedEvents, reader.nEvents , clonedEvents )

# Storing JSON file of processed events
if isData:
    jsonFile = filename+'.json'
    LumiList( runsAndLumis = outputLumiList ).writeJSON(jsonFile)
    logger.info( "Written JSON file %s",  jsonFile )

# Write one file per mass point for T2tt
if options.T2tt:
    output = Sample.fromDirectory("T2tt_output", outDir) 
    for s in signalWeight.keys():
        cut = "GenSusyMScan1=="+str(s[0])+"&&GenSusyMScan2=="+str(s[1])
        signalFile = os.path.join(signalDir, 'T2tt_'+str(s[0])+'_'+str(s[1])+'.root' )
        if not os.path.exists(signalFile) or options.overwrite:
            t = output.chain.CopyTree(cut)
            writeObjToFile(signalFile, t)
            logger.info( "Written signal file for masses mStop %i mNeu %i to %s", s[0], s[1], signalFile)
        else:
            logger.info( "Found file %s -> Skipping"%(signalFile) )

    output.clear() 
