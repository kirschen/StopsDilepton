import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array, operator
from StopsDilepton.tools.helpers import getObjDict, getEList, getVarValue, deltaR, getObjFromFile
from StopsDilepton.tools.objectSelection import getGenPartsAll, getGoodLeptons, getLeptons, looseMuID, looseEleID, getJets, leptonVars, jetVars, getGoodTaus
from StopsDilepton.tools.genParticleTools import getDaughters, descendDecay, decaysTo, printDecay
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.user import *

from RootTools.core.standard import *

lumiScale = 10.
lepPdgs = [11,13,15]
nuPdgs = [12,14,16]

maxN = -1

ttjets =  Sample.fromDirectory(name="TTJets_Lep", treeName="Events", isData=False, color=7, texName="t#bar{t} + Jets (lep)", \
            directory=['/scratch/rschoefbeck/cmgTuples/fromTom/postProcessed_Fall15_mAODv2/dilep/TTJets_DiLepton_comb/'], maxN = maxN)

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))

cuts=[
  ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
  ("njet2", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  ("nbtag1", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("mll20", "dl_mass>20"),
  ("met80", "met_pt>80"),
  ("metSig5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
  ("isOS","isOS==1"),
  ("SFZVeto","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
#  ("tauVeto","Sum$(TauGood_pt>20 && abs(TauGood_eta)<2.4 && TauGood_idDecayModeNewDMs>=1 && TauGood_idCI3hit>=1 && TauGood_idAntiMu>=1 && TauGood_idAntiE>=1)==0"),
#  ("mRelIso01", "LepGood_miniRelIso[l1_index]<0.1&&LepGood_miniRelIso[l2_index]<0.1"),
  ("multiIsoWP", multiIsoWP),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
#  ("evt", "evt==68296914")
    ]

#prefix+="_tauVeto_mRelIso01_looseLepVeto"
preselection = "&&".join([c[1] for c in cuts])

#ttjets.chain.Draw("min(LepGood_jetPtRatiov2[l1_index], LepGood_jetPtRatiov2[l2_index]):min(LepGood_jetPtRelv2[l1_index], LepGood_jetPtRelv2[l2_index])>>h(100,0,30,100,0,1.2)", preselection+"&&dl_mt2ll<100", "COLZ")
h = ROOT.TH2F("x","x", 100,0,30,100,0,1.2)
h.Draw()
evtList = ttjets.getEList( preselection+"&&dl_mt2ll>140")
stuff=[]
for i in range(evtList.GetN()):
    ttjets.chain.GetEntry(evtList.GetEntry(i))
    allLeptons = getLeptons(ttjets.chain, collVars=leptonVars+['mcMatchId','mcMatchAny','mcMatchTau','mcPt','ip3d', 'relIso03', 'relIso04', 'jetPtRatiov1', 'jetPtRelv1', 'jetPtRelv2', 'jetPtRatiov2', 'jetBTagCSV', 'jetDR'])
    leptons = filter(lambda l: looseMuID(l) or looseEleID(l), allLeptons)
    l = ROOT.TLine(leptons[0]['jetPtRelv2'], leptons[0]['jetPtRatiov2'], leptons[1]['jetPtRelv2'], leptons[1]['jetPtRatiov2']) 
    l.Draw()
    stuff.append(l)
