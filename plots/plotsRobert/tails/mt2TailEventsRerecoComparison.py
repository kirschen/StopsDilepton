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

# flat ntuples
postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import DoubleMuon_Run2016BCD_backup as flat_prompt

data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import DoubleMuon_Run2016BCD_backup as flat_rereco

read_variables = ["evt/l", "run/I", "lumi/I"]
read_variables += [ "JetGood[pt/F,eta/F,phi/F,btagCSV/F,id/I]", "nJetGood/I", "isOS/I", 'nGoodMuons/I', 'nGoodElectrons/I', 'met_phi/F']
read_variables += [ "LepGood[pt/F,eta/F,phi/F]", "met_pt/F", "met_phi/F", "l1_pt/F", "l2_pt/F", "l1_eta/F", "l2_eta/F", "l1_phi/F", "l2_phi/F", "dl_mt2ll/F", "dl_pt/F", "l1_mIsoWP/I", "l2_mIsoWP/I"]
read_variables += [ "metSig/F", "nGoodMuons/I", "nGoodElectrons/I", "nJetGood/I", "nBTag/I", "ht/F"]
read_variables += [ "isMuMu/I", "l1_pdgId/I", "l2_pdgId/I", "dl_mass/F" ]

dPhi = "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"
looseLeptonVeto = "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"

rereco_outliers = [
    (274388,1786,3134346174),
    (275310,1394,2244735321),
    (274284,45,85068029),
    (275836,537,999589926),
    (275778,35,61059415),
    (276283,607,1123841210),
    (275832,15,24881293),
    (276242,228,432326318),
    (275836,786,1409261985),
    (275918,130,226876391),
    (275890,1333,2488530389),
    (276811,812,1475357441),
    (276776,1511,2529572580),
    (276437,2022,3578336590),
    (276437,1627,2922867003),
    (276525,695,1125693285),
    (276525,2811,4731377226),
    (276582,643,1155298468),
    (276525,1949,3364898172),
    (276587,357,539332187),
]
prompt_outliers = [
    (274344,522,804746941),
    (274388,1786,3134346174),
    (275068,164,330683466),
    (275291,155,265511308),
    (275836,471,884559286),
    (276242,228,432326318),
    (275778,35,61059415),
    (276587,357,539332187),
    (276776,1511,2529572580),
    (276811,812,1475357441),
    (276437,2022,3578336590),
]

products = {
    'pfJets':{'type':'vector<pat::Jet>', 'label': ("slimmedJets")},
    'pfMet':{'type':'vector<pat::MET>','label':( "slimmedMETs" )},
    'electrons':{'type':'vector<pat::Electron>','label':( "slimmedElectrons" )},
    'muons':{'type':'vector<pat::Muon>', 'label':("slimmedMuons") },
    'pfCand':{'type':'vector<pat::PackedCandidate>', 'label': ("packedPFCandidates")},
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
#evt_break = 85068029   #0 appears. leading mu passes medium mu ID, artificial non-PF mu duplicate (sub-leading) is not the issue
#evt_break = 3134346174 #1 in both.  
#evt_break = 330683466  #2 disappears. nBTag 1->0 in rereco
#evt_break = 265511308  #3 disappears. fails dPhi(MET, jet), leading jet cos(dPhi) 0.79 -> 0.84 (we cut at 0.8)
evt_break = 2244735321 #4 spurious mu
#evt_break = 61059415   #5 in both.
# evt_break = 24881293 #6 +20 GeV in MET, just passes MT2ll. non-PF mu duplicate seems not to be the issue
#evt_break = 265511308 fails dPhi in rereco
#evt_break = 999589926 passes dPhi in rereco
#evt_break = 1125693285

#evt_break = 24881293

for i_evt, evt in enumerate(evt_common):
    # if evt not in rereco_outliers: continue

    if evt_break>0 and not evt_break in evt: continue

    r_prompt.goToPosition( p_prompt[ evt ] )
    r_rereco.goToPosition( p_rereco[ evt ] )

    print     
    print "Event %2i   %i:%i:%i"%((i_evt,) + evt )
    print "  mAOD: MET rereco %3.2f prompt %3.2f"%( r_rereco.products['pfMet'][0].pt(), r_prompt.products['pfMet'][0].pt())

    for collection in ['muons', 'electrons']:
        for name, r in [ ['prompt', r_prompt], ['rereco', r_rereco]]:
            for i in range( r.products[collection].size()):
                if  r.products[collection][i].pt()>20:
                    print "  slimmed %s %s pt %3.2f eta %3.2f phi %3.2f isPF? %i" % ( name, collection, r.products[collection][i].pt(), r.products[collection][i].eta(), r.products[collection][i].phi(),  r.products[collection][i].isPFMuon() if abs(r.products[collection][i].pdgId())==13 else -1)
                    prompt_pfCands = filter( 
                        lambda p_: deltaR({'eta':p_.eta(), 'phi':p_.phi()}, {'eta':r.products[collection][i].eta(), 'phi':r.products[collection][i].phi()})<0.3, r_prompt.products['pfCand'])
                    for p in prompt_pfCands:
                        print "    prompt pfCand %i, pt/eta/phi %3.2f/%3.2f/%3.2f"%( p.pdgId(), p.pt(), p.eta(), p.phi())
                    rereco_pfCands = filter( 
                        lambda p_: deltaR({'eta':p_.eta(), 'phi':p_.phi()}, {'eta':r.products[collection][i].eta(), 'phi':r.products[collection][i].phi()})<0.3, r_rereco.products['pfCand'])
                    for p in rereco_pfCands:
                        print "    rereco pfCand %i, pt/eta/phi %3.2f/%3.2f/%3.2f"%( p.pdgId(), p.pt(), p.eta(), p.phi())
                    if abs( sum(p.pt() for p in rereco_pfCands) - sum(p.pt() for p in prompt_pfCands) ) > 10.:
                        print "    MISMATCH sumPt rereco - prompt %3.2f" % (sum(p.pt() for p in rereco_pfCands) - sum(p.pt() for p in prompt_pfCands) )

    evt_str = "%i:%i:%i"%evt
    if evt in prompt_outliers: 
        print "    in prompt!"
    else:
        print "NOT in prompt!"
    if evt in rereco_outliers: 
        print "    in rereco!"
    else:
        print "NOT in rereco!"

    delta_met_mu = sqrt( \
             ( sum([j.pt()*cos(j.phi()) for j in r_prompt.products['pfCand'] if abs(j.pdgId())==13 ], 0) 
               - sum([j.pt()*cos(j.phi()) for j in r_rereco.products['pfCand'] if abs(j.pdgId())==13 ], 0))**2 + 
             ( sum([j.pt()*sin(j.phi()) for j in r_prompt.products['pfCand'] if abs(j.pdgId())==13 ], 0) 
               - sum([j.pt()*sin(j.phi()) for j in r_rereco.products['pfCand'] if abs(j.pdgId())==13 ], 0))**2 ) 
    delta_mht = sqrt( \
             ( sum([j.pt()*cos(j.phi()) for j in r_prompt.products['pfJets']  ], 0) 
               - sum([j.pt()*cos(j.phi()) for j in r_rereco.products['pfJets'] ], 0))**2 + 
             ( sum([j.pt()*sin(j.phi()) for j in r_prompt.products['pfJets'] ], 0) 
               - sum([j.pt()*sin(j.phi()) for j in r_rereco.products['pfJets'] ], 0))**2 ) 

    print "  delta_met_mu %3.2f delta_mht %3.2f"% (delta_met_mu, delta_mht )
    print "  max ch had error %3.2f max mu error %3.2f" %( max([p.pseudoTrack().ptError() for p in r_rereco.products['pfCand'] if abs(p.pdgId())==211]+[0]), max([p.pseudoTrack().ptError() for p in r_rereco.products['pfCand'] if abs(p.pdgId())==13]+[0]) )
    for j in r_prompt.products['pfJets']:
        if j.pt()>30:
            bstr = "tag" if j.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")>0.8 else "   "
            print "  %s  prompt pt %3.2f eta %3.2f phi %3.2f mu-E %3.2f csvv2 %3.2f"%(bstr, j.pt(),j.eta(),j.phi(),j.pt()*j.muonEnergyFraction(),j.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")) 
    for j in r_rereco.products['pfJets']:
        if j.pt()>30:
            bstr = "tag" if j.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")>0.8 else "   "
            print "  %s  rereco pt %3.2f eta %3.2f phi %3.2f mu-E %3.2f csvv2 %3.2f"%(bstr, j.pt(),j.eta(),j.phi(),j.pt()*j.muonEnergyFraction(),j.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")) 

    r_flat_prompt = flat_prompt.treeReader( variables = map( TreeVariable.fromString, read_variables )  )
    r_flat_prompt.activateAllBranches()

    r_flat_rereco = flat_rereco.treeReader( variables = map( TreeVariable.fromString, read_variables )  )
    r_flat_rereco.activateAllBranches()

    event_list = flat_prompt.getEventList( "run==%i&&lumi==%i&&evt==%i"%(evt) )
    if event_list.GetN()==0:
        logger.warning("flat prompt not found: %s"%evt_str)
    elif event_list.GetN()==1:
        logger.info("flat prompt     found: %s"%evt_str)
        r_flat_prompt.setEventList( event_list )
        r_flat_prompt.start() 
        r_flat_prompt.run()
        print "  CMG: prompt dl_mt2ll %3.2f met_pt %3.2f met_phi %3.2f l1_pt %3.2f l1_mIsoWP %i l2_pt %3.2f l2_mIsoWP %i"%( r_flat_prompt.event.dl_mt2ll, r_flat_prompt.event.met_pt, r_flat_prompt.event.met_phi, r_flat_prompt.event.l1_pt, r_flat_prompt.event.l1_mIsoWP, r_flat_prompt.event.l2_pt, r_flat_prompt.event.l2_mIsoWP) 
        print "  CMG: prompt metSig %3.2f, ht %3.2f, isMuMu %i, dl_mass %3.2f, l1_pdgId %i, l2_pdgId %i, nGoodMu %i, nGoodEle %i, nJetGood %i, nBTag %i"% ( r_flat_prompt.event.metSig,r_flat_prompt.event.ht,r_flat_prompt.event.isMuMu, r_flat_prompt.event.dl_mass, r_flat_prompt.event.l1_pdgId, r_flat_prompt.event.l2_pdgId, r_flat_prompt.event.nGoodMuons,r_flat_prompt.event.nGoodElectrons,r_flat_prompt.event.nJetGood,r_flat_prompt.event.nBTag )

    else:
        raise RuntimeError( "Found %i events for %s"%(event_list.GetN(), evt_str) )
    flat_prompt.chain.SetEventList( 0 )

    event_list = flat_rereco.getEventList( "run==%i&&lumi==%i&&evt==%i"%(evt) )
    if event_list.GetN()==0:
        logger.warning("flat rereco not found: %s"%evt_str) 
    elif event_list.GetN()==1:
        logger.info("flat rereco     found: %s"%evt_str)
        r_flat_rereco.setEventList( event_list )
        r_flat_rereco.start() 
        r_flat_rereco.run() 
        print "  CMG: rereco dl_mt2ll %3.2f met_pt %3.2f met_phi %3.2f l1_pt %3.2f l1_mIsoWP %i l2_pt %3.2f l2_mIsoWP %i"%( r_flat_rereco.event.dl_mt2ll, r_flat_rereco.event.met_pt, r_flat_rereco.event.met_phi, r_flat_rereco.event.l1_pt, r_flat_rereco.event.l1_mIsoWP, r_flat_rereco.event.l2_pt, r_flat_rereco.event.l2_mIsoWP) 
        print "  CMG: rereco metSig %3.2f, ht %3.2f, isMuMu %i, dl_mass %3.2f, l1_pdgId %i, l2_pdgId %i, nGoodMu %i, nGoodEle %i, nJetGood %i, nBTag %i"% ( r_flat_rereco.event.metSig,r_flat_rereco.event.ht,r_flat_rereco.event.isMuMu, r_flat_rereco.event.dl_mass, r_flat_rereco.event.l1_pdgId, r_flat_rereco.event.l2_pdgId, r_flat_rereco.event.nGoodMuons,r_flat_rereco.event.nGoodElectrons,r_flat_rereco.event.nJetGood,r_flat_rereco.event.nBTag )
    else:
        raise RuntimeError( "Found %i events for %s"%(event_list.GetN(), evt_str) )
    flat_rereco.chain.SetEventList( 0 )
    

    if evt_break in evt: break

    # break

#    for e in r.products['electrons']:
#        if e.pt()<20: continue
#        print "ele pt %3.2f eta %3.2f phi %3.2f conv-veto %i lost hits %i"%(e.pt(), e.eta(), e.phi(), e.passConversionVeto(), lostHits(e))
##        for id_ in eleIDs:
##            print "       passes %i %s"%(e.electronID(id_), id_)
#        print "       passingCutBasedPreselection %i trackMomentumError %3.2f"% (e.passingCutBasedPreselection(), e.trackMomentumError() )
#        print "       sigmaIEtaIEta  %5.4f"% sigmaIEtaIEta( e )
#        print "       dEtaScTrkIn    %5.4f"% dEtaScTrkIn( e )
#        print "       dPhiScTrkIn    %5.4f"% dPhiScTrkIn( e )
#        print "       hadronicOverEm %5.4f"% hadronicOverEm( e )
#        print "       eInvMinusPInv  %5.4f"% eInvMinusPInv( e )
#        print "       losthits       %i"% lostHits( e )
#        print "       expectedMissingInnerHits       %i"% expectedMissingInnerHits( e )
#        print "       ecalPFClusterIso/pt %5.4f"%( e.ecalPFClusterIso()/e.pt() ) 
#        print "       hcalPFClusterIso/pt %5.4f"%( e.hcalPFClusterIso()/e.pt() )
#        print "       dr03TkSumPt     /pt %5.4f"%( e.dr03TkSumPt()/e.pt() )
#        print "       dxy            %5.4f"% e.dB(ROOT.pat.Electron.PV2D)
#        gsft = e.gsfTrack()
#        print "       gsfTrack().pt()       %3.2f ptError %3.2f normChi2 %3.2f"%(gsft.pt(), gsft.ptError(), gsft.normalizedChi2() )
#        print "       isGsfCtfScPixChargeConsistent %i isGsfScPixChargeConsistent %i"%(e.isGsfCtfScPixChargeConsistent(), e.isGsfScPixChargeConsistent())
#        
#    for m in r.products['muons']:
#        if m.pt()<20: continue
#        print "muon pt %3.2f eta %3.2f phi %3.2f"%(m.pt(), m.eta(), m.phi())
#        print "       dxy            %5.4f"% m.dB(ROOT.pat.Muon.PV2D)
#        print "       track().pt()       %3.2f ptError %3.2f normChi2 %3.2f"%(m.track().pt(), m.track().ptError(), m.track().normalizedChi2())
#        it = m.innerTrack()
#        print "       innerTrack().pt()  %3.2f ptError %3.2f normChi2 %3.2f HP? %i"%(it.pt(), it.ptError(), it.normalizedChi2(), it.quality(it.highPurity))
#        print "       globalTrack().pt() %3.2f ptError %3.2f normChi2 %3.2f relPtErr %3.2f"%(m.globalTrack().pt(), m.globalTrack().ptError(), m.globalTrack().normalizedChi2(), m.globalTrack().ptError()/m.globalTrack().pt())
#    #break
#
         
#Type                                  Module                      Label             Process   
#----------------------------------------------------------------------------------------------
#edm::TriggerResults                   "TriggerResults"            ""                "HLT"     
#HcalNoiseSummary                      "hcalnoise"                 ""                "RECO"    
#L1GlobalTriggerReadoutRecord          "gtDigis"                   ""                "RECO"    
#double                                "fixedGridRhoAll"           ""                "RECO"    
#double                                "fixedGridRhoFastjetAll"    ""                "RECO"    
#double                                "fixedGridRhoFastjetAllCalo"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentral"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralCalo"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralChargedPileUp"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralNeutral"   ""                "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEgamma"             "reducedEBRecHits"   "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEgamma"             "reducedEERecHits"   "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEgamma"             "reducedESRecHits"   "RECO"    
#edm::TriggerResults                   "TriggerResults"            ""                "RECO"    
#edm::ValueMap<float>                  "offlineSlimmedPrimaryVertices"   ""                "RECO"    
#pat::PackedTriggerPrescales           "patTrigger"                ""                "RECO"    
#pat::PackedTriggerPrescales           "patTrigger"                "l1max"           "RECO"    
#pat::PackedTriggerPrescales           "patTrigger"                "l1min"           "RECO"    
#reco::BeamHaloSummary                 "BeamHaloSummary"           ""                "RECO"    
#reco::BeamSpot                        "offlineBeamSpot"           ""                "RECO"    
#reco::CSCHaloData                     "CSCHaloData"               ""                "RECO"    
#vector<l1extra::L1EmParticle>         "l1extraParticles"          "Isolated"        "RECO"    
#vector<l1extra::L1EmParticle>         "l1extraParticles"          "NonIsolated"     "RECO"    
#vector<l1extra::L1EtMissParticle>     "l1extraParticles"          "MET"             "RECO"    
#vector<l1extra::L1EtMissParticle>     "l1extraParticles"          "MHT"             "RECO"    
#vector<l1extra::L1HFRings>            "l1extraParticles"          ""                "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Central"         "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Forward"         "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "IsoTau"          "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Tau"             "RECO"    
#vector<l1extra::L1MuonParticle>       "l1extraParticles"          ""                "RECO"    
#vector<pat::Electron>                 "slimmedElectrons"          ""                "RECO"    
#vector<pat::Jet>                      "slimmedJets"               ""                "RECO"    
#vector<pat::Jet>                      "slimmedJetsAK8"            ""                "RECO"    
#vector<pat::Jet>                      "slimmedJetsPuppi"          ""                "RECO"    
#vector<pat::Jet>                      "slimmedJetsAK8PFCHSSoftDropPacked"   "SubJets"         "RECO"    
#vector<pat::Jet>                      "slimmedJetsCMSTopTagCHSPacked"   "SubJets"         "RECO"    
#vector<pat::MET>                      "slimmedMETs"               ""                "RECO"    
#vector<pat::MET>                      "slimmedMETsPuppi"          ""                "RECO"    
#vector<pat::Muon>                     "slimmedMuons"              ""                "RECO"    
#vector<pat::PackedCandidate>          "lostTracks"                ""                "RECO"    
#vector<pat::PackedCandidate>          "packedPFCandidates"        ""                "RECO"    
#vector<pat::Photon>                   "slimmedPhotons"            ""                "RECO"    
#vector<pat::Tau>                      "slimmedTaus"               ""                "RECO"    
#vector<pat::TriggerObjectStandAlone>    "selectedPatTrigger"        ""                "RECO"    
#vector<reco::CATopJetTagInfo>         "caTopTagInfosPAT"          ""                "RECO"    
#vector<reco::CaloCluster>             "reducedEgamma"             "reducedEBEEClusters"   "RECO"    
#vector<reco::CaloCluster>             "reducedEgamma"             "reducedESClusters"   "RECO"    
#vector<reco::Conversion>              "reducedEgamma"             "reducedConversions"   "RECO"    
#vector<reco::Conversion>              "reducedEgamma"             "reducedSingleLegConversions"   "RECO"    
#vector<reco::GsfElectronCore>         "reducedEgamma"             "reducedGedGsfElectronCores"   "RECO"    
#vector<reco::PhotonCore>              "reducedEgamma"             "reducedGedPhotonCores"   "RECO"    
#vector<reco::SuperCluster>            "reducedEgamma"             "reducedSuperClusters"   "RECO"    
#vector<reco::Vertex>                  "offlineSlimmedPrimaryVertices"   ""                "RECO"    
#vector<reco::VertexCompositePtrCandidate>    "slimmedSecondaryVertices"   ""                "RECO"    
#unsigned int                          "bunchSpacingProducer"      ""                "RECO"    

#Type                                  Module                      Label             Process   
#----------------------------------------------------------------------------------------------
#LHEEventProduct                       "externalLHEProducer"       ""                "LHE"     
#GenEventInfoProduct                   "generator"                 ""                "SIM"     
#edm::TriggerResults                   "TriggerResults"            ""                "SIM"     
#edm::TriggerResults                   "TriggerResults"            ""                "HLT"     
#int                                   "addPileupInfo"             "bunchSpacing"    "HLT"     
#vector<PileupSummaryInfo>             "addPileupInfo"             ""                "HLT"     
#vector<int>                           "genParticles"              ""                "HLT"     
#vector<reco::GenJet>                  "ak4GenJets"                ""                "HLT"     
#vector<reco::GenJet>                  "ak4GenJetsNoNu"            ""                "HLT"     
#vector<reco::GenJet>                  "ak8GenJets"                ""                "HLT"     
#vector<reco::GenJet>                  "ak8GenJetsNoNu"            ""                "HLT"     
#vector<reco::GenMET>                  "genMetCalo"                ""                "HLT"     
#vector<reco::GenMET>                  "genMetTrue"                ""                "HLT"     
#vector<reco::GenParticle>             "genParticles"              ""                "HLT"     
#trigger::TriggerEvent                 "hltTriggerSummaryAOD"      ""                "HLT"     
#ClusterSummary                        "clusterSummaryProducer"    ""                "RECO"    
#EBDigiCollection                      "selectDigi"                "selectedEcalEBDigiCollection"   "RECO"    
#EEDigiCollection                      "selectDigi"                "selectedEcalEEDigiCollection"   "RECO"    
#HcalNoiseSummary                      "hcalnoise"                 ""                "RECO"    
#HcalUnpackerReport                    "castorDigis"               ""                "RECO"    
#HcalUnpackerReport                    "hcalDigis"                 ""                "RECO"    
#L1GlobalTriggerObjectMaps             "l1L1GtObjectMap"           ""                "RECO"    
#L1GlobalTriggerReadoutRecord          "gtDigis"                   ""                "RECO"    
#double                                "fixedGridRhoAll"           ""                "RECO"    
#double                                "fixedGridRhoFastjetAll"    ""                "RECO"    
#double                                "fixedGridRhoFastjetAllCalo"   ""                "RECO"    
#double                                "fixedGridRhoFastjetAllTmp"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentral"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralCalo"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralChargedPileUp"   ""                "RECO"    
#double                                "fixedGridRhoFastjetCentralNeutral"   ""                "RECO"    
#double                                "ak4CaloJets"               "rho"             "RECO"    
#double                                "ak4PFJets"                 "rho"             "RECO"    
#double                                "ak4PFJetsCHS"              "rho"             "RECO"    
#double                                "ak4TrackJets"              "rho"             "RECO"    
#double                                "ak5CastorJets"             "rho"             "RECO"    
#double                                "ak7CastorJets"             "rho"             "RECO"    
#double                                "ak8PFJetsCHS"              "rho"             "RECO"    
#double                                "ak8PFJetsCHSSoftDrop"      "rho"             "RECO"    
#double                                "cmsTopTagPFJetsCHS"        "rho"             "RECO"    
#double                                "ak4CaloJets"               "sigma"           "RECO"    
#double                                "ak4PFJets"                 "sigma"           "RECO"    
#double                                "ak4PFJetsCHS"              "sigma"           "RECO"    
#double                                "ak4TrackJets"              "sigma"           "RECO"    
#double                                "ak5CastorJets"             "sigma"           "RECO"    
#double                                "ak7CastorJets"             "sigma"           "RECO"    
#double                                "ak8PFJetsCHS"              "sigma"           "RECO"    
#double                                "ak8PFJetsCHSSoftDrop"      "sigma"           "RECO"    
#double                                "cmsTopTagPFJetsCHS"        "sigma"           "RECO"    
#edm::Association<vector<reco::DeDxHitInfo> >    "dedxHitInfo"               ""                "RECO"    
#edm::Association<vector<reco::Vertex> >    "offlinePrimaryVertices"    ""                "RECO"    
#edm::Association<vector<reco::Vertex> >    "offlinePrimaryVerticesWithBS"   ""                "RECO"    
#edm::AssociationMap<edm::OneToOne<vector<reco::SuperCluster>,vector<reco::HFEMClusterShape>,unsigned int> >    "hfEMClusters"              ""                "RECO"    
#edm::AssociationMap<edm::OneToOne<vector<reco::Track>,vector<reco::Track>,unsigned int> >    "tevMuons"                  "default"         "RECO"    
#edm::AssociationMap<edm::OneToOne<vector<reco::Track>,vector<reco::Track>,unsigned int> >    "tevMuons"                  "dyt"             "RECO"    
#edm::AssociationMap<edm::OneToOne<vector<reco::Track>,vector<reco::Track>,unsigned int> >    "tevMuons"                  "firstHit"        "RECO"    
#edm::AssociationMap<edm::OneToOne<vector<reco::Track>,vector<reco::Track>,unsigned int> >    "tevMuons"                  "picky"           "RECO"    
#edm::AssociationVector<edm::RefProd<vector<reco::PFTau> >,vector<edm::Ref<vector<reco::PFTauTransverseImpactParameter>,reco::PFTauTransverseImpactParameter,edm::refhelper::FindUsingAdvance<vector<reco::PFTauTransverseImpactParameter>,reco::PFTauTransverseImpactParameter> > >,edm::Ref<vector<reco::PFTau>,reco::PFTau,edm::refhelper::FindUsingAdvance<vector<reco::PFTau>,reco::PFTau> >,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "hpsPFTauTransverseImpactParameters"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<edm::RefVector<vector<reco::Track>,reco::Track,edm::refhelper::FindUsingAdvance<vector<reco::Track>,reco::Track> > >,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "ak4JetTracksAssociatorAtVertex"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<edm::RefVector<vector<reco::Track>,reco::Track,edm::refhelper::FindUsingAdvance<vector<reco::Track>,reco::Track> > >,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "ak4JetTracksAssociatorAtVertexPF"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<edm::RefVector<vector<reco::Track>,reco::Track,edm::refhelper::FindUsingAdvance<vector<reco::Track>,reco::Track> > >,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "ak4JetTracksAssociatorExplicit"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedCvsBJetTags"     ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedCvsLJetTags"     ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedInclusiveSecondaryVertexV2BJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedInclusiveSecondaryVertexV2BJetTagsEI"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedMVABJetTags"     ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedMVAV2BJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedSecondaryVertexBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedSecondaryVertexSoftLeptonBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfCombinedSecondaryVertexV2BJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfJetBProbabilityBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfJetProbabilityBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfSimpleSecondaryVertexHighEffBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfSimpleSecondaryVertexHighPurBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfTrackCountingHighEffBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "pfTrackCountingHighPurBJetTags"   ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "softPFElectronBJetTags"    ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<float>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "softPFMuonBJetTags"        ""                "RECO"    
#edm::AssociationVector<edm::RefToBaseProd<reco::Jet>,vector<reco::JetExtendedAssociation::JetExtendedData>,edm::RefToBase<reco::Jet>,unsigned int,edm::helper::AssociationIdenticalKeyReference>    "ak4JetExtender"            ""                "RECO"    
#edm::ConditionsInEventBlock           "conditionsInEdm"           ""                "RECO"    
#edm::OwnVector<TrackingRecHit,edm::ClonePolicy<TrackingRecHit> >    "displacedGlobalMuons"      ""                "RECO"    
#edm::OwnVector<TrackingRecHit,edm::ClonePolicy<TrackingRecHit> >    "displacedStandAloneMuons"   ""                "RECO"    
#edm::OwnVector<TrackingRecHit,edm::ClonePolicy<TrackingRecHit> >    "refittedStandAloneMuons"   ""                "RECO"    
#edm::OwnVector<TrackingRecHit,edm::ClonePolicy<TrackingRecHit> >    "standAloneMuons"           ""                "RECO"    
#edm::RangeMap<CSCDetId,edm::OwnVector<CSCSegment,edm::ClonePolicy<CSCSegment> >,edm::ClonePolicy<CSCSegment> >    "cscSegments"               ""                "RECO"    
#edm::RangeMap<DTChamberId,edm::OwnVector<DTRecSegment4D,edm::ClonePolicy<DTRecSegment4D> >,edm::ClonePolicy<DTRecSegment4D> >    "dt4DCosmicSegments"        ""                "RECO"    
#edm::RangeMap<DTChamberId,edm::OwnVector<DTRecSegment4D,edm::ClonePolicy<DTRecSegment4D> >,edm::ClonePolicy<DTRecSegment4D> >    "dt4DSegments"              ""                "RECO"    
#edm::RangeMap<RPCDetId,edm::OwnVector<RPCRecHit,edm::ClonePolicy<RPCRecHit> >,edm::ClonePolicy<RPCRecHit> >    "rpcRecHits"                ""                "RECO"    
#edm::SortedCollection<CastorRecHit,edm::StrictWeakOrdering<CastorRecHit> >    "castorreco"                ""                "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEcalRecHitsEB"      ""                "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEcalRecHitsEE"      ""                "RECO"    
#edm::SortedCollection<EcalRecHit,edm::StrictWeakOrdering<EcalRecHit> >    "reducedEcalRecHitsES"      ""                "RECO"    
#edm::SortedCollection<HBHERecHit,edm::StrictWeakOrdering<HBHERecHit> >    "reducedHcalRecHits"        "hbhereco"        "RECO"    
#edm::SortedCollection<HFRecHit,edm::StrictWeakOrdering<HFRecHit> >    "reducedHcalRecHits"        "hfreco"          "RECO"    
#edm::SortedCollection<HORecHit,edm::StrictWeakOrdering<HORecHit> >    "reducedHcalRecHits"        "horeco"          "RECO"    
#edm::TriggerResults                   "TriggerResults"            ""                "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProd"              "PhotonCutBasedIDLoose"   "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProdGED"           "PhotonCutBasedIDLoose"   "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProd"              "PhotonCutBasedIDLooseEM"   "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProdGED"           "PhotonCutBasedIDLooseEM"   "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProd"              "PhotonCutBasedIDTight"   "RECO"    
#edm::ValueMap<bool>                   "PhotonIDProdGED"           "PhotonCutBasedIDTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidAllArbitrated"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidGMStaChiCompatibility"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidGMTkChiCompatibility"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidGMTkKinkTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidGlobalMuonPromptTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidRPCMuLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTM2DCompatibilityLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTM2DCompatibilityTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationAngLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationAngTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationOptimizedLowPtLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationOptimizedLowPtTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMLastStationTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMOneStationAngLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMOneStationAngTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMOneStationLoose"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTMOneStationTight"   "RECO"    
#edm::ValueMap<bool>                   "muons"                     "muidTrackerMuonArbitrated"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueCharged03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueCharged04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueChargedAll03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueChargedAll04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueGamma03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueGamma04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueGammaHighThreshold03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueGammaHighThreshold04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueNeutral03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueNeutral04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueNeutralHighThreshold03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValueNeutralHighThreshold04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValuePU03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFMeanDRIsoValuePU04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueCharged03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueCharged04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueChargedAll03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueChargedAll04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueGamma03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueGamma04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueGammaHighThreshold03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueGammaHighThreshold04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueNeutral03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueNeutral04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueNeutralHighThreshold03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValueNeutralHighThreshold04"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValuePU03"   "RECO"    
#edm::ValueMap<double>                 "muons"                     "muPFSumDRIsoValuePU04"   "RECO"    
#edm::ValueMap<edm::Ptr<reco::PFCandidate> >    "particleFlow"              "electrons"       "RECO"    
#edm::ValueMap<edm::Ptr<reco::PFCandidate> >    "particleFlow"              "muons"           "RECO"    
#edm::ValueMap<edm::Ptr<reco::PFCandidate> >    "particleFlow"              "photons"         "RECO"    
#edm::ValueMap<float>                  "ak8PFJetsCHSSoftDropMass"   ""                "RECO"    
#edm::ValueMap<float>                  "eidLoose"                  ""                "RECO"    
#edm::ValueMap<float>                  "eidRobustHighEnergy"       ""                "RECO"    
#edm::ValueMap<float>                  "eidRobustLoose"            ""                "RECO"    
#edm::ValueMap<float>                  "eidRobustTight"            ""                "RECO"    
#edm::ValueMap<float>                  "eidTight"                  ""                "RECO"    
#edm::ValueMap<float>                  "electronEcalPFClusterIsolationProducer"   ""                "RECO"    
#edm::ValueMap<float>                  "electronHcalPFClusterIsolationProducer"   ""                "RECO"    
#edm::ValueMap<float>                  "offlinePrimaryVertices"    ""                "RECO"    
#edm::ValueMap<float>                  "offlinePrimaryVerticesWithBS"   ""                "RECO"    
#edm::ValueMap<float>                  "photonEcalPFClusterIsolationProducer"   ""                "RECO"    
#edm::ValueMap<float>                  "photonHcalPFClusterIsolationProducer"   ""                "RECO"    
#edm::ValueMap<int>                    "offlinePrimaryVertices"    ""                "RECO"    
#edm::ValueMap<int>                    "offlinePrimaryVerticesWithBS"   ""                "RECO"    
#edm::ValueMap<reco::CastorJetID>      "ak5CastorJetID"            ""                "RECO"    
#edm::ValueMap<reco::CastorJetID>      "ak7CastorJetID"            ""                "RECO"    
#edm::ValueMap<reco::DeDxData>         "dedxHarmonic2"             ""                "RECO"    
#edm::ValueMap<reco::JetID>            "ak4JetID"                  ""                "RECO"    
#edm::ValueMap<reco::MuonCosmicCompatibility>    "muons"                     "cosmicsVeto"     "RECO"    
#edm::ValueMap<reco::MuonMETCorrectionData>    "muonMETValueMapProducer"   "muCorrData"      "RECO"    
#edm::ValueMap<reco::MuonShower>       "muons"                     "muonShowerInformation"   "RECO"    
#edm::ValueMap<reco::MuonTimeExtra>    "muons"                     "combined"        "RECO"    
#edm::ValueMap<reco::MuonTimeExtra>    "muons"                     "csc"             "RECO"    
#edm::ValueMap<reco::MuonTimeExtra>    "muons"                     "dt"              "RECO"    
#edm::ValueMap<vector<edm::Ref<vector<reco::PFCandidate>,reco::PFCandidate,edm::refhelper::FindUsingAdvance<vector<reco::PFCandidate>,reco::PFCandidate> > > >    "particleBasedIsolation"    "gedGsfElectrons"   "RECO"    
#edm::ValueMap<vector<edm::Ref<vector<reco::PFCandidate>,reco::PFCandidate,edm::refhelper::FindUsingAdvance<vector<reco::PFCandidate>,reco::PFCandidate> > > >    "particleBasedIsolation"    "gedPhotons"      "RECO"    
#edm::ValueMap<unsigned int>           "muons"                     "cosmicsVeto"     "RECO"    
#int                                   "tcdsDigis"                 "nibble"          "RECO"    
#reco::BeamHaloSummary                 "BeamHaloSummary"           ""                "RECO"    
#reco::BeamSpot                        "offlineBeamSpot"           ""                "RECO"    
#reco::GlobalHaloData                  "GlobalHaloData"            ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauChargedIsoPtSum"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByDeadECALElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByDecayModeFinding"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByDecayModeFindingNewDMs"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByDecayModeFindingOldDMs"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3newDMwLTraw"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3newDMwoLTraw"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3oldDMwLTraw"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3oldDMwoLTraw"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseChargedIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseCombinedIsolationDBSumPtCorr3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseMuonRejection2"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLooseMuonRejection3"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByLoosePileupWeightedIsolation3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5LooseElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5MediumElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5TightElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5VLooseElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5VTightElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5rawElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVALooseMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVAMediumMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVATightMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVArawMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumChargedIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumCombinedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumCombinedIsolationDBSumPtCorr3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumMuonRejection2"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMediumPileupWeightedIsolation3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByPhotonPtSumOutsideSignalCone"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByRawChargedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByRawCombinedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByRawCombinedIsolationDBSumPtCorr3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByRawGammaIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByRawPileupWeightedIsolation3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightChargedIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightCombinedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightCombinedIsolationDBSumPtCorr3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightElectronRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightMuonRejection"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightMuonRejection2"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightMuonRejection3"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByTightPileupWeightedIsolation3Hits"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseChargedIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseCombinedIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolationDBSumPtCorr"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVLooseIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVTightIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVTightIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVTightIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVTightIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVVTightIsolationMVA3newDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVVTightIsolationMVA3newDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVVTightIsolationMVA3oldDMwLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByVVTightIsolationMVA3oldDMwoLT"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauNeutralIsoPtSum"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauPUcorrPtSum"       ""                "RECO"    
#reco::PFTauDiscriminator              "pfTausDiscriminationByDecayModeFinding"   ""                "RECO"    
#reco::PFTauDiscriminator              "pfTausDiscriminationByIsolation"   ""                "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3newDMwLTraw"   "category"        "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3newDMwoLTraw"   "category"        "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3oldDMwLTraw"   "category"        "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByIsolationMVA3oldDMwoLTraw"   "category"        "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVA5rawElectronRejection"   "category"        "RECO"    
#reco::PFTauDiscriminator              "hpsPFTauDiscriminationByMVArawMuonRejection"   "category"        "RECO"    
#vector<BeamSpotOnline>                "scalersRawToDigi"          ""                "RECO"    
#vector<DcsStatus>                     "scalersRawToDigi"          ""                "RECO"    
#vector<L1AcceptBunchCrossing>         "scalersRawToDigi"          ""                "RECO"    
#vector<L1TriggerScalers>              "scalersRawToDigi"          ""                "RECO"    
#vector<Level1TriggerScalers>          "scalersRawToDigi"          ""                "RECO"    
#vector<LumiScalers>                   "scalersRawToDigi"          ""                "RECO"    
#vector<double>                        "ak4PFJetsCHS"              "rhos"            "RECO"    
#vector<double>                        "ak8PFJetsCHS"              "rhos"            "RECO"    
#vector<double>                        "ak8PFJetsCHSSoftDrop"      "rhos"            "RECO"    
#vector<double>                        "cmsTopTagPFJetsCHS"        "rhos"            "RECO"    
#vector<double>                        "ak4PFJetsCHS"              "sigmas"          "RECO"    
#vector<double>                        "ak8PFJetsCHS"              "sigmas"          "RECO"    
#vector<double>                        "ak8PFJetsCHSSoftDrop"      "sigmas"          "RECO"    
#vector<double>                        "cmsTopTagPFJetsCHS"        "sigmas"          "RECO"    
#vector<edm::ErrorSummaryEntry>        "logErrorHarvester"         ""                "RECO"    
#vector<edm::FwdPtr<reco::PFCandidate> >    "particleFlowPtrs"          ""                "RECO"    
#vector<edm::FwdPtr<reco::PFCandidate> >    "particleFlowTmpPtrs"       ""                "RECO"    
#vector<edm::FwdPtr<reco::PFCandidate> >    "pfIsolatedElectronsEI"     ""                "RECO"    
#vector<edm::FwdPtr<reco::PFCandidate> >    "pfIsolatedMuonsEI"         ""                "RECO"    
#vector<float>                         "generalTracks"             "MVAValues"       "RECO"    
#vector<l1extra::L1EmParticle>         "l1extraParticles"          "Isolated"        "RECO"    
#vector<l1extra::L1EmParticle>         "l1extraParticles"          "NonIsolated"     "RECO"    
#vector<l1extra::L1EtMissParticle>     "l1extraParticles"          "MET"             "RECO"    
#vector<l1extra::L1EtMissParticle>     "l1extraParticles"          "MHT"             "RECO"    
#vector<l1extra::L1HFRings>            "l1extraParticles"          ""                "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Central"         "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Forward"         "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "IsoTau"          "RECO"    
#vector<l1extra::L1JetParticle>        "l1extraParticles"          "Tau"             "RECO"    
#vector<l1extra::L1MuonParticle>       "l1extraParticles"          ""                "RECO"    
#vector<reco::BasicJet>                "ak5CastorJets"             ""                "RECO"    
#vector<reco::BasicJet>                "ak7CastorJets"             ""                "RECO"    
#vector<reco::BasicJet>                "ak8PFJetsCHSSoftDrop"      ""                "RECO"    
#vector<reco::BasicJet>                "cmsTopTagPFJetsCHS"        ""                "RECO"    
#vector<reco::CaloCluster>             "hfEMClusters"              ""                "RECO"    
#vector<reco::CaloCluster>             "particleFlowEGamma"        "EBEEClusters"    "RECO"    
#vector<reco::CaloCluster>             "particleFlowEGamma"        "ESClusters"      "RECO"    
#vector<reco::CaloCluster>             "hybridSuperClusters"       "hybridBarrelBasicClusters"   "RECO"    
#vector<reco::CaloCluster>             "multi5x5SuperClusters"     "multi5x5EndcapBasicClusters"   "RECO"    
#vector<reco::CaloCluster>             "particleFlowSuperClusterECAL"   "particleFlowBasicClusterECALBarrel"   "RECO"    
#vector<reco::CaloCluster>             "particleFlowSuperClusterECAL"   "particleFlowBasicClusterECALEndcap"   "RECO"    
#vector<reco::CaloCluster>             "particleFlowSuperClusterECAL"   "particleFlowBasicClusterECALPreshower"   "RECO"    
#vector<reco::CaloCluster>             "hybridSuperClusters"       "uncleanOnlyHybridBarrelBasicClusters"   "RECO"    
#vector<reco::CaloJet>                 "ak4CaloJets"               ""                "RECO"    
#vector<reco::CaloMET>                 "caloMet"                   ""                "RECO"    
#vector<reco::CaloMET>                 "caloMetBE"                 ""                "RECO"    
#vector<reco::CaloMET>                 "caloMetBEFO"               ""                "RECO"    
#vector<reco::CaloMET>                 "caloMetM"                  ""                "RECO"    
#vector<reco::CastorTower>             "CastorTowerReco"           ""                "RECO"    
#vector<reco::Conversion>              "allConversions"            ""                "RECO"    
#vector<reco::Conversion>              "conversions"               ""                "RECO"    
#vector<reco::Conversion>              "particleFlowEGamma"        ""                "RECO"    
#vector<reco::Conversion>              "uncleanedOnlyAllConversions"   ""                "RECO"    
#vector<reco::DeDxHitInfo>             "dedxHitInfo"               ""                "RECO"    
#vector<reco::GsfElectron>             "gedGsfElectrons"           ""                "RECO"    
#vector<reco::GsfElectron>             "uncleanedOnlyGsfElectrons"   ""                "RECO"    
#vector<reco::GsfElectronCore>         "gedGsfElectronCores"       ""                "RECO"    
#vector<reco::GsfElectronCore>         "uncleanedOnlyGsfElectronCores"   ""                "RECO"    
#vector<reco::GsfTrack>                "electronGsfTracks"         ""                "RECO"    
#vector<reco::HFEMClusterShape>        "hfEMClusters"              ""                "RECO"    
#vector<reco::JPTJet>                  "JetPlusTrackZSPCorJetAntiKt4"   ""                "RECO"    
#vector<reco::Muon>                    "muons"                     ""                "RECO"    
#vector<reco::Muon>                    "muonsFromCosmics"          ""                "RECO"    
#vector<reco::Muon>                    "muonsFromCosmics1Leg"      ""                "RECO"    
#vector<reco::PFCandidate>             "particleFlow"              ""                "RECO"    
#vector<reco::PFCandidate>             "pfIsolatedElectronsEI"     ""                "RECO"    
#vector<reco::PFCandidate>             "pfIsolatedMuonsEI"         ""                "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "AddedMuonsAndHadrons"   "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedCosmicsMuons"   "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedFakeMuons"   "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedHF"       "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedPunchThroughMuons"   "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedPunchThroughNeutralHadrons"   "RECO"    
#vector<reco::PFCandidate>             "particleFlowTmp"           "CleanedTrackerAndGlobalMuons"   "RECO"    
#vector<reco::PFJet>                   "ak4PFJets"                 ""                "RECO"    
#vector<reco::PFJet>                   "ak4PFJetsCHS"              ""                "RECO"    
#vector<reco::PFJet>                   "ak8PFJetsCHS"              ""                "RECO"    
#vector<reco::PFJet>                   "pfJetsEI"                  ""                "RECO"    
#vector<reco::PFJet>                   "ak8PFJetsCHSSoftDrop"      "SubJets"         "RECO"    
#vector<reco::PFJet>                   "cmsTopTagPFJetsCHS"        "caTopSubJets"    "RECO"    
#vector<reco::PFMET>                   "pfChMet"                   ""                "RECO"    
#vector<reco::PFMET>                   "pfMet"                     ""                "RECO"    
#vector<reco::PFMET>                   "pfMetEI"                   ""                "RECO"    
#vector<reco::PFRecHit>                "particleFlowRecHitECAL"    "Cleaned"         "RECO"    
#vector<reco::PFRecHit>                "particleFlowRecHitHBHE"    "Cleaned"         "RECO"    
#vector<reco::PFRecHit>                "particleFlowRecHitHF"      "Cleaned"         "RECO"    
#vector<reco::PFRecHit>                "particleFlowRecHitHO"      "Cleaned"         "RECO"    
#vector<reco::PFRecHit>                "particleFlowRecHitPS"      "Cleaned"         "RECO"    
#vector<reco::PFTau>                   "hpsPFTauProducer"          ""                "RECO"    
#vector<reco::PFTau>                   "pfTausEI"                  ""                "RECO"    
#vector<reco::PFTauTransverseImpactParameter>    "hpsPFTauTransverseImpactParameters"   "PFTauTIP"        "RECO"    
#vector<reco::Photon>                  "gedPhotons"                ""                "RECO"    
#vector<reco::Photon>                  "photons"                   ""                "RECO"    
#vector<reco::PhotonCore>              "gedPhotonCore"             ""                "RECO"    
#vector<reco::PhotonCore>              "photonCore"                ""                "RECO"    
#vector<reco::PreshowerCluster>        "multi5x5SuperClustersWithPreshower"   "preshowerXClusters"   "RECO"    
#vector<reco::PreshowerCluster>        "multi5x5SuperClustersWithPreshower"   "preshowerYClusters"   "RECO"    
#vector<reco::PreshowerClusterShape>    "multi5x5PreshowerClusterShape"   "multi5x5PreshowerXClustersShape"   "RECO"    
#vector<reco::PreshowerClusterShape>    "multi5x5PreshowerClusterShape"   "multi5x5PreshowerYClustersShape"   "RECO"    
#vector<reco::RecoChargedRefCandidate>    "trackRefsForJets"          ""                "RECO"    
#vector<reco::RecoEcalCandidate>       "hfRecoEcalCandidate"       ""                "RECO"    
#vector<reco::RecoTauPiZero>           "hpsPFTauProducer"          "pizeros"         "RECO"    
#vector<reco::SuperCluster>            "correctedHybridSuperClusters"   ""                "RECO"    
#vector<reco::SuperCluster>            "correctedMulti5x5SuperClustersWithPreshower"   ""                "RECO"    
#vector<reco::SuperCluster>            "hfEMClusters"              ""                "RECO"    
#vector<reco::SuperCluster>            "particleFlowEGamma"        ""                "RECO"    
#vector<reco::SuperCluster>            "particleFlowSuperClusterECAL"   "particleFlowSuperClusterECALBarrel"   "RECO"    
#vector<reco::SuperCluster>            "particleFlowSuperClusterECAL"   "particleFlowSuperClusterECALEndcapWithPreshower"   "RECO"    
#vector<reco::SuperCluster>            "hybridSuperClusters"       "uncleanOnlyHybridSuperClusters"   "RECO"    
#vector<reco::Track>                   "ckfInOutTracksFromConversions"   ""                "RECO"    
#vector<reco::Track>                   "ckfOutInTracksFromConversions"   ""                "RECO"    
#vector<reco::Track>                   "conversionStepTracks"      ""                "RECO"    
#vector<reco::Track>                   "cosmicMuons"               ""                "RECO"    
#vector<reco::Track>                   "cosmicMuons1Leg"           ""                "RECO"    
#vector<reco::Track>                   "displacedGlobalMuons"      ""                "RECO"    
#vector<reco::Track>                   "displacedStandAloneMuons"   ""                "RECO"    
#vector<reco::Track>                   "displacedTracks"           ""                "RECO"    
#vector<reco::Track>                   "generalTracks"             ""                "RECO"    
#vector<reco::Track>                   "globalMuons"               ""                "RECO"    
#vector<reco::Track>                   "refittedStandAloneMuons"   ""                "RECO"    
#vector<reco::Track>                   "standAloneMuons"           ""                "RECO"    
#vector<reco::Track>                   "uncleanedOnlyCkfInOutTracksFromConversions"   ""                "RECO"    
#vector<reco::Track>                   "uncleanedOnlyCkfOutInTracksFromConversions"   ""                "RECO"    
#vector<reco::Track>                   "refittedStandAloneMuons"   "UpdatedAtVtx"    "RECO"    
#vector<reco::Track>                   "standAloneMuons"           "UpdatedAtVtx"    "RECO"    
#vector<reco::Track>                   "tevMuons"                  "default"         "RECO"    
#vector<reco::Track>                   "tevMuons"                  "dyt"             "RECO"    
#vector<reco::Track>                   "tevMuons"                  "firstHit"        "RECO"    
#vector<reco::Track>                   "tevMuons"                  "picky"           "RECO"    
#vector<reco::TrackExtra>              "displacedGlobalMuons"      ""                "RECO"    
#vector<reco::TrackExtra>              "displacedStandAloneMuons"   ""                "RECO"    
#vector<reco::TrackExtra>              "globalMuons"               ""                "RECO"    
#vector<reco::TrackExtra>              "refittedStandAloneMuons"   ""                "RECO"    
#vector<reco::TrackExtra>              "standAloneMuons"           ""                "RECO"    
#vector<reco::TrackExtra>              "tevMuons"                  "default"         "RECO"    
#vector<reco::TrackExtra>              "tevMuons"                  "dyt"             "RECO"    
#vector<reco::TrackExtra>              "tevMuons"                  "firstHit"        "RECO"    
#vector<reco::TrackExtra>              "tevMuons"                  "picky"           "RECO"    
#vector<reco::TrackExtrapolation>      "trackExtrapolator"         ""                "RECO"    
#vector<reco::TrackJet>                "ak4TrackJets"              ""                "RECO"    
#vector<reco::Vertex>                  "inclusiveSecondaryVertices"   ""                "RECO"    
#vector<reco::Vertex>                  "offlinePrimaryVertices"    ""                "RECO"    
#vector<reco::Vertex>                  "offlinePrimaryVerticesWithBS"   ""                "RECO"    
#vector<reco::VertexCompositeCandidate>    "generalV0Candidates"       "Kshort"          "RECO"    
#vector<reco::VertexCompositeCandidate>    "generalV0Candidates"       "Lambda"          "RECO"    
#vector<reco::VertexCompositePtrCandidate>    "inclusiveCandidateSecondaryVertices"   ""                "RECO"    
#vector<reco::VertexCompositePtrCandidate>    "inclusiveCandidateSecondaryVerticesCvsL"   ""                "RECO"    

