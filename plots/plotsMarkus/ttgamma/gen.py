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
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='genLevel')
argParser.add_argument('--era',                action='store', type=str,      default="Run2016")
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1')
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
if args.reweightBosonPt:              args.plot_directory += "_photonToZ"
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
    mc             = [ TTZ_16 ]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    mc             = [ TTZ_17 ]
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

def drawPlots(plots, scale):
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.era, args.plot_directory, args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
    
      _drawObjects = []
    
      plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio = {'histos':[(1,0)], 'logY': False, 'style': styles.lineStyle(ROOT.kBlack), 'texY': 't#bar{t}#gamma/t#bar{t}Z', 'yRange': (0.1, 1.9), 'drawObjects':[]},
        logX = False, logY = False, sorting = True, 
        yRange = (0.001, "auto"),
        scaling = {0:1},
        legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
        drawObjects = drawObjects( lumi_scale, scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
read_variables += ["nPhotonGood/I", "overlapRemoval/I", "nGoodMuons/I", "nGoodElectrons/I", "photon_pt/F", "photon_eta/F", "photon_phi/F"]
read_variables += ["dl_mt2ll_photonEstimated/F", "met_pt_photonEstimated/F", "metSig_photonEstimated/F", "dlg_mass/F"]
#read_variables += ["photonJetdR/F", "photonLepdR/F"]
read_variables += [
                VectorTreeVariable.fromString("GenPart[pt/F,pdgId/I,genPartIdxMother/I,status/I,statusFlags/I]", nMax=200), 
                "nGenPart/I", "zBoson_genPt/F", "nGoodLeptons/I"
                ]

sequence = []

def make_newMET( event, sample ):
    if "TTG" in sample.name:
        # add photon to missing energy
        newmet_x = event.met_pt*cos(event.met_phi) + event.photon_pt*cos(event.photon_phi)
        newmet_y = event.met_pt*sin(event.met_phi) + event.photon_pt*sin(event.photon_phi)
        event.met_pt = sqrt(newmet_x**2 + newmet_y**2)
        event.met_phi = atan2(newmet_y, newmet_x)

        # calculate mt2ll
        mt2Calculator.reset()
        mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
        mt2Calculator.setMet(event.met_pt, event.met_phi)
        event.dl_mt2ll = mt2Calculator.mt2ll()

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
    #print event.mass_llg, abs(event.mass_llg-91.1876)>15
    # add offZ cut for mass_llg via weight
    if not args.reweightBosonPt or abs(event.mass_llg-91.1876)>15:
        event.weight_llgOffZ = 1
    else:
        event.weight_llgOffZ = 0

sequence.append( make_mass_llg )

def make_genLevel( event, sample ):
    if "TTZ" in sample.name:
        # get p_T of Z boson 

        #print event.nGenPart
        for i in range(event.nGenPart):
            if event.GenPart_pdgId[i]==23 and event.GenPart_status[i]==62:
                #print "~~", i, event.GenPart_pdgId[i], event.GenPart_pt[i]
                event.Z_pt = event.GenPart_pt[i]
                #event.photon_pt = event.GenPart_pt[i]
        #if not (event.zBoson_genPt-event.Z_pt == 0): print event.zBoson_genPt, event.Z_pt
        # should also work:
        # if event.GenPart_pdgId[2]==23 and event.GenPart_status[2]==22: event.Z_pt = event.GenPart_pt[2] 

#sequence.append( make_genLevel )


leptonSelection = "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)"

if args.reweightBosonPt:
    logger.info( "Now obtaining photon to Z reweighting histograms" )

    # leptonSelection = "nGoodMuons+nGoodElectrons==2&&isOS"
    cutSelection = cutInterpreter.cutString("lepSel-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1")
    selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), leptonSelection, cutSelection])
    # TTZ selection
    ZSelectionString = selectionString #+ "zBoson_genPt>30"#+ "&&Sum$(GenPart_pt>30&&GenPart_pdgId==23&&GenPart_status==22)==1"
    photonSelectionString = selectionString #+ "photon_pt>30"#+ "&&Sum$(GenPart_pt>30&&GenPart_pdgId==23&&GenPart_status==22)==1"

    # photon histogram
    photon_pt_histo = mc[1].get1DHistoFromDraw( "photon_pt", [400/5, 0, 400], selectionString=photonSelectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF" )
    photon_pt_histo.Scale(1./photon_pt_histo.Integral() if photon_pt_histo.Integral() != 0 else 1.)

    # Z boson histogram
    Z_pt_histo = mc[0].get1DHistoFromDraw( "zBoson_genPt", [400/5, 0, 400], selectionString=ZSelectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF")
    Z_pt_histo.Scale(1./Z_pt_histo.Integral() if Z_pt_histo.Integral() != 0 else 1.)

    # reweight photon to Z boson
    def photonToZReweighting( photon_pt ):
        i_bin = photon_pt_histo.FindBin( photon_pt )
        #j_bin = Z_pt_histo.FindBin( photon_pt )
        Z_val = Z_pt_histo.GetBinContent( i_bin )
        photon_val = photon_pt_histo.GetBinContent( i_bin )
        #print "i(bin) %i #Z %f #g %f x %f"%(i_bin, Z_val, photon_val, Z_val/photon_val if photon_val>0 else 1.)
        return Z_val/photon_val if photon_val>0 else 1.


# prepare plots
if args.reweightBosonPt:
  weight_ = lambda event, sample: event.weight*event.weight_llgOffZ
else:
  weight_ = lambda event, sample: event.weight

for sample in mc:
  sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F']
  if "TTG" in sample.name and args.reweightBosonPt:
    sample.weight         = lambda event, sample: photonToZReweighting(event.photon_pt)*event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
  else:
    sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
  sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), leptonSelection, "overlapRemoval==1"])
  sample.style = styles.errorStyle(sample.color)

# TTZ selection
#mc[0].addSelectionString(["Sum$(GenPart_pt>30&&GenPart_pdgId==23&&GenPart_status==22)==1&&zBoson_genPt>20"])
#mc[0].addSelectionString(["zBoson_genPt>30"])
#mc[1].addSelectionString(["photon_pt>30&&photon_eta<2.5"])

stack = Stack(mc[0], mc[1])

# Use some defaults
Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), histo_class=ROOT.TH1D)

plots = []

plots.append(Plot(
  name = "boson_pt",
  texX = 'p_{T}(boson) (GeV)', texY = 'Normalized units',
  attribute = lambda event, sample: event.photon_pt if "TTG" in sample.name else event.zBoson_genPt,
  #attribute = "photon_pt",
  binning=[400/5,0,400], addOverFlowBin = None#'upper',
))

#plots.append(Plot(
#  name = "Z_pt",
#  texX = 'p_{T}(Z boson) (GeV)', texY = 'Normalized units',
#  attribute = lambda event, sample: event.Z_pt if "TTZ" in sample.name else event.photon_pt,
#  binning=[400/5,0,400], addOverFlowBin = None#'upper',
#))
#
#plots.append(Plot(
#  name = "zBoson_genPt",
#  texX = 'p_{T}(Z boson) (GeV)', texY = 'Normalized units',
#  attribute = lambda event, sample: event.zBoson_genPt if "TTZ" in sample.name else event.photon_pt,
#  #attribute = "zBoson_genPt",
#  binning=[400/5,0,400], addOverFlowBin = None#'upper',
#))

plots.append(Plot(
  name = 'met_pt', texX = 'E_{T}^{miss} (including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
  #attribute = lambda event, sample: event.met_pt_photonCalculated if "TTG" in sample.name else event.met_pt,
  attribute = lambda event, sample: event.met_pt,
  binning=[400/20, 0, 400],
))

#plots.append(Plot(
#  texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
#  attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
#  binning=[300/20,0,300]
#))

plots.append(Plot(
  name = 'dl_mt2ll', 
  texX = 'M_{T2}(ll) (MET including #gamma for t#bar{t}#gamma) (GeV)', texY = 'Normalized units',
  #attribute = lambda event, sample: event.dl_mt2llPlusPhoton if "TTG" in sample.name else event.dl_mt2ll,
  attribute = lambda event, sample: event.dl_mt2ll,
  binning=[300/15, 0, 300]
))

plots.append(Plot(
  name = 'yield', texX = 'yield', texY = 'Number of Events',
  attribute = lambda event, sample: 0.5,
  binning=[3, 0, 3], 
))  

plotting.fill(plots, read_variables = read_variables, sequence = sequence)

yields = {}
# Get normalization yields from yield histogram 
for plot in plots: 
  if plot.name == "yield": 
    for i, l in enumerate(plot.histos): 
      for j, h in enumerate(l): 
        yields[plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5)) 
        h.GetXaxis().SetBinLabel(1, "yield") 
bosonPtScale = yields["TTG"]/yields["TTZ"] if yields["TTZ"] != 0 else float('nan') 

drawPlots(plots, bosonPtScale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

