import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain,getWeight,getVarValue
from StopsDilepton.tools.localInfo import *
from datetime import datetime

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True

btagcoeff          = 0.89
metcut             = 80.
metsignifcut       = 5.
dphicut            = 0.25
mllcut             = 20
ngoodleptons       = 2

flavour = "MuMu"

presel_met         = 'met_pt>'+str(metcut)
presel_nbjet       = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>'+str(btagcoeff)+')>=1'
presel_njet        = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2'
presel_metsig      = 'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>'+str(metsignifcut)
presel_mll         = 'dl_mass>'+str(mllcut)
presel_OS          = 'isOS'
presel_dPhi        = 'cos(met_phi-Jet_phi[0])<cos('+str(dphicut)+')&&cos(met_phi-Jet_phi[1])<cos('+str(dphicut)+')'

presel_flavour     = 'isMuMu&&nGoodElectrons==0&&nGoodMuons==2&&HLT_mumuIso==1&&weight>0'
if flavour=="MuMu":
    presel_flavour     = 'isMuMu==1&&nGoodElectrons==0&&nGoodMuons==2&&HLT_mumuIso'
elif flavour=="EE":
    presel_flavour     = 'isEE==1&&nGoodElectrons==2&&nGoodMuons==0&&HLT_ee_DZ'
elif flavour=="EMu":
    presel_flavour     = 'isEMu==1&&nGoodElectrons==1&&nGoodMuons==1&&HLT_mue'


#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = presel_njet+'&&'+presel_OS+'&&'+presel_mll+'&&'+presel_dPhi+'&&'+presel_met+'&&'+presel_metsig+'&&'+presel_flavour

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

backgrounds = [TTJets]


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds:
    s['chain'] = getChain(s,histname="")

mllbinning = "(50,0,150)"
jetptbinning = '(50,0,600)'
njetbinning = '(50,0,14)'
htbinning = '(50,0,800)'
metbinning = '(50,0,300)'
mt2llbinning = '(50,0,300)'

lumi = 10000/1000

plots = {\
    'nominal':{
        'dl_mass':{'title':'m_{ll} (GeV)', 'name':'Mll', 'binning': mllbinning, 'histo':{}},
        'Jet_pt[0]':{'title':'1st Jet p_{T} (GeV)', 'name':'Jet1Pt', 'binning': jetptbinning, 'histo':{}},
        'Jet_pt[3]':{'title':'4th Jet p_{T} (GeV)', 'name':'Jet4Pt', 'binning': jetptbinning, 'histo':{}},
        'Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))':{'title':'H_{T} (GeV)', 'name':'HT', 'binning': htbinning, 'histo':{}},
        'nJet':{'title':'nJet', 'name':'nJet', 'binning': njetbinning, 'histo':{}},
        'met_pt':{'title':'MET (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
        'dl_mt2ll':{'title':'M^{2}_{T}(ll) (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
        },
    'topPt':{
        'dl_mass':{'title':'m_{ll} (GeV)', 'name':'Mll', 'binning': mllbinning, 'histo':{}},
        'Jet_pt[0]':{'title':'1st Jet p_{T} (GeV)', 'name':'Jet1Pt', 'binning': jetptbinning, 'histo':{}},
        'Jet_pt[3]':{'title':'4th Jet p_{T} (GeV)', 'name':'Jet4Pt', 'binning': jetptbinning, 'histo':{}},
        'Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))':{'title':'H_{T} (GeV)', 'name':'HT', 'binning': htbinning, 'histo':{}},
        'nJet':{'title':'nJet', 'name':'nJet', 'binning': njetbinning, 'histo':{}},
        'met_pt':{'title':'MET (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
        'dl_mt2ll':{'title':'M^{2}_{T}(ll) (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
        },

    }


#######################################################
#            Start filling in the histograms          #
#######################################################

for s in backgrounds:
    chain = s["chain"]
    for plot in plots['nominal'].keys():
        chain.Draw(plot+">>"+plots['nominal'][plot]['name']+s["name"]+plots['nominal'][plot]['binning'],"(weight*"+str(lumi)+")*("+preselection+")")
        plots['nominal'][plot]['histo'][s["name"]] = ROOT.gDirectory.Get(plots['nominal'][plot]['name']+s["name"])
    for plot in plots['topPt'].keys():
        chain.Draw(plot+">>"+plots['topPt'][plot]['name']+s["name"]+"_topPt"+plots['topPt'][plot]['binning'],"(weight*"+str(lumi)+"*reweightTopPt)*("+preselection+")")
        plots['topPt'][plot]['histo'][s["name"]] = ROOT.gDirectory.Get(plots['topPt'][plot]['name']+s["name"]+"_topPt")

    for selection in plots.keys():

        nbinsx        = plots[selection][plot]['histo'][s['name']].GetNbinsX()
        lastbin       = plots[selection][plot]['histo'][s['name']].GetBinContent(nbinsx)
        error         = plots[selection][plot]['histo'][s['name']].GetBinError(nbinsx)
        overflowbin   = plots[selection][plot]['histo'][s['name']].GetBinContent(nbinsx+1)
        overflowerror = plots[selection][plot]['histo'][s['name']].GetBinError(nbinsx+1)
        plots[selection][plot]['histo'][s['name']].SetBinContent(nbinsx,lastbin+overflowbin)
        plots[selection][plot]['histo'][s['name']].SetBinError(nbinsx,sqrt(error**2+overflowerror**2))
        plots[selection][plot]['histo'][s['name']].SetBinContent(nbinsx+1,0.)
        plots[selection][plot]['histo'][s['name']].SetBinError(nbinsx+1,0.)

processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################

legendtextsize = 0.032
lumitagpos = [0.4,0.95,0.6,1.0]
legendpos = [0.7,0.8,0.95,0.9]

ROOT.gStyle.SetErrorX(0.5)

if makedraw1D:
    for i,b in enumerate(backgrounds):
        for plot in plots['nominal'].keys():

            plots['nominal'][plot]['histo'][b["name"]].SetLineColor(ROOT.kBlue)
            plots['nominal'][plot]['histo'][b["name"]].SetLineWidth(3)
            plots['topPt'][plot]['histo'][b["name"]].SetLineColor(ROOT.kRed)
            plots['topPt'][plot]['histo'][b["name"]].SetLineWidth(3)

            c1 = ROOT.TCanvas("c1","c1",800,800)
            lumitag = ROOT.TPaveText(lumitagpos[0],lumitagpos[1],lumitagpos[2],lumitagpos[3],"NDC")
            lumitag.AddText("Lumi: "+str(lumi)+" fb^{-1}")
            lumitag.SetFillColor(ROOT.kWhite)
            lumitag.SetShadowColor(ROOT.kWhite)
            lumitag.SetBorderSize(0)
            lumitag.Draw()

            l=ROOT.TLegend(legendpos[0],legendpos[1],legendpos[2],legendpos[3])
            l.SetFillColor(0)
            l.SetBorderSize(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetTextSize(legendtextsize)
            pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,0.95)
            pad1.SetTopMargin(0)
            pad1.Draw()
            pad1.cd()

            plots['nominal'][plot]['histo'][b["name"]].Draw("HIST")
            plots['topPt'][plot]['histo'][b["name"]].Draw("HISTSAME")
            pad1.SetBottomMargin(0)
            #pad1.SetGridx()

            pad1.SetLogy()

            l.AddEntry(plots['nominal'][plot]['histo'][b["name"]],"nominal","l")
            l.AddEntry(plots['topPt'][plot]['histo'][b["name"]],"reweighted","l")

            c1.cd()

            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
            pad2.SetTopMargin(0)
            pad2.SetBottomMargin(0.3)
            #pad2.SetGridx()
            pad2.SetGrid()
            pad2.Draw()
            pad2.cd()

            plots['nominal'][plot]['histo'][b["name"]].GetYaxis().SetTitleSize(20);
            plots['nominal'][plot]['histo'][b["name"]].GetYaxis().SetTitleFont(43);
            plots['nominal'][plot]['histo'][b["name"]].GetYaxis().SetTitleOffset(1.55);

            ratio = plots['nominal'][plot]['histo'][b["name"]].Clone()
            ratio.Divide(plots['topPt'][plot]['histo'][b["name"]])
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(1)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)
            #ratio.SetMarkerStyle(21)

            ratio.GetYaxis().SetTitle("Nominal/Reweighted");
            ratio.GetYaxis().SetNdivisions(505);
            ratio.GetYaxis().SetTitleSize(18);
            ratio.GetYaxis().SetTitleFont(43);
            ratio.GetYaxis().SetTitleOffset(1.55);
            ratio.GetYaxis().SetLabelFont(43);

            ratio.GetYaxis().SetLabelSize(15);

            ratio.GetXaxis().SetTitleSize(20);
            ratio.GetXaxis().SetTitleFont(43);
            ratio.GetXaxis().SetTitleOffset(4.);
            ratio.GetXaxis().SetLabelFont(43);

            ratio.GetXaxis().SetLabelSize(15);

            ratio.GetXaxis().SetTitle(plots['nominal'][plot]['title'])
            ratio.Draw("ep")

            c1.cd()
            l.Draw()
            ROOT.gPad.RedrawAxis()

            path = plotDir+'/test/TopPtReweight/'+flavour+'_njet_2m_nbjet_1m_isOS'+'_dPhi_0.25_met_'+str(int(metcut))+'_metsig_'+str(int(metsignifcut))+'_mll_'+str(int(mllcut))+'/'
            if not os.path.exists(path): os.makedirs(path)
            c1.Print(path+plots['nominal'][plot]['name']+"_"+b["name"]+".png")

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
