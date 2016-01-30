import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from ROOT import TTree, TFile, AddressOf, gROOT, TH1D, TH2F, TString, TColor
from array import array
import numpy as n
from math import *
import string



#background = ["TTJets2L2Nu", "WJets", "QCDMu", "DrellYan", "TTX", "singleTop"]
background = ["DrellYanHT", "DrellYanInclusive"]
signal = ["T2ttS425N325"]
data = ["DoubleElec", "DoubleMuon", "MuonElec"]

#everything = signal + background + data
everything =  background

for process in range(len(everything)):

	print everything[process]
	#f = ROOT.TFile.Open("~/public/4Nicolas/v5/"+ everything[process] +".root")
	f = ROOT.TFile.Open("ntuples/"+ everything[process] +".root")
	plot = TH1D("plot", "plot", 50, 0, 500)

	for event in f.anaTree :

		isSF=0
		isOF=0

		lumi = 10.

		if event.isElecElec or event.isMuonMuon:
			isSF=1
		if event.isMuonElec:
			isOF=1

		ZVeto=abs(event.dileptonInvariantMass-91.2)>=15

		#if event.dileptonInvariantMass > 20 and event.MET > 140 and event.mindPhiMetJet12 > 0.25 and event.MET/sqrt(event.HT) > 8 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and ( (isSF and ZVeto) or isOF ):
		if event.dileptonInvariantMass > 20 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and ( (isSF and ZVeto) or isOF ):
	
			plot.Sumw2()

			if event.isMC:
				plot.Fill( event.HT, event.xsecWeight*lumi/100)
			else:
				plot.Fill( event.HT)


#	print "Process: %s,\t\t Integral: %.2f,\t\t Entries: %i" % (everything[process], plot.Integral(), plot.GetEntries())




#plots

	c1 = ROOT.TCanvas("c1","example",650,700)
	#plot.SetMaximum(2*plot.GetMaximum())
	plot.SetMaximum(10**3)
	plot.SetMinimum(1)
	plot.Draw()
	plot.GetXaxis().SetTitle("HT")
	plot.GetYaxis().SetTitle("Events")
	c1.SetLogy()
	c1.Print("~/www/php-plots/2LeptonStops13TeV/dataMC/"+ everything[process] +"_HT2.png")

"""

h_plot = plot.Clone();
pad2 = ROOT.TPad("pad2","pad2",0,0.07,1,0.26)
xmax = h_plot.GetXaxis().GetXmax()
xmin = h_plot.GetXaxis().GetXmin()
line = ROOT.TLine(xmin,1.,xmax,1.)
pad2.SetTopMargin(0)
pad2.Draw()
pad2.cd()
pad2.SetGrid()
h_plot.Sumw2()
h_plot.GetYaxis().SetRangeUser(0., 2.)
h_plot.GetYaxis().SetNdivisions(4)
h_plot.GetXaxis().SetTitleSize(0.23)
h_plot.GetXaxis().SetLabelSize(0.20)
h_plot.GetYaxis().SetLabelSize(0.20)
h_plot.GetYaxis().SetTitleSize(0.20)
h_plot.GetYaxis().SetTitleOffset(0.4)
h_plot.GetXaxis().SetTitleOffset(0.9)
h_plot.GetYaxis().SetTitle("Data / MC")
h_plot.SetMarkerColor(ROOT.kBlack)
h_plot.SetMarkerStyle(20)
h_plot.SetMarkerSize(1.1)
h_plot.Sumw2()
h_plot.Divide(h_plot)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kRed)
h_plot.Draw("ep")
line.Draw("same")
h_plot.Draw("epsame")
pad2.RedrawAxis()
"""


