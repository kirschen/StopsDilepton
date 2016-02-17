import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain,getWeight,getVarValue
from StopsDilepton.tools.user import *
from datetime import datetime

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'


#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
#preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
#preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2&&Sum$(abs(genPartAll_pdgId)==15 & abs(genPartAll_motherId)==23)==0'
preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = True

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.samples.cmgTuples_SPRING15_WardPrivateProduction import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DYWARD, singleTop, TTJets]#, QCD]
backgrounds = [DY_15,TTJets_15]
signals = [SMS_T2tt_2J_mStop425_mLSP325,SMS_T2tt_2J_mStop650_mLSP325]#, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
#signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
    if s.has_key('totalweight'): s['chain'] = getChain(s,histname="",treeName="tree")
    else:                        s['chain'] = getChain(s,histname="")

plots = {\
    'ee':{\
        'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'histo':{}},
        'dPhi_1':{'title':'cos(dPhi(MET,jet_1))', 'name':'CosDphiLeadingJet', 'histo':{}},
        'dPhi_2':{'title':'cos(dPhi(MET,jet_2))', 'name':'CosDphiSubleadingJet', 'histo':{}},
        'minDphi':{'title':'cos(min(dPhi(MET,jet_1|jet_2)))', 'name':'MinDphiJets', 'histo':{}},
        'njets': {'title':'nJets', 'name':'nJets', 'histo':{}},
      },
    'mumu':{\
        'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'histo':{}},
        'dPhi_1':{'title':'cos(dPhi(MET,jet_1))', 'name':'CosDphiLeadingJet', 'histo':{}},
        'dPhi_2':{'title':'cos(dPhi(MET,jet_2))', 'name':'CosDphiSubleadingJet', 'histo':{}},
        'minDphi':{'title':'cos(min(dPhi(MET,jet_1|jet_2)))', 'name':'MinDphiJets', 'histo':{}},
        'njets': {'title':'nJets', 'name':'nJets', 'histo':{}},
        },
    'emu':{\
        'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'histo':{}},
        'dPhi_1':{'title':'cos(dPhi(MET,jet_1))', 'name':'CosDphiLeadingJet', 'histo':{}},
        'dPhi_2':{'title':'cos(dPhi(MET,jet_2))', 'name':'CosDphiSubleadingJet', 'histo':{}},
        'minDphi':{'title':'cos(min(dPhi(MET,jet_1|jet_2)))', 'name':'MinDphiJets', 'histo':{}},
        'njets': {'title':'nJets', 'name':'nJets', 'histo':{}},
        }
    }
plots2D = {\
    'ee':{\
        'metvsdPhi_1':{'Xtitle':'Cos(dPhi(MET,jet_1))','Ytitle':'MET', 'name':'METvsCosDphiLeadingJet', 'histo':{}},
        'metvsdPhi_2':{'Xtitle':'Cos(dPhi(MET,jet_2))','Ytitle':'MET', 'name':'METvsCosDphiSubleadingJet', 'histo':{}},
        'metvsMinDphi':{'Xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','Ytitle':'MET', 'name':'METvsMinDphiJets', 'histo':{}},
        'metvsMaxdPhi_MaxIf':{'Xtitle':'Max(Cos(dPhi(MET,jet))','Ytitle':'MET', 'name':'max(METvsdPhi),jet_pt>100_MaxIf', 'histo':{}}
        },
    'mumu':{\
        'metvsdPhi_1':{'Xtitle':'Cos(dPhi(MET,jet_1))','Ytitle':'MET', 'name':'METvsCosDphiLeadingJet', 'histo':{}},
        'metvsdPhi_2':{'Xtitle':'Cos(dPhi(MET,jet_2))','Ytitle':'MET', 'name':'METvsCosDphiSubleadingJet', 'histo':{}},
        'metvsMinDphi':{'Xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','Ytitle':'MET', 'name':'METvsMinDphiJets', 'histo':{}},
        'metvsMaxdPhi_MaxIf':{'Xtitle':'Max(Cos(dPhi(MET,jet))','Ytitle':'MET', 'name':'max(METvsdPhi),jet_pt>100_MaxIf', 'histo':{}}
        },
    'emu':{\
        'metvsdPhi_1':{'Xtitle':'Cos(dPhi(MET,jet_1))','Ytitle':'MET', 'name':'METvsCosDphiLeadingJet', 'histo':{}},
        'metvsdPhi_2':{'Xtitle':'Cos(dPhi(MET,jet_2))','Ytitle':'MET', 'name':'METvsCosDphiSubleadingJet', 'histo':{}},
        'metvsMinDphi':{'Xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','Ytitle':'MET', 'name':'METvsMinDphiJets', 'histo':{}},
        'metvsMaxdPhi_MaxIf':{'Xtitle':'Max(Cos(dPhi(MET,jet))','Ytitle':'MET', 'name':'max(METvsdPhi),jet_pt>100_MaxIf', 'histo':{}}
        }
    }


#######################################################
#            Start filling in the histograms          #
#######################################################
for i,s in enumerate(backgrounds+signals):
    chain = s["chain"]

    for channels in plots.keys():
        if channels == 'ee': channel = '&&abs(LepGood_pdgId[0])==11&&abs(LepGood_pdgId[1])==11'
        elif channels == 'mumu': channel = '&&abs(LepGood_pdgId[0])==13&&abs(LepGood_pdgId[1])==13'
        elif channels == 'emu': channel = '&&(abs(LepGood_pdgId[0])*abs(LepGood_pdgId[1]))==143'

        chain.Draw("met_pt>>met"+channels+str(i)+"(25,20,1020)",preselection+channel)
        plots[channels]['met']['histo'][s["name"]] = ROOT.gDirectory.Get("met"+channels+str(i))

        chain.Draw("cos(met_phi-Jet_phi[0])>>cos_1"+channels+str(i)+"(50,-1.1,1.1)",preselection+channel)
        plots[channels]['dPhi_1']['histo'][s["name"]] = ROOT.gDirectory.Get("cos_1"+channels+str(i))

        chain.Draw("cos(met_phi-Jet_phi[1])>>cos_2"+channels+str(i)+"(50,-1.1,1.1)",preselection+channel)
        plots[channels]['dPhi_2']['histo'][s["name"]] = ROOT.gDirectory.Get("cos_2"+channels+str(i))

        chain.Draw("cos((met_phi-Jet_phi[0]))>>mincos"+channels+str(i)+"(50,-1.1,1.1)",preselection+channel+'&&(abs((met_phi-Jet_phi[0]))<abs((met_phi-Jet_phi[1])))')
        chain.Draw("cos((met_phi-Jet_phi[1]))>>+mincos"+channels+str(i)+"(50,-1.1,1.1)",preselection+channel+'&&(abs((met_phi-Jet_phi[0]))>=abs((met_phi-Jet_phi[1])))')
        plots[channels]['minDphi']['histo'][s["name"]] = ROOT.gDirectory.Get("mincos"+channels+str(i))

        chain.Draw("Length$(Jet_pt)>>njets"+channels+str(i)+"(10,0,10)",preselection+channel)
        plots[channels]['njets']['histo'][s['name']] = ROOT.gDirectory.Get("njets"+channels+str(i))

        chain.Draw("met_pt:cos(met_phi-Jet_phi[0])>>metvsdphi_1"+channels+str(i)+"(50,-1,1,50,0,1000)",preselection+channel)
        plots2D[channels]['metvsdPhi_1']['histo'][s['name']] = ROOT.gDirectory.Get("metvsdphi_1"+channels+str(i))

        chain.Draw("met_pt:cos(met_phi-Jet_phi[1])>>metvsdphi_2"+channels+str(i)+"(50,-1,1,50,0,1000)",preselection+channel)
        plots2D[channels]['metvsdPhi_2']['histo'][s['name']] = ROOT.gDirectory.Get("metvsdphi_2"+channels+str(i))

        chain.Draw("met_pt:cos(met_phi-Jet_phi[0])>>metvsmindphi"+channels+str(i)+"(50,-1,1,50,0,1000)",preselection+channel,'&&(abs((met_phi-Jet_phi[0]))<abs((met_phi-Jet_phi[1])))')
        chain.Draw("met_pt:cos(met_phi-Jet_phi[1])>>+metvsmindphi"+channels+str(i)+"(50,-1,1,50,0,1000)",preselection+channel,'&&(abs((met_phi-Jet_phi[0]))>=abs((met_phi-Jet_phi[1])))')
        plots2D[channels]['metvsMinDphi']['histo'][s['name']] = ROOT.gDirectory.Get("metvsmindphi"+channels+str(i))

        chain.Draw("met_pt:MaxIf$(cos(met_phi-Jet_phi),Jet_pt>100)>>max_metvsdphi"+channels+str(i)+"(50,-1,1,50,0,1000)",preselection+'&&Jet_pt>100'+channel)
        plots2D[channels]['metvsMaxdPhi_MaxIf']['histo'][s['name']] = ROOT.gDirectory.Get("max_metvsdphi"+channels+str(i))


processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring
DY["color"]=ROOT.kBlue
DY_15["color"]=ROOT.kRed
TTJets_15["color"]=ROOT.kOrange
SMS_T2tt_2J_mStop425_mLSP325['color']=ROOT.kViolet
SMS_T2tt_2J_mStop650_mLSP325['color']=ROOT.kGreen

legendtextsize = 0.032

if makedraw1D:
    for channels in plots.keys():
        for plot in plots[channels].keys():
            for s in backgrounds+signals:
                integral = plots[channels][plot]['histo'][s['name']].Integral()
                plots[channels][plot]['histo'][s['name']].Scale(1./integral)

            #Make a stack for backgrounds
            l=ROOT.TLegend(0.6,0.8,1.0,1.0)
            l.SetFillColor(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(1)
            l.SetTextSize(legendtextsize)

        #Plot!
            c1 = ROOT.TCanvas()
            for i,b in enumerate(backgrounds+signals):
                plots[channels][plot]['histo'][b["name"]].SetLineColor(b["color"])
                plots[channels][plot]['histo'][b["name"]].SetLineWidth(3)
                plots[channels][plot]['histo'][b["name"]].SetMarkerSize(0)
                plots[channels][plot]['histo'][b["name"]].Draw("same")
                l.AddEntry(plots[channels][plot]['histo'][b["name"]],b['name'])
                if i == 0:
                    plots[channels][plot]['histo'][b["name"]].GetXaxis().SetTitle(plots[channels][plot]['title'])
                    plots[channels][plot]['histo'][b["name"]].GetYaxis().SetTitle("Events (A.U.)")
                    if plot!="met": plots[channels][plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.001,2)
                    else:           plots[channels][plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.00001,2)
            c1.SetLogy()
            l.Draw()
            c1.Print(plotDir+"/testDY_channels/"+plots[channels][plot]['name']+"_"+channels+".png")

if makedraw2D:
    for channels in plots2D.keys():
        for b in backgrounds+signals:
            for plot in plots2D[channels].keys():
                c1 = ROOT.TCanvas()
                ROOT.gStyle.SetOptStat(0)
                ROOT.gStyle.SetPalette(1)
                c1.SetRightMargin(0.16)

                l=ROOT.TLegend(0.6,0.9,1.0,1.0)
                l.SetFillColor(0)
                l.SetShadowColor(ROOT.kWhite)
                l.SetBorderSize(1)
                l.SetTextSize(legendtextsize)

                plots2D[channels][plot]['histo'][b["name"]].Draw("colz")
                ROOT.gPad.Update()
                palette = plots2D[channels][plot]['histo'][b["name"]].GetListOfFunctions().FindObject("palette")
                palette.SetX1NDC(0.85)
                palette.SetX2NDC(0.9)
                palette.Draw()

                l.AddEntry(plots2D[channels][plot]['histo'][b["name"]],b['name'])
                plots2D[channels][plot]['histo'][b["name"]].GetXaxis().SetTitle(plots2D[channels][plot]['Xtitle'])
                plots2D[channels][plot]['histo'][b["name"]].GetYaxis().SetTitle(plots2D[channels][plot]['Ytitle'])
                if b==DY_15: plots2D[channels][plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0,700)
                l.Draw()
                c1.SetLogz()
                c1.Print(plotDir+"/testDY_channels/"+plots2D[channels][plot]['name']+'_'+b['name']+"_"+channels+".png")
                c1.Close()

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
