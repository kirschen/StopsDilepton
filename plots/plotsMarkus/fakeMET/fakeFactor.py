#!/usr/bin/env python
''' Script for ttZ smearing>
'''
#
# Standard imports and batch mode
#
import ROOT, os
from math                                import sqrt, cos, sin, pi, atan2
from RootTools.core.standard             import *
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.objectSelection import getJets

from StopsDilepton.tools.mt2Calculator      import mt2Calculator
mt2Calc = mt2Calculator()

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0')
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
args = argParser.parse_args()


if args.small:                        args.plot_directory += "_small"

data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
mySample=Top_pow_18


pre_selection = cutInterpreter.cutString(args.selection)

# lepton selection
mySample.setSelectionString([pre_selection])

if args.small:
    mySample.reduceFiles(to=1)


histo = ROOT.TH1F("histo","fake MET;fake MET (GeV);number of events/25 GeV",400/25,0,400)
histo.SetFillColor(ROOT.kRed + 2)
histo.SetFillStyle(3005)

histo1p1 = ROOT.TH1F("histo1p1","fake MET;fake MET (GeV);number of events/25 GeV",400/25,0,400)
histo1p1.SetFillColor(ROOT.kCyan - 3)

histomt2ll = ROOT.TH1F("histomt2ll","M_{T2}(ll);M_{T2}(ll) (GeV);number of events/20 GeV",300/20,0,300)
histomt2ll.SetFillColor(ROOT.kRed + 2)
histomt2ll.SetFillStyle(3005)

histomt2llnew = ROOT.TH1F("histomt2llnew","M_{T2}(ll);M_{T2}(ll) (GeV);number of events/20 GeV",300/20,0,300)
histomt2llnew.SetFillColor(ROOT.kCyan - 3)

myCanvas= ROOT.TCanvas("myCanvas", "fake MET ttbar", 1000, 600)
myCanvas.Divide(2,1)
pad=myCanvas.GetPad(1)
pad.SetLogy()
pad=myCanvas.GetPad(2)
pad.SetLogy()


i=0
mt2Calc.reset()

reader = mySample.treeReader( variables = map( TreeVariable.fromString, ["MET_pt/F", "MET_phi/F", "GenMET_pt/F", "GenMET_phi/F", "l1_pt/F", "l1_phi/F", "l1_eta/F", "l2_pt/F", "l2_phi/F", "l2_eta/F", 'event/I'] ) )
reader.start()
while reader.run():
    i += 1
    
    met_pt=reader.event.MET_pt
    met_phi=reader.event.MET_phi
    genMet_pt=reader.event.GenMET_pt
    genMet_phi=reader.event.GenMET_phi
    
    # calculate fake MET
    fakeMET_x=met_pt*cos(met_phi)-genMet_pt*cos(genMet_phi)
    fakeMET_y=met_pt*sin(met_phi)-genMet_pt*sin(genMet_phi)
    
    fakeMET_pt=sqrt( fakeMET_x**2 + fakeMET_y**2)
    fakeMET_phi=atan2( fakeMET_y, fakeMET_x ) 
    
    histo.Fill(float(fakeMET_pt), 1)
    histo1p1.Fill(float(fakeMET_pt)*1.1, 1)
    
    # scale fake MET by 10%
    newfakeMET_pt=fakeMET_pt*1.1
    
    # calculate newMET
    newMET_x=genMet_pt*cos(genMet_phi) + newfakeMET_pt*cos(fakeMET_phi)
    newMET_y=genMet_pt*sin(genMet_phi) + newfakeMET_pt*sin(fakeMET_phi)
    
    newMET_pt=sqrt( newMET_x**2 + newMET_y**2 )
    newMET_phi=atan2( newMET_y, newMET_x )
    
    # print "MET(pt,phi)=", met_pt, met_phi, ", GenMET(pt, phi)=", genMet_pt, genMet_phi, ", fakeMET(pt, phi)=", fakeMET_pt, fakeMET_phi, ", newMET(pt, phi)=", newMET_pt, newMET_phi
    
    # leptons >= 2 ?
    mt2Calc.setLeptons(reader.event.l1_pt, reader.event.l1_eta, reader.event.l1_phi, reader.event.l2_pt, reader.event.l2_eta, reader.event.l2_phi)
    mt2Calc.setMet(met_pt, met_phi)
    histomt2ll.Fill(mt2Calc.mt2ll(), 1)
    
    mt2Calc.reset()
    mt2Calc.setLeptons(reader.event.l1_pt, reader.event.l1_eta, reader.event.l1_phi, reader.event.l2_pt, reader.event.l2_eta, reader.event.l2_phi)
    mt2Calc.setMet(newMET_pt, newMET_phi)
    histomt2llnew.Fill(mt2Calc.mt2ll(), 1)
    
    #if i == 10:
    #    break


myCanvas.cd(1)
histo1p1.Draw()
histo.Draw("Same")

legend = ROOT.TLegend(0.60, 0.90, 0.95, .75)
legend.SetHeader("t#bar{t} sample","C") # option "C" allows to center the header
legend.AddEntry(histo,"fakeMET_pt")
legend.AddEntry(histo1p1,"fakeMET_pt * 1.1")
legend.Draw()



myCanvas.cd(2)
histomt2llnew.Draw()
histomt2ll.Draw("Same")

legend2 = ROOT.TLegend(0.50, 0.90, 0.95, .75)
legend2.SetHeader("t#bar{t} sample","C") # option "C" allows to center the header
legend2.AddEntry(histomt2ll,"M_{T2}(ll)")
legend2.AddEntry(histomt2llnew,"M_{T2}(ll) with fakeMET_pt*1.1")
legend2.Draw()



myCanvas.SaveAs("/afs/hephy.at/user/m/mdoppler/www/"+args.selection+"+scaledBy1p1.png")
