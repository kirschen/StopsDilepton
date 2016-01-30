import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TH3F, TString, TColor
from array import array
import numpy as n
from math import *
import string


ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetCanvasColor(0)
ROOT.gStyle.SetPadColor(0)
ROOT.gStyle.SetMarkerStyle(15)
ROOT.gStyle.SetMarkerSize(0.25)
ROOT.gStyle.SetTextFont(42)
ROOT.gStyle.SetMarkerColor(37)


def ThreeD(ThreeDhist):

	nbinsX = ThreeDhist.GetNbinsX()
	nbinsY = ThreeDhist.GetNbinsY()
	nbinsZ = ThreeDhist.GetNbinsZ()
	
	hout = TH1F("","",nbinsX*nbinsY*nbinsZ,0.5,nbinsX*nbinsY*nbinsZ+0.5)
	l=1
	for i in range(1,nbinsX+1):
		for j in range(1,nbinsY+1):
			for k in range(1,nbinsZ+1):
				bin = ThreeDhist.GetBin(i,j,k)
				hout.SetBinContent(l,ThreeDhist.GetBinContent(bin))
				hout.SetBinError(l,ThreeDhist.GetBinError(bin))
				l+=1
	return hout


path = "/afs/cern.ch/work/w/wvandrie/public/STOPS/ANALYSIS/CMSSW_7_4_7_patch1/src/HiggsAnalysis/CombinedLimit/histograms_ward_10fb_met140_metsig8_njets2ormore_bnjets1ormore_dphi0.25/"


fttSF = ROOT.TFile.Open(path+"tt+Jets2L2Nu_SF.root")
httSF =  fttSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fttOF = ROOT.TFile.Open(path+"tt+Jets2L2Nu_emu.root")
httOF =  fttOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fwjetsSF = ROOT.TFile.Open(path+"W+Jets_SF.root")
hwjetsSF =  fwjetsSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fwjetsOF = ROOT.TFile.Open(path+"W+Jets_emu.root")
hwjetsOF =  fwjetsOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fttxSF = ROOT.TFile.Open(path+"TTX_SF.root")
httxSF =  fttxSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fttxOF = ROOT.TFile.Open(path+"TTX_emu.root")
httxOF =  fttxOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fsingletopSF = ROOT.TFile.Open(path+"singletop_SF.root")
hsingletopSF =  fsingletopSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fsingletopOF = ROOT.TFile.Open(path+"singletop_emu.root")
hsingletopOF =  fsingletopOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fdibosonsSF = ROOT.TFile.Open(path+"WW+WZ+ZZ_SF.root")
hdibosonsSF =  fdibosonsSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fdibosonsOF = ROOT.TFile.Open(path+"WW+WZ+ZZ_emu.root")
hdibosonsOF =  fdibosonsOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fdySF = ROOT.TFile.Open(path+"DY_SF.root")
hdySF =  fdySF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fdyOF = ROOT.TFile.Open(path+"DY_emu.root")
hdyOF =  fdyOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fqcdSF = ROOT.TFile.Open(path+"QCD_Mu_SF.root")
hqcdSF =  fqcdSF.Get("h3_mt2bbvsmt2blblvsmt2ll")
fqcdOF = ROOT.TFile.Open(path+"QCD_Mu_emu.root")
hqcdOF =  fqcdOF.Get("h3_mt2bbvsmt2blblvsmt2ll")

fsig = ROOT.TFile.Open(path+"SMS_T2tt_2J_mStop650_mLSP325.root")
hsig =  fsig.Get("h3_mt2bbvsmt2blblvsmt2ll")


# unrolling
httSF1 = ThreeD(httSF)
httOF1 = ThreeD(httOF)
hwjetsSF1 = ThreeD(hwjetsSF)
hwjetsOF1 = ThreeD(hwjetsOF)
httxSF1 = ThreeD(httxSF)
httxOF1 = ThreeD(httxOF)
hsingletopSF1 = ThreeD(hsingletopSF)
hsingletopOF1 = ThreeD(hsingletopOF)
hdibosonsSF1 = ThreeD(hdibosonsOF)
hdibosonsOF1 = ThreeD(hdibosonsOF)
hdySF1 = ThreeD(hdySF)
hdyOF1 = ThreeD(hdyOF)
hqcdSF1 = ThreeD(hqcdSF)
hqcdOF1 = ThreeD(hqcdOF)
hsig1 = ThreeD(hsig)
hsig1.Sumw2()


# plots
bkg_stack = ROOT.THStack("bkgs","bkgs")
bkg_stack.Add(hwjetsSF1)
bkg_stack.Add(hwjetsOF1)
bkg_stack.Add(hqcdSF1)
bkg_stack.Add(hqcdOF1)
bkg_stack.Add(httxSF1)
bkg_stack.Add(httxOF1)
bkg_stack.Add(hdibosonsSF1)
bkg_stack.Add(hdibosonsOF1)
bkg_stack.Add(hdySF1)
bkg_stack.Add(hdyOF1)
bkg_stack.Add(hsingletopSF1)
bkg_stack.Add(hsingletopOF1)
bkg_stack.Add(httSF1)
bkg_stack.Add(httOF1)



httSF1.SetFillColor(ROOT.kCyan)
httOF1.SetFillColor(ROOT.kCyan)
hwjetsSF1.SetFillColor(ROOT.kRed-10)
hwjetsOF1.SetFillColor(ROOT.kRed-10)
httxSF1.SetFillColor(ROOT.kPink)
httxOF1.SetFillColor(ROOT.kPink)
hdibosonsSF1.SetFillColor(ROOT.kOrange)
hdibosonsOF1.SetFillColor(ROOT.kOrange)
hsingletopSF1.SetFillColor(40)
hsingletopOF1.SetFillColor(40)
hdySF1.SetFillColor(8)
hdyOF1.SetFillColor(8)
hqcdSF1.SetFillColor(46)
hqcdOF1.SetFillColor(46)

httSF1.SetLineColor(ROOT.kCyan)
httOF1.SetLineColor(ROOT.kCyan)
hwjetsSF1.SetLineColor(ROOT.kRed-10)
hwjetsOF1.SetLineColor(ROOT.kRed-10)
httxSF1.SetLineColor(ROOT.kPink)
httxOF1.SetLineColor(ROOT.kPink)
hdibosonsSF1.SetLineColor(ROOT.kOrange)
hdibosonsOF1.SetLineColor(ROOT.kOrange)
hsingletopSF1.SetLineColor(40)
hsingletopOF1.SetLineColor(40)
hdySF1.SetLineColor(8)
hdyOF1.SetLineColor(8)
hqcdSF1.SetLineColor(46)
hqcdOF1.SetLineColor(46)

hsig1.SetLineColor(ROOT.kBlue)
hsig1.SetLineWidth(2)




c1 = ROOT.TCanvas("c1","example",650,700)
pad1 = ROOT.TPad("pad1","pad1",0,0.29,1,0.97)
pad1.SetBottomMargin(0)
pad1.Draw()
pad1.cd()
httSF1.GetXaxis().SetRangeUser(1,27)
httSF1.SetMaximum(10**4)
httSF1.SetMinimum(10**-1.5)
httSF1.Draw()
bkg_stack.Draw("histsame")
hsig1.Draw("histE1same")
httSF1.GetXaxis().SetTitle("Bin")
httSF1.GetYaxis().SetTitle("Events / Bin")
#httSF1.GetYaxis().SetTitleOffset(1.4)
#httSF1.GetXaxis().SetNdivisions(8)
pad1.SetLogy()
pad1.RedrawAxis()
c1.cd()

l=ROOT.TLegend(0.6,0.5,0.98,0.9)
l.SetFillStyle(0)
l.SetBorderSize(0)
l.SetTextSize(0.04)
l.SetTextFont(42)
l.AddEntry(httSF1, "t#bar{t} #rightarrow 2l2#nu" , "f")
l.AddEntry(hsingletopSF1, "Single top" , "f")
l.AddEntry(hdySF1, "Drell-Yan" , "f")
l.AddEntry(hdibosonsSF1, "WW+WZ+ZZ" , "f")
l.AddEntry(httxSF1, "TTX (X=H,W,Z)" , "f")
l.AddEntry(hqcdSF1, "QCD" , "f")
l.AddEntry(hwjetsSF1, "W+jets" , "f")
l.AddEntry(hsig1, "T2tt(650,325)" , "l")
l.Draw()


l1 = ROOT.TLatex()
l1.SetTextAlign(12)
l1.SetTextSize(0.042)
l1.SetNDC()
l1.DrawLatex(0.18, 0.98, "CMS preliminary, L = 10 fb^{-1}")
l1.DrawLatex(0.7, 0.98, "#sqrt{s} = 13 TeV")


"""
h_bkg_stack = httSF1.Clone();
pad2 = ROOT.TPad("pad2","pad2",0,0.07,1,0.26)
xmax = h_bkg_stack.GetXaxis().GetXmax()
xmin = h_bkg_stack.GetXaxis().GetXmin()
line = ROOT.TLine(xmin,1.,xmax,1.)
pad2.SetTopMargin(0)
pad2.Draw()
pad2.cd()
pad2.SetGrid()
h_bkg_stack.Sumw2()
h_bkg_stack.GetYaxis().SetRangeUser(0., 2.)
h_bkg_stack.GetYaxis().SetNdivisions(4)
h_bkg_stack.GetXaxis().SetTitleSize(0.23)
h_bkg_stack.GetXaxis().SetLabelSize(0.20)
h_bkg_stack.GetYaxis().SetLabelSize(0.20)
h_bkg_stack.GetYaxis().SetTitleSize(0.20)
h_bkg_stack.GetYaxis().SetTitleOffset(0.4)
h_bkg_stack.GetXaxis().SetTitleOffset(0.9)
h_bkg_stack.GetYaxis().SetTitle("Data / MC")
h_bkg_stack.SetMarkerColor(ROOT.kBlack)
h_bkg_stack.SetMarkerStyle(20)
h_bkg_stack.SetMarkerSize(1.1)
h_bkg_stack.SetMarkerSize(0)
h_bkg_stack.Sumw2()
h_bkg_stack.Divide(h_bkg_stack)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kRed)
h_bkg_stack.Draw("ep")
line.Draw("same")
h_bkg_stack.Draw("epsame")
pad2.RedrawAxis()

"""
c1.cd()
c1.Print("~/www/php-plots/2LeptonStops13TeV/dataMC/unrolled1D.png")
