#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools
import pickle
from math                                import sqrt, cos, sin, pi
import array
import uuid

# RootTools
from RootTools.core.standard             import *

# StopsDilepton
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, map_level
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--mode',               action='store',      default="mumu",          nargs='?', choices=["mumu", "ee", "SF"], help="Lepton flavor")
argParser.add_argument('--plot_directory',     action='store',      default='qTLep')
argParser.add_argument('--era',                action='store', type=str,      default="2016")
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small: args.plot_directory += "_small"
plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era)

#
# Make samples, will be searched for in the postProcessing directory
#
if "2016" in args.era:
    year = 2016
elif "2017" in args.era:
    year = 2017
elif "2018" in args.era:
    year = 2018

logger.info( "Working in year %i", year )
if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    tt = Top_pow_16
    dy = DY_LO_16
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    tt = Top_pow_17
    dy = DY_LO_17
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    tt = Top_pow_18
    dy = DY_LO_18


# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

# Text on the plots
tex2 = ROOT.TLatex()
tex2.SetNDC()
tex2.SetTextSize(0.03)
tex2.SetTextAlign(11) # align right

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)&&" + offZ+")||isEMu)"

selectionString = "&&".join( [ cutInterpreter.cutString(args.selection), getLeptonSelection( args.mode ), getFilterCut(isData=False,year=year) ] )

# small 
if args.small:
    for sample in [ tt, dy ]:
        sample.normalization = 1.
        sample.reduceFiles( to=1 )

# qT + ETmiss + u = 0
u_para_fake = "-met_pt*cos(met_phi-dl_phi)+GenMET_pt*cos(GenMET_phi-dl_phi)" # u_para is actually (u+qT)_para = -ET.n_para
u_perp_fake = "-met_pt*cos(met_phi-(dl_phi-pi/2.))+GenMET_pt*cos(GenMET_phi-(dl_phi-pi/2.))" # u_perp = -ET.n_perp (where n_perp is n with phi->phi-pi/2) 

#qT          = "sqrt((l1_pt*cos(l1_phi) + l2_pt*cos(l2_phi) + GenMET_pt*cos(GenMET_phi))**2+(l1_pt*sin(l1_phi) + l2_pt*sin(l2_phi) + GenMET_pt*sin(GenMET_phi))**2)"
qT          = "dl_pt"

##nJetGood_binning = [1, 10 ]
qt_binning    = [0, 50, 100, 150, 200, 300, 400 ]
qt_bins = [ (qt_binning[i],qt_binning[i+1]) for i in range(len(qt_binning)-1) ]
u_para_binning   = [ i*10 for i in range(-20, 21) ]

h_u_para_fake = {}
h_u_perp_fake = {}
for s in [tt, dy]:
    h_u_para_fake[s.name]={}
    h_u_perp_fake[s.name]={}
    for qt_bin in qt_bins:
        logger.info( "At qt bin %r for sample %s", qt_bin, s.name)
        #print selectionString+"&&"+qT+">%i"%(qt_bin[0])+"&&"+qT+"<%i"%(qt_bin[1])
        h_u_para_fake[s.name][qt_bin] = s.get1DHistoFromDraw( u_para_fake, u_para_binning, 
            selectionString = selectionString+"&&"+qT+">%i"%(qt_bin[0])+"&&"+qT+"<%i"%(qt_bin[1]), 
            weightString = "weight", binningIsExplicit = True)
        if h_u_para_fake[s.name][qt_bin].Integral()>0:
            h_u_para_fake[s.name][qt_bin].Scale(1./h_u_para_fake[s.name][qt_bin].Integral())
        h_u_para_fake[s.name][qt_bin].style = styles.lineStyle( s.color )

        h_u_perp_fake[s.name][qt_bin] = s.get1DHistoFromDraw( u_perp_fake, u_para_binning, 
            selectionString = selectionString+"&&"+qT+">%i"%(qt_bin[0])+"&&"+qT+"<%i"%(qt_bin[1]), 
            weightString = "weight", binningIsExplicit = True)
        if h_u_perp_fake[s.name][qt_bin].Integral()>0:
            h_u_perp_fake[s.name][qt_bin].Scale(1./h_u_perp_fake[s.name][qt_bin].Integral())
        h_u_perp_fake[s.name][qt_bin].style = styles.lineStyle( s.color )

for qt_bin in qt_bins:
    u_para_fake_plot = Plot.fromHisto( "u_para_fake_qT_%i_%i"%qt_bin, [ [h_u_para_fake[dy.name][qt_bin]], [h_u_para_fake[tt.name][qt_bin]] ], texX = "u_para_fake" )
    print h_u_para_fake[dy.name][qt_bin].Integral(), h_u_para_fake[tt.name][qt_bin].Integral()
    plotting.draw(u_para_fake_plot, plot_directory = os.path.join( plot_directory_ ), ratio = None, logY = True, logX = False, copyIndexPHP = True, yRange=(10**-4,1))
    u_perp_fake_plot = Plot.fromHisto( "u_perp_fake_qT_%i_%i"%qt_bin, [ [h_u_perp_fake[dy.name][qt_bin]], [h_u_perp_fake[tt.name][qt_bin]] ], texX = "u_perp_fake" )
    print h_u_perp_fake[dy.name][qt_bin].Integral(), h_u_perp_fake[tt.name][qt_bin].Integral()
    plotting.draw(u_perp_fake_plot, plot_directory = os.path.join( plot_directory_ ), ratio = None, logY = True, logX = False, copyIndexPHP = True, yRange=(10**-4,1))
