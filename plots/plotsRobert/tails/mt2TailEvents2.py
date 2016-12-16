# Standard imports
import ROOT
from math import sqrt, sin, cos, atan2
import operator

#StopsDilepton
from StopsDilepton.tools.helpers import getObjDict, getEList, getVarValue, deltaR, getCollection, bestDRMatchInCollection
from StopsDilepton.tools.objectSelection import getGenPartsAll, getGoodLeptons, getGoodJets, jetVars, getLeptons, default_muon_selector, default_ele_selector, getJets, leptonVars, jetVars, getGoodTaus, getGoodAndOtherLeptons, muonSelector, eleSelector
##Local Jet response
#import StopsDilepton.tools.localJetResponse 
#localJetResponse = StopsDilepton.tools.localJetResponse.localJetResponse()
# Calculate MT2
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
#MC tools
from StopsDilepton.tools.mcTools import pdgToName, GenSearch, B_mesons, D_mesons, B_mesons_abs, D_mesons_abs
genSearch = GenSearch()

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

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

lumiScale = 10.

lepPdgs = [11,13,15]
nuPdgs = [12,14,16]

dilep = True

maxN  = -1
evtNr = -1
#evtNr = 19956300 # event 9, e matched to gamma
#evtNr = 55481323 # event 24, tautoE 205 GeV extra neutrino

if dilep:
    sample = Sample.fromDirectory(name="TTJets_Lep", treeName="Events", isData=False, color=7, texName="t#bar{t} + Jets (lep)", \
                directory=['/afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v7/dilep/TTJets_DiLepton_comb/'], maxN = maxN)
else:
    pass
    #samples = [ Sample.fromDirectory(name=name, treeName="Events", isData=False, color=7, texName="t#bar{t} + Jets", \
    #            directory=['/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_Fall15_mAODv2/dilep/%s/'%name ], maxN = maxN) for name in \
    #                ["TTJets_SingleLeptonFromTbar_comb", "TTJets_SingleLeptonFromT_comb"] ]
    #sample = Sample.combine( "TTJets_singleLep", samples, maxN = maxN )

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

cuts=[\
  ("filterCut", "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadron&&Flag_badMuon" ),
  ("leptons", "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1 || ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"),
  ("mll20", "dl_mass>20"),
  ("l1pt25", "l1_pt>25"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
  ("isOS","isOS==1"),
  ("njet2", "nJetGood>=2" ),
  ("nbtag1", "nBTag>=1" ),
  ("met80", "met_pt>80" ),
  ("metSig5", "metSig>5" ),
    ]

if evtNr>0:
    cuts = [("evt", "evt=="+str(evtNr))] + cuts

#prefix+="_tauVeto_mRelIso01_looseLepVeto"
selection = "&&".join([c[1] for c in cuts])
tail_selection = "dl_mt2ll>140"

jetCorrInfo = ['corr/F', 'corr_JECUp/F', 'corr_JECDown/F']
jetMCInfo = ['mcMatchFlav/I', 'partonId/I', 'partonMotherId/I', 'mcPt/F', 'mcFlavour/I', 'hadronFlavour/I', 'mcMatchId/I']
jetVars = ['pt/F', 'rawPt/F', 'eta/F', 'phi/F', 'id/I', 'btagCSV/F'] + jetCorrInfo + jetMCInfo
genLepVars      = ['pt/F', 'phi/F', 'eta/F', 'pdgId/I', 'index/I', 'lepGoodMatchIndex/I', 'matchesPromptGoodLepton/I', 'n_t/I','n_W/I', 'n_B/I', 'n_D/I', 'n_tau/I']

common_variables= [\
    TreeVariable.fromString('met_pt/F'), TreeVariable.fromString( 'met_phi/F' ),
    TreeVariable.fromString('met_genPt/F'), TreeVariable.fromString( 'met_genPhi/F' ),
    TreeVariable.fromString('nTrueInt/F'),

    TreeVariable.fromString('ngenPartAll/I'),
    VectorTreeVariable.fromString('genPartAll[pt/F,eta/F,phi/F,pdgId/I,status/I,charge/F,motherId/I,grandmotherId/I,nMothers/I,motherIndex1/I,motherIndex2/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I]', nMax=200 ),

    TreeVariable.fromString( 'nLepGood/I' ),

]
common_variables.extend( map( TreeVariable.fromString, [ 'run/I', 'lumi/I', 'evt/l' ] ) )

cmg_variables = [\
    TreeVariable.fromString( 'nJet/I' ),
    VectorTreeVariable.fromString('Jet[pt/F,eta/F,phi/F,mcPt/F,btagCSV/F,id/I]'),
    TreeVariable.fromString( 'nLepOther/I' ),
    VectorTreeVariable.fromString('LepOther[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,lostHits/I,dEtaScTrkIn/F,dPhiScTrkIn/F,eleCutIdSpring15_25ns_v1/I]'),
    VectorTreeVariable.fromString('LepGood[pt/F,eta/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,lostHits/I,dEtaScTrkIn/F,dPhiScTrkIn/F,eleCutIdSpring15_25ns_v1/I]'),
]

postProcessed_variables = [\
    TreeVariable.fromString('weight/F'),
    TreeVariable.fromString( 'nGenLep/I' ),

    VectorTreeVariable.fromString('GenLep[%s]'% ( ','.join(genLepVars) ) ),

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

# original cmg sample
from StopsDilepton.samples.helpers import fromHeppySample
if dilep:
    cmg_samples = [ fromHeppySample(s, data_path = user.cmg_directory, maxN = -1) for s in ["TTJets_DiLepton", "TTJets_DiLepton_ext"] ]
    cmg_sample = Sample.combine("cmg_sample", cmg_samples, maxN = -1)
else:
    cmg_samples = [ fromHeppySample(s, data_path = user.cmg_directory, maxN = -1) for s in ["TTJets_SingleLeptonFromTbar", "TTJets_SingleLeptonFromT", "TTJets_SingleLeptonFromTbar_ext", "TTJets_SingleLeptonFromT_ext"] ]
    cmg_sample = Sample.combine("cmg_sample", cmg_samples, maxN = -1)

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

    # gen particles
    gPart = getGenPartsAll( reader.data )
    genSearch.init( gPart )

    # reco leptons
    mu_selector = muonSelector( iso = 999., dxy = 1., dz = 0.1 )
    ele_selector = eleSelector( iso = 999., dxy = 1., dz = 0.1 )
    all_reco_leps = getGoodAndOtherLeptons(cmg_reader.data, ptCut=10, mu_selector = mu_selector, ele_selector = ele_selector)
    #all_reco_leps = getGoodAndOtherLeptons(cmg_reader.data, ptCut=10, miniRelIso = 999. , dz = 0.1, dxy = 1.)

    # Start with generated leptons and match to reco ones
    # W decay modes
    W_decay = []
    prompt_gen_leptons = []
    for W in filter(lambda p:abs(p['pdgId'])==24 and p['daughterIndex2']>0, gPart):

        W_daughters = [gPart[W['daughterIndex1']], gPart[W['daughterIndex2']] ]
        W_daughters_pdgId = map(lambda p:abs(p['pdgId']), W_daughters)
        W_daughters_pdgId.sort()
        #prompt e
        if W_daughters_pdgId==[11,12]:
            W_decay.append( "E" )
            e = filter( lambda l:abs(l['pdgId'])==11, W_daughters )[0]
            e = genSearch.descend( e )
            e['source'] = 'fromW'
            prompt_gen_leptons.append( e )
        #prompt mu
        elif W_daughters_pdgId==[13,14]:
            W_decay.append( "Mu" )
            mu = filter( lambda l:abs(l['pdgId'])==13, W_daughters )[0]
            mu = genSearch.descend( mu )
            mu['source'] = 'fromW'
            prompt_gen_leptons.append( mu )
        #tau
        elif W_daughters_pdgId==[15,16]:
            decayMode = "Tau"
            tau = filter(lambda p:abs(p['pdgId'])==15, W_daughters)[0]
            tau = genSearch.descend( tau )
            # Search for all tau daughters
            tau_daughters = filter( lambda p: p['motherIndex1']==tau['index'], gPart )
            lepton_daughters = filter( lambda l:abs(l['pdgId']) in [11, 13], tau_daughters )
            lepton_daughters = map( genSearch.descend, lepton_daughters )
            for l in lepton_daughters:
                l['source'] = 'fromTau'
            prompt_gen_leptons.extend( lepton_daughters )
            tau_daughters_pdgId = map(lambda p:abs(p['pdgId']), tau_daughters)
            tau_daughters_pdgId.sort()
            #tau to e
            if 12 in tau_daughters_pdgId:
                decayMode+="ToE"
            #tau to mu
            elif 14 in tau_daughters_pdgId:
                decayMode+="ToMu"
            else:
                decayMode+="ToHad"
            W_decay.append( decayMode )
        elif W_daughters_pdgId in [ [1,2], [3,4] ]:
            W_decay.append( "Had" )
        else:
            W_decay.append( "Unknown_%i_%i"%W_daughters )

    W_decay.sort()
    prompt_gen_leptons.sort(key = lambda l:-l['pt'] )

    prompt_gen_mu = filter( lambda l:abs(l['pdgId']) == 13, prompt_gen_leptons )
    prompt_gen_e  = filter( lambda l:abs(l['pdgId']) == 11, prompt_gen_leptons )

    logger.info( "GenDecay: %s providing prompt gen mu: %i ele: %i" , bold("/".join(W_decay) ), len(prompt_gen_mu), len(prompt_gen_e) )
    for l in prompt_gen_leptons:
        reco_match = bestDRMatchInCollection( l, filter(lambda p:p['pdgId']==l['pdgId'], all_reco_leps ), deltaRelPt = -1 )
        delta_pt = reco_match['pt'] - l['pt'] if reco_match else float('nan')
        if reco_match is None:
            selected_lepton_match_string = ""
        elif reco_match['pt']==reader.event.l1_pt:
            selected_lepton_match_string = bold("leading")
        elif reco_match['pt']==reader.event.l2_pt:
            selected_lepton_match_string = bold("trailing")
        else:
            selected_lepton_match_string = "Not matched to l1,l2"
        logger.info( "gen prompt %s %s pt %3.2f eta %3.2f all-reco-match %s delta_pt %3.2f matched to: %s", \
            pdgToName(l['pdgId']),l['source'], l['pt'], l['eta'],
            bool(reco_match), delta_pt, selected_lepton_match_string
            )

    # Status 1 gen leptons in acceptance
    gen_leps = filter( lambda p:abs(p['pdgId']) in [11, 13] and p['status']==1, gPart )
    for gl in gen_leps:
        ancestry = [ gPart[x]['pdgId'] for x in genSearch.ancestry( gl ) ]
        gl["n_D"]   =  sum([ancestry.count(p) for p in D_mesons])
        gl["n_B"]   =  sum([ancestry.count(p) for p in B_mesons])
        gl["n_W"]   =  sum([ancestry.count(p) for p in [24, -24]])
        gl["n_t"]   =  sum([ancestry.count(p) for p in [6, -6]])
        gl["n_tau"] =  sum([ancestry.count(p) for p in [15, -15]])
        gl["ancestry"] = ancestry

    for gl in gen_leps:
        #"t->W->l"
        gl['prompt_from_W']   =  gl["n_t"]>0 and gl["n_W"]>0 and gl["n_B"] == 0 and gl["n_D"]==0 and gl["n_tau"]==0
        gl['nonprompt']       =  gl["n_B"] >0 or gl["n_D"]>0
        gl['prompt_from_tau'] =  gl["n_t"]>0 and gl["n_W"]>0 and gl["n_B"] == 0 and gl["n_D"]==0 and gl["n_tau"]>0
        gl['other'] = not (gl['prompt_from_W'] or gl['nonprompt'] or gl['prompt_from_tau'])
        for key in ['prompt_from_W', 'nonprompt', 'prompt_from_tau', 'other']:
            if gl[key]: gl['source']=key
    # Start with reco leptons and match to generated
    logger.info( "gen lep:   %i, all_reco_leps %i", len(gen_leps), len(all_reco_leps) )
    logger.info( "prompt mu  %i, non-prompt mu %i, prompt mu from tau %i, other %i", \
        len(filter( lambda l:abs(l['pdgId'])==13 and l['prompt_from_W'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==13 and l['nonprompt'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==13 and l['prompt_from_tau'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==13 and l['other'], gen_leps ))
    )
    logger.info( "prompt ele %i, non-prompt ele %i, prompt ele from tau %i, other %i", \
        len(filter( lambda l:abs(l['pdgId'])==11 and l['prompt_from_W'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==11 and l['nonprompt'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==11 and l['prompt_from_tau'], gen_leps )),
        len(filter( lambda l:abs(l['pdgId'])==11 and l['other'], gen_leps ))
    )

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
    l1 = {'pt':reader.event.l1_pt, 'eta':reader.event.l1_eta, 'phi':reader.event.l1_phi, 'pdgId':reader.event.l1_pdgId}
    l2 = {'pt':reader.event.l2_pt, 'eta':reader.event.l2_eta, 'phi':reader.event.l2_phi, 'pdgId':reader.event.l2_pdgId}

    genlep_match_l1 =   bestDRMatchInCollection( l1, filter(lambda p:p['pdgId']==l1['pdgId'], gen_leps ), deltaRelPt = -1 )
    genlep_match_l2 =   bestDRMatchInCollection( l2, filter(lambda p:p['pdgId']==l2['pdgId'], gen_leps ), deltaRelPt = -1 )

    l1_match_str = "not matched" if not genlep_match_l1 else genlep_match_l1['source']
    l2_match_str = "not matched" if not genlep_match_l2 else genlep_match_l2['source']

    delta_pt_l1 = float('nan') if not genlep_match_l1 else l1['pt'] - genlep_match_l1['pt']
    delta_pt_l2 = float('nan') if not genlep_match_l2 else l2['pt'] - genlep_match_l2['pt']

    gPart_match_l1 =   bestDRMatchInCollection( l1, filter(lambda p:p['status']==1, gPart ) )
    gPart_match_l2 =   bestDRMatchInCollection( l2, filter(lambda p:p['status']==1, gPart ) )

    l1_gPart_match_str = "not matched" if not gPart_match_l1 else 'matched to %s'%pdgToName( gPart_match_l1['pdgId'] )
    l2_gPart_match_str = "not matched" if not gPart_match_l2 else 'matched to %s'%pdgToName( gPart_match_l2['pdgId'] )

    delta_pt_gPart_l1 = float('nan') if not gPart_match_l1 else l1['pt'] - gPart_match_l1['pt']
    delta_pt_gPart_l2 = float('nan') if not gPart_match_l2 else l2['pt'] - gPart_match_l2['pt']

    logger.info( bold("leading")+"  l1 %s pt %3.2f eta %3.2f Genleps: delta_pt %3.2f %s gPart: delta_pt %3.2f %s", \
        pdgToName(l1['pdgId']), l1['pt'], l1['eta'], delta_pt_l1, bold(l1_match_str), delta_pt_gPart_l1, l1_gPart_match_str 
        )
    logger.info( bold("trailing")+"  l2 %s pt %3.2f eta %3.2f Genleps: delta_pt %3.2f %s gPart: delta_pt %3.2f %s", \
        pdgToName(l2['pdgId']), l2['pt'], l2['eta'], delta_pt_l2, bold(l2_match_str), delta_pt_gPart_l2, l2_gPart_match_str
        )

    if gPart_match_l1 and gPart_match_l1['pdgId']==22:
        logger.info( "leading lepton photon match: pt %3.2f eta %3.2f phi %3.2f lostH %i dEta %5.4f dPhi %5.4f", 
            reader.event.LepGood_pt[reader.event.l1_index],  
            reader.event.LepGood_eta[reader.event.l1_index],  
            reader.event.LepGood_phi[reader.event.l1_index],  
            reader.event.LepGood_lostHits[reader.event.l1_index],  
            reader.event.LepGood_dEtaScTrkIn[reader.event.l1_index],  
            reader.event.LepGood_dPhiScTrkIn[reader.event.l1_index],  
        )
    if gPart_match_l2 and gPart_match_l2['pdgId']==22:
        logger.info( "trailing lepton photon match: pt %3.2f eta %3.2f phi %3.2f lostH %i dEta %5.4f dPhi %5.4f", 
            reader.event.LepGood_pt[reader.event.l2_index],  
            reader.event.LepGood_eta[reader.event.l2_index],  
            reader.event.LepGood_phi[reader.event.l2_index],  
            reader.event.LepGood_lostHits[reader.event.l2_index],  
            reader.event.LepGood_dEtaScTrkIn[reader.event.l2_index],  
            reader.event.LepGood_dPhiScTrkIn[reader.event.l2_index],  
        )

    # Neutrinos
    #neutrinos = filter( lambda p: abs(p['pdgId']) in [12,14,16] and p['status']==1, gPart )

    neutrinos_fromW   =  uniqueListOfDicts( [ genSearch.descend(q) for q in filter(lambda p: abs(p['motherId']) == 24 and abs(p['pdgId']) in [12, 14, 16], gPart) ] )
    neutrinos_fromTau =  uniqueListOfDicts( [ genSearch.descend(q) for q in filter(lambda p: abs(p['motherId']) == 15 and abs(p['pdgId']) in [12, 14, 16] and \
                           24 in [ abs(gPart[x]['pdgId']) for x in genSearch.ancestry(p) ], gPart) ] ) 
    neutrinos_other   =  uniqueListOfDicts( [ genSearch.descend(q) for q in filter(lambda p: abs(p['pdgId']) in [12, 14, 16], gPart) \
                            if not genSearch.descend(q) in neutrinos_fromW + neutrinos_fromTau ] )

    str_neutrinos_fromW = "%3.2f"%   vecPtSum(neutrinos_fromW)
    str_neutrinos_fromTau = "%3.2f"% vecPtSum(neutrinos_fromTau)
    str_neutrinos_other = "%3.2f"%   vecPtSum(neutrinos_other)

    #if vecPtSum( neutrinos_fromW ) > 30: str_neutrinos_fromW = bold(str_neutrinos_fromW) 
    if vecPtSum( neutrinos_fromTau ) > 30: str_neutrinos_fromTau = bold(str_neutrinos_fromTau) 
    if vecPtSum( neutrinos_other ) > 30: str_neutrinos_other = bold(str_neutrinos_other) 

    logger.info( "MET %3.2f genMET %3.2f pt(neutrinos from W) %s pt(neutrinos from tau from W) %s pt(other neutrinos) %s", \
        reader.event.met_pt, reader.event.met_genPt, str_neutrinos_fromW, str_neutrinos_fromTau, str_neutrinos_other )

    # Missing energy related
    met_pt = reader.event.met_pt
    met_phi = reader.event.met_phi
    met_genPt = reader.event.met_genPt
    met_genPhi = reader.event.met_genPhi
    delta_met = sqrt( ( met_pt*cos(met_phi)-met_genPt*cos(met_genPhi) )**2 + ( met_pt*sin(met_phi)-met_genPt*sin(met_genPhi) )**2 )

    mt2Calc.reset()
    mt2Calc.setMet( met_pt, met_phi )
    mt2Calc.setLeptons( reader.event.l1_pt, reader.event.l1_eta, reader.event.l1_phi, reader.event.l2_pt, reader.event.l2_eta, reader.event.l2_phi )
    if not mt2Calc.mt2ll() != reader.event.dl_mt2ll:
        logger.warning( "MT2 inconsistency!" )
    mt2Calc.setMet( met_genPt, met_genPhi )
    mt2ll_genMet = mt2Calc.mt2ll()
    if mt2ll_genMet<140:
        logger.info(bold("MET mismeasurement"))

    jets = [ getObjDict(cmg_reader.data, "Jet_", ["pt","eta","phi","mcPt","id"], i) for i in range(cmg_reader.event.nJet) ] 
    dx, dy = 0., 0.
    for j in jets:
        if j['mcPt']>0:
            dx+=(j['pt']-j['mcPt'])*cos(j['phi'])
            dy+=(j['pt']-j['mcPt'])*cos(j['phi'])
        if abs(j['pt'] - j['mcPt'])>50:
            logger.info( "Mismeasured jet pt %3.2f mcPt %3.2f diff %3.2f, eta %3.2f phi %3.2f id %i", j['pt'], j['mcPt'], j['pt']-j['mcPt'], j['eta'], j['phi'], j['id'] )
        #corr_pt = localJetResponse.corrected_jet_pt(j['pt'], j['eta'], j['phi'])
        #local_mism = corr_pt - j['pt']
        #if abs(local_mism) > 30:
        #    logger.info( bold("Local jet response difference!")+" mcPt %3.2f pt %3.2f corr.Pt %3.2f diff %3.2f eta %3.2f phi %3.2f id %i", j['mcPt'], j['pt'], corr_pt, local_mism, j['eta'], j['phi'], j['id'] )
    jet_mismeas = sqrt(dx**2+dy**2)

    logger.info( "Delta MET(reco-gen) %3.2f jet-mismeas %3.2f mt2ll %3.2f mt2ll(gen_met) %3.2f", delta_met, jet_mismeas, reader.event.dl_mt2ll, mt2ll_genMet )
    logger.info( "Location of %i:%i:%i %s:", cmg_reader.event.run, cmg_reader.event.lumi, cmg_reader.event.evt, cmg_reader.sample.chain.GetCurrentFile().GetName() )
    logger.info( "--------------------------------------------------------------" )
