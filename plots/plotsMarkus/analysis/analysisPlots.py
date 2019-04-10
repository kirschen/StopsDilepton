#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools

from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from Samples.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.plots.pieChart        import makePieChart

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--splitBosons',        action='store_true', default=False)
argParser.add_argument('--splitBosons2',       action='store_true', default=False)
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
argParser.add_argument('--unblinded',          action='store_true', default=False)
argParser.add_argument('--blinded',          action='store_true', default=False)
argParser.add_argument('--reweightPUVUp',      action='store_true', default=False)
argParser.add_argument('--isr',                action='store_true', default=False)
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
if args.noData:                       args.plot_directory += "_noData"
if args.splitBosons:                  args.plot_directory += "_splitMultiBoson"
if args.splitBosons2:                 args.plot_directory += "_splitMultiBoson2"
if args.signal == "DM":               args.plot_directory += "_DM"
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
if args.reweightPUVUp:                args.plot_directory += "_PUVUp"
if args.noBadPFMuonFilter:            args.plot_directory += "_noBadPFMuonFilter"
if args.noBadChargedCandidateFilter:  args.plot_directory += "_noBadChargedCandidateFilter"
if args.preHEM:                       args.plot_directory += "_preHEM"
if args.postHEM:                      args.plot_directory += "_postHEM"
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
    if args.splitBosons:
        mc         = [ Top_pow_16, TTXNoZ_16, TTZ_16, diBoson_16, triBoson_16, DY_LO_16]
    else:
        mc         = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
elif args.year == 2017:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    postProcessing_directory = "stops_2017_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    if args.splitBosons:
        mc         = [ Top_pow_17, TTXNoZ_17, TTZ_17, VVTo2L2Nu_17, WW_17, WZ_17, ZZ_17, triBoson_17, DY_LO_17]
    else:
        mc         = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
elif args.year == 2018:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2018_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    postProcessing_directory = "stops_2018_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    if args.splitBosons:
        mc         = [ Top_pow_18, TTXNoZ_18, TTZ_18, VVTo2L2Nu_18, WZ_18, ZZ_18, triboson_18, DY_LO_18]
    else:
        mc         = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]
    
    nTrueInt36fb_puRWVUp = getReweightingFunction(data="PU_2018_58830_XSecVUp", mc="Autumn18")
    if args.reweightPUVUp: nTrueInt_puRW = nTrueInt36fb_puRWVUp

data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
if args.signal == "T2tt":
    if args.year == 2016:
        postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import *
    else:
        postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import *
    T2tt                    = T2tt_750_0
    T2tt2                   = T2tt_600_300
    T2tt2.style             = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3 )
    signals = [ T2tt, T2tt2]
elif args.signal == "T8bbllnunu":
    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
    T8bbllnunu              = T8bbllnunu_XCha0p5_XSlep0p95_1300_1
    T8bbllnunu2             = T8bbllnunu_XCha0p5_XSlep0p95_1300_300
    T8bbllnunu3             = T8bbllnunu_XCha0p5_XSlep0p95_1300_600
    T8bbllnunu3.style       = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
    T8bbllnunu2.style       = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T8bbllnunu.style        = styles.lineStyle( ROOT.kBlack, width=3 )
    signals = [ T8bbllnunu, T8bbllnunu2, T8bbllnunu3 ]
elif args.signal == "compilation":
    postProcessing_directory = "postProcessed_80X_v30/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
    postProcessing_directory = "postProcessed_80X_v30/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
    T2tt                    = T2tt_800_1
    T8bbllnunu              = T8bbllnunu_XCha0p5_XSlep0p05_800_1
    T8bbllnunu2             = T8bbllnunu_XCha0p5_XSlep0p5_800_1
    T8bbllnunu3             = T8bbllnunu_XCha0p5_XSlep0p95_800_1
    T2tt.style              = styles.lineStyle( ROOT.kGreen-3, width=3 )
    T8bbllnunu.style        = styles.lineStyle( ROOT.kBlack, width=3 )
    T8bbllnunu2.style        = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T8bbllnunu3.style       = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
    signals = [ T2tt, T8bbllnunu, T8bbllnunu2, T8bbllnunu3 ]
    
elif args.signal == "DM":
    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
    #DM                      = TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10_ext1
    DM                      = TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10
    #DM2                     = TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50_ext1
    #DM2_alt                 = TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_50
    DM2                     = TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
    DM.style                = styles.lineStyle( ROOT.kBlack, width=3)
    #DM_alt.style            = styles.lineStyle( ROOT.kBlack, width=3, dotted=True)
    DM2.style               = styles.lineStyle( 28,          width=3)
    #DM2_alt.style           = styles.lineStyle( 28,          width=3, dotted=True)
    signals = [DM, DM2]
else:
    signals = []
#
# Text on the plots
#
def drawObjects( plotData, dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    if "mt2ll100" in args.selection and args.noData: lines += [(0.55, 0.5, 'M_{T2}(ll) > 100 GeV')] # Manually put the mt2ll > 100 GeV label
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', str(args.year), args.plot_directory, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = True,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {},
	    legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88) if not args.noData else (0.50,0.9-0.047*sum(map(len, plot.histos)),0.85,0.9),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
        copyIndexPHP = True,
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

#
#
# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ

##For PU reweighting
#from Analysis.Tools.puReweighting import getReweightingFunction
#nTrueInt27fb_puRW        = getReweightingFunction(data="PU_2016_27000_XSecCentral", mc="Spring16")
#nTrueInt27fb_puRWDown    = getReweightingFunction(data="PU_2016_27000_XSecDown", mc="Spring16")
#nTrueInt27fb_puRWUp      = getReweightingFunction(data="PU_2016_27000_XSecUp", mc="Spring16")
#nTrueInt12fb_puRW        = getReweightingFunction(data="PU_2016_12000_XSecCentral", mc="Spring16")

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  if args.year == 2016:
    data_sample = Run2016
    data_sample.texName = "data (2016)"
  elif args.year == 2017:
    data_sample = Run2017
    data_sample.texName = "data (2017)"
  elif args.year == 2018:
    data_sample = Run2018
    data_sample.texName = "data (2018)"
  

  data_sample.setSelectionString([getFilterCut(isData=True, year=args.year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  if args.preHEM:
    data_sample.addSelectionString("run<319077")
  if args.postHEM:
    data_sample.addSelectionString("run>=319077")
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I","run/I"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  data_sample.scale          = 1.
  lumi_scale                 = data_sample.lumi/1000
  if args.preHEM:   lumi_scale *= 0.37
  if args.postHEM:  lumi_scale *= 0.63

  if args.noData:
    if args.year == 2016: lumi_scale = 35.9
    elif args.year == 2017: lumi_scale = 41.9
    elif args.year == 2018: lumi_scale = 60.0
  weight_ = lambda event, sample: event.weight

  for sample in mc: sample.style = styles.fillStyle(sample.color)

  for sample in mc + signals:
    sample.scale          = lumi_scale
   #sample.read_variables = ['reweightTopPt/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F']
   #sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightLeptonHIPSF*event.reweightDilepTriggerBackup*nTrueInt27fb_puRW(event.nTrueInt)*event.reweightBTag_SF
    sample.read_variables = ['reweightPU36fb/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F']
    #if (('ttjets' in sample.name) or ('ttlep' in sample.name)) and args.isr:
    #    sample.read_variables = ['reweightTopPt/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F', 'reweight_nISR/F']
    #    sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightLeptonTrackingSF*event.reweight_nISR
    #else:
    if args.reweightPUVUp:
        sample.weight         = lambda event, sample: nTrueInt_puRW(event.Pileup_nTrueInt)
    else:
        sample.weight         = lambda event, sample: event.reweightPU36fb*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    sample.setSelectionString([getFilterCut(isData=False, year=args.year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])

  for sample in signals:
      if args.signal == "T2tt" or args.signal == "T8bbllnunu" or args.signal == "compilation":
        sample.scale          = lumi_scale
        sample.read_variables = ['reweightPU36fb/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F']
        sample.weight         = lambda event, sample: event.reweightPU36fb*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
        sample.setSelectionString([getFilterCut(isData=False, year=args.year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
        #sample.read_variables = ['reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightLeptonFastSimSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F']
        #sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightLeptonFastSimSF*event.reweightBTag_SF*event.reweightDilepTriggerBackup*event.reweightLeptonTrackingSF
      elif args.signal == "DM":
        sample.scale          = lumi_scale
        sample.read_variables = ['reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F']
        sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightLeptonTrackingSF
        sample.setSelectionString([getFilterCut(isData=False, year=args.year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
      else:
        raise NotImplementedError

  
  if not args.noData:
    stack = Stack(mc, data_sample)
  else:
    stack = Stack(mc)

  stack.extend( [ [s] for s in signals ] )

  if args.small:
        for sample in stack.samples:
            sample.normalization = 1.
            sample.reduceFiles( factor = 40 )
            sample.scale /= sample.normalization

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

  #plots.append(Plot(
  #  name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
  #  attribute = TreeVariable.fromString( "Pileup_nTrueInt/F" ),
  #  binning=[50,0,50],
  #))
    
  plots.append(Plot(
    name = 'PV_npvsGood', texX = 'N_{PV} (good)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
    binning=[100,0,100],
  ))
    
  plots.append(Plot(
    name = 'PV_npvs', texX = 'N_{PV} (total)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvs/I" ),
    binning=[100,0,100],
  ))

  plots.append(Plot(
      texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "met_pt/F" ),
      binning=[400/20,0,400],
  ))
    
  plots.append(Plot(
      texX = 'E_{T}^{miss} significance', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "MET_significance/F" ),
      binning=[40,0,100],
  ))

  plots.append(Plot(
      texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "met_phi/F" ),
      binning=[10,-pi,pi],
  ))

  #plots.append(Plot(
  #  texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
  #  attribute = TreeVariable.fromString('metSig/F'),
  #  binning= [80,20,100] if args.selection.count('metSig20') else ([25,5,30] if args.selection.count('metSig') else [30,0,30]),
  #))

  if not args.blinded:
    plots.append(Plot(
      texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
      binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
    ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = 'number of medium b-tags (CSVM)', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nBTag/I'),
    binning=[8,0,8],
  ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 25 GeV',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[500/25,0,600],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 4 GeV',
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
  ))

  plots.append(Plot(
    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "dl_pt/F" ),
    binning=[20,0,400],
  ))

  plots.append(Plot(
      texX = '#eta(ll) ', texY = 'Number of Events',
      name = 'dl_eta', attribute = lambda event, sample: abs(event.dl_eta), read_variables = ['dl_eta/F'],
      binning=[10,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(ll)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "dl_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'Cos(#Delta#phi(ll, E_{T}^{miss}))', texY = 'Number of Events',
    name = 'cosZMetphi',
    attribute = lambda event, sample: cos( event.dl_phi - event.met_phi ), 
    read_variables = ["met_phi/F", "dl_phi/F"],
    binning = [10,-1,1],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{1})', texY = 'Number of Events',
    name = 'l1_eta', attribute = lambda event, sample: abs(event.l1_eta), read_variables = ['l1_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{1})', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l1_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{2})', texY = 'Number of Events',
    name = 'l2_eta', attribute = lambda event, sample: abs(event.l2_eta), read_variables = ['l2_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{2})', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l2_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    name = "JZB",
    texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
    attribute = lambda event, sample: sqrt( (event.met_pt*cos(event.met_phi)+event.dl_pt*cos(event.dl_phi))**2 + (event.met_pt*sin(event.met_phi)+event.dl_pt*sin(event.dl_phi))**2) - event.dl_pt, 
  	read_variables = ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"],
    binning=[25,-200,600],
  ))

  # Plots only when at least one jet:
  if args.selection.count('njet2') or args.selection.count('njet1'):
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet0_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet0_eta', attribute = lambda event, sample: abs(event.JetGood_eta[0]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet0_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet0phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosMetJet0phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosMetJet0phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet0phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosMetJet0phi_extraSmallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [50,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet0phi',
      texX = 'Cos(#Delta#phi(Z, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ) ,
      read_variables =  ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

  # Plots only when at least two jets:
  if args.selection.count('njet2'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_eta', attribute = lambda event, sample: abs(event.JetGood_eta[1]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[10,-pi,pi],
    ))

    # 3rd jet plots
    plots.append(Plot(
      texX = 'p_{T}(3rd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[2],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(3rd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_eta', attribute = lambda event, sample: abs(event.JetGood_eta[2]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(3rd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_phi', attribute = lambda event, sample: event.JetGood_phi[2],
      binning=[10,-pi,pi],
    ))
    #

    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet1phi',
      texX = 'Cos(#Delta#phi(Z, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ),
      read_variables = ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet0Jet1phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    if not args.blinded:
        plots.append(Plot(
          texX = 'M_{T2}(bb) (GeV)', texY = 'Number of Events / 30 GeV',
          attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
          binning=[420/30,70,470],
        ))

        plots.append(Plot(
          texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
          attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
          binning=[420/30,0,400],
        ))

        plots.append(Plot( name = "dl_mt2blbl_coarse",       # SR binning of MT2ll
          texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
          attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
          binning=[400/100, 0, 400],
        ))
    
    #plots.append(Plot( name = "MVA_T2tt_default",
    #  texX = 'MVA_{T2tt} (default)', texY = 'Number of Events',
    #  attribute = TreeVariable.fromString( "MVA_T2tt_default/F" ),
    #  binning=[50, 0, 1],
    #))


  plotting.fill(plots, read_variables = read_variables, sequence = [])

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
  #makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart",    yields, mode, mc)
  #makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart_VV", yields, mode, multiBosonList)
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
  #makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart",    yields, mode, mc)
  #makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart_VV", yields, mode, multiBosonList)

# Write to tex file
columns = [i.name for i in mc] + ["MC", "data"] + ([DM.name, DM2.name] if args.signal=="DM" else []) + ([T2tt.name, T2tt2.name] if args.signal=="T2tt" else [])
texdir = "tex"
#if args.powheg: texdir += "_powheg"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["SF","all"]:
    f.write(mode + " & " + " & ".join([ (" %12.0f" if i == "data" else " %12.2f") % yields[mode][i] for i in columns]) + "\\\\ \n")

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

