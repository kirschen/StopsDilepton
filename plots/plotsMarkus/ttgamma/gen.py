#!/usr/bin/env python
''' script for gen level calculations
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

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',              action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--dpm',                action='store_true',     help='Use dpm?', )
argParser.add_argument('--plot_directory',     action='store',      default='gen')
argParser.add_argument('--beta',              action='store',      default=None, help="Add an additional subdirectory for minor changes to the plots")
argParser.add_argument('--era',                action='store', type=str,      default="Run2018")
argParser.add_argument('--selection',          action='store',      default='')
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

if args.reweightBosonPt:              args.plot_directory += "_gToZ"
if args.small:                        args.plot_directory += "_small"

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

#
# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

if "2016" in args.era:
    year = 2016
    lumi_scale                 = 35.9 
elif "2017" in args.era:
    year = 2017
    lumi_scale                 = 41.9 
elif "2018" in args.era:
    year = 2018
    lumi_scale                 = 59.97 

logger.info( "Working in year %i", year )

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    mc             = [ TTZ_16, TTG_16 ]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    mc             = [ TTZ_17, TTG_17 ]
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    mc             = [ TTZ_18, TTG_18 ]


for sample in mc:
    sample.scale          = lumi_scale

if args.small:
    for sample in mc:
        sample.normalization = 1.
        sample.reduceFiles( factor = 20 )
        #sample.reduceFiles( to = 1 )
        sample.scale /= sample.normalization

#
# Text on the plots
#
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def drawObjects( lumi_scale, scale ):
    lines = [
      (0.15, 0.95, 'CMS Simulation'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f' % (lumi_scale, scale) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, scale):
  for log in [False, True]:
    if args.beta is None:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.era, args.plot_directory, mode + ("_log" if log else ""))
    else:
        plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.era, args.plot_directory, args.beta, mode + ("_log" if log else ""))
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
    
      _drawObjects = []
    
      plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio = {'histos':[(1,0)], 'logY': False, 'style': styles.lineStyle(ROOT.kBlack), 'texY': 't#bar{t}#gamma/t#bar{t}Z', 'yRange': (0.1, 1.9), 'drawObjects':[]},
        logX = False, logY = log, sorting = True, 
        yRange = (0.001, "auto"),
        scaling = {1:0},
        legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
        drawObjects = drawObjects( lumi_scale, scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png", "pdf", "root"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagDeepB/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
read_variables += ["nPhotonGood/I", "overlapRemoval/I", "nGoodMuons/I", "nGoodElectrons/I", "photon_pt/F", "photon_eta/F", "photon_phi/F"]
read_variables += ["dl_mt2ll_photonEstimated/F", "dl_mt2blbl_photonEstimated/F", "met_pt_photonEstimated/F", "metSig_photonEstimated/F", "dlg_mass/F"]
#read_variables += ["photonJetdR/F", "photonLepdR/F"]
read_variables += [
                VectorTreeVariable.fromString("GenPart[pt/F,pdgId/I,genPartIdxMother/I,status/I,statusFlags/I]", nMax=200), 
                "nGenPart/I", "photon_genPt/F", "zBoson_genPt/F", "Z1_pt/F", "nGoodLeptons/I"
                ]

sequence = []

def make_newMET( event, sample ):
    event.met_pt_photonCalculated = event.met_pt
    event.dl_mt2ll_photonCalculated = event.dl_mt2ll
    event.dl_mt2blbl_photonCalculated = event.dl_mt2blbl
    if "TTG" in sample.name:
        # add photon to missing energy
        newmet_x = event.met_pt*cos(event.met_phi) + event.photon_pt*cos(event.photon_phi)
        newmet_y = event.met_pt*sin(event.met_phi) + event.photon_pt*sin(event.photon_phi)
        event.met_pt_photonCalculated = sqrt(newmet_x**2 + newmet_y**2)
        event.met_phi_photonCalculated = atan2(newmet_y, newmet_x)

        # calculate mt2ll
        mt2Calculator.reset()
        mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
        mt2Calculator.setMet(event.met_pt_photonCalculated, event.met_phi_photonCalculated)
        event.dl_mt2ll_photonCalculated = mt2Calculator.mt2ll()

        # obtain b-tagged jets
        if event.nJetGood>=2:
            bjets_idx = []
            for j in range(event.nJetGood):
                if event.JetGood_btagDeepB[j] > 0.4184:
                    bjets_idx.append(j)

            # add non-btagged jets if less than 2 b-tagged jets are in the event
            for j in range(event.nJetGood):
                if len(bjets_idx)<2:
                   bjets_idx.append(j)
                
            # calculate mt2blbl
            mt2Calculator.reset()
            mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
            mt2Calculator.setBJets(event.JetGood_pt[bjets_idx[0]], event.JetGood_eta[bjets_idx[0]], event.JetGood_phi[bjets_idx[0]], event.JetGood_pt[bjets_idx[1]], event.JetGood_eta[bjets_idx[1]], event.JetGood_phi[bjets_idx[1]])
            mt2Calculator.setMet(event.met_pt_photonCalculated, event.met_phi_photonCalculated)
            event.dl_mt2blbl_photonCalculated = mt2Calculator.mt2blbl()
        else:
            print "~~~> less than 2 jets"

sequence.append( make_newMET )

def make_mass_llg( event, sample ):
    # calculate 3 particle invariant mass m(llgamma)
    p_pt = [event.l1_pt, event.l2_pt, event.photon_pt]
    p_phi = [event.l1_phi, event.l2_phi, event.photon_phi]
    p_eta = [event.l1_eta, event.l2_eta, event.photon_eta]
    mass_llg2 = 0
    for j in range(1,3):
        for i in range(j):
            mass_llg2 += 2*p_pt[i]*p_pt[j]*(cosh(p_eta[i]-p_eta[j]) - cos(p_phi[i]-p_phi[j]))
    event.mass_llg = sqrt(mass_llg2)

    # add offZ cut for mass_llg via weight
    if not args.reweightBosonPt or abs(event.mass_llg-91.1876)>15:
        event.weight_llgOffZ = 1
    else:
        event.weight_llgOffZ = 0

sequence.append( make_mass_llg )

def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu"
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" 


yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}



  if args.reweightBosonPt:
      logger.info( "Now obtaining photon to Z reweighting histograms" )
  
      selectionString = "&&".join([cutInterpreter.cutString(args.selection), getLeptonSelection( mode )])
      ZSelectionString = selectionString + "&&Sum$( (abs(GenPart_pdgId)==12||abs(GenPart_pdgId)==14||abs(GenPart_pdgId)==16)&&GenPart_genPartIdxMother>=0&&GenPart_pdgId[GenPart_genPartIdxMother]==23)>0&&zBoson_genPt>30"
      gSelectionString = selectionString + "&&photon_genPt>30&&photon_genEta<2.5"
 
      for s in mc:
        s.setSelectionString("(1)")
 
      Z_pt_histo = mc[0].get1DHistoFromDraw( "zBoson_genPt", [400/10,0,400], selectionString=ZSelectionString, weightString = "weight*reweightPU*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF")
      g_pt_histo = mc[1].get1DHistoFromDraw( "photon_genPt", [400/10,0,400], selectionString=gSelectionString, weightString = "weight*reweightPU*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF" )
  
      Z_pt_histo.Scale(1./Z_pt_histo.Integral() if Z_pt_histo.Integral() != 0 else 1.)
      g_pt_histo.Scale(1./g_pt_histo.Integral() if g_pt_histo.Integral() != 0 else 1.)
  
      # reweight g to Z boson
      def gToZReweighting( g_pt ):
          i_bin = g_pt_histo.FindBin( g_pt )
          Z_val = Z_pt_histo.GetBinContent( i_bin )
          g_val = g_pt_histo.GetBinContent( i_bin )
          return Z_val/g_val if g_val>0 else 1.



  for sample in mc:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F']
    if "TTG" in sample.name and args.reweightBosonPt:
      sample.weight         = lambda event, sample: event.weight*gToZReweighting(event.photon_genPt)*event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    else:
      sample.weight         = lambda event, sample: event.weight*event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    #sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), leptonSelection, "overlapRemoval==1"])
    sample.setSelectionString("&&".join([cutInterpreter.cutString(args.selection), getLeptonSelection( mode )]))
    sample.style = styles.errorStyle(sample.color)
  
  # TTZ selection
  mc[0].addSelectionString(["Sum$( (abs(GenPart_pdgId)==12||abs(GenPart_pdgId)==14||abs(GenPart_pdgId)==16)&&GenPart_genPartIdxMother>=0&&GenPart_pdgId[GenPart_genPartIdxMother]==23)>0&&zBoson_genPt>30"])
  mc[0].texName = "t#bar{t}Z (Z to #nu#nu)"
  mc[1].addSelectionString(["photon_genPt>30&&photon_genEta<2.5"])
  
  stack = Stack(mc[0], mc[1])
  
  # Use some defaults
  #Plot.setDefaults(stack = stack, selectionString = cutInterpreter.cutString(args.selection), histo_class=ROOT.TH1D)
  Plot.setDefaults(stack = stack, histo_class=ROOT.TH1D)
  
  plots = []
  
  plots.append(Plot(
    name = "boson_genPt",
    texX = 'p_{T}(boson) (GeV)', texY = 'Normalized units',
    attribute = lambda event, sample: event.photon_genPt if "TTG" in sample.name else event.zBoson_genPt,
    binning=[400/10,0,400], addOverFlowBin = None,
  ))
  
  #plots.append(Plot(
  #  name = "boson_pt",
  #  texX = 'p_{T}(boson) (GeV)', texY = 'Normalized units',
  #  attribute = lambda event, sample: event.photon_pt if "TTG" in sample.name else event.Z1_pt,
  #  #attribute = "photon_pt",
  #  binning=[400/10,0,400], addOverFlowBin = None#'upper',
  #  #binning=[800/20,0,800], addOverFlowBin = 'upper',
  #))
  
  plots.append(Plot(
    name = 'met_pt_photonCalculated', texX = 'E_{T}^{miss} (including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
    attribute = lambda event, sample: event.met_pt_photonCalculated,
    binning=[400/20, 0, 400],
  ))
  
  plots.append(Plot(
    texX = 'E_{T}^{miss} (including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
    attribute = TreeVariable.fromString( "met_pt_photonEstimated/F" ),
    binning=[400/20, 0, 400],
  ))
  
  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll_photonEstimated/F" ),
    binning=[300/20,0,300]
  ))
  
  plots.append(Plot(
    name = 'dl_mt2ll_photonCalculated', 
    texX = 'M_{T2}(ll) (E_{T}^{miss} including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
    attribute = lambda event, sample: event.dl_mt2ll_photonCalculated,
    binning=[300/15, 0, 300]
  ))
  
  plots.append(Plot(
    texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2blbl_photonEstimated/F" ),
    binning=[300/20,0,300]
  ))
  
  plots.append(Plot(
    name = 'dl_mt2blbl_photonCalculated', 
    texX = 'M_{T2}(blbl) (E_{T}^{miss} including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
    attribute = lambda event, sample: event.dl_mt2blbl_photonCalculated,
    binning=[300/15, 0, 300]
  ))
  
  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5,
    binning=[3, 0, 3], 
  ))  
  
  plotting.fill(plots, read_variables = read_variables, sequence = sequence)
  
#  yields = {}
#  # Get normalization yields from yield histogram 
#  for plot in plots: 
#    if plot.name == "yield": 
#      for i, l in enumerate(plot.histos): 
#        for j, h in enumerate(l): 
#          yields[plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5)) 
#          h.GetXaxis().SetBinLabel(1, "yield") 
#
  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu")
          h.GetXaxis().SetBinLabel(2, "e#mu")
          h.GetXaxis().SetBinLabel(3, "ee")

  bosonPtScale = yields[mode]["TTG"]/yields[mode]["TTZ"] if yields[mode]["TTZ"] != 0 else float('nan') 

  drawPlots(plots, mode, bosonPtScale)
  allPlots[mode] = plots
#
  



# Add the different channels into SF and all
for mode in ["SF","all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
    except: yields[mode][y] = 0
  bosonPtScale = yields[mode]["TTG"]/yields[mode]["TTZ"] if yields[mode]["TTZ"] != 0 else float('nan') 

  for plot in allPlots['mumu']:
    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
          if i==k:
            j.Add(l)

  drawPlots(allPlots['mumu'], mode, bosonPtScale)




logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

