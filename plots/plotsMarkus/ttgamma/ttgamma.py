#!/usr/bin/env python
''' ttgamma background analysis script
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

from math                                import sqrt, cos, sin, pi, atan2, cosh
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from Samples.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator

# from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='ttgamma')
argParser.add_argument('--era',                action='store', type=str,      default="Run2016")
argParser.add_argument('--selection',          action='store',      default='lepSel-photon30-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1-photonJetdR')
argParser.add_argument('--reweightBosonPt',    action='store_true', default=False)
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
if args.reweightBosonPt:              args.plot_directory += "_gammaToZ"
#
# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

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
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ TTZ_18, TTG_18, Top_pow_18, TTXNoZ_18, multiBoson_18, DY_HT_LO_18]

try:
  data_sample = eval(args.era)
except Exception as e:
  logger.error( "Didn't find %s", args.era )
  raise e

lumi_scale                 = data_sample.lumi/1000
data_sample.scale          = 1.
for sample in mc:
    sample.scale          = lumi_scale

if args.small:
    for sample in mc + [data_sample]:
        sample.normalization = 1.
        sample.reduceFiles( factor = 40 )
        #sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

#
# Text on the plots
#
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

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = True, 
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {0:1},
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
read_variables += ["nPhotonGood/I", "overlapRemoval/I", "nGoodMuons/I", "nGoodElectrons/I", "photon_pt/F", "photon_eta/F", "photon_phi/F"]
read_variables += ["dl_mt2ll_photonEstimated/F", "met_pt_photonEstimated/F", "metSig_photonEstimated/F", "dlg_mass/F"]
#read_variables += ["photonJetdR/F", "photonLepdR/F"]

sequence = []

def make_newMET( event, sample ):
    # add photon to missing energy
    newmet_x = event.met_pt*cos(event.met_phi) + event.photon_pt*cos(event.photon_phi)
    newmet_y = event.met_pt*sin(event.met_phi) + event.photon_pt*sin(event.photon_phi)
    event.met_pt_photonCalculated = sqrt(newmet_x**2 + newmet_y**2)
    event.met_phi_photonCalculated = atan2(newmet_y, newmet_x)

    # calculate mt2ll
    mt2Calculator.reset()
    mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
    mt2Calculator.setMet(event.met_pt_photonCalculated, event.met_phi_photonCalculated)
    event.dl_mt2llPlusPhoton = mt2Calculator.mt2ll()

sequence.append( make_newMET )

def make_mass_llg( event, sample ):
    # calculate 3 particle invariant mass m(llgamma)
    #event.mass_llg = float('nan')
    p_pt = [event.l1_pt, event.l2_pt, event.photon_pt]
    p_phi = [event.l1_phi, event.l2_phi, event.photon_phi]
    p_eta = [event.l1_eta, event.l2_eta, event.photon_eta]
    mass_llg2 = 0
    for j in range(1,3):
        for i in range(j):
            mass_llg2 += 2*p_pt[i]*p_pt[j]*(cosh(p_eta[i]-p_eta[j]) - cos(p_phi[i]-p_phi[j]))
    event.mass_llg = sqrt(mass_llg2)

    # add offZ cut for mass_llg
    if abs(event.mass_llg-91.1876)>15:
        event.weight_llgOffZ = 1
    else:
        event.weight_llgOffZ = 0
#    if event.photonJetdR < 0.3 or event.photonLepdR < 0.3:
#        print "~~~~~> photonJetdR %f photonLepdR %f"%(event.photonJetdR,event.photonLepdR)

sequence.append( make_mass_llg )

#
#
# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)&&" + offZ+")||isEMu)"

# get boson pt reweighting histo
if args.reweightBosonPt:
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#    logger.info( "Now obtain nvtx reweighting histo" )
#    data_selectionString = "&&".join([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
#    data_nvtx_histo = data_sample.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=data_selectionString, weightString = "weight" )
#    data_nvtx_histo.Scale(1./data_nvtx_histo.Integral())
#
#    mc_selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
#    mc_histos  = [ s.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=mc_selectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF") for s in mc]
#    mc_nvtx_histo     = mc_histos[0]
#    for h in mc_histos[1:]:
#        mc_nvtx_histo.Add( h )
#    mc_nvtx_histo.Scale(1./mc_nvtx_histo.Integral())
#    def nvtx_puRW( nvtx ):
#        i_bin = mc_nvtx_histo.FindBin( nvtx )
#        mc_val = mc_nvtx_histo.GetBinContent( i_bin)
#        return data_nvtx_histo.GetBinContent( i_bin )/mc_val if mc_val>0 else 1
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    logger.info( "Now obtaining gamma -> Z reweighting histo" )

    gamma_selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF")])
    gamma_pt_histo = mc[1].get1DHistoFromDraw( "photon_pt", [100/5, 0, 100], selectionString=gamma_selectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF" )
    print "~~gamma histo integral %f"%gamma_pt_histo.Integral()
    gamma_pt_histo.Scale(1./gamma_pt_histo.Integral() if gamma_pt_histo.Integral() != 0 else 1.)

    Z_selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF")])
    Z_pt_histo  = mc[0].get1DHistoFromDraw( "Z_pt", [100/5, 0, 100], selectionString=Z_selectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF")
    print "~~Z histo integral %f"%gamma_pt_histo.Integral()
    Z_pt_histo.Scale(1./Z_pt_histo.Integral() if Z_pt_histo.Integral() != 0 else 1.)

    def gammaToZRW( photon_pt ):
        i_bin = Z_pt_histo.FindBin( photon_pt )
        Z_val = Z_pt_histo.GetBinContent( i_bin )
        return gamma_pt_histo.GetBinContent( i_bin )/Z_val if Z_val>0 else 1


#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}

  data_sample.setSelectionString([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I","run/I"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  if args.reweightBosonPt:
    weight_ = lambda event, sample: event.weight*event.weight_llgOffZ
  else:
    weight_ = lambda event, sample: event.weight

  for sample in mc:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', "l1_muIndex/I", "l2_muIndex/I"]
    if "TTG" in sample.name and args.reweightBosonPt:
        sample.weight         = lambda event, sample: gammaToZRW(event.photon_pt)*event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
#    elif args.reweightBosonPt:
#        sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.weight_llgOffZ
    else:
        sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode),"overlapRemoval==1"])
    if sample.name == "TTXNoZ": sample.color = ROOT.kMagenta + 2
  for sample in mc: sample.style = styles.fillStyle(sample.color)

  if not args.noData:
    stack = Stack(mc, data_sample)
  else:
    stack = Stack(mc)

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[100/5,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 5 GeV',
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[100/5,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'p_{T}(#gamma) (GeV)', texY = 'Number of Events / 5 GeV',
    attribute = TreeVariable.fromString( "photon_pt/F" ),
    binning=[100/5,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    name = "Z_pt",
    texX = 'p_{T}(Z) (GeV)', texY = 'Number of Events / 5 GeV',
    attribute = lambda event, sample: sqrt(2*event.l1_pt*event.l2_pt*(cosh(event.l1_eta-event.l2_eta)-cos(event.l1_phi-event.l2_phi))),
    binning=[100/5,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[40,0,400], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    name = 'met_pt_photonCalculated', texX = 'E_{T}^{miss} + photon (GeV)', texY = 'Number of Events',
    attribute = lambda event, sample: event.met_pt_photonCalculated,
    binning=[40, 0, 400],
  ))

  plots.append(Plot(
    name = 'mass_llg', texX = 'm(ll#gamma) (GeV)', texY = 'Number of Events / 10 GeV',
    attribute = lambda event, sample: event.mass_llg,
    binning=[310/10, 50, 360],
  ))

  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300]
  ))

  plots.append(Plot(
    name = 'dl_mt2ll_photonCalculated', 
    texX = 'M_{T2}(ll) (#gamma included for t#bar{t}#gamma) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = lambda event, sample: event.dl_mt2llPlusPhoton,
    binning=[300/20, 0, 300]
  ))

  # estimated values in tuple
  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll_photonEstimated/F" ),
    binning=[300/20,0,300]
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss} + photon (GeV)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "met_pt_photonEstimated/F" ),
    binning=[40,0,400]
  ))

  plots.append(Plot(
    texX = 'significance(E_{T}^{miss} + photon) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "metSig_photonEstimated/F" ),
    binning=[20,0,100]
  ))

  plots.append(Plot(
    texX = 'm(ll#gamma) (GeV)', texY = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "dlg_mass/F" ),
    binning=[310/10,50,360]
  ))

  plotting.fill(plots, read_variables = read_variables, sequence = sequence)

  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu")
          h.GetXaxis().SetBinLabel(2, "e#mu")
          h.GetXaxis().SetBinLabel(3, "ee")
  if args.noData: yields[mode]["data"] = 0
  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  drawPlots(plots, mode, dataMCScale)
  allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["SF","all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
    except: yields[mode][y] = 0
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  for plot in allPlots['mumu']:
    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
	for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	  if i==k:
	    j.Add(l)

  drawPlots(allPlots['mumu'], mode, dataMCScale)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

