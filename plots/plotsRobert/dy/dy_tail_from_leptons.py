#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools
import random

from math                                import sqrt, cos, sin, pi, atan2, cosh
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator

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
argParser.add_argument('--selection',          action='store',      default='njet2p-relIso0.12-looseLeptonVeto-mll20-POGMetSig12-dPhiJet0-dPhiJet1-allZ')
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
# Read variables and sequences
#

read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "RawMET_pt/F", "RawMET_phi/F"]

#
# Loop over channels
#
allPlots   = {}

lumi_scale = 136
weight_ = lambda event, sample: lumi_scale*event.weight

from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
dy_sample = DY_HT_LO_16

mc = [ dy_sample ]

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

for sample in [dy_sample]:
    sample.setSelectionString(  "&&".join([getFilterCut(isData=False, year=args.year), getLeptonSelection("SF"), cutInterpreter.cutString(args.selection)]) )
    #sample.style    = styles.fillStyle(sample.color, lineWidth = 0)
    #sample.scale    = lumi_scale
    sample.weight         = lambda event, sample: event.weight

    if args.small:
        sample.reduceFiles( to=30)

#AN 2018/008 v7 Sec. 5.2.2. Fig. 59:
# the fraction of strongly mismeasured muons >20% is a bit lower than about 4%*(pT-500)/2500

sequence = []
def calc_mt2ll_mism( event, sample ):
    mt2Calculator.reset()
    # Parametrisation vector - # define qt as GenMET + leptons

    #mismeasurement probability

    #p_mism_1 = 0.04*(event.l1_pt - 50)/250. if event.l1_pt>50 else 0
    #p_mism_2 = 0.04*(event.l2_pt - 50)/250. if event.l2_pt>50 else 0

    # recalc with mismeasured leptons
    dm_x = 0
    dm_y = 0
    if event.l1_pt>250:
        l1_pt_mism = event.l1_pt/0.8 
        dm_x += (event.l1_pt-l1_pt_mism)*cos(event.l1_phi)
        dm_y += (event.l1_pt-l1_pt_mism)*sin(event.l1_phi)
    else:
        l1_pt_mism = event.l1_pt
    if  event.l2_pt>250:
        l2_pt_mism = event.l2_pt/0.8 
        dm_x += (event.l2_pt-l2_pt_mism)*cos(event.l2_phi)
        dm_y += (event.l2_pt-l2_pt_mism)*sin(event.l2_phi)
    else:
        l2_pt_mism = event.l2_pt

    met_pt_mism   = sqrt( (event.met_pt*cos(event.met_phi) + dm_x)**2 + (event.met_pt*sin(event.met_phi) + dm_y)**2 )
    met_phi_mism  = atan2( event.met_pt*sin(event.met_phi) + dm_y,  event.met_pt*cos(event.met_phi) + dm_x )

    mt2Calculator.setLeptons(l1_pt_mism, event.l1_eta, event.l1_phi, l2_pt_mism, event.l2_eta, event.l2_phi)
    mt2Calculator.setMet(met_pt_mism, met_phi_mism)
    event.dl_mt2ll_mism     = mt2Calculator.mt2ll()

    event.dl_mass_mism = sqrt(2*l1_pt_mism*l2_pt_mism*(cosh(event.l1_eta-event.l2_eta)-cos(event.l1_phi-event.l2_phi)))

    #print event.dl_mass_mism, l1_pt_mism, event.l1_pt, event.dl_mt2ll_mism, event.dl_mt2ll

sequence.append( calc_mt2ll_mism )

stack = Stack([dy_sample])

# Use some defaults
Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper')

plots = []

plots.append(Plot( name = "dl_mt2ll",
  texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: event.dl_mt2ll_mism if abs(event.dl_mass-91.2)>15 else float('nan'),
  binning=[300/20, 0,300],
))
plots.append(Plot( name = "dl_mt2ll_mism",
  texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
  attribute = lambda event, sample: event.dl_mt2ll_mism if abs(event.dl_mass_mism-91.2)>15 else float('nan'),
  binning=[300/20, 0,300],
))

#
plotting.fill(plots, read_variables = read_variables, sequence = sequence)

Plot.setDefaults()

h_orig = plots[0].histos[0][0]
h_mism = plots[1].histos[0][0]

h_orig.style = styles.lineStyle( ROOT.kBlue )
h_mism.style = styles.lineStyle( ROOT.kRed )
h_orig.legendText = "orig"
h_mism.legendText = "mism"

plot = Plot.fromHisto( "dy_comp_x10" + ("_small" if args.small else ""), histos = [[h_orig], [h_mism]] ) 
plotting.draw( plot, plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/etc/", logY = True, yRange = (0.01, "auto"))
