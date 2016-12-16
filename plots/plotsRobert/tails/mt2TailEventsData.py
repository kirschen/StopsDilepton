# Standard imports
import ROOT
from math import sqrt, sin, cos, atan2
import operator
import os

#StopsDilepton
from StopsDilepton.tools.helpers import getObjDict, getEList, getVarValue, deltaR, getCollection, bestDRMatchInCollection
from StopsDilepton.tools.objectSelection import getGenPartsAll, getGoodLeptons, getGoodJets, jetVars, getLeptons, default_muon_selector, default_ele_selector, getJets, leptonVars, jetVars, getGoodTaus, getGoodAndOtherLeptons, muonSelector, eleSelector
# Calculate MT2
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()

import StopsDilepton.tools.user as user

#RootTools
from RootTools.core.standard import *

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")

argParser.add_argument('--logLevel',
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

argParser.add_argument('--mode',
    default='muEle',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle'])

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

lumiScale = 10.

maxN  = -1
evtNr = -1
#evtNr = 19956300 # event 9, e matched to gamma
#evtNr = 55481323 # event 24, tautoE 205 GeV extra neutrino

data_directory = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
postProcessing_directory = "postProcessed_Fall15_v3/dilep/" 
from StopsDilepton.samples.helpers import fromHeppySample

if args.mode=="doubleMu":
    sample     = Sample.fromDirectory(name="DoubleMuon_Run2015D",     treeName="Events", texName="DoubleMuon (Run2015D)",     directory=os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/dilep/DoubleMuon_Run2015D_16Dec') )
    cmg_sample = fromHeppySample("DoubleMuon_Run2015D_16Dec", data_path ="/scratch/rschoefbeck/cmgTuples/763/", maxN = -1)
    SFZCut = "( isMuMu==1&&abs(dl_mass-91.2)>=15 )"
elif args.mode=="doubleEle":
    sample     = Sample.fromDirectory(name="DoubleEG_Run2015D",     treeName="Events", texName="DoubleEG (Run2015D)",     directory=os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/dilep/DoubleEG_Run2015D_16Dec') )
    cmg_sample = fromHeppySample("DoubleEG_Run2015D_16Dec", data_path ="/scratch/rschoefbeck/cmgTuples/763/", maxN = -1)
    SFZCut = "( isEE==1&&abs(dl_mass-91.2)>=15 )"
elif args.mode=="muEle":
    sample     = Sample.fromDirectory(name="MuonEG_Run2015D",     treeName="Events", texName="MuonEG (Run2015D)",     directory=os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/dilep/MuonEG_Run2015D_16Dec') )
    cmg_sample = fromHeppySample("MuonEG_Run2015D_16Dec", data_path ="/scratch/rschoefbeck/cmgTuples/763/", maxN = -1)
    SFZCut = "( isEMu==1 )"

def bold(s):
    return '\033[1m'+s+'\033[0m'

def vecPtSum(objs, subtract=[]):
    px = sum([o['pt']*cos(o['phi']) for o in objs])
    py = sum([o['pt']*sin(o['phi']) for o in objs])
    px -= sum([o['pt']*cos(o['phi']) for o in subtract])
    py -= sum([o['pt']*sin(o['phi']) for o in subtract])
    return sqrt(px**2+py**2)

def uniqueListOfDicts( L ):
    return list({v['pt']:v for v in L}.values())

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))

cuts=[
  ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
  # ("filterCut", "Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter" ),
  ("filterCut", "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)" ),
  ("njet2", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  ("nbtag1", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("mll20", "dl_mass>20"),
  ("met80", "met_pt>80"),
  ("metSig5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
  ("isOS","isOS==1"),
  ("SFZVeto", SFZCut),
  #("tauVeto","Sum$(TauGood_pt>20 && abs(TauGood_eta)<2.4 && TauGood_idDecayModeNewDMs>=1 && TauGood_idCI3hit>=1 && TauGood_idAntiMu>=1 && TauGood_idAntiE>=1)==0"),
  ("multiIsoWP", multiIsoWP),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ]
if evtNr>0:
    cuts = [("evt", "evt=="+str(evtNr))] + cuts

#prefix+="_tauVeto_mRelIso01_looseLepVeto"
selection = "&&".join([c[1] for c in cuts])
tail_selection = "dl_mt2ll>100"

jetVars = ['pt/F', 'rawPt/F', 'eta/F', 'phi/F', 'id/I', 'btagCSV/F']

common_variables= [\
    TreeVariable.fromString('met_pt/F'), TreeVariable.fromString( 'met_phi/F' ),
    TreeVariable.fromString( 'nLepGood/I' ),

]
common_variables.extend( map( TreeVariable.fromString, [ 'run/I', 'lumi/I', 'evt/l' ] ) )

cmg_variables = [\
    TreeVariable.fromString( 'nJet/I' ),
    VectorTreeVariable.fromString('Jet[pt/F,eta/F,phi/F,btagCSV/F,id/I,muEF/F,eEF/F]'),
    TreeVariable.fromString( 'nLepOther/I' ),
    #VectorTreeVariable.fromString('LepOther[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,lostHits/I,dEtaScTrkIn/F,dPhiScTrkIn/F]'),
    #VectorTreeVariable.fromString('LepGood[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,lostHits/I,dEtaScTrkIn/F,dPhiScTrkIn/F]'),
    VectorTreeVariable.fromString('LepGood[chargedHadRelIso03/F,chargedHadRelIso04/F,softMuonId/I,pfMuonId/I,eleCutId2012_full5x5/I,trackerLayers/I,pixelLayers/I,trackerHits/I,lostOuterHits/I,innerTrackValidHitFraction/F,innerTrackChi2/F,nStations/F,caloCompatibility/F,globalTrackChi2/F,trkKink/F,segmentCompatibility/F,chi2LocalPosition/F,chi2LocalMomentum/F,glbTrackProbability/F,sigmaIEtaIEta/F,dEtaScTrkIn/F,dPhiScTrkIn/F,hadronicOverEm/F,eInvMinusPInv/F,eInvMinusPInv_tkMom/F,etaSc/F,charge/I,tightId/I,eleCutIdSpring15_25ns_v1/I,dxy/F,dz/F,edxy/F,edz/F,ip3d/F,sip3d/F,convVeto/I,lostHits/I,relIso03/F,relIso04/F,miniRelIso/F,relIsoAn04/F,tightCharge/I,mediumMuonId/I,pdgId/I,pt/F,eta/F,phi/F,mass/F,mvaIdSpring15/F,mvaTTH/F,jetPtRatiov2/F,jetPtRelv2/F,jetBTagCSV/F,jetDR/F]'),
    VectorTreeVariable.fromString('LepOther[chargedHadRelIso03/F,chargedHadRelIso04/F,softMuonId/I,pfMuonId/I,eleCutId2012_full5x5/I,trackerLayers/I,pixelLayers/I,trackerHits/I,lostOuterHits/I,innerTrackValidHitFraction/F,innerTrackChi2/F,nStations/F,caloCompatibility/F,globalTrackChi2/F,trkKink/F,segmentCompatibility/F,chi2LocalPosition/F,chi2LocalMomentum/F,glbTrackProbability/F,sigmaIEtaIEta/F,dEtaScTrkIn/F,dPhiScTrkIn/F,hadronicOverEm/F,eInvMinusPInv/F,eInvMinusPInv_tkMom/F,etaSc/F,charge/I,tightId/I,eleCutIdSpring15_25ns_v1/I,dxy/F,dz/F,edxy/F,edz/F,ip3d/F,sip3d/F,convVeto/I,lostHits/I,relIso03/F,relIso04/F,miniRelIso/F,relIsoAn04/F,tightCharge/I,mediumMuonId/I,pdgId/I,pt/F,eta/F,phi/F,mass/F,mvaIdSpring15/F,mvaTTH/F,jetPtRatiov2/F,jetPtRelv2/F,jetBTagCSV/F,jetDR/F]'),
]

def printLepton( event, index ):
    print "pdgId ", event.LepGood_pdgId[index],
    print "pt ", event.LepGood_pt[index],
    print "eta ", event.LepGood_eta[index],
    print "phi ", event.LepGood_phi[index],
    print "charge ", event.LepGood_charge[index],
    print "tightCharge ", event.LepGood_tightCharge[index],
    print "mass ", event.LepGood_mass[index]

    print "softMuonId ", event.LepGood_softMuonId[index],
    print "pfMuonId ", event.LepGood_pfMuonId[index],
    print "eleCutId2012_full5x5 ", event.LepGood_eleCutId2012_full5x5[index],
    print "tightId ", event.LepGood_tightId[index],
    print "mediumMuonId ", event.LepGood_mediumMuonId[index],
    print "mvaIdSpring15 ", event.LepGood_mvaIdSpring15[index],
    print "mvaTTH ", event.LepGood_mvaTTH[index],
    print "eleCutIdSpring15_25ns_v1 ", event.LepGood_eleCutIdSpring15_25ns_v1[index]

    print "chargedHadRelIso03 ", event.LepGood_chargedHadRelIso03[index],
    print "chargedHadRelIso04 ", event.LepGood_chargedHadRelIso04[index],
    print "relIso03 ", event.LepGood_relIso03[index],
    print "relIso04 ", event.LepGood_relIso04[index],
    print "miniRelIso ", event.LepGood_miniRelIso[index],
    print "relIsoAn04 ", event.LepGood_relIsoAn04[index],
    print "jetPtRatiov2 ", event.LepGood_jetPtRatiov2[index],
    print "jetPtRelv2 ", event.LepGood_jetPtRelv2[index],
    print "jetBTagCSV ", event.LepGood_jetBTagCSV[index],
    print "jetDR ", event.LepGood_jetDR[index]

    print "trackerLayers ", event.LepGood_trackerLayers[index],
    print "pixelLayers ", event.LepGood_pixelLayers[index],
    print "trackerHits ", event.LepGood_trackerHits[index],
    print "lostOuterHits ", event.LepGood_lostOuterHits[index],
    print "innerTrackValidHitFraction ", event.LepGood_innerTrackValidHitFraction[index],
    print "innerTrackChi2 ", event.LepGood_innerTrackChi2[index],
    print "nStations ", event.LepGood_nStations[index],
    print "caloCompatibility ", event.LepGood_caloCompatibility[index],
    print "globalTrackChi2 ", event.LepGood_globalTrackChi2[index],
    print "trkKink ", event.LepGood_trkKink[index],
    print "segmentCompatibility ", event.LepGood_segmentCompatibility[index],
    print "chi2LocalPosition ", event.LepGood_chi2LocalPosition[index],
    print "chi2LocalMomentum ", event.LepGood_chi2LocalMomentum[index],
    print "glbTrackProbability ", event.LepGood_glbTrackProbability[index],
    print "sigmaIEtaIEta ", event.LepGood_sigmaIEtaIEta[index],
    print "dEtaScTrkIn ", event.LepGood_dEtaScTrkIn[index],
    print "dPhiScTrkIn ", event.LepGood_dPhiScTrkIn[index],
    print "hadronicOverEm ", event.LepGood_hadronicOverEm[index],
    print "eInvMinusPInv ", event.LepGood_eInvMinusPInv[index],
    print "tkMom ", event.LepGood_eInvMinusPInv_tkMom[index],
    print "etaSc ", event.LepGood_etaSc[index]

    print "dxy ", event.LepGood_dxy[index],
    print "dz ", event.LepGood_dz[index],
    print "edxy ", event.LepGood_edxy[index],
    print "edz ", event.LepGood_edz[index],
    print "ip3d ", event.LepGood_ip3d[index],
    print "sip3d ", event.LepGood_sip3d[index],
    print "lostHits ", event.LepGood_lostHits[index],
    print "convVeto ", event.LepGood_convVeto[index]

postProcessed_variables = [\
    TreeVariable.fromString('weight/F'),

    TreeVariable.fromString( 'nJetGood/I' ),
    VectorTreeVariable.fromString( 'JetGood[%s]' % ( ','.join(jetVars) ) ),
]


postProcessed_variables.extend( map( TreeVariable.fromString, [\
    'l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_pdgId/I', 'l1_index/I', 'l1_jetPtRelv2/F', 'l1_jetPtRatiov2/F', 'l1_miniRelIso/F', 'l1_dxy/F', 'l1_dz/F',
    'l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_pdgId/I', 'l2_index/I', 'l2_jetPtRelv2/F', 'l2_jetPtRatiov2/F', 'l2_miniRelIso/F', 'l2_dxy/F', 'l2_dz/F',
    'isEE/I', 'isMuMu/I', 'isEMu/I', 'isOS/I',
    'dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_mass/F',
    'dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F'
    ] ) )
postProcessed_variables.extend( [
    VectorTreeVariable.fromString('LepGood[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,lostHits/I,dEtaScTrkIn/F,dPhiScTrkIn/F]'),
    ] )

mu_selector = muonSelector( iso = 999., dxy = 1., dz = 0.1 )
ele_selector = eleSelector( iso = 999., dxy = 1., dz = 0.1 )


logger.info( "Analyzing sample %s",  sample.name )
logger.info( "Selection: %s", selection)
logger.info( "Tail selection: %s", tail_selection)

sample.setSelectionString( "&&".join( [ selection, tail_selection] ) )

# Define a reader
reader = sample.treeReader( \
    variables = common_variables + postProcessed_variables,
    #selectionString =
    )

reader.activateAllBranches()
event_list = sample.getEventList( sample.selectionString )
reader.setEventList( event_list )

logger.info( "Found %i events in sample %s", event_list.GetN(), sample.name )

positions = {}
reader.start()
while reader.run():
    positions[( reader.event.run, reader.event.lumi, reader.event.evt )] = reader.position - 1

selected_events = "||".join([ "run==%i&&lumi==%i&&evt==%i" % e for e in positions.keys() ] )
logger.info( "Constructing event selection: %s", selected_events )

cmg_reader = cmg_sample.treeReader( \
    variables = common_variables + cmg_variables,
    #selectionString =
    )

cmg_reader.activateAllBranches()
logger.info( "Now get event list in cmg sample.")
cmg_event_list =  cmg_sample.getEventList( selected_events )
logger.info( "Done.")
cmg_reader.setEventList( cmg_event_list )
cmg_positions = {}
cmg_reader.start()
while cmg_reader.run():
    cmg_positions[( cmg_reader.event.run, cmg_reader.event.lumi, cmg_reader.event.evt )] = cmg_reader.position - 1

reader.start()
cmg_reader.start()

intersec = list(set(positions.keys()).intersection(set(cmg_positions.keys())))
intersec.sort()

logger.info( "Have %i events in sample, %i events in cmg_sample and %i in common", len(positions), len(cmg_positions), len(intersec) )

reader.start()
cmg_reader.start()

for i_event, event in enumerate( intersec ):

    reader.goToPosition( positions[event] )
    cmg_reader.goToPosition( cmg_positions[event] )

    # Make sure alignement of trees is OK
    assert reader.event.met_pt == cmg_reader.event.met_pt, "Events inconsistent!"

    logger.info( "###################### Event %2i #############################" % i_event )
    logger.info( "Run %i lumi %i event %i", reader.event.run, reader.event.lumi, reader.event.evt )

    all_jets = filter(lambda j:j['id'] and j['btagCSV']< 0.460 , getJets(cmg_reader.event, jetVars = ['eta', 'pt', 'phi', 'btagCSV', 'id', 'muEF', 'eEF']) )
    max_lEF_jet = max(all_jets, key=lambda j:max([j['eEF'], j['muEF']]) )
    
    logger.info( "non-b jet with maximum lEF %3.2f %3.2f btag %3.2f", max([max_lEF_jet['eEF'], max_lEF_jet['muEF']]), max_lEF_jet['pt'], max_lEF_jet['btagCSV'])
    
    nonId_jets = filter(lambda j:j['pt']>30 and not j['id'], getJets(cmg_reader.event))
    for j in nonId_jets:
        logger.info( "Non-ID Jet found pt %3.2f eta %3.2f phi %3.2f", j['pt'], j['eta'], j['phi'] )

    # reco leptons
    all_reco_leps = getGoodAndOtherLeptons(cmg_reader.event, ptCut=10, mu_selector = mu_selector, ele_selector = ele_selector)

    loose_mu = filter(lambda l:abs(l['pdgId'])==13 and default_muon_selector(l), all_reco_leps )
    loose_e  = filter(lambda l:abs(l['pdgId'])==11 and default_ele_selector(l), all_reco_leps )

    extra_mu = filter(lambda l:abs(l['pdgId'])==13 and not default_muon_selector(l), all_reco_leps )
    extra_e  = filter(lambda l:abs(l['pdgId'])==11 and not default_ele_selector(l), all_reco_leps )

    reco_mode = "unknown"
    if reader.event.isMuMu:
        reco_mode = "MuMu"
    if reader.event.isEE:
        reco_mode = "EE"
    if reader.event.isEMu:
        reco_mode = "EMu"

    logger.info( "reco'd as %s isOS %i, loose_mu %i, loose_e %i", bold(reco_mode), reader.event.isOS, len(loose_mu), len(loose_e) )
    logger.info( "extra mu %i, extra e %i", len(extra_mu), len(extra_e) )
#    l1 = {'pt':reader.event.l1_pt, 'eta':reader.event.l1_eta, 'phi':reader.event.l1_phi, 'pdgId':reader.event.l1_pdgId}
#    l2 = {'pt':reader.event.l2_pt, 'eta':reader.event.l2_eta, 'phi':reader.event.l2_phi, 'pdgId':reader.event.l2_pdgId}
    logger.info( "l1 pdgId %i pt %3.2f eta %3.2f phi %3.2f dxy %5.4f dz %5.4f", reader.event.l1_pdgId, reader.event.l1_pt, reader.event.l1_eta, reader.event.l1_phi, reader.event.LepGood_dxy[reader.event.l1_index], reader.event.LepGood_dz[reader.event.l1_index])
    logger.info( "l2 pdgId %i pt %3.2f eta %3.2f phi %3.2f dxy %5.4f dz %5.4f", reader.event.l2_pdgId, reader.event.l2_pt, reader.event.l2_eta, reader.event.l2_phi, reader.event.LepGood_dxy[reader.event.l2_index], reader.event.LepGood_dz[reader.event.l2_index])

    #printLepton( cmg_reader.event, reader.event.l1_index )
    #printLepton( cmg_reader.event, reader.event.l2_index )

    # Missing energy related
    met_pt = reader.event.met_pt
    met_phi = reader.event.met_phi



    logger.info( "--------------------------------------------------------------" )
