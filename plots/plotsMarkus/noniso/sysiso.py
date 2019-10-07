#!/usr/bin/env python
''' analysis script for MT plots with systematic errors
'''

# Standard imports and batch mode
import ROOT
ROOT.gROOT.SetBatch(True)
import operator
import pickle, os, time, sys
from math                                import sqrt, cos, sin, pi, atan2

# RootTools
from RootTools.core.standard             import *

#Analysis / StopsDilepton / Samples
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, add_histos
from Analysis.Tools.metFilters           import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.RecoilCorrector import RecoilCorrector
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puReweighting        import getReweightingFunction
from Analysis.Tools.DirDB                import DirDB

from StopsDilepton.tools.objectSelection import muonSelector, eleSelector, getGoodMuons, getGoodElectrons

# JEC corrector
from JetMET.JetCorrector.JetCorrector    import JetCorrector, correction_levels_data, correction_levels_mc
corrector_data     = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_data )
corrector_mc       = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_mc )


# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',          action='store',      default='INFO',     nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',            action='store',      default=None,        nargs='?', choices=['None', "T2tt",'DM'], help="Add signal to plot")
argParser.add_argument('--plot_directory',    action='store',      default='isoVSinvIso')
argParser.add_argument('--selection',         action='store',      default='lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1')
argParser.add_argument('--variation',         action='store',      default=None, help="Which systematic variation to run. Don't specify for producing plots.")
argParser.add_argument('--small',             action='store_true',     help='Run only on a small subset of the data?')
argParser.add_argument('--normalize',         action='store_true')
argParser.add_argument('--appendCmds',        action='store_true')
argParser.add_argument('--dpm',               action='store_true',     help='Use dpm?', )
argParser.add_argument('--noDYHT',            action='store_true',     help='run without HT-binned DY')
argParser.add_argument('--scaling',           action='store',      default=None, choices = [None, 'mc', 'top'],     help='Scale top to data in mt2ll<100?')
argParser.add_argument('--variation_scaling', action='store_true', help='Scale the variations individually to mimick bkg estimation?')
argParser.add_argument('--overwrite',         action='store_true',     help='Overwrite?')
argParser.add_argument('--mode',              action='store',      default = 'all', choices = ['mumu', 'ee', 'mue', 'emu', 'all'],   help='Which mode?')
argParser.add_argument('--normalizeBinWidth', action='store_true', default=False,       help='normalize wider bins?')
argParser.add_argument('--reweightPU',        action='store',      default='Central', choices=[ 'Central', 'VUp'] )
#argParser.add_argument('--recoil',             action='store', type=str,      default="Central", choices = ["nvtx", "VUp", "Central"])
argParser.add_argument('--era',               action='store', type=str,      default="Run2016")
argParser.add_argument('--beta',              action='store',      default=None, help="Add an additional subdirectory for minor changes to the plots")

args = argParser.parse_args()

# Logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
import Analysis.Tools.logger as logger_an
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)
logger_an = logger_an.get_logger(args.logLevel, logFile = None)

# Year
if "2016" in args.era:
    year = 2016
elif "2017" in args.era:
    year = 2017
elif "2018" in args.era:
    year = 2018

logger.info( "Working in year %i", year )

def jetSelectionModifier( sys, returntype = "func"):
    #Need to make sure all jet variations of the following observables are in the ntuple
    variiedJetObservables = ['nJetGood', 'nBTag', 'dl_mt2ll', 'dl_mt2blbl', 'MET_significance', 'met_pt', 'met_phi', 'metSig']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedJetObservables:
                string = string.replace(s, s+'_'+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+'_'+sys for v in variiedJetObservables ]

def metSelectionModifier( sys, returntype = 'func'):
    #Need to make sure all MET variations of the following observables are in the ntuple
    variiedMetObservables = ['dl_mt2ll', 'dl_mt2blbl', 'MET_significance', 'met_pt', 'met_phi', 'metSig']
    if returntype == "func":
        def changeCut_( string ):
            for s in variiedMetObservables:
                string = string.replace(s, s+'_'+sys)
            return string
        return changeCut_
    elif returntype == "list":
        return [ v+'_'+sys for v in variiedMetObservables ]

# these are the nominal MC weights we always apply
if args.reweightPU == 'Central': 
    nominalMCWeights = ["weight", "reweightLeptonSF", "reweightPU", "reweightBTag_SF", "reweightLeptonTrackingSF", "reweightL1Prefire", "reweightHEM"]
if args.reweightPU == 'VUp':
    nominalMCWeights = ["weight", "reweightLeptonSF", "reweightPUVUp", "reweightBTag_SF", "reweightLeptonTrackingSF", "reweightL1Prefire", "reweightHEM"]

# weights to use for PU variation
if args.reweightPU == 'Central':
    nominalPuWeight, upPUWeight, downPUWeight = "reweightPU", "reweightPUUp", "reweightPUDown"
elif args.reweightPU == 'VUp':
    nominalPuWeight, upPUWeight, downPUWeight = "reweightPUVUp", "reweightPUVVUp", "reweightPUUp"

# weight the MC according to a variation
def MC_WEIGHT( variation, returntype = "string"):
    variiedMCWeights = list(nominalMCWeights)   # deep copy
    if variation.has_key('replaceWeight'):
        for i_w, w in enumerate(variiedMCWeights):
            if w == variation['replaceWeight'][0]:
                variiedMCWeights[i_w] = variation['replaceWeight'][1]
                break
        # Let's make sure we don't screw it up ... because we mostly do.
        if variiedMCWeights==nominalMCWeights:
            raise RuntimeError( "Tried to change weight %s to %s but didn't find it in list %r" % ( variation['replaceWeight'][0], variation['replaceWeight'][1], variiedMCWeights ))
    # multiply strings for ROOT weights
    if returntype == "string":
        return "*".join(variiedMCWeights)
    # create a function that multiplies the attributes of the event
    elif returntype == "func":
        getters = map( operator.attrgetter, variiedMCWeights)
        def weight_( event, sample):
            return reduce(operator.mul, [g(event) for g in getters], 1)
        return weight_
    elif returntype == "list":
        return variiedMCWeights

def data_weight( event, sample ):
    return event.weight*event.reweightHEM

data_weight_string = "weight*reweightHEM"

# Define all systematic variations
jet_systematics    = ['jesTotalUp','jesTotalDown', 'jerUp', 'jerDown']
met_systematics    = ['unclustEnUp', 'unclustEnDown']
jme_systematics    = jet_systematics + met_systematics

variations = {
    'central'           : {'read_variables': [ '%s/F'%v for v in nominalMCWeights ]},
    'jesTotalUp'        : {'selectionModifier':jetSelectionModifier('jesTotalUp'),               'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('jesTotalUp','list')]},
    'jesTotalDown'      : {'selectionModifier':jetSelectionModifier('jesTotalDown'),             'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('jesTotalDown','list')]},
    'jerUp'             : {'selectionModifier':jetSelectionModifier('jerUp'),                    'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('jerUp','list')]},
    'jerDown'           : {'selectionModifier':jetSelectionModifier('jerDown'),                  'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('jerDown','list')]},
    'unclustEnUp'       : {'selectionModifier':metSelectionModifier('unclustEnUp'),              'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('unclustEnUp','list')]},
    'unclustEnDown'     : {'selectionModifier':metSelectionModifier('unclustEnDown'),            'read_variables' : [ '%s/F'%v for v in nominalMCWeights + jetSelectionModifier('unclustEnDown','list')]},
    'PUUp'              : {'replaceWeight':(nominalPuWeight,upPUWeight),                         'read_variables' : [ '%s/F'%v for v in nominalMCWeights + [upPUWeight] ]},
    'PUDown'            : {'replaceWeight':(nominalPuWeight,downPUWeight),                       'read_variables' : [ '%s/F'%v for v in nominalMCWeights + [downPUWeight] ]},
    'BTag_SF_b_Down'    : {'replaceWeight':('reweightBTag_SF','reweightBTag_SF_b_Down'),         'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightBTag_SF_b_Down']]},  
    'BTag_SF_b_Up'      : {'replaceWeight':('reweightBTag_SF','reweightBTag_SF_b_Up'),           'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightBTag_SF_b_Up'] ]},
    'BTag_SF_l_Down'    : {'replaceWeight':('reweightBTag_SF','reweightBTag_SF_l_Down'),         'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightBTag_SF_l_Down']]},
    'BTag_SF_l_Up'      : {'replaceWeight':('reweightBTag_SF','reweightBTag_SF_l_Up'),           'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightBTag_SF_l_Up'] ]},
#    'DilepTriggerDown'  : {'replaceWeight':('reweightDilepTrigger','reweightDilepTriggerDown'),  'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightDilepTriggerDown']]},
#    'DilepTriggerUp'    : {'replaceWeight':('reweightDilepTrigger','reweightDilepTriggerUp'),    'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightDilepTriggerUp']]},
    'LeptonSFDown'      : {'replaceWeight':('reweightLeptonSF','reweightLeptonSFDown'),          'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightLeptonSFDown']]},
    'LeptonSFUp'        : {'replaceWeight':('reweightLeptonSF','reweightLeptonSFUp'),            'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightLeptonSFUp']]},
    'L1PrefireDown'     : {'replaceWeight':('reweightL1Prefire','reweightL1PrefireDown'),        'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightL1PrefireDown']]},
    'L1PrefireUp'       : {'replaceWeight':('reweightL1Prefire','reweightL1PrefireUp'),          'read_variables' : [ '%s/F'%v for v in nominalMCWeights + ['reweightL1PrefireUp']]},
#    'TopPt':{},
}

# Add a default selection modifier that does nothing
for key, variation in variations.iteritems():
    if not variation.has_key('selectionModifier'):
        variation['selectionModifier'] = lambda string:string
    if not variation.has_key('read_variables'):
        variation['read_variables'] = [] 

# Check if we know the variation
if args.variation is not None and args.variation not in variations.keys():
    raise RuntimeError( "Variation %s not among the known: %s", args.variation, ",".join( variation.keys() ) )

# arguments & directory
plot_subdirectory = args.plot_directory
if args.signal == "DM":           plot_subdirectory += "_DM"
if args.signal == "T2tt":         plot_subdirectory += "_T2tt"
if args.small:                    plot_subdirectory += "_small"
if args.reweightPU:               plot_subdirectory += "_reweightPU%s"%args.reweightPU
#if args.recoil:                  plot_subdirectory  += '_recoil_'+args.recoil

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"
    
if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    Top_pow, TTXNoZ, TTZ_LO, multiBoson, DY_HT_LO = Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16
    if args.noDYHT:
        mc          = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
        #print "~~~~> using normal DY sample instead of HT binned one"
    else:
        mc          = [ Top_pow_16, Top_pow_1l_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    Top_pow, TTXNoZ, TTZ_LO, multiBoson, DY_HT_LO = Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17
    if args.noDYHT:
        mc          = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
        #print "~~~~> using normal DY sample instead of HT binned one"
    else:
        mc          = [ Top_pow_17, Top_pow_1l_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_HT_LO_17]

elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    Top_pow, TTXNoZ, TTZ_LO, multiBoson, DY_HT_LO = Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18
    if args.noDYHT:
        mc          = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]
        #print "~~~~> using normal DY sample instead of HT binned one"
    else:
        mc          = [ Top_pow_18, Top_pow_1l_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18]

# postions of MC components in list
position = {s.name:i_s for i_s,s in enumerate(mc)}

#if args.recoil:
#    from Analysis.Tools.RecoilCorrector import RecoilCorrector
#    if args.recoil == "nvtx":
#        recoilCorrector = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine_nvtx_loop", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )
#    elif args.recoil == "VUp":
#        recoilCorrector = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine_VUp_loop", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )
#    elif args.recoil is "Central":
#        recoilCorrector = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )
#

# Read variables and sequences
read_variables = ["weight/F", "l1_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "dl_pt/F", "dl_phi/F",
                  "l1_pdgId/I", "l2_pdgId/I",
#                  "Jet[pt/F,rawFactor/F,pt_nom/F,eta/F,area/F]", "run/I", "fixedGridRhoFastjetAll/F",
#                  "nMuon/I", "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]",
                  #"LepGood[pt/F,eta/F,miniRelIso/F]", "nGoodMuons/F", "nGoodElectrons/F", "l1_mIsoWP/F", "l2_mIsoWP/F",
                  "metSig/F", "ht/F", "nBTag/I", "nJetGood/I","run/I","event/l","reweightHEM/F"]
read_variables += [
            "nMuon/I", "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]",
            "nElectron/I", "Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,phi/F,pt/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,pdgId/I,tightCharge/I,lostHits/b,vidNestedWPBitmap/I]"
            ]

sequence = []

ele_selector_iso     = eleSelector(  'tightMiniIso02', year )
mu_selector_iso      = muonSelector( 'tightMiniIso02', year )
ele_selector_noIso   = eleSelector(  'tightNoIso', year )
mu_selector_noIso    = muonSelector( 'tightNoIso', year )

def make_invIso(event, sample):
    event.iso_mt        = float('nan')
    event.invIso_mt      = float('nan')
    event.invIso_relIso  = float('nan')
    event.mt2ll  = float('nan')

    # MET systematics
    if args.variation in jme_systematics:
        met_pt = getattr(event, "met_pt_"+args.variation) 
        met_phi = getattr(event, "met_phi_"+args.variation) 
    else:
        met_pt = event.met_pt
        met_phi = event.met_phi

    noIsoLeptons = getGoodMuons(event, mu_selector = mu_selector_noIso) + getGoodElectrons(event, ele_selector = ele_selector_noIso)

    # leptons with high isolation
    invIso_leptons = []
    for l in noIsoLeptons:
        if l['miniPFRelIso_all'] > 0.2:
            invIso_leptons.append(l)

    # isolation of trailing lepton (if leading is isolated)
    noIsoLeptons.sort( key = lambda p:-p['pt'] )
    event.trailing_ele_iso = -1 
    event.trailing_mu_iso  = -1 
    if len(noIsoLeptons)>1:
        if abs(noIsoLeptons[0]['pdgId'])==11 and ele_selector_iso(noIsoLeptons[0]) or abs(noIsoLeptons[0]['pdgId'])==13 and mu_selector_iso(noIsoLeptons[0]):
            if abs(noIsoLeptons[1]['pdgId'])==11:
                event.trailing_ele_iso = noIsoLeptons[1]['miniPFRelIso_all']
            elif abs(noIsoLeptons[1]['pdgId'])==13:
                event.trailing_mu_iso = noIsoLeptons[1]['miniPFRelIso_all']
            

    if sample.mode == "mumu" or sample.mode == "emu": # second (non isolated) lepton is a MUON
        pdgID = 13
    elif sample.mode == "mue" or sample.mode == "ee": # second (non isolated) lepton is an ELECTRON
        pdgID = 11

    if len(invIso_leptons)>0:
        l1 = {"pt": event.l1_pt, "phi": event.l1_phi, "eta": event.l1_eta, "pdgId": event.l1_pdgId}

        l = invIso_leptons[0]
        ll = {"pt": l["pt"], "phi": l["phi"], "eta": l["eta"], "pdgId": l["pdgId"], "miniPFRelIso_all": l['miniPFRelIso_all']}

        if abs(ll["pdgId"]) == pdgID:
            event.iso_mt       = sqrt(2*l1["pt"]*met_pt*(1-(cos(l1["phi"]-met_phi))))
            event.invIso_mt     = sqrt(2*ll["pt"]*met_pt*(1-(cos(ll["phi"]-met_phi))))
            event.invIso_relIso = ll["miniPFRelIso_all"]
    
            # MT2ll
            l1_pt  = l1["pt"]
            l1_phi = l1["phi"]
            l1_eta = l1["eta"]
            l2_pt  = ll["pt"]
            l2_phi = ll["phi"]
            l2_eta = ll["eta"]
            mt2Calculator.reset()
            mt2Calculator.setLeptons(l1_pt, l1_eta, l1_phi, l2_pt, l2_eta, l2_phi)
            mt2Calculator.setMet(met_pt, met_phi)
            event.mt2ll = mt2Calculator.mt2ll()


sequence.append( make_invIso )



signals = []

# selection
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==1"
  elif mode=="mue":  return "nGoodMuons==1"
  elif mode=="emu":  return "nGoodElectrons==1"
  elif mode=="ee":   return "nGoodElectrons==1"

modes   = ['mumu', 'mue', 'emu', 'ee'] if args.mode=='all' else [args.mode]

allPlots   = {}

logger.info('Working on modes: %s', ','.join(modes))

try:
  data_sample = eval(args.era)
except Exception as e:
  logger.error( "Didn't find %s", args.era )
  raise e

# Define samples
data_sample.name           = "data"
data_sample.read_variables = ["event/I","run/I"]
data_sample.style          = styles.errorStyle(ROOT.kBlack)
data_sample.scale          = 1.
lumi_scale                 = data_sample.lumi/1000
logger.info('Lumi scale is ' + str(lumi_scale))
for sample in mc:
    sample.scale           = lumi_scale
    sample.style           = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables  = ['Pileup_nTrueInt/F', 'GenMET_pt/F', 'GenMET_phi/F', "l1_muIndex/I", "l2_muIndex/I"]
    # append variables for systematics
    if args.variation is not None:
        sample.read_variables+=list(set(variations[args.variation]['read_variables']))

# reduce if small
if args.small:
  data_sample.normalization = 1.
  #data_sample.reduceFiles( factor = 40 )
  data_sample.reduceFiles( to = 1 )
  data_sample.scale /= data_sample.normalization
  for sample in mc:
    sample.normalization = 1.
    #sample.reduceFiles( factor = 40 )
    sample.reduceFiles( to = 1 )
    sample.scale /= sample.normalization

# Fire up the cache
dirDB = DirDB(os.path.join(plot_directory, 'systematicPlots', args.era, plot_subdirectory , args.selection, 'cache'))

# loop over modes
for mode in modes:
    logger.info('Working on mode: %s', mode)

    # set selection
    data_sample.setSelectionString([getFilterCut(isData=True, year=year), getLeptonSelection(mode)])
    for sample in mc:
        sample.setSelectionString([getFilterCut(isData=False, year=year), getLeptonSelection(mode)])

    # hack to have mode in sequence
    for s in [data_sample]+mc:
        s.mode = mode            

    # Use some defaults
    Plot.setDefaults( selectionString = cutInterpreter.cutString(args.selection) )

    # if we're running a variation specify
    if args.variation is not None:
        selectionModifier = variations[args.variation]['selectionModifier']
        mc_weight         = MC_WEIGHT( variation = variations[args.variation], returntype='func')
    else:
        selectionModifier = None 
        mc_weight         = None 

    # Stack
    stack_mc   = Stack( mc )
    stack_data = Stack( data_sample )

    plots      = []

    mt2llBinning = [0,20,40,60,80,100,140,240,340]
    if args.variation == 'central':
        mt2ll_data   = Plot(
            name        = "mt2ll_data",
            texX        = 'M_{T2}(ll) for iso/non-iso lepton pair (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = Binning.fromThresholds(mt2llBinning),
            stack       = stack_data,
            attribute   = lambda event, sample: event.mt2ll,
            weight      = data_weight )
        plots.append( mt2ll_data )

    mt2ll_mc  = Plot(\
        name            = "mt2ll_mc",
        texX            = 'M_{T2}(ll) for iso/non-iso lepton pair (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = Binning.fromThresholds(mt2llBinning),
        stack           = stack_mc,
        attribute       = lambda event, sample: event.mt2ll,
#        attribute       = lambda event, sample: getattr(event, "mt2ll_"+args.variation) if args.variation in jme_systematics else event.mt2ll,
#        attribute       = TreeVariable.fromString( selectionModifier("mt2ll/F"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( mt2ll_mc )

    if args.variation == 'central':
        iso_mt_data   = Plot(
            name        = "iso_mT_data",
            texX        = 'M_{T} for isolated lepton (GeV)', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = [400/10, 0, 400],
            stack       = stack_data,
            attribute   = lambda event, sample: event.iso_mt,
            weight      = data_weight )
        plots.append( iso_mt_data )

    iso_mt_mc  = Plot(\
        name            = "iso_mT_mc",
        texX            = 'M_{T} for isolated lepton (GeV)', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = [400/10, 0, 400],
        stack           = stack_mc,
        attribute       = lambda event, sample: event.iso_mt,
#        attribute       = lambda event, sample: getattr(event, "iso_mt_"+args.variation) if args.variation in jme_systematics else event.iso_mt,
#        attribute       = TreeVariable.fromString( selectionModifier("iso_mt/F"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( iso_mt_mc )

    if args.variation == 'central':
        invIso_mt_data   = Plot(
            name        = "invIso_mT_data",
            texX        = 'M_{T} for non-isolated lepton (GeV)', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = [400/10, 0, 400],
            stack       = stack_data,
            attribute   = lambda event, sample: event.invIso_mt,
            weight      = data_weight )
        plots.append( invIso_mt_data )

    invIso_mt_mc  = Plot(\
        name            = "invIso_mT_mc",
        texX            = 'M_{T} for non-isolated lepton (GeV)', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = [400/10, 0, 400],
        stack           = stack_mc,
        attribute       = lambda event, sample: event.invIso_mt,
#        attribute       = lambda event, sample: getattr(event, "invIso_mt_"+args.variation) if args.variation in jme_systematics else event.invIso_mt,
#        attribute       = TreeVariable.fromString( selectionModifier("invIso_mt/F"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( invIso_mt_mc )

    if args.variation == 'central':
        trailing_ele_iso_data   = Plot(
            name        = "trailing_ele_iso_data",
            texX        = 'I_{mini} for trailing ele', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = [40, 0, 1],
            stack       = stack_data,
            attribute   = lambda event, sample: event.trailing_ele_iso,
            weight      = data_weight )
        plots.append( trailing_ele_iso_data )

    trailing_ele_iso_mc  = Plot(\
        name            = "trailing_ele_iso_mc",
        texX            = 'I_{mini} for trailing ele', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = [40,0,1],
        stack           = stack_mc,
        attribute       = lambda event, sample: event.trailing_ele_iso,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( trailing_ele_iso_mc )

    if args.variation == 'central':
        trailing_mu_iso_data   = Plot(
            name        = "trailing_mu_iso_data",
            texX        = 'I_{mini} for trailing ele', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = [40, 0, 1],
            stack       = stack_data,
            attribute   = lambda event, sample: event.trailing_mu_iso,
            weight      = data_weight )
        plots.append( trailing_mu_iso_data )

    trailing_mu_iso_mc  = Plot(\
        name            = "trailing_mu_iso_mc",
        texX            = 'I_{mini} for trailing ele', texY = 'Number of Events / 10 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = [40,0,1],
        stack           = stack_mc,
        attribute       = lambda event, sample: event.trailing_mu_iso,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( trailing_mu_iso_mc )





#    dl_mt2ll_corr_mc  = Plot(\
#        name            = "dl_mt2ll_corr_mc",
#        texX            = 'corrected M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
#        binning         = Binning.fromThresholds(mt2llCorrBinning),
#        stack           = stack_mc,
#        #FIXME: attribute       = lambda event, sample: getattr(event, selectionModifier("dl_mt2ll_corr/F") if selectionModifier is not None else None, 
#        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
#        weight          = mc_weight )
#    plots.append( dl_mt2ll_corr_mc )
    
    nBtagBinning = [6, 0, 6] 
    if args.variation == 'central':
        nbtags_data   = Plot(
            name        = "nbtags_data",
            texX        = 'number of b-tags (CSVM)', texY = 'Number of Events' if args.normalizeBinWidth else "Number of Events",
            binning     = nBtagBinning,
            stack       = stack_data,
            attribute   = TreeVariable.fromString( "nBTag/I" ),
            weight      = data_weight )
        plots.append( nbtags_data )

    nbtags_mc  = Plot(\
        name            = "nbtags_mc",
        texX            = 'number of b-tags (CSVM)', texY = 'Number of Events' if args.normalizeBinWidth else "Number of Events",
        binning         = nBtagBinning,
        stack           = stack_mc,
        attribute       = TreeVariable.fromString( selectionModifier("nBTag/I"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( nbtags_mc )
    

    jetBinning = [8,0,10] 
    if args.variation == 'central':
        njets_data   = Plot(
            name        = "njets_data",
            texX        = 'number of jets', texY = 'Number of Events' if args.normalizeBinWidth else "Number of Events",
            binning     = jetBinning,
            stack       = stack_data,
            attribute   = TreeVariable.fromString( "nJetGood/I" ),
            weight      = data_weight )
        plots.append( njets_data )

    njets_mc  = Plot(\
        name            = "njets_mc",
        texX            = 'number of jets', texY = 'Number of Events' if args.normalizeBinWidth else "Number of Events",
        binning         = jetBinning,
        stack           = stack_mc,
        attribute       = TreeVariable.fromString( selectionModifier("nJetGood/I"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( njets_mc )
    
    
    metBinning = [0,20,40,60,80] if args.selection.count('metInv') else [80,130,180,230,280,320,420,520,800] if args.selection.count('met80') else [0,80,130,180,230,280,320,420,520,800]
    if args.variation == 'central':
        met_data = Plot( 
            name        = "met_data",
            texX        = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 50 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = Binning.fromThresholds( metBinning ),
            stack       = stack_data, 
            attribute   = TreeVariable.fromString( "met_pt/F" ),
            weight      = data_weight,
            )
        plots.append( met_data )
  
    met_mc  = Plot(\
        name            = "met_pt_mc",
        texX            = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 50 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = Binning.fromThresholds( metBinning ),
        stack           = stack_mc,
        attribute       = TreeVariable.fromString( selectionModifier("met_pt/F") )      if selectionModifier is not None else None,
        selectionString = selectionModifier( cutInterpreter.cutString(args.selection) ) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( met_mc )
    

    metBinning2 = [0,20,40,60,80] if args.selection.count('metInv') else [80,100,120,140,160,200,500] if args.selection.count('met80') else [0,80,100,120,140,160,200,500]
    if args.variation == 'central':
        met2_data   = Plot(
            name        = "met2_data",
            texX        = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = Binning.fromThresholds(metBinning2),
            stack       = stack_data,
            attribute   = TreeVariable.fromString( "met_pt/F" ),
            weight      = data_weight )
        plots.append( met2_data )

    met2_mc  = Plot(\
        name            = "met2_mc",
        texX            = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
        binning         = Binning.fromThresholds(metBinning2),
        stack           = stack_mc,
        attribute       = TreeVariable.fromString( selectionModifier("met_pt/F"))   if selectionModifier is not None else None,
        selectionString = selectionModifier(cutInterpreter.cutString(args.selection)) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( met2_mc )


    metSigBinning = [0,2,4,6,8,10,12] if args.selection.count('POGMetSig0To12') else [12,16,20,24,28,32,36,40,45,50,55,60,65,70,75,80,85,90,95,100] if args.selection.count('POGMetSig12') else [0,4,8,12,16,20,24,28,32,36,40,45,50,55,60,65,70,75,80,85,90,95,100]
    if args.variation == 'central': 
        metSig_data  = Plot( 
            name        = "MET_significance_data",
            texX        = 'E_{T}^{miss} significance (GeV)', texY = 'Number of Events / 5 GeV' if args.normalizeBinWidth else "Number of Events",
            binning     = Binning.fromThresholds( metSigBinning ),
            stack       = stack_data, 
            attribute   = TreeVariable.fromString( "MET_significance/F" ),
            weight      = data_weight,
            )
        plots.append( metSig_data )
    
    metSig_mc  = Plot(\
        name = "MET_significance_mc",
        texX = 'E_{T}^{miss} significance (GeV)', texY = 'Number of Events / 5 GeV' if args.normalizeBinWidth else "Number of Events",
        stack = stack_mc,
        attribute = TreeVariable.fromString( selectionModifier("MET_significance/F") )  if selectionModifier is not None else None,
        binning=Binning.fromThresholds( metSigBinning ),
        selectionString = selectionModifier( cutInterpreter.cutString(args.selection) ) if selectionModifier is not None else None,
        weight          = mc_weight )
    plots.append( metSig_mc )

    ## Make plot directory
    #plot_directory_ = os.path.join(plot_directory, 'systematicPlots', args.plot_directory, args.selection, args.era, mode)
    #try: 
    #    os.makedirs(plot_directory_)
    #except: 
    #    pass

    if args.variation is not None:
        key  = (args.era, mode, args.variation)

        database_complete = False
        if dirDB.contains(key) and not args.overwrite:
            #normalisation_mc, normalisation_data, histos = dirDB.get( key )
            histos = dirDB.get( key )
            for i_p, h_s in enumerate(histos):
                plots[i_p].histos = h_s
            logger.info( "Loaded normalisations and histograms for %s in mode %s from cache.", args.era, mode)
            logger.debug("Loaded normalisation_mc: %r normalisation_data: %r", normalisation_mc, normalisation_data )
            if normalisation_mc['Top_pow']<=0:
                database_complete = False
                logger.info( "!!! Top_pow histo is zero !!!" )
            else: 
                database_complete = True
        if not database_complete:
            logger.info( "Obtain normalisations and histograms for %s in mode %s.", args.era, mode)
            # Calculate the normalisation yield for mt2ll<100
            normalization_selection_string = selectionModifier(cutInterpreter.cutString(args.selection + '-mt2llTo100'))
            mc_normalization_weight_string    = MC_WEIGHT(variations[args.variation], returntype='string')
            normalisation_mc = {s.name :s.scale*s.getYieldFromDraw(selectionString = normalization_selection_string, weightString = mc_normalization_weight_string)['val'] for s in mc}
            #print normalization_selection_string, mc_normalization_weight_string

            if args.variation == 'central':
                normalisation_data = data_sample.scale*data_sample.getYieldFromDraw( selectionString = normalization_selection_string, weightString = data_weight_string)['val']
            else:
                normalisation_data = -1

            logger.info( "Making plots.")
            plotting.fill(plots, read_variables = read_variables, sequence = sequence)

            # Delete lambda because we can't serialize it
            for plot in plots:
                del plot.weight

            # save
            #print "normalisation_mc %f"%(normalisation_mc)
            #dirDB.add( key, (normalisation_mc, normalisation_data, [plot.histos for plot in plots]), overwrite = args.overwrite)
            dirDB.add( key, ([plot.histos for plot in plots]), overwrite = args.overwrite)

            logger.info( "Done with %s in channel %s.", args.variation, mode)

if args.variation is not None:
    logger.info( "Done with modes %s and variation %s of selection %s. Quit now.", ",".join( modes ), args.variation, args.selection )
    sys.exit(0)

# Systematic pairs:( 'name', 'up', 'down' )
systematics = [\
    {'name':'JEC',         'pair':('jesTotalUp', 'jesTotalDown')},
    {'name':'Unclustered', 'pair':('unclustEnUp', 'unclustEnDown')},
    {'name':'PU',          'pair':('PUUp', 'PUDown')},
    {'name':'BTag_b',      'pair':('BTag_SF_b_Down', 'BTag_SF_b_Up' )},
    {'name':'BTag_l',      'pair':('BTag_SF_l_Down', 'BTag_SF_l_Up')},
#    {'name':'trigger',     'pair':('DilepTriggerDown', 'DilepTriggerUp')},
    {'name':'leptonSF',    'pair':('LeptonSFDown', 'LeptonSFUp')},
    #{'name': 'TopPt',     'pair':(  'TopPt', 'central')},
    {'name': 'JER',        'pair':('jerUp', 'jerDown')},
    {'name': 'L1Prefire',  'pair':('L1PrefireUp', 'L1PrefireDown')},
]

# loop over modes
missing_cmds   = []
variation_data = {}
for mode in modes:
    logger.info('Working on mode: %s', mode)
    logger.info('Now attempting to load all variations from dirDB %s', dirDB.directory)
   
    for variation in variations.keys():
        key  = (args.era, mode, variation)
        database_complete = False
        if dirDB.contains(key) and not args.overwrite:
            #normalisation_mc, normalisation_data, histos = dirDB.get(key)
            histos = dirDB.get(key)
            #variation_data[(mode, variation)] = {'histos':histos, 'normalisation_mc':normalisation_mc, 'normalisation_data':normalisation_data}
            variation_data[(mode, variation)] = {'histos':histos}
            logger.info( "Loaded normalisations and histograms for variation %s, era %s in mode %s from cache.", variation, args.era, mode)
            database_complete = True
 
        if not database_complete:
            # prepare sub variation command
            cmd = ['python', 'sysiso.py']
            if args.dpm: cmd.append('--dpm')
            cmd.append('--logLevel=%s'%args.logLevel)
            if args.signal is not None: cmd.append( '--signal=%s'%args.signal )
            cmd.append('--era=%s'%args.era)
            cmd.append('--plot_directory=%s'%args.plot_directory)
            cmd.append('--reweightPU=%s'%args.reweightPU)
            cmd.append('--selection=%s'%args.selection)
            cmd.append('--mode=%s'%args.mode)
            cmd.append('--variation=%s'%variation)
            if args.normalizeBinWidth: cmd.append('--normalizeBinWidth')
            if args.noDYHT: cmd.append('--noDYHT')
            if args.overwrite: cmd.append('--overwrite')
            if args.small: cmd.append('--small')

            cmd_string = ' '.join( cmd )
            missing_cmds.append( cmd_string )
            logger.info("Missing variation %s, era %s in mode %s in cache. Need to run: \n%s", variation, args.era, mode, cmd_string)

# write missing cmds
filename = 'missing.sh'
if os.path.exists(filename) and args.appendCmds:
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not
missing_cmds = list(set(missing_cmds))
if len(missing_cmds)>0:
    with file( filename, append_write ) as f:
        # if we start the file:
        if append_write == 'w':
            f.write("#!/bin/sh\n")
        for cmd in missing_cmds:
            f.write( cmd + '\n')
    logger.info( "Written %i variation commands to ./missing.sh. Now I quit!", len(missing_cmds) )
    sys.exit(0)
    
# make 'all' and 'SF' from ee/mumu/mue
new_modes = []
all_modes = list(modes)
#if 'mumu' in modes and 'ee' in modes:
#    new_modes.append( ('SF', ('mumu', 'ee')) )
#    all_modes.append( 'SF' )
if 'mumu' in modes and 'ee' in modes and 'mue' in modes and 'emu' in modes:
    new_modes.append( ('all', ('mumu', 'mue', 'emu', 'ee')) )
    all_modes.append( 'all' )
for variation in variations:
    for new_mode, old_modes in new_modes:
        new_key = ( new_mode, variation )
        variation_data[new_key] = {}
#        # Adding up data_normalisation 
#        if variation == 'central':
#            variation_data[new_key]['normalisation_data'] = sum( variation_data[( old_mode, variation )]['normalisation_data'] for old_mode in old_modes )
#        else:
#            variation_data[new_key]['normalisation_data'] = -1 
#
#        # Adding up mc normalisation
#        sample_keys = variation_data[( old_modes[0], variation )]['normalisation_mc'].keys()
#        variation_data[new_key]['normalisation_mc'] = {}
#        for sample_key in sample_keys: 
#            variation_data[new_key]['normalisation_mc'][sample_key] = variation_data[( old_modes[0], variation )]['normalisation_mc'][sample_key]
#            for mode in old_modes[1:]:
#                variation_data[new_key]['normalisation_mc'][sample_key] += variation_data[( mode, variation )]['normalisation_mc'][sample_key]

        # Adding up histos (clone old_modes[0] at 3rd level, then add)
        variation_data[new_key]['histos'] = [[[ h.Clone() for h in hs ] for hs in plot_histos ] for plot_histos in variation_data[( old_modes[0], variation )]['histos']]
        for mode in old_modes[1:]:
            for i_plot_histos, plot_histos in  enumerate(variation_data[( mode, variation )]['histos']):
                for i_hs, hs in enumerate(plot_histos):
                    for i_h, h in enumerate(hs):
                        variation_data[new_key]['histos'][i_plot_histos][i_hs][i_h].Add(h)
                    
#from RootTools.plot.Plot import addOverFlowBin1D
#for p in plots:
#  p.histos = allPlots[p.name]
#  for s in p.histos:
#    for h in s:
#      addOverFlowBin1D(h, "upper")
#      if h.Integral()==0: logger.warning( "Found empty histogram %s in results file %s", h.GetName(), result_file )


# SF for top central such that we get area normalisation 
dataMC_SF = {}
for mode in all_modes:
    # All SF to 1
    dataMC_SF[mode] = {variation:{s.name:1 for s in mc} for variation in variations} 
#    yield_data = variation_data[(mode,'central')]['normalisation_data'] 
#    if args.scaling == 'top': 
#        # scale variations individually
#        if args.variation_scaling:
#            logger.info( "Scaling top yield to data for mt2ll<100 individually for all variations." )
#            for variation in variations.keys():
#                #print ""%()
#                yield_non_top = sum( val for name, val in variation_data[(mode,variation)]['normalisation_mc'].iteritems() if name != Top_pow.name)
#                yield_top     = variation_data[(mode,variation)]['normalisation_mc'][Top_pow.name]
#                #print "mode %s yield_data %f yield_non_top %f yield_top %f"%(mode, yield_data, yield_non_top, yield_top)
#                dataMC_SF[mode][variation][Top_pow.name] = (yield_data - yield_non_top)/yield_top
#                #if mode=='mumu' and variation=='central': assert False, ''
#        # scale all variations with the central factor
#        else:
#            logger.info( "Scaling top yield to data for mt2ll<100 ( all variations are scaled by central SF)" )
#            yield_non_top = sum( val for name, val in variation_data[(mode,'central')]['normalisation_mc'].iteritems() if name != Top_pow.name)
#            yield_top     = variation_data[(mode,'central')]['normalisation_mc'][Top_pow.name]
#            sf = (yield_data - yield_non_top)/yield_top
#            for variation in variations.keys():
#                dataMC_SF[mode][variation][Top_pow.name] = sf 
#    elif args.scaling == 'mc':
#        # scale variations individually
#        if args.variation_scaling:
#            logger.info( "Scaling MC yield to data for mt2ll<100 individually for all variations." )
#            for variation in variations.keys():
#                yield_mc = sum( val for name, val in variation_data[(mode,variation)]['normalisation_mc'].iteritems())
#                for s in mc:
#                    dataMC_SF[mode][variation][s.name] = yield_data/yield_mc
#        # scale all variations with the central factor
#        else:
#            logger.info( "Scaling MC yield to data for mt2ll<100 ( all variations are scaled by central SF)" )
#            yield_mc = sum( val for name, val in variation_data[(mode,'central')]['normalisation_mc'].iteritems())
#            sf = yield_data/yield_mc
#            for variation in variations.keys():
#                for s in mc:
#                    dataMC_SF[mode][variation][s.name] = sf 

def drawObjects( scaling, scaleFactor ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) SF=%3.2f'% ( lumi_scale, scaleFactor ) ) if scaling == 'mc' else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) SF(top)=%3.2f'% ( lumi_scale, scaleFactor ) ) if scaling == 'top' else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% ( lumi_scale) ),
      ]
    return [tex.DrawLatex(*l) for l in lines]

# We plot now. 
if args.normalize: plot_subdirectory += "_normalized"
if args.beta: plot_subdirectory += "_%s"%args.beta
for mode in all_modes:
    for i_plot, plot in enumerate(plots):
        
        # for central (=no variation), we store plot_data_1, plot_mc_1, plot_data_2, plot_mc_2, ...
        data_histo_list = variation_data[(mode, 'central')]['histos'][2*i_plot]
        mc_histo_list   = {'central': variation_data[(mode, 'central')]['histos'][2*i_plot+1] }
        # for the other variations, there is no data
        for variation in variations.keys():
            if variation=='central': continue
            mc_histo_list[variation] = variation_data[(mode, variation)]['histos'][i_plot]

        # copy styles and tex
        data_histo_list[0][0].style = data_sample.style
        data_histo_list[0][0].legendText = data_sample.texName
        for i_mc_hm, mc_h in enumerate( mc_histo_list['central'][0] ):
            mc_h.style = stack_mc[0][i_mc_hm].style
            mc_h.legendText = stack_mc[0][i_mc_hm].texName

        # perform the scaling
        for variation in variations.keys():
            for s in mc:
                mc_histo_list[variation][0][position[s.name]].Scale( dataMC_SF[mode][variation][s.name] ) 

        # Add histos, del the stack (which refers to MC only )
        plot.histos =  mc_histo_list['central'] + data_histo_list
        plot.stack  = Stack(  mc, [data_sample]) 
        
        # Make boxes and ratio boxes
        boxes           = []
        ratio_boxes     = []
        # Compute all variied MC sums
        total_mc_histo   = {variation:add_histos( mc_histo_list[variation][0]) for variation in variations.keys() }

        # loop over bins & compute shaded uncertainty boxes
        boxes   = []
        r_boxes = []
        for i_b in range(1, 1 + total_mc_histo['central'].GetNbinsX() ):
            # Only positive yields
            total_central_mc_yield = total_mc_histo['central'].GetBinContent(i_b)
            if total_central_mc_yield<=0: continue
            variance = 0.
            for systematic in systematics:
                # Use 'central-variation' (factor 1) and 0.5*(varUp-varDown)
                if 'central' in systematic['pair']: 
                    factor = 1
                else:
                    factor = 0.5
                # sum in quadrature
                variance += ( factor*(total_mc_histo[systematic['pair'][0]].GetBinContent(i_b) - total_mc_histo[systematic['pair'][1]].GetBinContent(i_b)) )**2

            sigma     = sqrt(variance)
            sigma_rel = sigma/total_central_mc_yield 

            box = ROOT.TBox( 
                    total_mc_histo['central'].GetXaxis().GetBinLowEdge(i_b),
                    max([0.03, (1-sigma_rel)*total_central_mc_yield]),
                    total_mc_histo['central'].GetXaxis().GetBinUpEdge(i_b), 
                    max([0.03, (1+sigma_rel)*total_central_mc_yield]) )
            box.SetLineColor(ROOT.kBlack)
            box.SetFillStyle(3444)
            box.SetFillColor(ROOT.kBlack)
            boxes.append(box)

            r_box = ROOT.TBox( 
                total_mc_histo['central'].GetXaxis().GetBinLowEdge(i_b),  
                max(0.1, 1-sigma_rel), 
                total_mc_histo['central'].GetXaxis().GetBinUpEdge(i_b), 
                min(1.9, 1+sigma_rel) )
            r_box.SetLineColor(ROOT.kBlack)
            r_box.SetFillStyle(3444)
            r_box.SetFillColor(ROOT.kBlack)
            ratio_boxes.append(r_box)

        for log in [False, True]:
            #if args.beta is None:
            plot_directory_ = os.path.join(plot_directory, 'systematicPlots', args.era, plot_subdirectory, args.selection, mode + ("_log" if log else ""))
            #else:
            #    plot_directory_ = os.path.join(plot_directory, 'systematicPlots', args.era, plot_subdirectory, args.selection, args.beta, mode + ("_log" if log else ""))
            #if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
            texMode = "#mu#mu" if mode == "mumu" else "#mue" if mode == "mue" else "e#mu" if mode =="emu" else mode
            if    mode == "all": plot.histos[1][0].legendText = "data (%s)"%args.era
            else:                plot.histos[1][0].legendText = "data (%s, %s)"%(args.era, texMode)

            _drawObjects = []

            plotting.draw(plot,
              plot_directory = plot_directory_,
              ratio = {'yRange':(0.1,1.9), 'drawObjects':ratio_boxes},
              logX = False, logY = log, sorting = True,
              yRange = (0.03, "auto") if log else (0.001, "auto"),
              scaling = {0:1} if args.normalize else {},
              legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
              drawObjects = drawObjects( args.scaling, dataMC_SF[mode]['central'][Top_pow.name] ) + boxes,
              copyIndexPHP = True, extensions = ["png", "pdf"],
            )         
