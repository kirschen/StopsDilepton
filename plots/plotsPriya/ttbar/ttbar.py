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
from Samples.Tools.metFilters            import getFilterCut
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
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
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
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
if args.noBadPFMuonFilter:            args.plot_directory += "_noBadPFMuonFilter"
if args.noBadChargedCandidateFilter:  args.plot_directory += "_noBadChargedCandidateFilter"

# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

logger.info( "Working in year %i", year )

from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
#mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
#mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
#mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18]

stack = Stack( [Top_pow_16], [Top_pow_17], [Top_pow_18] )

#if args.small:
#    for sample in samples:
#        sample.reduceFiles( to = 1 )
#
## Text on the plots
##
#tex = ROOT.TLatex()
#tex.SetNDC()
#tex.SetTextSize(0.04)
#tex.SetTextAlign(11) # align right
#
#def drawObjects( plotData, dataMCScale, lumi_scale ):
#    lines = [
#      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
#      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
#    ]
#    return [tex.DrawLatex(*l) for l in lines] 
#
#def drawPlots(plots, mode, dataMCScale):
#  for log in [False, True]:
#    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, mode + ("_log" if log else ""), args.selection)
#    for plot in plots:
#      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
#      if mode == "all": plot.histos[1][0].legendText = "Data"
#      if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"
#
#      _drawObjects = []
#
#      plotting.draw(plot,
#	    plot_directory = plot_directory_,
#	    ratio = None,
#	    logX = False, logY = log, sorting = not (args.splitMET or args.splitMETSig),
#	    yRange = (0.03, "auto") if log else (0.001, "auto"),
#	    #scaling = {0:1},
#	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
#	    drawObjects = drawObjects( False, dataMCScale , lumi_scale ) + _drawObjects,
#        copyIndexPHP = True, extensions = ["png"],
#      )
#
##
## Read variables and sequences
##
#read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
#
#sequence = []
#
#def recoil_weight( var_bin, qt_bin):
#    #if args.recoil == 'v4':
#    def _weight_( event, sample):
#        return event.weight*(event.dl_phi>var_bin[0])*(event.dl_phi<=var_bin[1])*(event.dl_pt>qt_bin[0])*(event.dl_pt<qt_bin[1]) 
#    #elif args.recoil == 'v5':
#    #    def _weight_( event, sample):
#    #        return event.weight*(event.PV_npvsGood>var_bin[0])*(event.PV_npvsGood<=var_bin[1])*(event.dl_pt>qt_bin[0])*(event.dl_pt<qt_bin[1]) 
#    return _weight_
#
#if args.recoil:
#    def corr_recoil( event, sample ):
#        mt2Calculator.reset()
#        if not sample.isData: 
#            # Parametrisation vector - # define qt as GenMET + leptons
#            qt_px = event.l1_pt*cos(event.l1_phi) + event.l2_pt*cos(event.l2_phi) + event.GenMET_pt*cos(event.GenMET_phi)
#            qt_py = event.l1_pt*sin(event.l1_phi) + event.l2_pt*sin(event.l2_phi) + event.GenMET_pt*sin(event.GenMET_phi)
#
#            qt = sqrt( qt_px**2 + qt_py**2 )
#            qt_phi = atan2( qt_py, qt_px )
#
#            #ref_phi = qt_phi
#            ref_phi = event.dl_phi
#
#            # compute fake MET 
#            fakeMET_x = event.met_pt*cos(event.met_phi) - event.GenMET_pt*cos(event.GenMET_phi)
#            fakeMET_y = event.met_pt*sin(event.met_phi) - event.GenMET_pt*sin(event.GenMET_phi)
#
#            fakeMET = sqrt( fakeMET_x**2 + fakeMET_y**2 )
#            fakeMET_phi = atan2( fakeMET_y, fakeMET_x )
#
#            # project fake MET on qT
#            fakeMET_para = fakeMET*cos( fakeMET_phi - ref_phi ) 
#            fakeMET_perp = fakeMET*cos( fakeMET_phi - ( ref_phi - pi/2) ) 
#            
#            # FIXME: signs should be negative for v3 and positive for v2 
#            #if args.recoil == "v4":
#            fakeMET_para_corr = - recoilCorrector.predict_para( ref_phi, qt, -fakeMET_para ) 
#            fakeMET_perp_corr = - recoilCorrector.predict_perp( ref_phi, qt, -fakeMET_perp )
#            #elif args.recoil == "v5":
#            #    fakeMET_para_corr = - recoilCorrector.predict_para( event.PV_npvsGood, qt, -fakeMET_para ) 
#            #    fakeMET_perp_corr = - recoilCorrector.predict_perp( event.PV_npvsGood, qt, -fakeMET_perp )
#
#            # rebuild fake MET vector
#            fakeMET_px_corr = fakeMET_para_corr*cos(ref_phi) + fakeMET_perp_corr*cos(ref_phi - pi/2) 
#            fakeMET_py_corr = fakeMET_para_corr*sin(ref_phi) + fakeMET_perp_corr*sin(ref_phi - pi/2) 
#
#            #print "%s qt: %3.2f para %3.2f->%3.2f perp %3.2f->%3.2f fakeMET(%3.2f,%3.2f) -> (%3.2f,%3.2f)" % ( sample.name, qt, fakeMET_para, fakeMET_para_corr, fakeMET_perp, fakeMET_perp_corr, fakeMET, fakeMET_phi, sqrt( fakeMET_px_corr**2+fakeMET_py_corr**2), atan2( fakeMET_py_corr, fakeMET_px_corr) )
#       
#            met_px_corr = event.met_pt*cos(event.met_phi) - fakeMET_x + fakeMET_px_corr 
#            met_py_corr = event.met_pt*sin(event.met_phi) - fakeMET_y + fakeMET_py_corr
#        
#            event.met_pt_corr  = sqrt( met_px_corr**2 + met_py_corr**2 ) 
#            event.met_phi_corr = atan2( met_py_corr, met_px_corr ) 
#
#        else:
#            event.met_pt_corr  = event.met_pt 
#            event.met_phi_corr = event.met_phi
#
#        mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
#        mt2Calculator.setMet(event.met_pt_corr, event.met_phi_corr)
#        event.dl_mt2ll_corr =  mt2Calculator.mt2ll()
#
#        #print event.dl_mt2ll, event.dl_mt2ll_corr
#
#    sequence.append( corr_recoil )
#  
##
##
## default offZ for SF
#offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
#def getLeptonSelection( mode ):
#  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
#  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
#  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
#  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
#  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)&&" + offZ+")||isEMu)"
#
### get nvtx reweighting histo
##if args.reweightPU =='nvtx':
##    logger.info( "Now obtain nvtx reweighting histo" )
##    data_selectionString = "&&".join([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
##    data_nvtx_histo = data_sample.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=data_selectionString, weightString = "weight" )
##    data_nvtx_histo.Scale(1./data_nvtx_histo.Integral())
##
##    mc_selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
##    mc_histos  = [ s.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=mc_selectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF") for s in mc]
##    mc_nvtx_histo     = mc_histos[0]
##    for h in mc_histos[1:]:
##        mc_nvtx_histo.Add( h )
##    mc_nvtx_histo.Scale(1./mc_nvtx_histo.Integral())
##    def nvtx_puRW( nvtx ):
##        i_bin = mc_nvtx_histo.FindBin( nvtx )
##        mc_val = mc_nvtx_histo.GetBinContent( i_bin)
##        return data_nvtx_histo.GetBinContent( i_bin )/mc_val if mc_val>0 else 1
#
##
## Loop over channels
##
#yields     = {}
#allPlots   = {}
#allModes   = ['mumu','mue','ee']
#for index, mode in enumerate(allModes):
#  yields[mode] = {}
#
#  data_sample.setSelectionString([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
#  data_sample.name           = "data"
#  data_sample.read_variables = ["event/I","run/I"]
#  data_sample.style          = styles.errorStyle(ROOT.kBlack)
#  weight_ = lambda event, sample: event.weight
#
#  for sample in mc:
#    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F']
#    # Need individual pu reweighting functions for each sample in 2017, so nTrueInt_puRW is only defined here
#    if args.reweightPU and args.reweightPU not in ["noPUReweighting", "nvtx"]:
#        sample.read_variables.append( 'reweightPU%s/F'%args.reweightPU )
#    #    if year == 2017:
#    #        logger.info("Getting PU profile and weight for sample %s", sample.name)
#    #        puProfiles = puProfile( source_sample = sample )
#    #        mcHist = puProfiles.cachedTemplate( selection="( 1 )", weight='genWeight', overwrite=False ) # use genWeight for amc@NLO samples. No problems encountered so far
#    #        nTrueInt_puRW = getReweightingFunction(data="PU_2017_41860_XSec%s"%args.reweightPU, mc=mcHist)
#
#    if args.reweightPU == "noPUReweighting":
#        sample.weight         = lambda event, sample: event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
#    elif args.reweightPU == "nvtx":
#        sample.weight         = lambda event, sample: nvtx_puRW(event.PV_npvsGood) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
#    elif args.reweightPU:
#        pu_getter = operator.attrgetter("reweightPU%s"%args.reweightPU)
#        sample.weight         = lambda event, sample: pu_getter(event) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
#    else: #default
#        sample.weight         = lambda event, sample: event.reweightPUCentral*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
#
#    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
#
#  if args.splitMET:
#    mc_ = splitMetMC(mc)
#  elif args.splitMETSig:
#    mc_ = splitMetSigMC(mc)
#  else:
#    mc_ = mc 
#
#  for sample in mc_: sample.style = styles.fillStyle(sample.color)
#
#  stack = Stack(mc_)
#
#  # Use some defaults
#  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
#  
#  plots = []
#
#  plots.append(Plot(
#    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
#    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
#    binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
#  ))
#
#  plotting.fill(plots, read_variables = read_variables, sequence = sequence)
#
#  drawPlots(plots, mode, dataMCScale)
#  allPlots[mode] = plots
#
#logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )
#
