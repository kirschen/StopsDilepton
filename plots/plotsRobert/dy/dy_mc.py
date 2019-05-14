#!/usr/bin/env python
''' Analysis script for standard plots
'''
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
from Samples.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-relIso0.12-looseLeptonVeto-mll20-allZ')
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
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    DY_NLO_16         = Sample.fromDirectory( "DY_NLO_16", "/afs/hephy.at/data/rschoefbeck02/nanoTuples/stops_2016_nano_v0p7/dilep/DYJetsToLL_M50_ext2" )
    DY_NLO_M10to50_16 = Sample.fromDirectory( "DY_NLO_M10to50_16", "/afs/hephy.at/data/rschoefbeck02/nanoTuples/stops_2016_nano_v0p7/dilep/DYJetsToLL_M10to50" )

    DY_NLO, DY_NLO_lowM, DY_LO, DY_LO_lowM = DY_NLO_16, DY_NLO_M10to50_16, DY_HT_LO_M50_16, DY_HT_LO_M5to50_16

samples = [ DY_NLO, DY_NLO_lowM, DY_LO, DY_LO_lowM ]

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
    if "mt2ll100" in args.selection and args.noData: lines += [(0.55, 0.5, 'M_{T2}(ll) > 100 GeV')] # Manually put the mt2ll > 100 GeV label
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      _drawObjects = []

      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_,
            ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = not (args.splitMET or args.splitMETSig),
            yRange = (0.03, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png"],
          )
      elif isinstance( plot, Plot2D ):

          p_mc = Plot2D.fromHisto( plot.name+'_mc', plot.histos[:1], texX = plot.texX, texY = plot.texY )
          plotting.draw2D(p_mc,
            plot_directory = plot_directory_,
            #ratio = {'yRange':(0.1,1.9)},
            logX = False, logY = False, logZ = log, #sorting = True,
            #yRange = (0.03, "auto") if log else (0.001, "auto"),
            #scaling = {},
            #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
            copyIndexPHP = True, extensions = ["png"], 
          )
          p_data = Plot2D.fromHisto( plot.name+'_data', plot.histos[1:], texX = plot.texX, texY = plot.texY )
          plotting.draw2D(p_data,
            plot_directory = plot_directory_,
            #ratio = {'yRange':(0.1,1.9)},
            logX = False, logY = False, logZ = log, #sorting = True,
            #yRange = (0.03, "auto") if log else (0.001, "auto"),
            #scaling = {},
            #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
            copyIndexPHP = True, extensions = ["png"], 
          )

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"


for sample in samples:
    sample.setSelectionString(  "&&".join([getFilterCut(isData=False, year=args.year), getLeptonSelection("SF"), cutInterpreter.cutString(args.selection)]) )
    if args.small:
        sample.reduceFiles( to=1)

samples = [ DY_NLO, DY_NLO_lowM, DY_LO, DY_LO_lowM ]

h_DY_NLO            = DY_NLO.get1DHistoFromDraw("dl_mass", [50,10,150], "(1)", "weight")
h_DY_NLO.style      = styles.lineStyle( ROOT.kOrange, dashed = True)
h_DY_NLO.legendText = "NLO M50" 
h_DY_NLO_lowM       = DY_NLO_lowM.get1DHistoFromDraw("dl_mass", [50,10,150], "(1)", "weight")
h_DY_NLO_lowM.style = styles.lineStyle( ROOT.kRed, dashed = True)
h_DY_NLO_lowM.legendText = "NLO M10to50" 

h_DY_NLO_tot        = h_DY_NLO.Clone()
h_DY_NLO_tot.Add( h_DY_NLO_lowM )
h_DY_NLO_tot.style  = styles.lineStyle( ROOT.kRed)
h_DY_NLO_tot.legendText = "NLO inc." 

h_DY_LO             = DY_LO.get1DHistoFromDraw("dl_mass", [50,10,150], "(1)", "weight")
h_DY_LO.style       = styles.lineStyle( ROOT.kGreen, dashed = True)
h_DY_LO.legendText  = "LO M50" 
h_DY_LO_lowM        = DY_LO_lowM.get1DHistoFromDraw("dl_mass", [50,10,150], "(1)", "weight")
h_DY_LO_lowM.style  = styles.lineStyle( ROOT.kBlue, dashed = True)
h_DY_LO_lowM.legendText = "LO M10to50" 

h_DY_LO_tot         = h_DY_LO.Clone()
h_DY_LO_tot.Add( h_DY_LO_lowM )
h_DY_LO_tot.style   = styles.lineStyle( ROOT.kBlue)
h_DY_LO_tot.legendText = "LO inc." 


plot = Plot.fromHisto( args.selection+"_mll", [[h_DY_LO], [h_DY_LO_lowM], [h_DY_NLO_lowM], [h_DY_NLO], [h_DY_NLO_tot], [h_DY_LO_tot], ] )

plotting.draw(plot, plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/DY/", logY = True, 
    ratio = {'histos':[(4,5)], 'yRange':(0.5,2), 'texY':"NLO/LO"},
    legend = ( [0.15, 0.6, 0.8, 0.9],2),
    )
