import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy, os, glob

from math import *
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, deltaPhi
from StopsDilepton.tools.texHelpers import latexmaker_1
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts, getGoodLeptons, getGoodElectrons, getGoodMuons
from StopsDilepton.tools.user import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator

mt2Calc = mt2Calculator()


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat         = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
scaletodata        = True
makedraw1D         = True
makedraw2D         = False
makelatextables    = True #Ignore this if you're not Ward
mt2llcuts          = {'0':0.,'80':80., '100':100., '110':110., '120':120., '130':130., '140':140., '150':150.} #make plots named mt2llwithcutat..... I.E. lines 134-136
btagcoeff          = 0.89
metcut             = 80.
metsignifcut       = 5.
dphicut            = 0.25
mllcut             = 20
ngoodleptons       = 2
#luminosity         = 1500
njetscut           = [">=2",'2m']
nbjetscut          = [">=1",'1m']

presel_met         = 'met_pt>'+str(metcut)
presel_nbjet       = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>'+str(btagcoeff)+')'+nbjetscut[0]
presel_njet        = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)'+njetscut[0]
presel_metsig      = 'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>'+str(metsignifcut)
presel_mll         = 'dl_mass>'+str(mllcut)
presel_ngoodlep    = '((nGoodMuons+nGoodElectrons)=='+str(ngoodleptons)+')'
presel_OS          = 'isOS'
presel_dPhi        = 'cos(met_phi-Jet_phi[0])<cos('+str(dphicut)+')&&cos(met_phi-Jet_phi[1])<cos('+str(dphicut)+')'

dataCut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#See here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = presel_met+'&&'+presel_nbjet+'&&'+presel_njet+'&&'+presel_metsig+'&&'+presel_mll+'&&'+presel_ngoodlep+'&&'+presel_OS+'&&'+presel_dPhi

#######################################################
#                 load all the samples                #
#######################################################
#from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

#backgrounds = [QCD_Mu5,WJetsToLNu,diBoson,DY_HT_LO,singleTop,TTX,TTJets]
backgrounds = [QCD_Mu5,WJetsToLNu,diBoson,DY_HT_LO,singleTop,TTW,TTZ,TZQ,TTH,TTJets]
#backgrounds = [TTJets]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []
data = [DoubleEG_Run2015D,DoubleMuon_Run2015D,MuonEG_Run2015D]
#data = []

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals+data:
    s['chain'] = getChain(s,histname="")
    s['name'] = s["name"].replace(" ","")
    s['name'] = s["name"].replace("(","_")
    s['name'] = s["name"].replace(",","_")
    s['name'] = s["name"].replace(")","_")

#######################################################
#           define binning of 1D histograms           #
#######################################################
mllbinning = [50,0,150]
metbinning = [20,0,800]
mt2llbinning = [3,0,300]
mt2bbbinning = [3,70,370]
mt2blblbinning = [3,0,300]
mt2llbinninglong = [25,0,300]
mt2bbbinninglong = [25,70,370]
mt2blblbinninglong = [25,0,300]
kinMetSigbinning = [25,0,25]
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]
phibinning = [20,0,pi]
htbinning = [20,0,1500]
nvertbinning = [30,0,30]
ntrueintbinning = [30,0,30]

#######################################################
#             make plot in each sample:               #
#######################################################
plots = {\
    'mumu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'mt2lllong': {'title':'M_{T2ll} (GeV)', 'name':'MT2lllong', 'binning': mt2llbinninglong, 'histo':{}},
    'mt2bblong':{'title':'M_{T2bb} (GeV)', 'name':'MT2bblong', 'binning': mt2bbbinninglong, 'histo':{}},
    'mt2blbllong':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbllong', 'binning': mt2blblbinninglong, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    'nvert':{'title':'nVert', 'name':'nVert', 'binning':nvertbinning,'histo':{}},
    },
    'ee':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'mt2lllong': {'title':'M_{T2ll} (GeV)', 'name':'MT2lllong', 'binning': mt2llbinninglong, 'histo':{}},
    'mt2bblong':{'title':'M_{T2bb} (GeV)', 'name':'MT2bblong', 'binning': mt2bbbinninglong, 'histo':{}},
    'mt2blbllong':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbllong', 'binning': mt2blblbinninglong, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    'nvert':{'title':'nVert', 'name':'nVert', 'binning':nvertbinning,'histo':{}},
    },
    'emu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'mt2lllong': {'title':'M_{T2ll} (GeV)', 'name':'MT2lllong', 'binning': mt2llbinninglong, 'histo':{}},
    'mt2bblong':{'title':'M_{T2bb} (GeV)', 'name':'MT2bblong', 'binning': mt2bbbinninglong, 'histo':{}},
    'mt2blbllong':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbllong', 'binning': mt2blblbinninglong, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
    'ht':{'title':'H_{T} (GeV)', 'name':'HT', 'binning':htbinning, 'histo':{}},
    'nvert':{'title':'nVert', 'name':'nVert', 'binning':nvertbinning,'histo':{}},
    },
}

for channel in plots.keys():
    for mt2llcut in mt2llcuts.keys():
        plots[channel]['mt2llwithcut'+mt2llcut] = {'title':'M_{T2ll} (GeV)', 'name':'MT2llwithcutat'+str(mt2llcut), 'binning': mt2llbinning, 'histo':{}}



#######################################################
#                   2D plots                          #
#######################################################
dimensional = {\
    'ee': {\
        'mt2blblvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'M_{T2blbl} (GeV)', 'name': 'MT2blblvsMT2ll', 'ybinning': mt2blblbinning, 'xbinning': mt2llbinning, 'histo': {}},
        'metvsmetsig': {'xtitle': 'MET/#sqrt{H_{T}} (GeV^{1/2})', 'ytitle':'E^{miss}_{T} (GeV)', 'name':'METvsMETsig', 'ybinning':metbinning, 'xbinning': kinMetSigbinning, 'histo':{}},
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
        'metvsmetsig': {'xtitle': 'MET/#sqrt{H_{T}} (GeV^{1/2})', 'ytitle':'E^{miss}_{T} (GeV)', 'name':'METvsMETsig', 'ybinning':metbinning, 'xbinning': kinMetSigbinning, 'histo':{}},
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
        'metvsmetsig': {'xtitle': 'MET/#sqrt{H_{T}} (GeV^{1/2})', 'ytitle':'E^{miss}_{T} (GeV)', 'name':'METvsMETsig', 'ybinning':metbinning, 'xbinning': kinMetSigbinning, 'histo':{}},
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
        'metvsmetsig': {'xtitle': 'MET/#sqrt{H_{T}} (GeV^{1/2})', 'ytitle':'E^{miss}_{T} (GeV)', 'name':'METvsMETsig', 'ybinning':metbinning, 'xbinning': kinMetSigbinning, 'histo':{}},
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

######################################################
#	   Remove old trees_met histograms           #
######################################################
treepath = "./trees_metcut_"+str(int(metcut))+"_metsig_"+str(int(metsignifcut))+"/"
if not os.path.exists(treepath): os.makedirs(treepath)
treefiles = glob.glob(treepath+'/*')
for f in treefiles: os.remove(f)

#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals+data:
    #construct 1D histograms
    for pk in plots.keys():
        for plot in plots[pk].keys():
            plots[pk][plot]['histo'][s["name"]] = ROOT.TH1D(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
            plots[pk][plot]['histo'][s["name"]].Sumw2()
    #construct 2D histograms
    for pk in dimensional.keys():
        for plot in dimensional[pk].keys():
            dimensional[pk][plot]['histo'][s["name"]] = ROOT.TH2D(dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['xbinning'][0], dimensional[pk][plot]['xbinning'][1],dimensional[pk][plot]['xbinning'][2], dimensional[pk][plot]['ybinning'][0], dimensional[pk][plot]['ybinning'][1],dimensional[pk][plot]['ybinning'][2])
    #construct 3D histograms
    for pk in threedimensional.keys():
        for plot in threedimensional[pk].keys():
            threedimensional[pk][plot]['histo'][s["name"]] = ROOT.TH3D(threedimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, threedimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, threedimensional[pk][plot]['xbinning'][0], threedimensional[pk][plot]['xbinning'][1],threedimensional[pk][plot]['xbinning'][2], threedimensional[pk][plot]['ybinning'][0], threedimensional[pk][plot]['ybinning'][1],threedimensional[pk][plot]['ybinning'][2], threedimensional[pk][plot]['zbinning'][0], threedimensional[pk][plot]['zbinning'][1],threedimensional[pk][plot]['zbinning'][2])

    chain = s["chain"]

    chain.SetBranchStatus("*",0)
    chain.SetBranchStatus("nVert",1)
    chain.SetBranchStatus("met_pt",1)
    chain.SetBranchStatus("met_phi",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("LepGood_pt",1)
    chain.SetBranchStatus("LepGood_eta",1)
    chain.SetBranchStatus("LepGood_phi",1)
    chain.SetBranchStatus("LepGood_dxy",1)
    chain.SetBranchStatus("LepGood_dz",1)
    chain.SetBranchStatus("LepGood_tightId",1)
    chain.SetBranchStatus("LepGood_pdgId",1)
    chain.SetBranchStatus("LepGood_mediumMuonId",1)
    chain.SetBranchStatus("LepGood_miniRelIso",1)
    chain.SetBranchStatus("LepGood_sip3d",1)
    chain.SetBranchStatus("LepGood_convVeto",1)
    chain.SetBranchStatus("LepGood_lostHits",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_phi",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("weight",1)
    chain.SetBranchStatus("l1_pt",1)
    chain.SetBranchStatus("l2_pt",1)
    chain.SetBranchStatus("dl_mass",1)
    chain.SetBranchStatus("dl_mt2ll",1)
    chain.SetBranchStatus("dl_mt2bb",1)
    chain.SetBranchStatus("dl_mt2blbl",1)
    chain.SetBranchStatus("dl_mass",1)
    chain.SetBranchStatus("nGoodMuons",1)
    chain.SetBranchStatus("nGoodElectrons",1)
    chain.SetBranchStatus("isOS",1)
    chain.SetBranchStatus("isEE",1)
    chain.SetBranchStatus("isEMu",1)
    chain.SetBranchStatus("isMuMu",1)
    chain.SetBranchStatus("HLT_mumuIso",1)
    chain.SetBranchStatus("HLT_ee_DZ",1)
    chain.SetBranchStatus("HLT_mue",1)
    chain.SetBranchStatus("nVert",1)
    if s not in data:
        chain.SetBranchStatus("genWeight",1)
        chain.SetBranchStatus("xsec",1)
        chain.SetBranchStatus("weightPU",1)
        chain.SetBranchStatus("weightPUUp",1)
        chain.SetBranchStatus("weightPUDown",1)
    else:
        chain.SetBranchStatus("Flag_HBHENoiseFilter",1)
        chain.SetBranchStatus("Flag_goodVertices",1)
        chain.SetBranchStatus("Flag_CSCTightHaloFilter",1)
        chain.SetBranchStatus("Flag_eeBadScFilter",1)
    #Using Event loop
    #get EList after preselection
    print '\n', "Looping over %s" % s["name"]


    if s['isData'] : eList = getEList(chain, preselection+'&&'+dataCut)
    else:            eList = getEList(chain, preselection)


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

        #MET
        met = getVarValue(chain, "met_pt")
        metPhi = getVarValue(chain, "met_phi")
        #jetpt
        leadingjetpt = getVarValue(chain, "Jet_pt",0)
        subleadingjetpt = getVarValue(chain, "Jet_pt",1)
        #leptons
        l0pt = getVarValue(chain, "l1_pt")
        l1pt = getVarValue(chain, "l2_pt")
        mll = getVarValue(chain,"dl_mass")

        #Leptons
        nGoodMuons = getVarValue(chain,"nGoodMuons")
        nGoodElectrons = getVarValue(chain,"nGoodElectrons")

        isEE = getVarValue(chain, "isEE")
        isMuMu = getVarValue(chain, "isMuMu")
        isEMu = getVarValue(chain, "isEMu")

        #triggers
        triggerMuMu = getVarValue(chain,"HLT_mumuIso")
        triggerEleEle = getVarValue(chain,"HLT_ee_DZ")
        triggerMuEle = getVarValue(chain,"HLT_mue")

        #SF and OF channels
        channels = ['mumu','ee','emu']

        mumuselection = True if (triggerMuMu and isMuMu==1 and nGoodMuons==2 and nGoodElectrons==0) and abs(91.2-mll)>15 else False
        eeselection =   True if (triggerEleEle and isEE==1 and nGoodMuons==0 and nGoodElectrons==2) and abs(91.2-mll)>15 else False
        emuselection =  True if (triggerMuEle  and isEMu==1 and nGoodMuons==1 and nGoodElectrons==1) else False

        for channel in channels:
            if (channel=='mumu' and mumuselection) or (channel == 'ee' and eeselection) or (channel=='emu' and emuselection):
                if channel == 'mumu':
                    weight = reduceStat*getVarValue(chain, "weight")*(DoubleMuon_Run2015D['lumi']/1000.) if not s['isData'] else 1
                elif channel == 'ee':
                    weight = reduceStat*getVarValue(chain, "weight")*(DoubleEG_Run2015D['lumi']/1000.) if not s['isData'] else 1
                elif channel == 'emu':
                    weight = reduceStat*getVarValue(chain, "weight")*(MuonEG_Run2015D['lumi']/1000.) if not s['isData'] else 1

                plots[channel]['mll']['histo'][s['name']].Fill(mll,weight)

                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                ht = sum([j['pt'] for j in jets])
                PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
                PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))

                PhiMetJet_small = min(PhiMetJet1,PhiMetJet2)

                mt2ll = getVarValue(chain,"dl_mt2ll")

                if mt2ll>mt2llbinning[-1]:  mt2ll = mt2llbinning[-1]-1 #overflow bin

                if mt2ll<mt2llbinning[-2]:  mt2ll = mt2llbinning[-2]+1 #underflow bin

                plots[channel]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
                plots[channel]['mt2lllong']['histo'][s["name"]].Fill(mt2ll, weight)
                plots[channel]['nvert']['histo'][s['name']].Fill(getVarValue(chain,"nVert"),weight)

                for mt2llcut in mt2llcuts.keys():
                    if mt2ll >= mt2llcuts[mt2llcut]: plots[channel]['mt2llwithcut'+mt2llcut]['histo'][s["name"]].Fill(mt2ll, weight)

                plots[channel]['MinDphi']['histo'][s['name']].Fill(PhiMetJet_small,weight)
                dimensional[channel]['metvsmetsig']['histo'][s["name"]].Fill(met/sqrt(ht),met,weight)
                    #dimensional[channel]['metvsmt2ll']['histo'][s["name"]].Fill(mt2ll,met,weight)
                    #dimensional[channel]['MT2llvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),mt2ll,weight)
                    #dimensional[channel]['MT2llvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),mt2ll,weight)
                    #dimensional[channel]['MT2llvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,mt2ll,weight)
                    #dimensional[channel]['MT2llvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,mt2ll,weight)
                    #dimensional[channel]['metvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),met,weight)
                    #dimensional[channel]['metvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),met,weight)
                    #dimensional[channel]['metvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,met,weight)
                    #dimensional[channel]['metvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,met,weight)

                    #dimensional[channel]['MT2llvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet_small),mt2ll,weight)
                    #dimensional[channel]['MT2llvsMinDphi']['histo'][s['name']].Fill(PhiMetJet_small,mt2ll,weight)
                    #dimensional[channel]['metvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet_small),met,weight)
                    #dimensional[channel]['metvsMinDphi']['histo'][s['name']].Fill(PhiMetJet_small,met,weight)

                plots[channel]['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)

                plots[channel]['met']['histo'][s["name"]].Fill(met, weight)
                bjetspt = filter(lambda j:j['btagCSV']>btagcoeff, jets)
                nobjets = filter(lambda j:j['btagCSV']<=btagcoeff, jets)
                plots[channel]['njets']['histo'][s["name"]].Fill(len(jets),weight)
                plots[channel]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
                plots[channel]['ht']['histo'][s["name"]].Fill(ht,weight)

                mt2bb = getVarValue(chain, "dl_mt2bb")
                mt2blbl = getVarValue(chain, "dl_mt2blbl")

                if mt2bb>mt2bbbinning[-1]:  mt2bb = mt2bbbinning[-1] - 1 #overflow bin
                if mt2bb<mt2bbbinning[-2]:  mt2bb = mt2bbbinning[-2] + 1 #underflow bin
                if mt2blbl>mt2blblbinning[-1]:  mt2blbl = mt2blblbinning[-1] - 1 #overflow bin
                if mt2blbl<mt2blblbinning[-2]:  mt2blbl = mt2blblbinning[-2] + 1 #underflow bin

                plots[channel]['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
                plots[channel]['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
                plots[channel]['mt2bblong']['histo'][s["name"]].Fill(mt2bb, weight)
                plots[channel]['mt2blbllong']['histo'][s["name"]].Fill(mt2blbl, weight)
                dimensional[channel]['mt2blblvsmt2ll']['histo'][s["name"]].Fill(mt2ll,mt2blbl, weight)
                threedimensional[channel]['mt2bbvsmt2blblvsmt2ll']['histo'][s["name"]].Fill(mt2ll,mt2blbl,mt2bb,weight)
    del eList


    #############################################
    #         Overflow to last bin              #
    #############################################
    for pk in plots.keys():
      for plot in plots[pk].keys():
          nXbins = plots[pk][plot]['histo'][s['name']].GetNbinsX()
          overflow = plots[pk][plot]['histo'][s['name']].GetBinContent(nXbins+1)
          error = plots[pk][plot]['histo'][s['name']].GetBinError(nXbins)
          overflowerror = plots[pk][plot]['histo'][s['name']].GetBinError(nXbins+1)
          plots[pk][plot]['histo'][s['name']].AddBinContent(nXbins, overflow)
          plots[pk][plot]['histo'][s['name']].SetBinError(nXbins, sqrt(error**2+overflowerror**2))
          plots[pk][plot]['histo'][s['name']].SetBinContent(nXbins+1, 0.)
          plots[pk][plot]['histo'][s['name']].SetBinError(nXbins+1, 0.)

      # ##########################################
      #     bins with negative events to 0       #
      # ##########################################
          for i in range(nXbins):
              if plots[pk][plot]['histo'][s['name']].GetBinContent(i+1) < 0: plots[pk][plot]['histo'][s['name']].SetBinContent(i+1,0.)

      for plot in dimensional[pk].keys():
          nXbins = dimensional[pk][plot]['histo'][s['name']].GetNbinsX()
          nYbins = dimensional[pk][plot]['histo'][s['name']].GetNbinsY()
          for i in range(nXbins):
              for j in range(nYbins):
                  bin = dimensional[pk][plot]['histo'][s['name']].GetBin(i+1,j+1)
                  if dimensional[pk][plot]['histo'][s['name']].GetBinContent(bin) < 0: dimensional[pk][plot]['histo'][s['name']].SetBinContent(bin,0.)

      for plot in threedimensional[pk].keys():
          nXbins = threedimensional[pk][plot]['histo'][s['name']].GetNbinsX()
          nYbins = threedimensional[pk][plot]['histo'][s['name']].GetNbinsY()
          nZbins = threedimensional[pk][plot]['histo'][s['name']].GetNbinsZ()
          for i in range(nXbins):
              for j in range(nYbins):
                  for k in range(nZbins):
                      bin = threedimensional[pk][plot]['histo'][s['name']].GetBin(i+1,j+1,k+1)
                      if threedimensional[pk][plot]['histo'][s['name']].GetBinContent(bin) < 0: threedimensional[pk][plot]['histo'][s['name']].SetBinContent(bin,0.)

######################################
#          Scaling to data           #
######################################

if scaletodata:
    for channel in plots.keys():
        totalint = 0
        for b in backgrounds:
            totalint += plots[channel]['mt2ll']['histo'][b["name"]].Integral()
        for plot in plots[channel].keys():
            if channel == 'mumu':
                plots[channel][plot]['SF'] = plots[channel]['mt2ll']['histo'][DoubleMuon_Run2015D['name']].Integral()/totalint
            elif channel == 'ee':
                plots[channel][plot]['SF'] = plots[channel]['mt2ll']['histo'][DoubleEG_Run2015D['name']].Integral()/totalint
            elif channel == 'emu':
                plots[channel][plot]['SF'] = plots[channel]['mt2ll']['histo'][MuonEG_Run2015D['name']].Integral()/totalint
            for b in backgrounds:
                plots[channel][plot]['histo'][b["name"]].Scale(plots[channel][plot]['SF'])

    #############################################
    #            Write out trees                #
    #############################################

for s in backgrounds+signals+data:
    for pk in plots.keys():
        #ROOT output file
        TreeFile = ROOT.TFile(treepath+s["name"]+"_"+pk+".root","recreate")

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


#print plots['emu']['mt2ll']['histo'][DY_25ns['name']].Integral()
#print plots['ee']['mt2ll']['histo'][DY_25ns['name']].Integral()

# for s in backgrounds+data:
#   print s['name'], ", ee: ", plots['ee']['mt2ll']['histo'][s['name']].Integral()
#   print s['name'], ", mumu: ", plots['mumu']['mt2ll']['histo'][s['name']].Integral()
#   print s['name'], ", emu: ", plots['emu']['mt2ll']['histo'][s['name']].Integral()

#######################################################
#           provide tables from histograms            #
#######################################################
if makelatextables:
    latexmaker_1('ee', plots, mt2llcuts)
    latexmaker_1('mumu', plots, mt2llcuts)
    latexmaker_1('emu',plots, mt2llcuts)


#######################################################
#             Drawing done here                       #
#######################################################

#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 0.01
ymaximum = 1000
legendtextsize = 0.028
signalscaling = 100
histopad =  [0.0, 0.2, 1.0, .95]
datamcpad = [0.0, 0.0, 1.0, 0.2]
lumitagpos = [0.4,0.95,0.6,1.0]
channeltagpos = [0.45,0.8,0.6,0.85]
legendpos = [0.6,0.6,1.0,1.0]
scalepos = [0.8,0.95,1.0,1.0]
stuff=[]

if makedraw1D:
    for pk in plots.keys():
        for plot in plots[pk].keys():
            #Make a stack for backgrounds
            l=ROOT.TLegend(legendpos[0],legendpos[1],legendpos[2],legendpos[3])
            stuff.append(l)
            l.SetFillColor(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(1)
            l.SetTextSize(legendtextsize)
            bkg_stack = ROOT.THStack("bkgs","bkgs")
            totalbackground = plots[pk][plot]['histo'][backgrounds[0]["name"]].Clone()
            for b in sorted(backgrounds,key=lambda sort:plots[pk][plot]['histo'][sort['name']].Integral()):
                plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
                bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
                l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["texName"],"f")
                if b != backgrounds[0]: totalbackground.Add(plots[pk][plot]['histo'][b["name"]])
            if len(data)!= 0:
                if pk == 'emu' :
                    datahist = plots[pk][plot]['histo'][MuonEG_Run2015D["name"]].Clone()
                    luminosity = MuonEG_Run2015D['lumi']
                elif pk == 'ee' :
                    datahist = plots[pk][plot]['histo'][DoubleEG_Run2015D["name"]].Clone()
                    luminosity = DoubleEG_Run2015D['lumi']
                elif pk == 'mumu' :
                    datahist = plots[pk][plot]['histo'][DoubleMuon_Run2015D["name"]].Clone()
                    luminosity = DoubleMuon_Run2015D['lumi']
                datahist.SetMarkerColor(ROOT.kBlack)

            #Plot!
            c1 = ROOT.TCanvas("c1","c1",800,800)
            if len(data)>0:
                pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
                pad1.SetBottomMargin(0)
                pad1.SetTopMargin(0)
                pad1.SetRightMargin(0)
                pad1.Draw()
                pad1.cd()
            bkg_stack.SetMaximum(ymaximum*bkg_stack.GetMaximum())
            bkg_stack.SetMinimum(yminimum)
            bkg_stack.Draw()
            bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
            bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
            if len(data)>0:
                pad1.SetLogy()
                bkg_stack.GetXaxis().SetLabelSize(0.)
            else:           c1.SetLogy()
            if len(signals)>0:
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
                l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
                l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
            if len(data)!= 0:
                datahist.Draw("peSAME")
                l.AddEntry(datahist, "data", "pe")
            l.Draw()
            ROOT.gPad.RedrawAxis()
            channeltag = ROOT.TPaveText(channeltagpos[0],channeltagpos[1],channeltagpos[2],channeltagpos[3],"NDC")
            lumitag = ROOT.TPaveText(lumitagpos[0],lumitagpos[1],lumitagpos[2],lumitagpos[3],"NDC")
            scaletag = ROOT.TPaveText(scalepos[0],scalepos[1],scalepos[2],scalepos[3],"NDC")
            firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
            if firstlep == 'mu':
                firstlep = '#' + firstlep
            if secondlep == 'mu':
                secondlep = '#' + secondlep
            channeltag.AddText(firstlep+secondlep)
            if plots[pk][plot].has_key('tag'):
                print 'Tag found, adding to histogram'
                channeltag.AddText(plots[pk][plot]['tag'])
            lumitag.AddText("lumi: "+str(luminosity)+' pb^{-1}')
            scaletag.AddText("Scale Factor: " +str(round(plots[pk][plot]['SF'],2)))
            channeltag.SetFillColor(ROOT.kWhite)
            channeltag.SetShadowColor(ROOT.kWhite)
            channeltag.SetBorderSize(0)
            lumitag.SetFillColor(ROOT.kWhite)
            lumitag.SetShadowColor(ROOT.kWhite)
            lumitag.SetBorderSize(0)
            scaletag.SetShadowColor(ROOT.kWhite)
            scaletag.SetFillColor(ROOT.kWhite)
            scaletag.SetBorderSize(0)
            channeltag.Draw()
            if len(data)>0:
                c1.cd()
                pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
                pad2.SetGrid()
                pad2.SetBottomMargin(0.4)
                pad2.SetTopMargin(0)
                pad2.SetRightMargin(0)
                pad2.Draw()
                pad2.cd()
                ratio = datahist.Clone()
                stuff.append(ratio)
                ratio.Divide(totalbackground)
                ratio.SetMarkerStyle(20)
                ratio.GetYaxis().SetTitle("Data/Bkg.")
            #ratio.GetYaxis().SetNdivisions(502)
                ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
                ratio.GetXaxis().SetTitleSize(0.2)
                ratio.GetYaxis().SetTitleSize(0.18)
                ratio.GetYaxis().SetTitleOffset(0.29)
                ratio.GetXaxis().SetTitleOffset(0.8)
                ratio.GetYaxis().SetLabelSize(0.1)
                ratio.GetXaxis().SetLabelSize(0.18)
                ratio.SetMinimum(0)
                ratio.SetMaximum(3)
                ratio.Draw("pe")
                c1.cd()
            lumitag.Draw()
            scaletag.Draw()
            path = plotDir+'/test/1D/'+pk+'_njet_'+njetscut[1]+'_btag_'+nbjetscut[1]+'_isOS_dPhi_'+str(dphicut)+'_met_'+str(int(metcut))+'_metsig_'+str(int(metsignifcut))+'_mll_'+str(int(mllcut))+'/'
            if not os.path.exists(path): os.makedirs(path)
            c1.Print(path+plots[pk][plot]['name']+".png")
            if len(data)>0:del ratio
            c1.Clear()

    for plot in plots['mumu'].keys():
        bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
        l=ROOT.TLegend(legendpos[0],legendpos[1],legendpos[2],legendpos[3])
        stuff.append(l)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        totalbackground = plots['ee'][plot]['histo'][backgrounds[0]["name"]].Clone()
        totalbackground.Add(plots['mumu'][plot]['histo'][backgrounds[0]["name"]])
        for b in sorted(backgrounds,key=lambda sort:plots[pk][plot]['histo'][sort['name']].Integral()):
            bkgforstack = plots['ee'][plot]['histo'][b["name"]]
            bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
            bkg_stack_SF.Add(bkgforstack,"h")
            if b != backgrounds[0]: totalbackground.Add(bkgforstack)
            l.AddEntry(bkgforstack, b["texName"],"f")

        if len(data)!= 0:
            datahist = plots['ee'][plot]['histo'][DoubleEG_Run2015D["name"]].Clone()
            datahist.Add(plots['mumu'][plot]['histo'][DoubleMuon_Run2015D["name"]])
            datahist.SetMarkerColor(ROOT.kBlack)
        c1 = ROOT.TCanvas("c1","c1",800,800)
        if len(data)>0:
            pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
            pad1.SetBottomMargin(0)
            pad1.SetTopMargin(0)
            pad1.SetRightMargin(0)
            pad1.Draw()
            pad1.cd()
        bkg_stack_SF.SetMaximum(ymaximum*bkg_stack_SF.GetMaximum())
        bkg_stack_SF.SetMinimum(yminimum)
        bkg_stack_SF.Draw()
        bkg_stack_SF.GetXaxis().SetTitle(plots['mumu'][plot]['title'])
        bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plots['mumu'][plot]['binning'][2]-plots['mumu'][plot]['binning'][1])/plots['mumu'][plot]['binning'][0]) )
        if len(data)>0:
            pad1.SetLogy()
            bkg_stack_SF.GetXaxis().SetLabelSize(0.)
        else:           c1.SetLogy()
        if len(signals)>0:
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
            l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
        if len(data)!= 0:
            datahist.Draw("peSAME")
            l.AddEntry(datahist, "data", "pe")
        l.Draw()
        ROOT.gPad.RedrawAxis()
        channeltag = ROOT.TPaveText(channeltagpos[0],channeltagpos[1],channeltagpos[2],channeltagpos[3],"NDC")
        lumitag = ROOT.TPaveText(lumitagpos[0],lumitagpos[1],lumitagpos[2],lumitagpos[3],"NDC")
        scaletag = ROOT.TPaveText(scalepos[0],scalepos[1],scalepos[2],scalepos[3],"NDC")
        channeltag.AddText("SF")
        if plots['mumu'][plot].has_key('tag'):
            print 'Tag found, adding to histogram'
            channeltag.AddText(plots['mumu'][plot]['tag'])
        lumitag.AddText("lumi: "+str(DoubleMuon_Run2015D['lumi']+DoubleEG_Run2015D['lumi'])+' pb^{-1}')
        scaletag.AddText("Scale Factor: " +str(round((plots['ee'][plot]['SF']+plots['mumu'][plot]['SF'])/2,2)))
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.SetBorderSize(0)
        lumitag.SetFillColor(ROOT.kWhite)
        lumitag.SetShadowColor(ROOT.kWhite)
        lumitag.SetBorderSize(0)
        scaletag.SetFillColor(ROOT.kWhite)
        scaletag.SetShadowColor(ROOT.kWhite)
        scaletag.SetBorderSize(0)
        channeltag.Draw()
        if len(data)>0:
            c1.cd()
            pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
            pad2.SetGrid()
            pad2.SetBottomMargin(0.4)
            pad2.SetTopMargin(0)
            pad2.SetRightMargin(0)
            pad2.Draw()
            pad2.cd()
            ratio = datahist.Clone()
            stuff.append(ratio)
            ratio.Divide(totalbackground)
            ratio.SetMarkerStyle(20)
            ratio.GetYaxis().SetTitle("Data/Bkg.")
            #ratio.GetYaxis().SetNdivisions(502)
            ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
            ratio.GetXaxis().SetTitleSize(0.2)
            ratio.GetYaxis().SetTitleSize(0.18)
            ratio.GetYaxis().SetTitleOffset(0.29)
            ratio.GetXaxis().SetTitleOffset(0.8)
            ratio.GetYaxis().SetLabelSize(0.1)
            ratio.GetXaxis().SetLabelSize(0.18)
            ratio.SetMinimum(0)
            ratio.SetMaximum(3)
            ratio.Draw("pe")
            c1.cd()
        lumitag.Draw()
        scaletag.Draw()
        path = plotDir+'/test/1D/SF_njet_'+njetscut[1]+'_btag_'+nbjetscut[1]+'_isOS_dPhi_'+str(dphicut)+'_met_'+str(int(metcut))+'_metsig_'+str(int(metsignifcut))+'_mll_'+str(int(mllcut))+'/'
        if not os.path.exists(path): os.makedirs(path)
        c1.Print(path+plots['mumu'][plot]['name']+".png")
        if len(data)>0:
            del ratio
            pad1.Delete()
            pad2.Delete()
        c1.Clear()

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
