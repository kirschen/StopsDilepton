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
preselection = 'met_pt>40'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
backgrounds = [DY_HT_LO]
#backgrounds = []
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []
#data = [DoubleEG_25ns,DoubleMuon_25ns,MuonEG_25ns]
#data = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
    s['chain'] = getChain(s,histname="")

plots = {\
    'lheHTIncoming': {'title':'lheHTIncoming (GeV)', 'name':'lheHTIncoming', 'histo':{}},
    }


#######################################################
#            Start filling in the histograms          #
#######################################################
for i,s in enumerate(backgrounds+signals):
    chain = s["chain"]

    chain.Draw("lheHTIncoming>>lheHTIncoming"+str(i)+"(25,0,1000)","(weight)*("+preselection+")")
    plots['lheHTIncoming']['histo'][s["name"]] = ROOT.gDirectory.Get("lheHTIncoming"+str(i))

processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################
legendtextsize = 0.032

if makedraw1D:
    for plot in plots.keys():
        for s in backgrounds+signals:
            integral = plots[plot]['histo'][s['name']].Integral()
            #plots[plot]['histo'][s['name']].Scale(1./integral)

            #Make a stack for backgrounds
        l=ROOT.TLegend(0.6,0.8,1.0,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)

        #Plot!
        c1 = ROOT.TCanvas()
        for i,b in enumerate(backgrounds+signals):
            plots[plot]['histo'][b["name"]].SetLineColor(b["color"])
            plots[plot]['histo'][b["name"]].SetLineWidth(3)
            plots[plot]['histo'][b["name"]].SetMarkerSize(0)
            plots[plot]['histo'][b["name"]].Draw("HISTsame")
            l.AddEntry(plots[plot]['histo'][b["name"]],b['name'])
            if i == 0:
                plots[plot]['histo'][b["name"]].GetXaxis().SetTitle(plots[plot]['title'])
                plots[plot]['histo'][b["name"]].GetYaxis().SetTitle("Events (A.U.)")
        c1.SetLogy()
        l.Draw()
        c1.Print("./"+plots[plot]['name']+".png")

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
