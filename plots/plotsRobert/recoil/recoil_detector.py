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

# RootTools
from RootTools.core.standard             import *

# StopsDilepton
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, map_level
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.GaussianFit     import GaussianFit
from StopsDilepton.plots.pieChart        import makePieChart

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--mode',               action='store',      default="mumu",          nargs='?', choices=["mumu", "ee"], help="Lepton flavor")
argParser.add_argument('--overwrite',                               action='store_true',     help='Overwrite?', )
argParser.add_argument('--plot_directory',     action='store',      default='StopsDilepton/recoil')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ')
argParser.add_argument('--preHEM',             action='store_true', default=False)
argParser.add_argument('--postHEM',            action='store_true', default=False)
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
#
from Analysis.Tools.puReweighting import getReweightingFunction

if args.year == 2016:
    data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
elif args.year == 2017:
    data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
elif args.year == 2018:
    data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]
    
#if args.small:
#    mc = mc[-2:]

for sample in mc: sample.style = styles.fillStyle(sample.color)

# output directory
postfix = ''
if args.year==2018:
    if args.preHEM:
        postfix = '_preHEM'
    elif args.postHEM:
        postfix = '_postHEM'

output_directory = os.path.join(plot_directory, args.plot_directory, str(args.year)+postfix, args.selection )

# Text on the plots
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def defDrawObjects( plotData, dataMCScale, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, dataMCScale, drawObjects = None):
  for log in [False, True]:
    plot_directory_ = os.path.join(output_directory, mode + ("_log" if log else ""))
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if mode == "all": plot.histos[1][0].legendText = "Data"
      if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)},
	    logX = False, logY = log, sorting = True,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {},
	    legend = (0.15,0.88-0.04*sum(map(len, plot.histos)),0.65,0.88),
	    drawObjects = defDrawObjects( True, dataMCScale , lumi_scale ) + ( drawObjects if drawObjects is not None else [] ) ,
        copyIndexPHP = True,
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ

u_x = "met_pt*cos(met_phi)"
u_y = "met_pt*sin(met_phi)"

#nJetGood_binning = [0, 1, 2, 3, 4, 10 ]
dl_pt_binning    = [0, 50, 100, 150, 200, 300, 500 ]
dl_eta_binning   = [ -5, -3, -1, 1, 3, 5 ]
dl_phi_binning   = [-3.1415, -2, -0.5, 0.5, 2, 3.1415 ]
u_x_binning   = [ i*5 for i in range(-40, 41) ]
u_y_binning   = [ i*5 for i in range(-40, 41) ]

#nJetGood_bins = [ (nJetGood_binning[i],nJetGood_binning[i+1]) for i in range(len(nJetGood_binning)-1) ]
dl_pt_bins = [ (dl_pt_binning[i],dl_pt_binning[i+1]) for i in range(len(dl_pt_binning)-1) ]
dl_eta_bins = [ (dl_eta_binning[i],dl_eta_binning[i+1]) for i in range(len(dl_eta_binning)-1) ]
dl_phi_bins = [ (dl_phi_binning[i],dl_phi_binning[i+1]) for i in range(len(dl_phi_binning)-1) ]

#
# Loop over channels
#

# Selection & weights 
if args.year == 2016:
  data_sample = Run2016
  data_sample.texName = "data (2016)"
elif args.year == 2017:
  data_sample = Run2017
  data_sample.texName = "data (2017)"
elif args.year == 2018:
  data_sample = Run2018
  data_sample.texName = "data (2018)"

data_sample.name           = "data"
data_sample.style          = styles.errorStyle(ROOT.kBlack)

# Data weight & cut 
weightString =  "weight"
data_sample.setSelectionString([getFilterCut(isData=True, year=args.year), getLeptonSelection(args.mode), cutInterpreter.cutString(args.selection)])
data_sample.setWeightString( weightString )

# HEM flag
if args.preHEM:
    data_sample.addSelectionString("run<319077")
if args.postHEM:
    data_sample.addSelectionString("run>=319077")

# MC weight & cut
for sample in mc:
  weightString =  "weight*reweightPU36fb*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF"
  sample.setSelectionString([getFilterCut(isData=False, year=args.year), getLeptonSelection(args.mode), cutInterpreter.cutString(args.selection)])
  sample.setWeightString(weightString)

stack = Stack(mc, data_sample)

lumi_scale                 = data_sample.lumi/1000
if args.preHEM:   lumi_scale *= 0.37
if args.postHEM:  lumi_scale *= 0.63

data_sample.scale          = 1.

for sample in mc:
    sample.scale          = lumi_scale

# small 
if args.small:
    for sample in stack.samples:
        sample.normalization = 1.
        sample.reduceFiles( factor = 40 )
        sample.scale /= sample.normalization

pickle_file = os.path.join(output_directory, 'recoil_detector_%s.pkl'%args.mode )
if not os.path.exists( output_directory ): 
    os.makedirs( output_directory )
if not os.path.isfile( pickle_file ) or args.overwrite:
    # Make 3D plot to get u_x/u_y for in nJet and dl_pt bins
    u_proj_x = {}
    u_proj_y = {}
    for sample in stack.samples:
        u_proj_x[sample.name] = {} 
        u_proj_y[sample.name] = {} 
        for dl_pt_bin in dl_pt_bins:
            logger.info( "Sample %s pt bin %r", sample.name, dl_pt_bin )
            u_proj_x[sample.name][dl_pt_bin] = sample.get2DHistoFromDraw(u_x+":dl_phi:dl_eta", [dl_eta_binning,dl_phi_binning], binningIsExplicit=True, isProfile = 's') 
            u_proj_y[sample.name][dl_pt_bin] = sample.get2DHistoFromDraw(u_y+":dl_phi:dl_eta", [dl_eta_binning,dl_phi_binning], binningIsExplicit=True, isProfile = 's') 
            u_proj_x[sample.name][dl_pt_bin].Scale(sample.scale)
            u_proj_y[sample.name][dl_pt_bin].Scale(sample.scale)

    pickle.dump( [u_proj_x, u_proj_y], file( pickle_file, 'w' ) )
    logger.info( "Written pkl %s", pickle_file )
else:
    logger.info( "Loading pkl %s", pickle_file )
    u_proj_x, u_proj_y = pickle.load( file( pickle_file ) )

for dl_pt_bin in dl_pt_bins:
    for prefix, u_proj in  [ [ "x", u_proj_x], [ "y", u_proj_y ] ]:
        # Get histos
        histos =  map_level( lambda s: u_proj[s.name][dl_pt_bin], stack, 2 )

        # make plot
        plot2D =  Plot2D.fromHisto( name = "u_%s_dl_pt_%i_%i"%( prefix, dl_pt_bin[0], dl_pt_bin[1] ), 
                histos = histos, 
                texX = "u_{%s}" % prefix ) 
        # sums
        h_mc   = plot2D.histos_added[0][0]
        h_data = plot2D.histos_added[1][0]

        for log in [False, True]:
            plot_directory_ = os.path.join(output_directory, args.mode + ("_log" if log else ""))
            for postfix, h2D in [ [ "mc", h_mc ], [ "data", h_data ] ]: 
                plotting.draw2D(
                    Plot2D.fromHisto( 
                        name = "%s_u_%s_dl_pt_%i_%i"%( postfix, prefix, dl_pt_bin[0], dl_pt_bin[1] ),
                        histos = [[h_mc]], texX = "u_{%s}" % prefix ),
                
                    plot_directory = plot_directory_,
                    logX = False, logY = False, logZ = False,
                    copyIndexPHP = True,
            )
