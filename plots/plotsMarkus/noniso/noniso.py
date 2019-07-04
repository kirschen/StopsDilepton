#!/usr/bin/env python
''' analysis script using 1 isolated and one anti-isolated lepton
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

from StopsDilepton.tools.objectSelection import muonSelector, eleSelector, getGoodMuons, getGoodElectrons

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='noniso')
argParser.add_argument('--era',                action='store', type=str,      default="Run2016")
argParser.add_argument('--selection',          action='store',      default='lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1')
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
argParser.add_argument('--dpm',                action='store_true', default=False)
argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp', 'noPUReweighting', 'nvtx'])
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
if args.reweightPU:                   args.plot_directory += "_PU%s"%args.reweightPU

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

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16, WW_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_HT_LO_17, WW_17]
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
#    mc             = [Top_pow_18]
    mc             = [Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18, WW_18] 

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
read_variables += [
            "l1_pdgId/I", "l2_pdgId/I", "nElectron/I", "nMuon/I"]
read_variables += [
            "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]",
            "Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,phi/F,pt/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,pdgId/I,tightCharge/I,lostHits/b,vidNestedWPBitmap/I]"
            ]

sequence = []

ele_selector_iso     = eleSelector(  'tightMiniIso02', year )
mu_selector_iso      = muonSelector( 'tightMiniIso02', year )
ele_selector_noIso   = eleSelector(  'tightNoIso', year )
mu_selector_noIso    = muonSelector( 'tightNoIso', year )

def make_noIso(event, sample):
    event.iso_mt    = float('nan')
    event.noIso_mt = float('nan')

#        print event.nElectron
#        isoLeptons =  getGoodMuons(event, mu_selector = mu_selector_iso) + getGoodElectrons(event, ele_selector = ele_selector_iso)
    noIsoLeptons = getGoodMuons(event, mu_selector = mu_selector_noIso) + getGoodElectrons(event, ele_selector = ele_selector_noIso) 

#        print "sum:", str(event.nMuon+event.nElectron), "#iso: ", len(isoLeptons), "#non-iso", len(nonisoLeptons)
    loose_leptons = []
    for l in noIsoLeptons:#+isoLeptons:
        if l['miniPFRelIso_all'] > 0.2:
            #print "l_pt", l['pt'], "l_pdgId", l['pdgId'], l['miniPFRelIso_all']
            loose_leptons.append(l)
    #print "l1: ", event.l1_pt
    #print "l2: ", event.l2_pt
    if len(loose_leptons)>0:
#            for l in loose_leptons:
#                print l["pt"]
#            print "\n"
        l1 = {"pt": event.l1_pt, "phi": event.l1_phi, "eta": event.l1_eta, "pdgId": event.l1_pdgId}

        l = loose_leptons[0]
        ll = {"pt": l["pt"], "phi": l["phi"], "eta": l["eta"], "pdgId": l["pdgId"], "miniPFRelIso_all": l['miniPFRelIso_all']}

        event.iso_mt = sqrt(2*l1["pt"]*event.met_pt*(1-(cos(l1["phi"]-event.met_phi))))
        event.noIso_mt = sqrt(2*ll["pt"]*event.met_pt*(1-(cos(ll["phi"]-event.met_phi))))
        #print event.iso_mt, event.noIso_mt
        #print l1, "\n", ll

sequence.append( make_noIso )

#
#
# default offZ for SF
def getLeptonSelection( mode ):
  if   mode=="mu": return "nGoodMuons==1"
  elif mode=="e":  return "nGoodElectrons==1"

# Loop over channels

yields     = {}
allPlots   = {}
allModes   = ['mu','e']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  
  data_sample.setSelectionString([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I", "run/I", "reweightHEM/F"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  weight_ = lambda event, sample: event.weight*event.reweightHEM
  
  for sample in mc:
      sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', "l1_muIndex/I", "l2_muIndex/I", "reweightHEM/F"]
      sample.read_variables += ['reweightPU%s/F'%args.reweightPU if args.reweightPU != "Central" else "reweightPU/F"]
      #if args.reweightPU == 'Central':
      #    sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightHEM
      #else:
      sample.weight         = lambda event, sample: getattr(event, "reweightPU"+args.reweightPU if args.reweightPU != "Central" else "reweightPU")*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
      sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
 
  print "\n\n", sample.selectionString, "\n\n" 
  for sample in mc: sample.style = styles.fillStyle(sample.color)
  
  if not args.noData:
      stack = Stack(mc, data_sample)
  else:
      stack = Stack(mc)
  
  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), histo_class=ROOT.TH1D)
  
  plots = []
  
  plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + index,
      binning=[2, 0, 2],
  ))
  
  plots.append(Plot(
      texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
      binning=[300/20, 100,400], 
  ))
  
  plots.append(Plot(
      texX = 'M_T for isolated lepton (GeV)', texY = 'Number of Events / 10 GeV',
      name = "iso_mT", attribute =lambda event, sample: event.iso_mt, 
      binning=[200/10, 0, 200],
  ))
  
  plots.append(Plot(
      texX = 'M_T for non-isolated lepton (GeV)', texY = 'Number of Events / 10 GeV',
      name = "noIso_mT", attribute =lambda event, sample: event.noIso_mt, 
      binning=[200/10, 0, 200],
  ))
  
  plotting.fill(plots, read_variables = read_variables, sequence = sequence)
  
  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5 + index))
          h.GetXaxis().SetBinLabel(1, "#mu")
          h.GetXaxis().SetBinLabel(2, "e")
  if args.noData: yields[mode]["data"] = 0
  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
  
  drawPlots(plots, mode, dataMCScale)
  allPlots[mode] = plots

## Add the different channels into SF and all
#for mode in ["SF","all"]:
#  yields[mode] = {}
#  for y in yields[allModes[0]]:
#    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
#    except: yields[mode][y] = 0
#  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
#
#  for plot in allPlots['mumu']:
#    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
#      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
#	for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
#	  if i==k:
#	    j.Add(l)
#
#  drawPlots(allPlots['mumu'], mode, dataMCScale)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

