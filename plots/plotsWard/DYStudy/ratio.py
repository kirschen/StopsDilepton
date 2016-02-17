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

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True

btagcoeff          = 0.89
metcut             = 0.
metsignifcut       = 8.
dphicut            = 0.25
mllcut             = 20
ngoodleptons       = 2
luminosity         = 10000

presel_met         = 'met_pt>'+str(metcut)
presel_nbjet       = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>'+str(btagcoeff)+')>=1'
presel_njet        = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2'
presel_metsig      = 'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>'+str(metsignifcut)
presel_mll         = 'dl_mass>'+str(mllcut)
presel_ngoodlep    = '((nGoodMuons+nGoodElectrons)=='+str(ngoodleptons)+')'
presel_OS          = 'isOS'
presel_dphi        = 'cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)'
presel_isSF        = 'isMuMu == 1 || isEE == 1'
presel_onZ         = 'abs(dl_mass-91.2)<15'
presel_offZ        = 'abs(dl_mass-91.2)>=15'

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = presel_ngoodlep+'&&'+presel_OS+'&&'+presel_njet+'&&'+presel_nbjet+'&&'+presel_mll+'&&'+presel_dphi+'&&'+presel_isSF

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
#backgrounds = [DY_25ns,DYHT_25ns]
backgrounds = [DY_HT_LO]

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds:
    s['chain'] = getChain(s,histname="")


mt2llbinning = "(10,0,400)"
mllbinning = "(10,0,800)"


plots = {\
    'dl_mt2ll':{\
        '_ratio': {'title':'M^{2}_{T}(ll) (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
        },
    'dl_mass':{\
        '_ratio': {'title':'M_{ll} (GeV)', 'name':'Mll', 'binning': mllbinning, 'histo':{}},
        },
    }


#######################################################
#            Start filling in the histograms          #
#######################################################

for s in backgrounds:
    chain = s["chain"]
    for plot in plots.keys():

        chain.Draw(plot+">>"+plot+"_ratio"+s["name"]+plots[plot]['_ratio']['binning'],preselection)
        plots[plot]['_ratio']['histo'][s["name"]] = ROOT.gDirectory.Get(plot+"_ratio"+s["name"])

        for selection in plots[plot].keys():
            plots[plot][selection]['histo'][s['name']].Sumw2()
            nbinsx= plots[plot][selection]['histo'][s['name']].GetNbinsX()
            lastbin = plots[plot][selection]['histo'][s['name']].GetBinContent(nbinsx)
            overflowbin = plots[plot][selection]['histo'][s['name']].GetBinContent(nbinsx)
            plots[plot][selection]['histo'][s['name']].SetBinContent(nbinsx,lastbin+overflowbin)


processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring
DY_25ns["color"]=8

legendtextsize = 0.032

ROOT.gStyle.SetErrorX(0.5)

for i,b in enumerate(backgrounds):
    for plot in plots.keys():

        #Make a stack for backgrounds
        l=ROOT.TLegend(0.5,0.8,0.95,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)

        #Plot!
        c1 = ROOT.TCanvas()

        for j,selection in enumerate(plots[plot].keys()):

            integral = plots[plot][selection]['histo'][b["name"]].Integral()
            plots[plot][selection]['histo'][b["name"]].Scale(1./integral)

            print plot, selection, integral

            plots[plot][selection]['histo'][b["name"]].SetLineColor(j+1)
            plots[plot][selection]['histo'][b["name"]].SetLineWidth(1)
            plots[plot][selection]['histo'][b["name"]].SetMarkerColor(j+1)
            plots[plot][selection]['histo'][b["name"]].Draw("pe1same")
            if j == 0:
                plots[plot][selection]['histo'][b["name"]].SetMaximum(3)
                plots[plot][selection]['histo'][b["name"]].SetMinimum(10**-4)
                plots[plot][selection]['histo'][b["name"]].GetXaxis().SetTitle(plots[plot][selection]['title'])
                plots[plot][selection]['histo'][b["name"]].GetYaxis().SetTitle("Events (A.U.)")
            l.AddEntry(plots[plot][selection]['histo'][b["name"]],plots[plot][selection]['name'])
        c1.SetLogy()
        l.Draw()
        c1.Print(plotDir+"/test/DYstudy/"+plot+"_"+s["name"]+".png")

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
