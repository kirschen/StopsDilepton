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
      default='INFO',
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
dirname = "/data/rschoefbeck/pickEvents/StopsDilepton/tail_ttjetsDilep_80X" 
s0 = FWLiteSample.fromDirectory("mt2Tail", directory = os.path.expanduser(dirname) )

products = {
    'pfJets':{'type':'vector<reco::PFJet>', 'label':( "ak4PFJets" ) },
    'pf':{'type':'vector<reco::PFCandidate>', 'label':( "particleFlow" ) },
    'gen':{'type':'vector<reco::GenParticle>', 'label':( "genParticles" ) },
    'pfMet':{'type':'vector<reco::PFMET>', 'label':( "pfMet" )},
}

r = s0.fwliteReader( products = products )
r.start()

def printHisto( p, prefix = ""):
    print "%s gen %10s status %i nMothers %i pt/eta/phi %5.1f/%5.1f/%5.1f" % ( prefix, \
        pdgToName(p.pdgId()), p.status(), p.numberOfMothers(), p.pt(), p.eta(), p.phi(),
    )
    for i in range( p.numberOfMothers() ):
        printHisto( p.mother(i), "  " + prefix )

def vecSumPt(particles):
    px = sum(p.px() for p in particles)
    py = sum(p.py() for p in particles)
    return sqrt(px**2+py**2)

while r.run():
#    if any(e in r.evt for e in [3991364, 4854452, 10356846, 21762195, 4532888, 15495640, 17276057, 20991689, 33607796, 40308549, 41117351, 42552044, 48024871, 51884514]):continue
#    if any(e in r.evt for e in [53964677, 56369604, 56740873, 58872109, 60203349, 61608051, 68707320, 71158655, 78110867, 87973932, 94275792]):continue
    print "At %i:%i:%i" % r.evt    

    # 80X
    # 0. 1:4953:3991364 # 300 GeV gamma lost in dead cell (jet mism.)
    # 1. 1:5468:4532888 # 80 GeV jet mismeasurement , -0.934/2.9678 (jet mism.)
    # 2. 1:6024:4854452 # 2x40 GeV lost 1.6/-2.4, 1.9/2.7 (gaussian jet mism.), 40 GeV neutrino from jet
    # 3. 1:6171:4972344 # drastic mismeasurement ecal 160 GeV 
    # 4. 1:12852:10356846 # lost K_plus 117.1/1.391/-2.527
    # 5. 1:13923:11219847 (most probably jet mismeasurement, no AOD available)
    # 6. 1:17046:13736425 jet mism. + 30 GeV neutrino in jet 
    # 7. 1:18692:15495640 # overmeasured muon at 148->184 2.287/-0.282? 30 GeV jet mismeasurement
    # 8. 1:20840:17276057 # lost high pt gammas at -1.5/0.6 (jet mism.), 40 GeV neutrino in jet
    # 9. 1:25322:20991689 # neutrino in a jet of 100GeV, just passing the threshold (142GeV)
    # 11. 1:27005:21762195 # lost gammas and neutrals in dead cell 1.152/-3.077 (jet mism.)
    # 12. 1:40541:33607796 # lost mu- from W, picked up 60 GeV e- fake, EMu->EE, some trk inefficieny at -2.175/0.183 (end of trk coverage, seems gaussian)
    # 13. 1:48624:40308549 # lost high pt gammas (jet mism.)
    # 14. 1:49599:41117351 # lost 50 GeV mu- in a jet 52.2/-0.999/0.558 
    # 15. 1:51330:42552044 # lost energy in ECAL (jet mism., 100 GeV) -0.837/2.890
    # 16. 1:57932:48024871 # overmeasured muon 125->330  0.289/-2.763, 50 GeV probably gaussian jet mismeasurement) 
    # 17. 1:62587:51884514 # likely gaussian jet mismeasurement (60 GeV in a 200GeV genjet plus 40 GeV neutrino in another jet)
    # 18. 1:65097:53964677 # mumu->emu, lost mu to pt cut, picked up fake e from conversion gamma, plus jet mism 40 GeV (gaussian) 
    # 19. 1:67998:56369604 # 60 GeV from neutrino from jet
    # 20. 1:68445:56740873 # tau decaying hadronically + non-prompt mu
    # 21. 1:71016:58872109  fake muon with 60 GeV inconsistency btw inner track and global track
    # 22. 1:72622:60203349 200 GeV neutrino in jet, plus 70 GeV photons lost 
    # 23. 1:74317:61608051 overmeasured muon 114.0/-2.275/-1.514 -> 154.1/-2.275/-1.51, 20 GeV neutrino in jet4
    # 24. 1:82880:68707320 likely non-prompt mu, no AOD available
    # 25. 1:85837:71158655 160 GeV neutrino from jet
    # 26. 1:94223:78110867 360 GeV gamma lost in crack
    # 27. 1:106121:87973932 150 GeV fake MET from various hadronic mism.
    # 28. 1:113723:94275792 jet mismeasurement at eta~3 + 20 GeV neutrino

    # 76X
    #if not 3460888 in r.evt: continue  #Evt 1, EMu, 150 GeV, lost p0(103) ->e+/e- pair at 1.013/0.665
    #if not 3991364 in r.evt: continue  #Evt 2, EMu, 315 GeV lost 330 GeV ISR gamma at -2.1/ -2.5 (leading gen particle)
    #if not 4854452 in r.evt: continue  #Evt 3, MuMu, 50 GeV, lost few neutrals and gammas at 1.6/-2.3, 40 GeV neutrino 
    #if not 10312243 in r.evt: continue #Evt 4, EMu, 400 GeV mismeasurement, eta -> gamma, gamma -> lost at 1.8/0.8
    #if not 13250511 in r.evt: continue #Evt 5, 42 GeV: 50 GeV jet mismeasurement (several small mism) 
    #if not 16492719 in r.evt: continue #Evt 6, EE, 45 GeV: K_plus and mu_plus at 50 GeV generated, only one ch.had. at 50 GeV reco'd
    #if not 17276057 in r.evt: continue #Evt 7, MuMu, 316 GeV: several 50,90 GeV gammas (from pi0 and omegas from a jet) missing at -1.539/0.630 
    #if not 21144763 in r.evt: continue #Evt 10, EE, 100 GeV: charged hadron mismeas. at -0.933/2.989, few gammas undermeasured (jet mism)
    #if not 25233964 in r.evt: continue #Evt 11, MuMu 540 GeV, 1.15TeV b-jet. Lost a 800 GeV mu :-)
    #if not 29094314 in r.evt: continue #Evt 13 100 GeV, lost gammas at -2.069/-2.430
    #if not 40308549 in r.evt: continue #Evt 18, MuMu 140 GeV, lost gammas at 0.985/1.688
    #if not 52311562 in r.evt: continue #Evt 20, EMu, 140 GeV lost gammas at 3.024/2.659 (energy is lost in crack between HE and HF)
    #if not 52834013 in r.evt: continue #Evt 21, EMu, 120 GeV, two jet mism 
    #if not 54909633 in r.evt: continue #Evt 23, 50 GeV -> looks OK? several small mism.
    #if not 59284952 in r.evt: continue #Evt 25, 115 GeV, several gammas lost at -0.093/-1.037
    #if not 61847446 in r.evt: continue #Evt 26, 50 GeV, small mism adding up.
    #if not 65772127 in r.evt: continue #Evt 28, EE, 116 GeV, several high pt gamma lost at 1.455/2.789 (plus some smaller mism in other directions, 1.141/-3.027)
    #if not 71404140 in r.evt: continue #Evt 31, 100 GeV isolated 100 GeV photon lost at -0.105/-2.545
    #if not 71630610 in r.evt: continue #Evt 32, 120 GeV, few charged and neutral hadrons missed, reco'd 200 GeV jet instead of 300 
    #if not 73435936 in r.evt: continue #Evt 33, 55 GeV, don't have the guy (2/38)
    #if not 78110867 in r.evt: continue #Evt 34, 350 GeV, lost 300 GeV gamma at 1.775/-2.024
    #if not 87143733 in r.evt: continue #Evt 35, 78 GeV, don't have the guy
    #if not 96010586 in r.evt: continue #Evt 36, 252 GeV, lost 50 GeV electron at 2.396/-1.872, MET comes from spurious (isolated??) e- of 311 GeV at 0.11/-1.57 (almost back to back)
    #if not 99537081 in r.evt: continue #Evt 37, MuMu, 114 GeV, lost 40 GeV gamma at -0.101/2.089, lost a few more neutrals


    gp = filter(lambda p:p.status()==1, r.products['gen'])
    gp.sort(key = lambda p: - p.pt() )

    pf = list(r.products['pf'])
    pf.sort(key = lambda p: - p.pt() )

#    for i in range(min([20, len(gp)])):
#        p = gp[i]
#        print "gen %10s pt/eta/phi %5.1f/%5.3f/%5.3f" % (\
#            pdgToName(gp[i].pdgId()), gp[i].pt(), gp[i].eta(), gp[i].phi(),
#            )
##        print
##        printHisto(p)
##        print
##    print
#
#    print "Matching leading gen particles"
#    for i in range(min([20, len(gp)])):
#        p = gp[i]
#        print "gen %10s pt/eta/phi %5.1f/%5.3f/%5.3f" % (\
#            pdgToName(gp[i].pdgId()), gp[i].pt(), gp[i].eta(), gp[i].phi(),
#            )
#
#        print 
#        reco_matches = filter( lambda m:m[0]<0.2, [ ( deltaR(toDict(reco),toDict(p)), reco ) for reco in pf ] )
#        reco_matches.sort( key = lambda m:m[0] )
#        gen_matches = [gen for gen in gp if gen.status()==1 and abs(gen.pdgId()) not in [12,14,16] and deltaR(toDict(gen), toDict(p))<0.2 ]
#        gen_matches = [(deltaR(toDict(gen),toDict(p)), gen ) for gen in gen_matches]
#        gen_matches.sort( key = lambda m:m[0] )
#        gen_sumPt, reco_sumPt = vecSumPt([g[1] for g in gen_matches]), vecSumPt([g[1] for g in reco_matches])
#        mismatched =  abs(gen_sumPt-reco_sumPt)>30
#        if mismatched: diff_str = bold("%5.1f"%(gen_sumPt-reco_sumPt))
#        else         : diff_str = "%5.1f"%(gen_sumPt-reco_sumPt)
#        print "   balancing 0.2 cone: gen %5.1f reco %5.1f diff %s" % (vecSumPt([g[1] for g in gen_matches]), vecSumPt([g[1] for g in reco_matches]) , diff_str)
#        for dr, reco in reco_matches: 
#            print "      reco %10s dr %3.2f pt/eta/phi %5.1f/%5.3f/%5.3f" % (\
#                pdgToName(reco.pdgId()), dr, reco.pt(), reco.eta(), reco.phi(),
#                )
#        print
#        for dr, gen in gen_matches: 
#            print "      gen  %10s dr %3.2f pt/eta/phi %5.1f/%5.3f/%5.3f" % (\
#                pdgToName(gen.pdgId()), dr, gen.pt(), gen.eta(), gen.phi(),
#                )
#        print 
#    break

    reco_muons = filter( lambda p:abs(p.pdgId())==13, pf )
    for i, m in enumerate(reco_muons):
        if m.pt()<15: continue
        gen_matches = [(deltaR(toDict(gen),toDict(m)), gen ) for gen in gp if gen.status()==1 and abs(gen.pdgId()) in [13] and deltaR(toDict(gen), toDict(m))<0.2 ]
        gen_matches.sort( key = lambda m:m[0] )
        if len(gen_matches) == 0:
            print "No gen match found! Reco %3.2f/%3.2f/%3.2f"%(m.pt(), m.eta(), m.phi())
            continue
        if abs(m.pt()-gen_matches[0][1].pt())/m.pt()>0.1:
            gm = gen_matches[0][1]
            print "Muon mismeasurement. Reco %3.2f/%3.2f/%3.2f Gen %3.2f/%3.2f/%3.2f"%(m.pt(), m.eta(), m.phi(), gm.pt(), gm.eta(), gm.phi())

         

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

