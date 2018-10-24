#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools

from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.plots.pieChart        import makePieChart

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--ht',                                      action='store_true',     help='HT binned?', )
argParser.add_argument('--plot_directory',     action='store',      default='PU_DY_MetSig')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory

data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
postProcessing_directory = "stops_2016_nano_v3/dilep/"
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
postProcessing_directory = "stops_2017_nano_v2/dilep/"
from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "MET_pt/F", "MET_phi/F", "MET_significance/F", "MET_sumEt/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="all": return "("+"||".join([getLeptonSelection(m) for m in ['mumu', 'ee', 'mue']]) +")"

#
# Loop over channels
#
allPlots   = {}

lumi_scale = 150
weight_ = lambda event, sample: event.weight

if args.ht:
    if args.year == 2016:
        dy_sample = DY_HT_LO_16
    elif args.year == 2017:
        dy_sample = DY_HT_LO_17
else:
    if args.year == 2016:
        dy_sample = DY_LO_16
    elif args.year == 2017:
        dy_sample = DY_LO_17

mc = [ dy_sample ]

for sample in mc:    
    sample.style    = styles.fillStyle(sample.color, lineWidth = 0)
    sample.scale    = lumi_scale
    sample.setSelectionString([getFilterCut(isData=False, year=args.year), getLeptonSelection("all")])
    sample.read_variables = ['reweightPU36fb/F']
    sample.weight         = lambda event, sample: event.reweightPU36fb

    if args.small:
        sample.reduceFiles( to = 1 )

# Text on the plots
#
def drawObjects( dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Simulation'), 
      (0.50, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% ( lumi_scale ) ), 
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'StopsDilepton', args.plot_directory, dy_sample.name+"_%i"%args.year, ("log" if log else "lin"), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio =  None,
	    logX = False, logY = log, sorting = False,
	    yRange = (0.0003, "auto") if log else (0.00001, "auto"),
	    scaling = {},
	    legend = (0.50,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88) ,
	    drawObjects = drawObjects( dataMCScale , lumi_scale ),
        copyIndexPHP = True,
      )
if args.year == 2016: 
    pu_bins = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50)]
elif args.year == 2017: 
    pu_bins = [(0, 20), (20, 40), (40, 60), (60,80), (80, 100)]

plots = []

h_MET              = {bin:dy_sample.get1DHistoFromDraw( "MET_pt", [20,0,200], selectionString=cutInterpreter.cutString(args.selection)+"&&PV_npvsGood>=%i&&PV_npvsGood<%i"%bin, weightString="weight") for bin in pu_bins }
plots.append( Plot.fromHisto("MET", [ [h_MET[bin]] for bin in pu_bins ], texX = "E_{T}^{miss} (GeV)") )

h_MET_significance = {bin:dy_sample.get1DHistoFromDraw( "MET_significance", [20,0,20], selectionString=cutInterpreter.cutString(args.selection)+"&&PV_npvsGood>=%i&&PV_npvsGood<%i"%bin, weightString="weight") for bin in pu_bins }
plots.append( Plot.fromHisto("MET_significance", [ [h_MET_significance[bin]] for bin in pu_bins ], texX = "E_{T}^{miss} significance") )

h_kinMetSig = {bin:dy_sample.get1DHistoFromDraw( "metSig", [30,0,30], selectionString=cutInterpreter.cutString(args.selection)+"&&PV_npvsGood>=%i&&PV_npvsGood<%i"%bin, weightString="weight") for bin in pu_bins }
plots.append( Plot.fromHisto("kinMetSig", [ [h_kinMetSig[bin]] for bin in pu_bins ], texX = "E_{T}^{miss}/#sqrt{H_{T}}") )

h_mt2ll = {bin:dy_sample.get1DHistoFromDraw( "dl_mt2ll", [20,0,240], selectionString=cutInterpreter.cutString(args.selection)+"&&PV_npvsGood>=%i&&PV_npvsGood<%i"%bin, weightString="weight") for bin in pu_bins }
plots.append( Plot.fromHisto("MT2ll", [ [h_mt2ll[bin]] for bin in pu_bins ], texX = "M_{T,2}(ll)") )

colors = [ ROOT.kBlue, ROOT.kGreen, ROOT.kRed, ROOT.kMagenta, ROOT.kOrange, ROOT.kCyan ]

for p in plots:
    for i_bin, bin in enumerate(pu_bins):
        h = p.histos[i_bin][0]
        h.style = styles.lineStyle(colors[i_bin])
        h.legendText = '%i#leq PV <%i'%bin
        scale = h.Integral()
        if scale>0:
            h.Scale(1./scale) 

h_nPV = dy_sample.get1DHistoFromDraw( "PV_npvsGood", [20,0,100], selectionString=cutInterpreter.cutString(args.selection), weightString="weight*150")
plots.append( Plot.fromHisto("nPV", [ [h_nPV] ], texX = "PV multiplicity") )
     
drawPlots( plots, 1 )

#stack = Stack(mc)
#
## Use some defaults
#Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper')
#
#plots = []
#
##plots.append(Plot(
##  name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
##  attribute = TreeVariable.fromString( "Pileup_nTrueInt/F" ),
##  binning=[50,0,50],
##))
#  
#plots.append(Plot(
#  name = 'PV_npvsGood', texX = 'N_{PV} (good)', texY = 'Number of Events',
#  attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
#  binning=[50,0,50],
#))
#  
#plots.append(Plot(
#  name = 'PV_npvs', texX = 'N_{PV} (total)', texY = 'Number of Events',
#  attribute = TreeVariable.fromString( "PV_npvs/I" ),
#  binning=[50,0,50],
#))
#
#plots.append(Plot(
#    texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
#    attribute = TreeVariable.fromString( "MET_pt/F" ),
#    binning=[400/20,0,400],
#))
#
#plots.append(Plot(
#  texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
#  attribute = TreeVariable.fromString('metSig/F'),
#  binning= [80,20,100] if args.selection.count('metSig20') else ([25,5,30] if args.selection.count('metSig') else [30,0,30]),
#))
#
#plots.append(Plot(
#  texX = 'E_{T}^{miss} significance', texY = 'Number of Events',
#  attribute = TreeVariable.fromString('MET_significance/F'),
#  binning= [50,0,200],
#))
#
#plots.append(Plot(
#  texX = 'uncl. E_{T} (GeV)', texY = 'Number of Events',
#  attribute = TreeVariable.fromString('MET_sumEt/F'),
#  binning= [60,0,6000],
#))
#
#plots.append(Plot(
#  texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
#  attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
#  binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
#))
#
#plots.append(Plot(
#texX = 'M_{T2}(bb) (GeV)', texY = 'Number of Events / 30 GeV',
#attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
#binning=[420/30,70,470],
#))
#
#plots.append(Plot(
#texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
#attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
#binning=[420/30,0,400],
#))
#
#plots.append(Plot( name = "dl_mt2blbl_coarse",       # SR binning of MT2ll
#texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
#attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
#binning=[400/100, 0, 400],
#))
#
##plots.append(Plot( name = "MVA_T2tt_default",
##texX = 'MVA_{T2tt} (default)', texY = 'Number of Events',
##attribute = TreeVariable.fromString( "MVA_T2tt_default/F" ),
##binning=[50, 0, 1],
##))
#
#
#plotting.fill(plots, read_variables = read_variables, sequence = [])
#
#drawPlots(plots, 1.)
#
#logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
