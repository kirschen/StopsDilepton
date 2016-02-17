import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, deltaPhi
from StopsDilepton.tools.texHelpers import latexmaker_1, piemaker
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts
from StopsDilepton.tools.user import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 100 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = False
makelatextables = False #Ignore this if you're not Ward
mt2llcuts = {'0':0.,'80':80., '100':100., '110':110., '120':120., '130':130., '140':140., '150':150.} #make plots named mt2llwithcutat..... I.E. lines 134-136
btagcoeff = 0.89
metcut = '40'
metsignifcut = 0.
dphicut = 0.
luminosity = 10000.

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#See here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>'+metcut+'&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>'+str(btagcoeff)+')>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)==2'
#preselection = "met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2"

#######################################################
#                 load all the samples                #
#######################################################
#from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
#backgrounds = [diBosons_50ns,WJetsToLNu_50ns,singleTop_50ns,QCDMu_50ns,DYHT_50ns,TTJets_50ns]
backgrounds = [diBosons_25ns,WJetsToLNu_25ns,singleTop_25ns,QCDMu_25ns,DYHT_25ns,TTJets_25ns]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
data = [DoubleEG_25ns,DoubleMuon_25ns,MuonEG_25ns]

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals+data:
    s['chain'] = getChain(s,histname="")

#######################################################
#           define binning of 1D histograms           #
#######################################################
mllbinning = [25,25,325]
#mt2llbinning = [25,0,300]
mt2llbinning = [4,0,300]
metbinning = [20,0,800]
mt2bbbinning = [4,0,550]
mt2blblbinning = [4,0,550]
kinMetSigbinning = [25,0,25]
leadingjetptbinning = [25,25,575]
subleadingjetptbinning = [25,25,575]
leadingleptonptbinning = [25,25,575]
subleadingleptonptbinning = [25,25,575]
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]
cosbinning = [25,-1.1,1.1]
partonbinning = [32,-10,22]
phibinning = [20,0,pi]
htbinning = [20,0,1500]

#######################################################
#             make plot in each sample:               #
#######################################################
plots = {\
    'mumu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
    'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
    'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
    'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
    'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
    'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    },
    'ee':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
    'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
    'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
    'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
    'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
    'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    },
    'emu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
    'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
    'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
    'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
    'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
    'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    },
}

for channel in plots.keys():
    for mt2llcut in mt2llcuts.keys():
        plots[channel]['mt2llwithcut'+mt2llcut] = {'title':'M_{T2ll} (GeV)', 'name':'MT2llwithcutat'+str(mt2llcut), 'binning': mt2llbinning, 'histo':{}}


#######################################################
#          make plots specifically for SF             #
#######################################################
plotsSF = {\
    'SF':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
    'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
    'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
    'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
    'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
    'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    },
}

for channel in plotsSF.keys():
    for mt2llcut in mt2llcuts.keys():
            plotsSF[channel]['mt2llwithcut'+mt2llcut] = {'title':'M_{T2ll} (GeV)', 'name':'MT2llwithcutat'+str(mt2llcut), 'binning': mt2llbinning, 'histo':{}}


#######################################################
#                   2D plots                          #
#######################################################
dimensional = {\
    'ee': {\
        'mt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)', 'name': 'MT2blblvsMT2ll', 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
    # 'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
  },
    'mumu': {\
        'mt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)', 'name': 'MT2blblvsMT2ll', 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
    # 'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
  },
    'emu': {\
        'mt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)', 'name': 'MT2blblvsMT2ll', 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
    # 'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
    }
}

dimensionalSF={\
    'SF': {\
        'mt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)', 'name': 'MT2blblvsMT2ll', 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
    # 'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
    # 'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
    # 'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
    # 'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
    }
}

threedimensional={\
    'ee':{\
        'mt2bbvsmt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)','ztitle':'M_{T2bb} (GeV)', 'name': 'MT2bbvsMT2blblvsMT2ll', 'zbinning': mt2bbbinning, 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    },
    'mumu':{\
        'mt2bbvsmt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)','ztitle':'M_{T2bb} (GeV)', 'name': 'MT2bbvsMT2blblvsMT2ll', 'zbinning': mt2bbbinning, 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    },
    'emu':{\
        'mt2bbvsmt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)','ztitle':'M_{T2bb} (GeV)', 'name': 'MT2bbvsMT2blblvsMT2ll', 'zbinning': mt2bbbinning, 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    },
}

threedimensionalSF={\
    'SF':{\
        'mt2bbvsmt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)','ztitle':'M_{T2bb} (GeV)', 'name': 'MT2bbvsMT2blblvsMT2ll', 'zbinning': mt2bbbinning, 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
    },
}

#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals+data:
    #construct 1D histograms
    for pk in plots.keys():
        for plot in plots[pk].keys():
            plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
            plots[pk][plot]['histo'][s["name"]].Sumw2()
    #construct 2D histograms
    for pk in dimensional.keys():
        for plot in dimensional[pk].keys():
            dimensional[pk][plot]['histo'][s["name"]] = ROOT.TH2F(dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['xbinning'][0], dimensional[pk][plot]['xbinning'][1],dimensional[pk][plot]['xbinning'][2], dimensional[pk][plot]['ybinning'][0], dimensional[pk][plot]['ybinning'][1],dimensional[pk][plot]['ybinning'][2])
    #construct 3D histograms
    for pk in threedimensional.keys():
        for plot in threedimensional[pk].keys():
            threedimensional[pk][plot]['histo'][s["name"]] = ROOT.TH3F(threedimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, threedimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, threedimensional[pk][plot]['xbinning'][0], threedimensional[pk][plot]['xbinning'][1],threedimensional[pk][plot]['xbinning'][2], threedimensional[pk][plot]['ybinning'][0], threedimensional[pk][plot]['ybinning'][1],threedimensional[pk][plot]['ybinning'][2], threedimensional[pk][plot]['zbinning'][0], threedimensional[pk][plot]['zbinning'][1],threedimensional[pk][plot]['zbinning'][2])

    chain = s["chain"]

    chain.SetBranchStatus("*",0)
    chain.SetBranchStatus("met_pt",1)
    chain.SetBranchStatus("met_phi",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("LepGood_pt",1)
    chain.SetBranchStatus("LepGood_eta",1)
    chain.SetBranchStatus("LepGood_phi",1)
    chain.SetBranchStatus("LepGood_charge",1)
    chain.SetBranchStatus("LepGood_dxy",1)
    chain.SetBranchStatus("LepGood_dz",1)
    chain.SetBranchStatus("LepGood_relIso03",1)
    chain.SetBranchStatus("LepGood_tightId",1)
    chain.SetBranchStatus("LepGood_pdgId",1)
    chain.SetBranchStatus("LepGood_mediumMuonId",1)
    chain.SetBranchStatus("LepGood_miniRelIso",1)
    chain.SetBranchStatus("LepGood_sip3d",1)
    chain.SetBranchStatus("LepGood_mvaIdPhys14",1)
    chain.SetBranchStatus("LepGood_convVeto",1)
    chain.SetBranchStatus("LepGood_lostHits",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_phi",1)
    chain.SetBranchStatus("Jet_btagCMVA",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("weight",1)
    if s not in data:
        chain.SetBranchStatus("genWeight",1)
        chain.SetBranchStatus("Jet_mcMatchFlav",1)
        chain.SetBranchStatus("xsec",1)
        chain.SetBranchStatus("Jet_partonId",1)

    #Using Event loop
    #get EList after preselection
    print '\n', "Looping over %s" % s["name"]
    eList = getEList(chain, preselection)
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)

    for ev in range(nEvents):

        increment = 50
        if nEvents>increment and ev%(nEvents/increment)==0:
            sys.stdout.write('\r' + "=" * (ev / (nEvents/increment)) +  " " * ((nEvents - ev)/ (nEvents/increment)) + "]" +  str(round((ev+1) / (float(nEvents)/100),2)) + "%")
            sys.stdout.flush()
            sys.stdout.write('\r')
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        #event weight (L= 4fb^-1)
        weight = reduceStat*getVarValue(chain, "weight")

        if s not in data: weight = weight*(luminosity/1000.)

        #MET
        met = getVarValue(chain, "met_pt")
        metPhi = getVarValue(chain, "met_phi")
        #jetpt
        leadingjetpt = getVarValue(chain, "Jet_pt",0)
        subleadingjetpt = getVarValue(chain, "Jet_pt",1)
        #Leptons
        allLeptons = getLeptons(chain)
        muons = filter(looseMuID, allLeptons)
        electrons = filter(looseEleID, allLeptons)

        #SF and OF channels
        leptons = {\
            'mu':   {'name': 'mumu', 'file': muons},
            'e':   {'name': 'ee', 'file': electrons},
            'emu': {'name': 'emu', 'file': [electrons,muons]},
            }

        for lep in leptons.keys():
            twoleptons = False
            #Same Flavor
            if lep != 'emu':
                if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:
                    #genmatching(leptons[lep]['file'][0],genparticles)
                    twoleptons = True
                    l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
                    l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
                    leadingleptonpt = l0pt
                    subleadingleptonpt = l1pt
                    mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                    plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
                    zveto = True
            #Opposite Flavor
            if lep == 'emu':
                if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
                    twoleptons = True
                    l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
                    l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
                    if l1pt > l0pt :
                        leadingleptonpt = l1pt
                        subleadingleptonpt = l0pt
                    else:
                        leadingleptonpt = l0pt
                        subleadingleptonpt = l1pt
                    mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                    plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
                    zveto = False
            if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-91.2)>15):
                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                ht = sum([j['pt'] for j in jets])
                PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
                PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))

                if PhiMetJet1 <= PhiMetJet2: PhiMetJet_small = PhiMetJet1
                else:                        PhiMetJet_small = PhiMetJet2

                if (met/sqrt(ht)) >= metsignifcut and PhiMetJet_small >= dphicut:

                    plots[leptons[lep]['name']]['leadingjetpt']['histo'][s["name"]].Fill(leadingjetpt, weight)
                    plots[leptons[lep]['name']]['subleadingjetpt']['histo'][s["name"]].Fill(subleadingjetpt, weight)
                    plots[leptons[lep]['name']]['leadingleptonpt']['histo'][s["name"]].Fill(leadingleptonpt, weight)
                    plots[leptons[lep]['name']]['subleadingleptonpt']['histo'][s["name"]].Fill(subleadingleptonpt, weight)
                    mt2Calc.setMet(met,metPhi)
                    mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)

                    mt2ll = mt2Calc.mt2ll()

                    plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)

                    for mt2llcut in mt2llcuts.keys():
                        if mt2ll >= mt2llcuts[mt2llcut]: plots[leptons[lep]['name']]['mt2llwithcut'+mt2llcut]['histo'][s["name"]].Fill(mt2ll, weight)

                    #dimensional[leptons[lep]['name']]['metvsmt2ll']['histo'][s["name"]].Fill(mt2ll,met)
                    #dimensional[leptons[lep]['name']]['MT2llvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),mt2ll)
                    #dimensional[leptons[lep]['name']]['MT2llvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),mt2ll)
                    #dimensional[leptons[lep]['name']]['MT2llvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,mt2ll)
                    #dimensional[leptons[lep]['name']]['MT2llvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,mt2ll)
                    #dimensional[leptons[lep]['name']]['metvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
                    #dimensional[leptons[lep]['name']]['metvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
                    #dimensional[leptons[lep]['name']]['metvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,met)
                    #dimensional[leptons[lep]['name']]['metvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,met)
                    if (PhiMetJet1 <= PhiMetJet2): #selecting min(dPhi)
                        #dimensional[leptons[lep]['name']]['MT2llvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),mt2ll)
                        #dimensional[leptons[lep]['name']]['MT2llvsMinDphi']['histo'][s['name']].Fill(PhiMetJet1,mt2ll)
                        plots[leptons[lep]['name']]['CosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),weight)
                        plots[leptons[lep]['name']]['MinDphi']['histo'][s['name']].Fill(PhiMetJet1,weight)
                        #dimensional[leptons[lep]['name']]['metvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
                        #dimensional[leptons[lep]['name']]['metvsMinDphi']['histo'][s['name']].Fill(PhiMetJet1,met)
                        if (mt2ll>=80):
                            plots[leptons[lep]['name']]['CosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet1),weight)
                            plots[leptons[lep]['name']]['MinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet1,weight)
                            #dimensional[leptons[lep]['name']]['metvsCosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
                            #dimensional[leptons[lep]['name']]['metvsMinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet1,met)
                    else:
                        #dimensional[leptons[lep]['name']]['MT2llvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),mt2ll)
                        #dimensional[leptons[lep]['name']]['MT2llvsMinDphi']['histo'][s['name']].Fill(PhiMetJet2,mt2ll)
                        plots[leptons[lep]['name']]['CosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),weight)
                        plots[leptons[lep]['name']]['MinDphi']['histo'][s['name']].Fill(PhiMetJet2,weight)
                        #dimensional[leptons[lep]['name']]['metvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
                        #dimensional[leptons[lep]['name']]['metvsMinDphi']['histo'][s['name']].Fill(PhiMetJet2,met)
                        if mt2ll>=80:
                            plots[leptons[lep]['name']]['CosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet2),weight)
                            plots[leptons[lep]['name']]['MinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet2,weight)
                            #dimensional[leptons[lep]['name']]['metvsCosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
                            #dimensional[leptons[lep]['name']]['metvsMinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet2,met)

                    plots[leptons[lep]['name']]['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)

                    plots[leptons[lep]['name']]['met']['histo'][s["name"]].Fill(met, weight)
                    bjetspt = filter(lambda j:j['btagCSV']>btagcoeff, jets)
                    nobjets = filter(lambda j:j['btagCSV']<=btagcoeff, jets)
                    plots[leptons[lep]['name']]['njets']['histo'][s["name"]].Fill(len(jets),weight)
                    plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
                    plots[leptons[lep]['name']]['ht']['histo'][s["name"]].Fill(ht,weight)
                    if s not in data: plots[leptons[lep]['name']]['leadingjetpartonId']['histo'][s["name"]].Fill(getVarValue(chain,"Jet_partonId",0),weight)
                    #2 or more bjets: two highest pt
                    if len(bjetspt)>=2:
                        mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], bjetspt[1]['pt'], bjetspt[1]['eta'], bjetspt[1]['phi'])
                    #1 bjets: bjet+jet with highest pt
                    if len(bjetspt)==1 and len(nobjets)>0:
                        mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], nobjets[0]['pt'], nobjets[0]['eta'], nobjets[0]['phi'])
                    if (len(bjetspt)==0) or (len(bjetspt)==1 and len(nobjets)==0): #last one seems necessary if btagCSV is 'nan'
                        continue
                    mt2bb   = mt2Calc.mt2bb()
                    mt2blbl = mt2Calc.mt2blbl()
                    plots[leptons[lep]['name']]['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
                    plots[leptons[lep]['name']]['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
                    dimensional[leptons[lep]['name']]['mt2blblvsmt2ll']['histo'][s["name"]].Fill(mt2ll,mt2blbl, weight)
                    threedimensional[leptons[lep]['name']]['mt2bbvsmt2blblvsmt2ll']['histo'][s["name"]].Fill(mt2ll,mt2blbl,mt2bb,weight)

      #Add overflow bin to last bin
    for pk in plots.keys():
        for plot in plots[pk].keys():
            nXbins = plots[pk][plot]['histo'][s['name']].GetNbinsX()
            overflow = plots[pk][plot]['histo'][s['name']].GetBinContent(nXbins+1)
            plots[pk][plot]['histo'][s['name']].AddBinContent(nXbins, overflow)
            plots[pk][plot]['histo'][s['name']].SetBinContent(nXbins+1, 0)
            overflow2 = plots[pk][plot]['histo'][s['name']].GetBinContent(nXbins+1)


    for pk in plots:

        #ROOT output file
        TreeFile = ROOT.TFile("./trees_metcut"+metcut+"/"+s["name"]+"_"+pk+".root","recreate")

        mt2llwithcutsoutput = {}
        for mt2llcut in mt2llcuts:
            mt2llwithcutsoutput["mt2llcut_"+mt2llcut] = plots[pk]['mt2llwithcut'+mt2llcut]['histo'][s['name']].Clone()
        mt2lloutput = plots[pk]['mt2ll']['histo'][s['name']].Clone()
        mt2blblvsmt2lloutput = dimensional[pk]['mt2blblvsmt2ll']['histo'][s['name']].Clone()
        mt2bbvsmt2blblvsmt2lloutput = threedimensional[pk]['mt2bbvsmt2blblvsmt2ll']['histo'][s['name']].Clone()

        for mt2llcut in mt2llcuts:
            mt2llwithcutsoutput["mt2llcut_"+mt2llcut].SetName("h1_mt2llcounting_mt2llcut_"+mt2llcut)
        mt2lloutput.SetName("h1_mt2ll")
        mt2blblvsmt2lloutput.SetName("h2_mt2blblvsmt2ll")
        mt2bbvsmt2blblvsmt2lloutput.SetName("h3_mt2bbvsmt2blblvsmt2ll")

        TreeFile.cd()
        for mt2llcut in mt2llcuts:
            mt2llwithcutsoutput["mt2llcut_"+mt2llcut].Write()
        mt2lloutput.Write()
        mt2blblvsmt2lloutput.Write()
        mt2bbvsmt2blblvsmt2lloutput.Write()
        TreeFile.Close()
    del eList

#print plots['emu']['mt2ll']['histo'][TTJets_50ns['name']].Integral()
#print plots['mumu']['mt2ll']['histo'][TTJets_50ns['name']].Integral()

#######################################################
#           provide tables from histograms            #
#######################################################
if makelatextables:
    latexmaker_1('ee', plots, mt2llcut)
    latexmaker_1('mumu', plots, mt2llcut)
    latexmaker_1('emu',plots, mt2llcut)


#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring

TTJets_50ns["color"]=7
DYHT_50ns["color"]=8
QCDMu_50ns["color"]=46
singleTop_50ns["color"]=40
diBosons_50ns["color"]=ROOT.kOrange
WJetsToLNu_50ns['color']=ROOT.kRed-10
#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 10
ymaximum = 100
legendtextsize = 0.028
signalscaling = 100
histopad =  [0.01, 0.2, 0.99, 0.99]
datamcpad = [0.01, 0.08, 0.99, 0.3]

if makedraw1D:

    for pk in plots.keys():
        for plot in plots[pk].keys():
            #Make a stack for backgrounds
            l=ROOT.TLegend(0.6,0.6,0.99,1.0)
            l.SetFillColor(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(1)
            l.SetTextSize(legendtextsize)
            bkg_stack = ROOT.THStack("bkgs","bkgs")
            #totalbackground = plots[pk][plot]['histo'][backgrounds[0]["name"]].Clone()
            for b in backgrounds:
                plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
                bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
                l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])
                #if b != backgrounds[0]: totalbackground.Add(plots[pk][plot]['histo'][b["name"]])
            if len(data)!= 0:datahist = plots[pk][plot]['histo'][data[0]["name"]].Clone()
            for d in data[1:]:
                datahist.Add(plots[pk][plot]['histo'][d["name"]])
            if len(data)!= 0: datahist.SetMarkerColor(ROOT.kBlack)
        #Plot!
            c1 = ROOT.TCanvas()
            #pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
            #pad1.Draw()
            #pad1.cd()
            bkg_stack.SetMaximum(ymaximum*bkg_stack.GetMaximum())
            bkg_stack.SetMinimum(yminimum)
            bkg_stack.Draw()
            bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
            bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
            #bkg_stack.GetXaxis().SetLabelSize(0.)
            #pad1.SetLogy()
            c1.SetLogy()
            signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
            signalPlot_2 = plots[pk][plot]['histo'][signal['path'][2]].Clone()
            signalPlot_1.Scale(signalscaling)
            signalPlot_2.Scale(signalscaling)
            signalPlot_1.SetLineColor(ROOT.kRed)
            signalPlot_2.SetLineColor(ROOT.kBlue)
            signalPlot_1.SetLineWidth(3)
            signalPlot_2.SetLineWidth(3)
            signalPlot_1.Draw("HISTsame")
            signalPlot_2.Draw("HISTsame")
            if len(data)!= 0:datahist.Draw("peSAME")
            l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
            if len(data)!= 0: l.AddEntry(datahist, "data", "pe")
            l.Draw()
            channeltag = ROOT.TPaveText(0.4,0.75,0.59,0.85,"NDC")
            firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
            if firstlep == 'mu':
                firstlep = '#' + firstlep
            if secondlep == 'mu':
                secondlep = '#' + secondlep
            channeltag.AddText(firstlep+secondlep)
            if plots[pk][plot].has_key('tag'):
                print 'Tag found, adding to histogram'
                channeltag.AddText(plots[pk][plot]['tag'])
            channeltag.AddText("lumi: "+str(luminosity)+' pb^{-1}')
            channeltag.SetFillColor(ROOT.kWhite)
            channeltag.SetShadowColor(ROOT.kWhite)
            channeltag.Draw()
            #c1.cd()
            #pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
            #pad2.SetGrid()
            #pad2.SetBottomMargin(0.4)
            #pad2.Draw()
            #pad2.cd()
            #ratio = datahist.Clone()
            #ratio.Divide(totalbackground)
            #ratio.SetMarkerStyle(20)
            #ratio.SetMarkerSize(0.5)
            #ratio.GetYaxis().SetTitle("Data/Bkg.")
            #ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
            #ratio.GetXaxis().SetTitleSize(0.2)
            #ratio.GetYaxis().SetTitleSize(0.18)
            #ratio.GetYaxis().SetTitleOffset(0.29)
            #ratio.GetXaxis().SetTitleOffset(0.8)
            #ratio.GetYaxis().SetLabelSize(0.1)
            #ratio.GetXaxis().SetLabelSize(0.18)
            #ratio.Draw("pe")
            #c1.cd()
            c1.Print(plotDir+"/test/1D/"+plots[pk][plot]['name']+"_"+pk+".png")

    for plot in plotsSF['SF'].keys():
        bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
        l=ROOT.TLegend(0.6,0.6,0.99,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        #totalbackground = plots['ee'][plot]['histo'][backgrounds[0]["name"]].Clone()
        #totalbackground.Add(plots['mumu'][plot]['histo'][backgrounds[0]["name"]])
        for b in backgrounds:
            bkgforstack = plots['ee'][plot]['histo'][b["name"]]
            bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
            bkg_stack_SF.Add(bkgforstack,"h")
            l.AddEntry(bkgforstack, b["name"])
            #if b != backgrounds[0]:
            #  totalbackground.Add(plots['ee'][plot]['histo'][b["name"]])
            #  totalbackground.Add(plots['mumu'][plot]['histo'][b["name"]])
        if len(data)!= 0:
            datahist = plots['ee'][plot]['histo'][data[0]["name"]].Clone()
            datahist.Add(plots['mumu'][plot]['histo'][data[0]["name"]])
            for d in data[1:]:
                datahist.Add(plots['ee'][plot]['histo'][d["name"]])
                datahist.Add(plots['mumu'][plot]['histo'][d["name"]])
            datahist.SetMarkerColor(ROOT.kBlack)
        c1 = ROOT.TCanvas()
        #pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
        #pad1.Draw()
        #pad1.cd()
        bkg_stack_SF.SetMaximum(ymaximum*bkg_stack_SF.GetMaximum())
        bkg_stack_SF.SetMinimum(yminimum)
        bkg_stack_SF.Draw()
        bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
        bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
        #bkg_stack_SF.GetXaxis().SetLabelSize(0.)
        #pad1.SetLogy()
        c1.SetLogy()
        signalPlot_1 = plots['ee'][plot]['histo'][signal['path'][0]].Clone()
        signalPlot_1.Add(plots['mumu'][plot]['histo'][signal['path'][0]])
        signalPlot_2 = plots['ee'][plot]['histo'][signal['path'][2]].Clone()
        signalPlot_2.Add(plots['mumu'][plot]['histo'][signal['path'][2]])
        signalPlot_1.Scale(signalscaling)
        signalPlot_2.Scale(signalscaling)
        signalPlot_1.SetLineColor(ROOT.kRed)
        signalPlot_2.SetLineColor(ROOT.kBlue)
        signalPlot_1.SetLineWidth(3)
        signalPlot_2.SetLineWidth(3)
        signalPlot_1.Draw("HISTsame")
        signalPlot_2.Draw("HISTsame")
        if len(data)!= 0: datahist.Draw("peSAME")
        l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
        l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
        if len(data)!= 0: l.AddEntry(datahist, "data", "pe")
        l.Draw()
        channeltag = ROOT.TPaveText(0.4,0.75,0.59,0.85,"NDC")
        channeltag.AddText("SF")
        if plotsSF['SF'][plot].has_key('tag'):
            print 'Tag found, adding to histogram'
            channeltag.AddText(plots[pk][plot]['tag'])
        channeltag.AddText("lumi: "+str(luminosity)+'pb^{-1}')
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.Draw()
        # c1.cd()
        # pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
        # pad2.SetGrid()
        # pad2.SetBottomMargin(0.4)
        # pad2.Draw()
        # pad2.cd()
        # ratio = datahist.Clone()
        # ratio.Divide(totalbackground)
        # ratio.SetMarkerStyle(20)
        # ratio.SetMarkerSize(0.5)
        # ratio.GetYaxis().SetTitle("Data/Bkg.")
        #   #ratio.GetYaxis().SetNdivisions(502)
        # ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
        # ratio.GetXaxis().SetTitleSize(0.2)
        # ratio.GetYaxis().SetTitleSize(0.18)
        # ratio.GetYaxis().SetTitleOffset(0.29)
        # ratio.GetXaxis().SetTitleOffset(0.8)
        # ratio.GetYaxis().SetLabelSize(0.1)
        # ratio.GetXaxis().SetLabelSize(0.18)
        # ratio.Draw("pe")
        # c1.cd()
        c1.Print(plotDir+"/test/1D/"+plotsSF['SF'][plot]['name']+"_SF.png")

if makedraw2D:

    c1 = ROOT.TCanvas()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(1)
    c1.SetRightMargin(0.16)
    c1.SetLogz()

    for pk in dimensional.keys():
        for plot in dimensional[pk].keys():
        #Plot!
            for s in backgrounds+signals:
                plot2D = dimensional[pk][plot]['histo'][s["name"]]

                plot2D.Draw("colz")
                if plot2D.Integral()==0:continue
                ROOT.gPad.Update()
                #palette = plot2D.GetListOfFunctions().FindObject("palette")
                #palette.SetX1NDC(0.85)
                #palette.SetX2NDC(0.9)
                #palette.Draw()
                plot2D.GetXaxis().SetTitle(dimensional[pk][plot]['xtitle'])
                plot2D.GetYaxis().SetTitle(dimensional[pk][plot]['ytitle'])

                l=ROOT.TLegend(0.25,0.95,0.9,1.0)
                l.SetFillColor(0)
                l.SetShadowColor(ROOT.kWhite)
                l.SetBorderSize(1)
                l.SetTextSize(legendtextsize)
                l.AddEntry(plot2D,s["name"])
                l.Draw()
                channeltag = ROOT.TPaveText(0.65,0.7,0.8,0.85,"NDC")
                firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
                if firstlep == 'mu':
                    firstlep = '#' + firstlep
                if secondlep == 'mu':
                    secondlep = '#' + secondlep
                channeltag.AddText(firstlep+secondlep)
                if s in signals:
                    index = signal['path'].index(s["name"])
                    channeltag.AddText(signal["name"][index])
                if s in backgrounds:
                    channeltag.AddText(s["name"])
                if dimensional[pk][plot].has_key('tag'):
                    print 'Tag found, adding to histogram'
                    channeltag.AddText(dimensional[pk][plot]['tag'])
                channeltag.AddText("lumi: "+str(luminosity)+'pb^{-1}')
                channeltag.SetFillColor(ROOT.kWhite)
                channeltag.SetShadowColor(ROOT.kWhite)
                channeltag.Draw()

                c1.Print(plotDir+"/test/2D/"+dimensional[pk][plot]['name']+"/"+dimensional[pk][plot]['name']+"_"+pk+"_"+s['name']+".png")
                c1.Clear()

    for pk in dimensionalSF.keys():
        for plot in dimensionalSF[pk].keys():
            for s in backgrounds+signals:
                plot2DSF = dimensional['ee'][plot]['histo'][s["name"]]
                plot2DSF.Add(dimensional['mumu'][plot]['histo'][s["name"]])

                plot2DSF.Draw("colz")
                if plot2DSF.Integral()==0:continue
                ROOT.gPad.Update()
                # palette = plot2DSF.GetListOfFunctions().FindObject("palette")
                # palette.SetX1NDC(0.85)
                # palette.SetX2NDC(0.9)
                # palette.Draw()
                plot2DSF.GetXaxis().SetTitle(dimensionalSF[pk][plot]['xtitle'])
                plot2DSF.GetYaxis().SetTitle(dimensionalSF[pk][plot]['ytitle'])

                l=ROOT.TLegend(0.25,0.95,0.9,1.0)
                l.SetFillColor(0)
                l.SetShadowColor(ROOT.kWhite)
                l.SetBorderSize(1)
                l.SetTextSize(legendtextsize)
                l.AddEntry(plot2DSF,s["name"])
                l.Draw()
                channeltag = ROOT.TPaveText(0.65,0.7,0.8,0.85,"NDC")
                channeltag.AddText("SF")
                if s in signals:
                    index = signal['path'].index(s["name"])
                    channeltag.AddText(signal["name"][index])
                if s in backgrounds:
                    channeltag.AddText(s["name"])
                if dimensionalSF['SF'][plot].has_key('tag'):
                    print 'Tag found, adding to histogram'
                    channeltag.AddText(dimensionalSF[pk][plot]['tag'])
                channeltag.AddText("lumi: "+str(luminosity)+'pb^{-1}')
                channeltag.SetFillColor(ROOT.kWhite)
                channeltag.SetShadowColor(ROOT.kWhite)
                channeltag.Draw()

                c1.Print(plotDir+"/test/2D/"+dimensionalSF[pk][plot]['name']+"/"+dimensionalSF[pk][plot]['name']+"_"+pk+"_"+s['name']+".png")
                c1.Clear()
