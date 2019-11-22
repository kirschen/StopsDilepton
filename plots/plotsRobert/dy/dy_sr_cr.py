#!/usr/bin/env python
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools
import copy
import array
import operator

from math                                import sqrt, cos, sin, pi, atan2
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p19')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-relIso0.12-looseLeptonVeto-mll20')
args = argParser.parse_args()

# Logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

if args.year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

    DY = DY_LO_16

DY_CR = copy.deepcopy( DY_LO_16 )
DY_CR.setSelectionString(cutInterpreter.cutString(args.selection+"-SF-OS-onZ-btag0"))
DY_CR.style = styles.errorStyle( ROOT.kBlue )
DY_SR = copy.deepcopy( DY_LO_16 )
DY_SR.setSelectionString(cutInterpreter.cutString(args.selection+"-SF-OS-offZ-btag1p"))
DY_SR.style = styles.errorStyle( ROOT.kRed )

samples = [DY_CR, DY_SR]

# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def drawObjects( plotData, dataMCScale, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

for sample in samples:
    sample.addSelectionString(  "&&".join([getFilterCut(isData=False, year=args.year), "dl_mt2ll>100"]) )
    if args.small:
        sample.reduceFiles( to = 1 )

h_DY_CR             = DY_CR.get1DHistoFromDraw("dl_mt2blbl", [10,0,250], "(1)", "weight")
h_DY_CR.style       = DY_CR.style                                  
h_DY_CR.legendText  = "DY CR"                                      
                                                                   
h_DY_SR             = DY_SR.get1DHistoFromDraw("dl_mt2blbl", [10,0,250], "(1)", "weight")
h_DY_SR.style       = DY_SR.style 
h_DY_SR.legendText  = "DY SR" 

if h_DY_CR.Integral()>0:
    h_DY_CR.Scale(1./h_DY_CR.Integral())
if h_DY_SR.Integral()>0:
    h_DY_SR.Scale(1./h_DY_SR.Integral())

plot = Plot.fromHisto( args.selection+"_mt2blbl", [[h_DY_CR], [h_DY_SR]] )

plotting.draw(plot, plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/DY/", logY = True, 
    ratio = {'histos':[(1,0)], 'texY':"SR/CR", "yRange":(0,2.2)},
    legend = [0.55, 0.7, 0.9, 0.9], yRange = (3*10**-3, 1.1),
    )
