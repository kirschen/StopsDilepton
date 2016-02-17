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

# import of tools
from StopsDilepton.tools.puReweighting import getReweightingFunction
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.addJERScaling import addJERScaling
from StopsDilepton.tools.leptonFastSimSF import leptonFastSimSF as leptonFastSimSF_
from StopsDilepton.tools.topPtReweighting import getUnscaledTopPairPtReweightungFunction, getTopPtDrawString, getTopPtsForReweighting
from StopsDilepton.tools.vetoList import vetoList
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons, getJets, getGoodBJets, getGoodJets, isBJet, jetVars, jetId, isBJet
from StopsDilepton.tools.user import *

# not sure if needed
#ROOT.gSystem.Load("libFWCoreFWLite.so")
#ROOT.AutoLibraryLoader.enable()


# central configuration 
targetLumi = 1000 #pb-1 Which lumi to normalize to

# convinience
defSampleStr = "ZZZ"

# option parser
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--keepPhotons", dest="keepPhotons", default = False, action="store_true", help="keep photons?")
parser.add_option("--keepLHEWeights", dest="keepLHEWeights", default = False, action="store_true", help="keep LHEWeights?")
parser.add_option("--skipVariations", dest="skipVariations", default = False, action="store_true", help="skipVariations: Don't calulcate JES and JER variations")
parser.add_option("--signal", dest="signal", default = False, action="store_true", help="Is this T2tt signal?")

def get_parser():
    ''' Argument parser for post-processing module.
    
    '''
     
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")
        
    argParser.add_argument('--logLevel', 
        action='store',
        nargs='?',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
        default='INFO',
        help="Log level for logging"
        )
    
    argParser.add_argument('--overwriteOutputFiles',
        action='store_true',
        help="Overwrite existing output files, bool flag set to True  if used")
    
    argParser.add_argument('--cmgTuples',
        dest='cmgTuples',
        action='store',
        nargs='?',
        type=str,
        default='RunIISpring15DR74_25ns',
        help="CMG ntuples to be post-processed"
        )
       
    argParser.add_argument('--processSamples',
        action='store',
        nargs='*',
        type=str,
        default='TTJets_LO',
        help="List of samples to be post-processed, given as CMG component name"
        )
    
    argParser.add_argument('--targetDir',
        action='store',
        nargs='?',
        type=str,
        default='/afs/hephy.at/data/' + user.afsDataName + '/cmgTuples',
        help="Name of the directory the post-processed files will be saved"
        )
    
    argParser.add_argument('--processingEra',
        action='store',
        nargs='?',
        type=str,
        default='postProcessed_mAODv2',
        help="Name of the processing era"
        )

    argParser.add_argument('--processingTag',
        action='store',
        nargs='?',
        type=str,
        default='v0',
        help="Name of the processing tag, preferably a tag for Workspace"
        )

    argParser.add_argument('--skim',
        action='store',
        nargs='?',
        type=str,
        default='',
        help="Skim conditions to be applied for post-processing"
        )
    
    argParser.add_argument('--leptonSelection',
        action='store',
        nargs='?',
        type=str,
        choices=['soft', 'hard', 'inc', 'dilep'],
        default='inc',
        help="Lepton selection to be applied for post-processing"
        )
    
    argParser.add_argument('--preselect',
        action='store_true',
        help="Apply preselection for the post processing, bool flag set to True if used"
        )
    
    argParser.add_argument('--runSmallSample',
        action='store_true',
        help="Run the file on a small sample (for test purpose), bool flag set to True if used"
        )
    
    argParser.add_argument('--testMethods',
        action='store_true',
        help="Testing only the post-processing methods, without saving ROOT files, on runSmallSample files " + \
        "\n bool flag set to True if used. \n runSmallSample will be set automatically to True"
        )
    # 
    return argParser



(options, args) = parser.parse_args()
#assert options.skim.lower() in ['inclusive', 'dilep'], "Unknown skim: %s"%options.skim
skimCond = "(1)"
interactive = sys.argv[0].count('ipython')
if interactive:
        options.small=False
        options.signal=False
        options.overwrite=False
        options.fastSim=True

#Loading samples
if options.signal:
        from StopsDilepton.samples.cmgTuples_Signals_mAODv2_25ns_0l import *
else:
        from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_TTbar_DM_0l import *
        from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2 import *
        if options.skim.lower().startswith("dilep"):
                from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l import *
        elif options.skim.lower().startswith("inclusive"):
                from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_0l import *

if options.skim.lower().startswith('dilep'):
        skimCond += "&&Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5)>=2"

maxN = 5 if options.small else -1
exec('allSamples=['+options.allSamples+']')
chunks, sumWeight = [], 0.

allData = False not in [s.isData for s in allSamples]
allMC   =  True not in [s.isData for s in allSamples]

assert allData or len(set([s.xSection for s in allSamples]))==1, "Not all samples have the same xSection: %s !"%(",".join([s.name for s in allSamples]))
assert allMC or len(allSamples)==1, "Don't concatenate data samples"

if allMC:
        puRW = getReweightingFunction(data="PU_2100_XSecCentral", mc="Spring15")
        puRWDown = getReweightingFunction(data="PU_2100_XSecDown", mc="Spring15")
        puRWUp   = getReweightingFunction(data="PU_2100_XSecUp", mc="Spring15")

assert False not in [hasattr(s, 'path') for s in allSamples], "Not all samples have a path: "+", ".join([s.name for s in allSamples])

for i, s in enumerate(allSamples):
        tchunks, tsumWeight = getChunks(s, maxN=maxN)
        chunks+=tchunks; sumWeight += tsumWeight
        print "Now %i chunks from sample %s with sumWeight now %f"%(len(chunks), s.name, sumWeight)

sample=allSamples[0]
if len(allSamples)>1:
        sample.name=sample.name+'_comb'

doTopPtReweighting = sample.name.startswith("TTJets") or sample.name.startswith("TTLep")
if doTopPtReweighting:
        print "Sample %s will have top pt reweights!"% sample.name
topPtReweightingFunc = getUnscaledTopPairPtReweightungFunction() if doTopPtReweighting else None

if options.fastSim:
        leptonFastSimSF = leptonFastSimSF_()

if not options.skipVariations:
        from StopsDilepton.tools.btagEfficiency import btagEfficiency, getTagWeightDict
        btagEff_1d = btagEfficiency(method='1d')

        maxMultBTagWeight = 2
        btagEff_1b = btagEfficiency(method='1b', fastSim = options.fastSim)

# do the following with other parameters
#if options.lheHTCut:
#        try:
#                float(options.lheHTCut)
#        except:
#                sys.exit("Float conversion of option lheHTCut failed. Got this: %s"%options.lheHTCut)
#        sample.name+="_lheHT"+options.lheHTCut
#        skimCond+="&&lheHTIncoming<"+options.lheHTCut

if "Run2015D" in sample.name and not hasattr(sample, "vetoList"):
        sys.exit("ERROR. Sample %s seems to be data but no vetoList was provided!!" %sample.name)

vetoList_ = vetoList(sample.vetoList) if hasattr(sample, "vetoList") else None
outDir = os.path.join(options.targetDir, options.skim, sample.name)
if os.path.exists(outDir):
        existingFiles = [outDir+'/'+f for f in os.listdir(outDir) if f.endswith('.root')]
        hasBadFile = any([not checkRootFile(f, checkForObjects=["Events"]) for f in existingFiles])
else:
        existingFiles = []
        hasBadFile = False

#print "Found bad file? %r"%hasBadFile
if os.path.exists(outDir) and len(existingFiles)>0 and (not hasBadFile) and not options.overwrite:
        print "Found non-empty directory: %s -> skipping! (found a bad file? %r.)"%(outDir, hasBadFile)
        sys.exit(0)
else:
        tmpDir = os.path.join(outDir,'tmp')
        if hasBadFile:
                print "Found a corrupted file. Remake sample. Delete %s"%outDir
                shutil.rmtree(outDir)
        if os.path.exists(outDir) and options.overwrite: #not options.update:
                print "Directory %s exists. Delete it."%outDir
                shutil.rmtree(outDir)
        if not os.path.exists(outDir): os.makedirs(outDir)
        if not os.path.exists(tmpDir): os.makedirs(tmpDir)

if options.signal:
        signalDir = os.path.join(options.targetDir, options.skim, "T2tt")
        if not os.path.exists(signalDir):
                os.makedirs(signalDir)

if doTopPtReweighting:
        print "Computing top pt average weight..."
        c = ROOT.TChain("tree")
        for chunk in chunks:
                c.Add(chunk['file'])
#  print getTopPtDrawString()
        topScaleF = getYieldFromChain(c, cutString = "(1)", weight=getTopPtDrawString())
        topScaleF/=c.GetEntries()
        c.IsA().Destructor(c)
        del c
        print "found a top pt average correction factor of %f"%topScaleF
else:
        print "Do not compute top pt reweight."

if options.signal:
        from StopsDilepton.tools.xSecSusy import xSecSusy
        xSecSusy_ = xSecSusy()
        channel='stop13TeV'
        signalWeight={}
        c = ROOT.TChain("tree")
        for chunk in chunks:
                c.Add(chunk['file'])
        print "Fetching signal weights..."
        mMax = 1500
        bStr = str(mMax)+','+str(mMax)
        c.Draw("GenSusyMScan2:GenSusyMScan1>>hNEvents("+','.join([bStr, bStr])+")")
        hNEvents = ROOT.gDirectory.Get("hNEvents")
        for i in range (mMax):
                for j in range (mMax):
                        n = hNEvents.GetBinContent(hNEvents.FindBin(i,j))
                        if n>0:
                                signalWeight[(i,j)] = {'weight':targetLumi*xSecSusy_.getXSec(channel=channel,mass=i,sigma=0)/n, 'xSecFacUp':xSecSusy_.getXSec(channel=channel,mass=i,sigma=1)/xSecSusy_.getXSec(channel=channel,mass=i,sigma=0), 'xSecFacDown':xSecSusy_.getXSec(channel=channel,mass=i,sigma=-1)/xSecSusy_.getXSec(channel=channel,mass=i,sigma=0)}
                                print "Found mStop %5i mNeu %5i Number of events: %6i, xSec: %10.6f, weight: %6.6f (+1 sigma rel: %6.6f, -1 sigma rel: %6.6f)"%(i,j,n, xSecSusy_.getXSec(channel=channel,mass=i,sigma=0),  signalWeight[(i,j)]['weight'], signalWeight[(i,j)]['xSecFacUp'], signalWeight[(i,j)]['xSecFacDown'])
        c.IsA().Destructor(c)
        del c
        del hNEvents
        print "Done fetching signal weights."

if options.skim.lower().count('tiny'):
        #branches to be kept for data and MC
        branchKeepStrings_DATAMC = ["run", "lumi", "evt", "isData", "nVert",
                                    "met_pt", "met_phi",
                                    "puppiMet_pt","puppiMet_phi",
                                    "Flag_HBHENoiseFilter", "Flag_HBHENoiseIsoFilter", "Flag_goodVertices", "Flag_CSCTightHaloFilter", "Flag_eeBadScFilter",
                                    "HLT_mumuIso", "HLT_ee_DZ", "HLT_mue",
                                    "HLT_3mu", "HLT_3e", "HLT_2e1mu", "HLT_2mu1e",
                                    'LepGood_eta','LepGood_pt','LepGood_phi', 'LepGood_dxy', 'LepGood_dz','LepGood_tightId', 'LepGood_pdgId', 'LepGood_mediumMuonId', 'LepGood_miniRelIso', 'LepGood_sip3d', 'LepGood_mvaIdSpring15', 'LepGood_convVeto', 'LepGood_lostHits',
                                    'Jet_eta','Jet_pt','Jet_phi','Jet_btagCSV', 'Jet_id' ,
#                       "nLepGood", "LepGood_*",
#                       "nTauGood", "TauGood_*",
                                ]

        #branches to be kept for MC samples only
        branchKeepStrings_MC = [ "nTrueInt", "genWeight", "xsec", "met_genPt", "met_genPhi", "lheHTIncoming"
        #                     "GenSusyMScan1", "GenSusyMScan2", "GenSusyMScan3", "GenSusyMScan4", "GenSusyMGluino", "GenSusyMGravitino", "GenSusyMStop", "GenSusyMSbottom", "GenSusyMStop2", "GenSusyMSbottom2", "GenSusyMSquark", "GenSusyMNeutralino", "GenSusyMNeutralino2", "GenSusyMNeutralino3", "GenSusyMNeutralino4", "GenSusyMChargino", "GenSusyMChargino2",
        #                     "ngenLep", "genLep_*",
        #                     "nGenPart", "GenPart_*",
        #                     "ngenPartAll","genPartAll_*","ngenLep","genLep_*"
        #                     "ngenTau", "genTau_*",
        #                     "ngenLepFromTau", "genLepFromTau_*"
                            ]

        #branches to be kept for data only
        branchKeepStrings_DATA = [
                                ]

else:
        #branches to be kept for data and MC
        branchKeepStrings_DATAMC = ["run", "lumi", "evt", "isData", "rho", "nVert",
#                     "nJet25", "nBJetLoose25", "nBJetMedium25", "nBJetTight25", "nJet40", "nJet40a", "nBJetLoose40", "nBJetMedium40", "nBJetTight40",
#                     "nLepGood20", "nLepGood15", "nLepGood10", "htJet25", "mhtJet25", "htJet40j", "htJet40", "mhtJet40", "nSoftBJetLoose25", "nSoftBJetMedium25", "nSoftBJetTight25",
                                "met_pt", "met_phi","met_Jet*", "met_Unclustered*", "met_sumEt", "met_rawPt","met_rawPhi", "met_rawSumEt",
                                "metNoHF_pt", "metNoHF_phi",
                                "puppiMet_pt","puppiMet_phi","puppiMet_sumEt","puppiMet_rawPt","puppiMet_rawPhi","puppiMet_rawSumEt",
                                "Flag_*","HLT_*",
#                     "nFatJet","FatJet_*",
                                "nJet", "Jet_*",
                                "nLepGood", "LepGood_*",
#                     "nLepOther", "LepOther_*",
                                "nTauGood", "TauGood_*",
                                ]

        #branches to be kept for MC samples only
        branchKeepStrings_MC = [ "nTrueInt", "genWeight", "xsec", "met_gen*", "lheHTIncoming",
        #                     "GenSusyMScan1", "GenSusyMScan2", "GenSusyMScan3", "GenSusyMScan4", "GenSusyMGluino", "GenSusyMGravitino", "GenSusyMStop", "GenSusyMSbottom", "GenSusyMStop2", "GenSusyMSbottom2", "GenSusyMSquark", "GenSusyMNeutralino", "GenSusyMNeutralino2", "GenSusyMNeutralino3", "GenSusyMNeutralino4", "GenSusyMChargino", "GenSusyMChargino2",
        #                     "ngenLep", "genLep_*",
        #                     "nGenPart", "GenPart_*",
                                                                                            "ngenPartAll","genPartAll_*","ngenLep","genLep_*"
        #                     "ngenTau", "genTau_*",
        #                     "ngenLepFromTau", "genLepFromTau_*"
                            ]

        #branches to be kept for data only
        branchKeepStrings_DATA = [
                                ]

if options.keepPhotons:
        branchKeepStrings_DATAMC+=["ngamma", "gamma_idCutBased", "gamma_hOverE", "gamma_r9", "gamma_sigmaIetaIeta", "gamma_chHadIso04", "gamma_chHadIso", "gamma_phIso", "gamma_neuHadIso", "gamma_relIso", "gamma_pdgId", "gamma_pt", "gamma_eta", "gamma_phi", "gamma_mass", "gamma_chHadIsoRC04", "gamma_chHadIsoRC"]
        if allMC: branchKeepStrings_DATAMC+=[ "gamma_mcMatchId", "gamma_mcPt", "gamma_genIso04", "gamma_genIso03", "gamma_drMinParton"]
if options.signal:
        branchKeepStrings_MC+=['GenSusyMScan1', 'GenSusyMScan2']
if options.keepLHEWeights:
        branchKeepStrings_MC+=["nLHEweight", "LHEweight_id", "LHEweight_wgt", "LHEweight_original"]

if sample.isData:
        lumiScaleFactor=1
        branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_DATA
        jetMCInfo = []
        from FWCore.PythonUtilities.LumiList import LumiList
        sample.lumiList = LumiList(os.path.expandvars(sample.json))
        outputLumiList = {}
        print "Loaded json %s"%sample.json
else:
        lumiScaleFactor = sample.xSection*targetLumi/float(sumWeight)
        branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC
        jetMCInfo = ['mcMatchFlav/I', 'partonId/I', 'mcPt/F', 'corr/F', 'corr_JECUp/F', 'corr_JECDown/F', 'hadronFlavour/I']

readVariables = ['met_pt/F', 'met_phi/F', 'run/I', 'lumi/I', 'evt/l', 'nVert/I']
if allMC: readVariables+= ['nTrueInt/I']
newVariables = ['weight/F','weightPU/F','weightPUUp/F','weightPUDown/F', 'reweightTopPt/F']
newVariables.extend( ['nGoodJets/I', 'nBTags/I', 'ht/F'] )
aliases = [ "met:met_pt", "metPhi:met_phi"]
if options.signal:
        aliases       +=  ["mStop:GenSusyMScan1", "mNeu:GenSusyMScan2"]
        readVariables += ['GenSusyMScan1/I', 'GenSusyMScan2/I']
        newVariables  += ['reweightXSecUp/F', 'reweightXSecDown/F']
        signalMassPoints = set()
if options.fastSim:
        newVariables  += ['reweightLeptonFastSimSF/F', 'reweightLeptonFastSimSFUp/F', 'reweightLeptonFastSimSFDown/F']

readVectors = [\
        {'prefix':'LepGood',  'nMax':8, 'vars':['pt/F', 'eta/F', 'phi/F', 'pdgId/I', 'charge/I', 'relIso03/F', 'tightId/I', 'miniRelIso/F','mass/F','sip3d/F','mediumMuonId/I', 'mvaIdSpring15/F','lostHits/I', 'convVeto/I', 'dxy/F', 'dz/F']},
        {'prefix':'Jet',  'nMax':100, 'vars':['pt/F', 'eta/F', 'phi/F', 'id/I','btagCSV/F'] + jetMCInfo}]
if allMC: readVectors+=[ {'prefix':'genPartAll',  'nMax':2000, 'vars':['pt/F', 'pdgId/I', 'status/I','nDaughters/I']} ]
if not sample.isData:
        aliases.extend(['genMet:met_genPt', 'genMetPhi:met_genPhi'])
if options.skim.lower().startswith('dilep'):
        newVariables.extend( ['nGoodMuons/I', 'nGoodElectrons/I' ] )
        newVariables.extend( ['dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_mass/F' , 'mlmZ_mass/F'] )
        newVariables.extend( ['dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F' ] )
#  newVariables.extend( ['dl_mtautau/F', 'dl_alpha0/F',  'dl_alpha1/F' ] )
        newVariables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_pdgId/I', 'l1_index/I' ] )
        newVariables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_pdgId/I', 'l2_index/I' ] )
        newVariables.extend( ['isEE/I', 'isMuMu/I', 'isEMu/I', 'isOS/I' ] )
if not options.skipVariations:
        for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
                newVariables.extend( ['nGoodJets_'+var+'/I', 'nBTags_'+var+'/I','ht_'+var+'/F'] )
                newVariables.extend( ['met_pt_'+var+'/F', 'met_phi_'+var+'/F'] )
                if options.skim.lower().startswith('dilep'):
                        newVariables.extend( ['dl_mt2ll_'+var+'/F', 'dl_mt2bb_'+var+'/F', 'dl_mt2blbl_'+var+'/F'] )
        for var in btagEff_1d.btagWeightNames:
                newVariables.append('reweightBTag_'+var+'/F')
        for i in range(maxMultBTagWeight+1):
                for var in btagEff_1b.btagWeightNames:#['MC', 'SF', 'SF_b_Down', 'SF_b_Up', 'SF_l_Down', 'SF_l_Up']:
                        newVariables.extend(['reweightBTag'+str(i)+'_'+var+'/F', 'reweightBTag'+str(i+1)+'p_'+var+'/F'])

newVars = [readVar(v, allowRenaming=False, isWritten = True, isRead=False) for v in newVariables]
readVars = [readVar(v, allowRenaming=False, isWritten=False, isRead=True) for v in readVariables]

for v in readVectors:
        readVars.append(readVar('n'+v['prefix']+'/I', allowRenaming=False, isWritten=False, isRead=True))
        v['vars'] = [readVar(v['prefix']+'_'+vvar, allowRenaming=False, isWritten=False, isRead=True) for vvar in v['vars']]

printHeader("Compiling class to write")
writeClassName = "ClassToWrite"
writeClassString = createClassString(className=writeClassName, vars= newVars, vectors=[], nameKey = 'stage2Name', typeKey = 'stage2Type')
s = compileClass(className=writeClassName, classString=writeClassString, tmpDir='/tmp/')

readClassName = "ClassToRead"
readClassString = createClassString(className=readClassName, vars=readVars, vectors=readVectors, nameKey = 'stage1Name', typeKey = 'stage1Type', stdVectors=False)
printHeader("Class to Read")
r = compileClass(className=readClassName, classString=readClassString, tmpDir='/tmp/')


filesForHadd=[]
#if options.small: chunks=chunks[:1]

nVetoEvents=0
for chunk in chunks:
        sourceFileSize = os.path.getsize(chunk['file'])
        nSplit = 1+int(sourceFileSize/(200*10**6)) #split into 200MB
        if nSplit>1: print "Chunk too large, will split into",nSplit,"of appox 200MB"
        for iSplit in range(nSplit):
                newFileName = sample.name+'_'+chunk['name']+'_'+str(iSplit)+'.root'
                newFile = os.path.join(tmpDir, newFileName)
                if os.path.exists(newFile):
                        good = checkRootFile(newFile, checkForObjects=["Events"])
                        if good:
                                print "Found file and looks OK -> skipping %s"%newFile
                                filesForHadd.append(newFileName)
                                continue
                        else:
                                print "Found file and looks like a zombie -> remake %s"%newFile

                t = getTreeFromChunk(chunk, skimCond, iSplit, nSplit)
                if not t:
                        print "Tree object not found:", t
                        continue
                t.SetName("Events")
                nEvents = t.GetEntries()
                for v in newVars:
#        print "new VAR:" , v
                        v['branch'] = t.Branch(v['stage2Name'], ROOT.AddressOf(s,v['stage2Name']), v['stage2Name']+'/'+v['stage2Type'])
                for v in readVars:
#        print "read VAR:" , v
                        t.SetBranchAddress(v['stage1Name'], ROOT.AddressOf(r, v['stage1Name']))
                for v in readVectors:
                        for var in v['vars']:
                                t.SetBranchAddress(var['stage1Name'], ROOT.AddressOf(r, var['stage1Name']))
                for a in aliases:
                        t.SetAlias(*(a.split(":")))
                print "File: %s Chunk: %s nEvents: %i (skim: %s) condition: %s lumiScaleFactor: %f"%(chunk['file'],chunk['name'], nEvents, options.skim, skimCond, lumiScaleFactor)

                for i in range(nEvents):
                        if (i%10000 == 0) and i>0 :
                                print i,"/",nEvents  , "name:" , chunk['name']
                        r.init()
                        s.init()
                        t.GetEntry(i)
                        if options.signal: signalMassPoints.add((r.GenSusyMScan1, r.GenSusyMScan2))
                        genWeight = 1 if sample.isData else t.GetLeaf('genWeight').GetValue()
                        if allMC and not options.signal:
                                s.weight = lumiScaleFactor*genWeight
                        if allData:
                                s.weight = 1.
                        if options.signal:
                                        s.weight=signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['weight']
                                        s.reweightXSecUp    = signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['xSecFacUp']
                                        s.reweightXSecDown  = signalWeight[(r.GenSusyMScan1, r.GenSusyMScan2)]['xSecFacDown']
                        s.reweightTopPt = topPtReweightingFunc(getTopPtsForReweighting(r))/topScaleF if doTopPtReweighting else 1.
                        if not sample.isData:
                                s.weightPU     = s.weight*puRW(r.nTrueInt)
                                s.weightPUDown = s.weight*puRWDown(r.nTrueInt)
                                s.weightPUUp   = s.weight*puRWUp(r.nTrueInt)
                        else:
                                s.weightPU     = 1
                                s.weightPUDown = 1
                                s.weightPUUp   = 1
                        if sample.isData:
                                if not sample.lumiList.contains(r.run, r.lumi):
        #        print "Did not find run %i lumi %i in json file %s"%(r.run, r.lumi, sample.json)
                                        s.weight=0
                                        s.weightPU=0
                                        s.weightPUUp=0
                                        s.weightPUDown=0
                                else:
                                        if r.run not in outputLumiList.keys():
                                                outputLumiList[r.run] = [r.lumi]
                                        else:
                                                if r.lumi not in outputLumiList[r.run]:
                                                        outputLumiList[r.run].append(r.lumi)
                        if vetoList_:
                                if (r.run, r.lumi, r.evt) in vetoList_.events:
#          print "Veto %i:%i:%i "%(r.run, r.lumi, r.evt)
                                        s.weight=0
                                        s.weightPU=0
                                        s.weightPUUp=0
                                        s.weightPUDown=0
                                        nVetoEvents+=1
#        print "Found %i:%i:%i in %s"%(r.run, r.lumi, r.evt, vetoList.filename)
#      else: print [r.run, r.lumi, r.evt], vetoList_.events[0]
#        print "Found run %i lumi %i in json file %s"%(r.run, r.lumi, sample.json)

                        allJets = getGoodJets(r, ptCut=0, jetVars=jetVars if options.skipVariations else jetVars+['mcPt', 'corr','corr_JECUp','corr_JECDown','hadronFlavour'])
                        jets = filter(lambda j:jetId(j, ptCut=30, absEtaCut=2.4), allJets)
                        s.nGoodJets   = len(jets)
                        s.ht          = sum([j['pt'] for j in jets])
                        s.nBTags      = len(filter(isBJet, jets))
                        if not options.skipVariations:
                                for j in allJets:
                                        j['pt_JECUp']   =j['pt']/j['corr']*j['corr_JECUp']
                                        j['pt_JECDown'] =j['pt']/j['corr']*j['corr_JECDown']
                                        addJERScaling(j)
                                jets_      = {}
                                bJets_     = {}
                                nonBJets_  = {}
                                metShifts_ = {}

                                for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
                                        jets_[var]       = filter(lambda j:jetId(j, ptCut=30, absEtaCut=2.4, ptVar='pt_'+var), allJets)
                                        bJets_[var]      = filter(isBJet, jets_[var])
                                        nonBJets_[var]      = filter(lambda j: not isBJet(j), jets_[var])
                                        met_corr_px = r.met_pt*cos(r.met_phi) + sum([(j['pt']-j['pt_'+var])*cos(j['phi']) for j in jets_[var] ])
                                        met_corr_py = r.met_pt*sin(r.met_phi) + sum([(j['pt']-j['pt_'+var])*sin(j['phi']) for j in jets_[var] ])

                                        setattr(s, "met_pt_"+var, sqrt(met_corr_px**2 + met_corr_py**2))
                                        setattr(s, "met_phi_"+var, atan2(met_corr_py, met_corr_px))
                                        setattr(s, "nGoodJets_"+var, len(jets_[var]))
                                        setattr(s, "ht_"+var, sum([j['pt_'+var] for j in jets_[var]]))
                                        setattr(s, "nBTags_"+var, len(bJets_[var]))

                        if options.skim.lower().startswith('dilep'):
                                leptons_pt10 = getGoodLeptons(r, ptCut=10)
                                leptons      = filter(lambda l:l['pt']>20, leptons_pt10)
                                if options.fastSim:
                                        s.reweightLeptonFastSimSF     = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert) for l in leptons], 1)
                                        s.reweightLeptonFastSimSFUp   = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert, sigma = +1) for l in leptons], 1)
                                        s.reweightLeptonFastSimSFDown = reduce(mul, [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert, sigma = -1) for l in leptons], 1)
#          if s.reweightLeptonFastSimSF==0:
#            print [leptonFastSimSF.get3DSF(pdgId=l['pdgId'], pt=l['pt'], eta=l['eta'] , nvtx = r.nVert) for l in leptons], leptons

                                s.nGoodMuons      = len(filter( lambda l:abs(l['pdgId'])==13, leptons))
                                s.nGoodElectrons  = len(filter( lambda l:abs(l['pdgId'])==11, leptons))
#          print "Leptons", leptons
                                if len(leptons)>=2:# and leptons[0]['pdgId']*leptons[1]['pdgId']<0 and abs(leptons[0]['pdgId'])==abs(leptons[1]['pdgId']): #OSSF choice
                                        mt2Calc.reset()
                                        s.l1_pt  = leptons[0]['pt']
                                        s.l1_eta = leptons[0]['eta']
                                        s.l1_phi = leptons[0]['phi']
                                        s.l1_pdgId  = leptons[0]['pdgId']
                                        s.l1_index  = leptons[0]['index']
                                        s.l2_pt  = leptons[1]['pt']
                                        s.l2_eta = leptons[1]['eta']
                                        s.l2_phi = leptons[1]['phi']
                                        s.l2_pdgId  = leptons[1]['pdgId']
                                        s.l2_index  = leptons[1]['index']

                                        l_pdgs = [abs(leptons[0]['pdgId']), abs(leptons[1]['pdgId'])]
                                        l_pdgs.sort()
                                        s.isMuMu = l_pdgs==[13,13]
                                        s.isEE = l_pdgs==[11,11]
                                        s.isEMu = l_pdgs==[11,13]
                                        s.isOS = s.l1_pdgId*s.l2_pdgId<0

                                        l1 = ROOT.TLorentzVector()
                                        l1.SetPtEtaPhiM(leptons[0]['pt'], leptons[0]['eta'], leptons[0]['phi'], 0 )
                                        l2 = ROOT.TLorentzVector()
                                        l2.SetPtEtaPhiM(leptons[1]['pt'], leptons[1]['eta'], leptons[1]['phi'], 0 )
                                        dl = l1+l2
                                        s.dl_pt  = dl.Pt()
                                        s.dl_eta = dl.Eta()
                                        s.dl_phi = dl.Phi()
                                        s.dl_mass   = dl.M()
                                        s.mlmZ_mass = closestOSDLMassToMZ(leptons_pt10)
                                        mt2Calc.setLeptons(s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi)
                                        mt2Calc.setMet(r.met_pt,r.met_phi)
                                        s.dl_mt2ll = mt2Calc.mt2ll()
#          s.dl_mtautau, s.dl_alpha0, s.dl_alpha1 = mtautau_(r.met_pt,r.met_phi, s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi, retAll=True)
                                        if len(jets)>=2:
                                                bJets = filter(lambda j:isBJet(j), jets)
                                                nonBJets = filter(lambda j:not isBJet(j), jets)
                                                bj0, bj1 = (bJets+nonBJets)[:2]
                                                mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
                                                s.dl_mt2bb   = mt2Calc.mt2bb()
                                                s.dl_mt2blbl = mt2Calc.mt2blbl()
                                        if not options.skipVariations:
                                                for var in ['JECUp', 'JECDown', 'JER', 'JERUp', 'JERDown']:
                                                        mt2Calc.setMet( getattr(s, "met_pt_"+var), getattr(s, "met_phi_"+var) )
                                                        setattr(s, "dl_mt2ll_"+var,  mt2Calc.mt2ll())
                                                        if len(jets_[var])>=2:
                                                                bj0, bj1 = (bJets_[var]+nonBJets_[var])[:2]
                                                                mt2Calc.setBJets(bj0['pt'], bj0['eta'], bj0['phi'], bj1['pt'], bj1['eta'], bj1['phi'])
                                                                setattr(s, 'dl_mt2bb_'+var, mt2Calc.mt2bb())
                                                                setattr(s, 'dl_mt2blbl_'+var,mt2Calc.mt2blbl())

                        if not options.skipVariations:
                                for j in jets:
                                        btagEff_1d.addBTagEffToJet(j)
                                for var in btagEff_1d.btagWeightNames:
                                        setattr(s, 'reweightBTag_'+var, reduce(mul, [j['beff'][var] for j in jets], 1) )
                                for j in jets:
                                        btagEff_1b.addBTagEffToJet(j)
                                for var in btagEff_1b.btagWeightNames:
                                        res = getTagWeightDict([j['beff'][var] for j in jets], maxMultBTagWeight)
                                        for i in range(maxMultBTagWeight+1):
                                                setattr(s, 'reweightBTag'+str(i)+'_'+var, res[i])
                                                setattr(s, 'reweightBTag'+str(i+1)+'p_'+var, 1-sum([res[j] for j in range(i+1)]))
                        for v in newVars:
                                v['branch'].Fill()
                filesForHadd.append(newFileName)
                if not options.small or interactive:
                        f = ROOT.TFile(newFile, 'recreate')
                        t.SetBranchStatus("*",0)
                        for b in branchKeepStrings + [v['stage2Name'] for v in newVars] +  [v.split(':')[1] for v in aliases]:
                                t.SetBranchStatus(b, 1)
                        t2 = t.CloneTree()
                        t2.Write()
                        f.Close()
                        print "Written",newFile
                        del f
                        del t2
                        t.Delete()
                        del t
                for v in newVars:
                        del v['branch']

print "Event loop end. Vetoed %i events."%nVetoEvents

if not options.small:
        size=0
        counter=0
        files=[]
        ofiles=[]
        for f in filesForHadd:
                size+=os.path.getsize(tmpDir+'/'+f)
                files.append(f)
                if size>(0.5*(10**9)) or f==filesForHadd[-1] or len(files)>300:
                        ofile = outDir+'/'+sample.name+'_'+str(counter)+'.root'
                        print "Running hadd on", tmpDir, files
                        os.system('cd '+tmpDir+';hadd -f '+ofile+' '+' '.join(files))
                        print "Written output file %s" % ofile
                        ofiles.append(ofile)
                        size=0
                        counter+=1
                        files=[]
        shutil.rmtree(tmpDir)
        if allData:
                jsonFile = outDir+'/'+sample.name+'.json'
                LumiList(runsAndLumis = outputLumiList).writeJSON(jsonFile)
                print "Written JSON file %s" % jsonFile
        if options.signal:
                c = ROOT.TChain('Events')
                for f in ofiles:c.Add(f)
                for s in signalMassPoints:
                        cut = "GenSusyMScan1=="+str(s[0])+"&&GenSusyMScan2=="+str(s[1])
                        signalFile = signalDir+'/T2tt_'+str(s[0])+'_'+str(s[1])+'.root'
                        if not os.path.exists(signalFile) or options.overwrite:
                                t = c.CopyTree(cut)
                                writeObjToFile(signalFile, t)
                                print "Written signal file for masses mStop %i mNeu %i to %s"%(s[0], s[1], signalFile)
        #      t.IsA().Destructor(c)
        #      del t
                        else:
                                print "Found file %s -> Skipping"%(signalFile)
                c.IsA().Destructor(c)
                del c
