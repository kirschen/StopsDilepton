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
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='analysisPlots/DYcomp')
argParser.add_argument('--era',                action='store', type=str,      default="2016")
argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"

if "2016" in args.era:
    year = 2016
elif "2017" in args.era:
    year = 2017
elif "2018" in args.era:
    year = 2018

logger.info( "Working in year %i", year )

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    DY = DY_HT_LO_16
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    DY = DY_HT_LO_17
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    DY = DY_HT_LO_18

offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

if args.small:
    DY.reduceFiles( to = 1 )

DY.setSelectionString([getFilterCut(isData=False, year=year), getLeptonSelection("all")])

#h_DY3 = DY.get1DHistoFromDraw("dl_mt2ll", binning=[0,20,40,60,80,100,140,240,340], binningIsExplicit = True, weightString = "weight", selectionString = 'Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) >=1')
#h_DY3.legendText = "DY:1 mismjet>40" 
#h_DY3.style = styles.fillStyle( ROOT.kGreen  )
#
#
#h_DY2 = DY.get1DHistoFromDraw("dl_mt2ll", binning=[0,20,40,60,80,100,140,240,340], binningIsExplicit = True, weightString = "weight", selectionString = 'Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) >= 40')
#h_DY2.legendText = "DY:~1& tot mismjet>40" 
#h_DY2.style = styles.fillStyle( ROOT.kGreen + 1 )

h_DY1 = DY.get1DHistoFromDraw("dl_mt2ll", binning=[0,20,40,60,80,100,140,240,340], binningIsExplicit = True, weightString = "weight", selectionString = '((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1))')
h_DY1.legendText = "#geq 1 lep nonPrompt" 
h_DY1.style = styles.fillStyle( ROOT.kGreen + 2 )
 
h_DY0 = DY.get1DHistoFromDraw("dl_mt2ll", binning=[0,20,40,60,80,100,140,240,340], binningIsExplicit = True, weightString = "weight", selectionString = '!(((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1)))')
h_DY0.legendText = "other" 
h_DY0.style = styles.fillStyle( ROOT.kGreen + 3 )

plotting.draw(
    Plot.fromHisto(name = "DY_comp", histos = [ [ h_DY0, h_DY1 ] ], texX = "M_{T2}(ll)", texY = "Number of Events"),
    plot_directory = os.path.join( plot_directory, args.plot_directory), 
    logX = False, logY = True, sorting = True,
     yRange = (0.0003, "auto"), 
    #ratio = ratio, 
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)
