#!/usr/bin/env python
''' Script for ttZ smearing
'''
#
# Standard imports and batch mode
#
import ROOT, os
from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
args = argParser.parse_args()


if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction


data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
mySample=Top_pow_18


pre_selection = cutInterpreter.cutString(args.selection)

# lepton selection

mySample.setSelectionString([pre_selection])

if args.small:
    mySample.reduceFiles(to=1)

r = mySample.treeReader( variables = map( TreeVariable.fromString, ["MET[pt/F,phi/F]", "GenMET[pt/F,phi/F]", 'event/I'] ) )
r.start()
while r.run():
    print "event number: " + str(r.event.event)
    #jets = getJets( r.event, jetColl="Jet", jetVars = ['mcPt', 'rawPt', 'mcEta', 'eta'] )

