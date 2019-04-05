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
from Samples.Tools.metFilters            import getFilterCut
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
argParser.add_argument('--plot_directory',     action='store',      default='StopsDilepton/recoil')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ')
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
    
if args.small:
    mc = mc[-2:]

for sample in mc: sample.style = styles.fillStyle(sample.color)
 
#
# Text on the plots
#

output_directory = os.path.join(plot_directory, args.plot_directory, str(args.year), args.selection )

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

u_para = "met_pt*cos(met_phi-dl_phi)"
u_perp = "met_pt*cos(met_phi-dl_phi+pi/2.)"

nJetGood_binning = [0, 1, 2, 3, 10 ]
dl_pt_binning    = [0, 50, 100, 150, 200, 300, 500 ]
u_para_binning   = [ i*2 for i in range(-100, 100) ]

nJetGood_bins = [ (nJetGood_binning[i],nJetGood_binning[i+1]) for i in range(len(nJetGood_binning)-1) ]
dl_pt_bins = [ (dl_pt_binning[i],dl_pt_binning[i+1]) for i in range(len(dl_pt_binning)-1) ]

#
# Loop over channels
#
allModes   = ['mumu','mue','ee']
if args.small:
    allModes = allModes[:1]

for index, mode in enumerate(allModes):
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
    data_sample.scale          = 1.
    lumi_scale                 = data_sample.lumi/1000
    if args.preHEM:   lumi_scale *= 0.37
    if args.postHEM:  lumi_scale *= 0.63

    # HEM flag
    if args.preHEM:
        data_sample.addSelectionString("run<319077")
    if args.postHEM:
        data_sample.addSelectionString("run>=319077")

    # Data weight & cut 
    weightString =  "weight"
    data_sample.setSelectionString([getFilterCut(isData=True, year=args.year), getLeptonSelection(mode), cutInterpreter.cutString(args.selection)])
    data_sample.setWeightString( weightString )

    # MC weight & cut
    for sample in mc:
      weightString =  "weight*reweightPU36fb*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF"
      sample.setSelectionString([getFilterCut(isData=False, year=args.year), getLeptonSelection(mode), cutInterpreter.cutString(args.selection)])
      sample.setWeightString(weightString)
  
    stack = Stack(mc, data_sample)
 
    # small 
    for sample in stack.samples:
        sample.scale          = lumi_scale
        if args.small:
            sample.normalization = 1.
            sample.reduceFiles( factor = 40 )
            sample.scale /= sample.normalization

    pickle_file = os.path.join(output_directory, 'recoil_%s.pkl'%mode )
    if not os.path.exists( output_directory ): 
        os.makedirs( output_directory )
    if not os.path.isfile( pickle_file ):
        # Make 3D plot to get u_para/u_perp for in nJet and dl_pt bins
        h3D_u_para = {}
        h3D_u_perp = {}
        for sample in stack.samples:
            h3D_u_para[sample.name] = sample.get3DHistoFromDraw("nJetGood:dl_pt:"+u_para, [u_para_binning,dl_pt_binning,nJetGood_binning], binningIsExplicit=True)
            h3D_u_perp[sample.name] = sample.get3DHistoFromDraw("nJetGood:dl_pt:"+u_perp, [u_para_binning,dl_pt_binning,nJetGood_binning], binningIsExplicit=True)

        # Projections and bookkeeping
        u_para_proj = {}
        u_perp_proj = {}
        for prefix, u_proj, h3D_u in  [ [ "para", u_para_proj, h3D_u_para], [ "perp", u_perp_proj, h3D_u_perp ] ]:
            for h_name, h in h3D_u.iteritems():
                u_proj[h_name] = {}
                for nJetGood_bin in nJetGood_bins:
                    u_proj[h_name][nJetGood_bin] = {}
                    i_jet_min = h.GetZaxis().FindBin(nJetGood_bin[0]) 
                    i_jet_max = h.GetZaxis().FindBin(nJetGood_bin[1]) 
                    for dl_pt_bin in dl_pt_bins:
                        i_dl_pt_min = h.GetYaxis().FindBin(dl_pt_bin[0]) 
                        i_dl_pt_max = h.GetYaxis().FindBin(dl_pt_bin[1]) 
                        u_proj[h_name][nJetGood_bin][dl_pt_bin] = h.ProjectionX("Proj_%s_%s_%i_%i_%i_%i"%( h_name, prefix, i_dl_pt_min, i_dl_pt_max-1, i_jet_min, i_jet_max-1), i_dl_pt_min, i_dl_pt_max-1, i_jet_min, i_jet_max-1) 

        pickle.dump( [u_para_proj, u_perp_proj], file( pickle_file, 'w' ) )
        logger.info( "Written pkl %s", pickle_file )
    else:
        logger.info( "Loading pkl %s", pickle_file )
        u_para_proj, u_perp_proj = pickle.load( file( pickle_file ) )

    for nJetGood_bin in nJetGood_bins:
        for dl_pt_bin in dl_pt_bins:
            for prefix, u_proj in  [ [ "para", u_para_proj], [ "perp", u_perp_proj ] ]:
                # Get histos
                histos =  map_level( lambda s: u_proj[s.name][nJetGood_bin][dl_pt_bin], stack, 2 )
                # Transfer styles & text
                for i_l, l in enumerate(stack):
                    for i_s, s in enumerate(l):
                        histos[i_l][i_s].style      = s.style
                        histos[i_l][i_s].legendText = s.texName
                # make plot
                plot =  Plot.fromHisto( name = "u_%s_nJet_%i_%i_dl_pt_%i_%i"%( prefix, nJetGood_bin[0], nJetGood_bin[1], dl_pt_bin[0], dl_pt_bin[1] ), 
                        histos = histos, 
                        texX = "u_{#parallel}" if prefix == "para" else "u_{#perp}" ) 
                # fit
                h_mc   = plot.histos_added[0][0]
                h_data = plot.histos_added[1][0]

                drawObjects = []
                #if h_mc.Integral()>0:
                #    mean_mc, sigma_mc     = GaussianFit( h_mc, isData = False, var_name = "u_%s"%prefix )
                #    f_mc   = ROOT.TF1("gauss","gaus(0)",u_para_binning[0],u_para_binning[-1])
                #    f_mc.SetLineColor(ROOT.kRed)
                #    f_mc.SetParameter(0, h_mc.Integral() ) 
                #    f_mc.SetParameter(1, mean_mc ) 
                #    f_mc.SetParameter(2, sigma_mc ) 
                #    extraDrawObjects.append( f_mc )

                #if h_data.Integral()>0:
                #    mean_data, sigma_data = GaussianFit( h_data, isData = True, var_name = "u_%s"%prefix )
                #    f_data = ROOT.TF1("gauss","gaus(0)",u_para_binning[0],u_para_binning[-1])
                #    f_data.SetParameter(0, h_data.Integral() ) 
                #    f_data.SetParameter(1, mean_data ) 
                #    f_data.SetParameter(2, sigma_data ) 
                #    extraDrawObjects.append( f_data )

                drawObjects.append( tex.DrawLatex(0.5, 0.85, 'data: #mu=% 3.2f #sigma=% 3.2f'%( h_data.GetMean(), h_data.GetStdDev()) ) )
                drawObjects.append( tex.DrawLatex(0.5, 0.80, 'MC:  #mu=% 3.2f #sigma=% 3.2f'%( h_mc.GetMean(), h_mc.GetStdDev()) ) )
                # draw
                drawPlots( [ plot ],  mode = mode, dataMCScale = -1, drawObjects = drawObjects )

