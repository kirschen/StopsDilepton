import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

import os
from StopsDilepton.tools.helpers import getChain, getObjFromFile, getObjDict, getEList, getVarValue, getPlotFromChain
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.user import *

#preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = 'isOS&&isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0'
dataCut = "(HLT_mumuIso&&Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)&&weight>0"
prefix="doubleMu_onZ_isOS_1500pb"

pileup_data = getObjFromFile(os.path.expandvars("$CMSSW_BASE/src/StopsDilepton/tools/python/puReweightingData/officialDataPileuphistogram_DoubleMuon_1500.root"), "pileup")

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *

backgrounds = [DY, TTJets_Lep, TTX, diBoson,  singleTop,  singleTop, WJetsToLNu, QCD_Mu5 ]
#backgrounds = [TTJets_25ns, DY_25ns, singleTop_25ns, diBoson_25ns, WJetsHTToLNu_25ns]#, QCD]
for b in backgrounds:
    b['isData']=False

#get the TChains for each sample
for s in backgrounds:
    s['chain'] = getChain(s,histname="")

#plots
plots = {\
    'nTrueInt': {'title':'nTrueInt', 'name':'nTrueInt', 'binning': [50,0,50], 'histo':{}},
}

#make plot in each sample:
for s in backgrounds:
    for pk in plots.keys():
        plots[pk]['histo'][s['name']] = getPlotFromChain(s['chain'], plots[pk]['name'], plots[pk]['binning'], cutString = preselection)

for pk in plots.keys():
    plots[pk]['sum'] =  plots[pk]['histo'][backgrounds[0]['name']].Clone()
    for b in backgrounds[1:]:
        plots[pk]['sum'].Add(plots[pk]['histo'][b['name']])


#Some coloring
TTJets_Lep["color"]=ROOT.kBlack
WJetsToLNu["color"]=ROOT.kGreen
#TTVH["color"]=ROOT.kMagenta
DY["color"]=ROOT.kBlue
diBoson["color"]=ROOT.kRed
QCD_Mu5["color"]=ROOT.kCyan
TTX["color"]=ROOT.kMagenta
singleTop["color"]=ROOT.kOrange

for pk in plots.keys():
    #Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    bkg_stack = ROOT.THStack("bkgs","bkgs")
    tot=0
    for b in reversed(backgrounds):
        plots[pk]['histo'][b['name']].SetFillColor(b["color"])
        plots[pk]['histo'][b['name']].SetMarkerColor(b["color"])
        plots[pk]['histo'][b['name']].SetMarkerSize(0)
#    plots[pk]['histo'][b['name']].GetYaxis().SetRangeUser(10**-2.5, 2*plots[pk]['histo'][b['name']].GetMaximum())
        bkg_stack.Add(plots[pk]['histo'][b['name']],"h")
        l.AddEntry(plots[pk]['histo'][b['name']], b["name"])
        tot+=plots[pk]['histo'][b['name']].Integral()
    for b in backgrounds:
        plots[pk]['histo'][b['name']].Scale(pileup_data.Integral()/tot)
    #Plot!
    c1 = ROOT.TCanvas()
    bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
    bkg_stack.SetMinimum(10**-1.5)
    bkg_stack.Draw('e')
    bkg_stack.GetXaxis().SetTitle(plots[pk]['title'])
    binning = plots[pk]['binning']
    bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
    c1.SetLogy()

    pileup_data.Draw('hsame')
#  signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
#  signalPlot = plots[pk]['histo'][signal].Clone()
#  signalPlot.Scale(100)
#  signalPlot.Draw("same")
#  l.AddEntry(signalPlot, signal+" x 100")
    l.Draw()
    c1.Print(plotDir+"/pngTMP/"+prefix+'_'+plots[pk]["name"]+".png")

    plots[pk]['sum'].Scale(1./plots[pk]['sum'].Integral())
    pileup_data.Scale(1./pileup_data.Integral())
    pileup_data.Divide(plots[pk]['sum'])
    pileup_data.Draw()
    pileup_data.SetName("nTrueIntReweight")
    pileup_data.SetTitle("nTrueIntReweight")
    c1.Print(plotDir+"/pngTMP/"+prefix+'_'+plots[pk]["name"]+"_reweight.png")
    f = ROOT.TFile(plotDir+"/pngTMP/"+prefix+'_'+plots[pk]["name"]+"_reweight.root", "recreate")
    pileup_data.Write()
    f.Close()
