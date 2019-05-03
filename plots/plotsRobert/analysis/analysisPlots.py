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
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--dataMCScaling',      action='store_true',     help='Data MC scaling?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--era',                action='store', type=str,      default="2016")
argParser.add_argument('--recoil',             action='store', type=str,      default=None, choices = ["nvtx", "VUp", None])
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--nvtxReweightSelection',          action='store',      default=None)
argParser.add_argument('--splitBosons',        action='store_true', default=False)
argParser.add_argument('--splitBosons2',       action='store_true', default=False)
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
argParser.add_argument('--unblinded',          action='store_true', default=False)
argParser.add_argument('--blinded',            action='store_true', default=False)
argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp', 'noPUReweighting', 'nvtx'])
argParser.add_argument('--isr',                action='store_true', default=False)
argParser.add_argument('--plotUPara',          action='store_true',     help='Plot u_para?', )
argParser.add_argument('--splitMET',           action='store_true',     help='Split in MET bins?' )
argParser.add_argument('--splitMETSig',        action='store_true',     help='Split in METSig bins?' )
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.recoil:                       args.plot_directory += '_recoil_'+args.recoil
if args.small:                        args.plot_directory += "_small"
if args.splitMET:                     args.plot_directory += "_splitMET"
if args.splitMETSig:                  args.plot_directory += "_splitMETSig"
if args.noData:                       args.plot_directory += "_noData"
if args.splitBosons:                  args.plot_directory += "_splitMultiBoson"
if args.splitBosons2:                 args.plot_directory += "_splitMultiBoson2"
if args.signal == "DM":               args.plot_directory += "_DM"
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
if args.noBadPFMuonFilter:            args.plot_directory += "_noBadPFMuonFilter"
if args.noBadChargedCandidateFilter:  args.plot_directory += "_noBadChargedCandidateFilter"
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
    #if args.reweightPU and not args.reweightPU in ["noPUReweighting", "nvtx"]:
    #    nTrueInt_puRW = getReweightingFunction(data="PU_2016_35920_XSec%s"%args.reweightPU, mc="Summer16")
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
    #if args.reweightPU:
    #    # need sample based weights
    #    pass
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18]

    #from StopsDilepton.tools.vetoList import vetoList
    #Run2018D.vetoList = vetoList.fromDirectory('/afs/hephy.at/data/rschoefbeck02/StopsDilepton/splitMuonVeto/')
    #if args.reweightPU and not args.reweightPU in ["noPUReweighting", "nvtx"]:
    #    nTrueInt_puRW = getReweightingFunction(data="PU_2018_58830_XSec%s"%args.reweightPU, mc="Autumn18")

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
        #sample.reduceFiles( factor = 40 )
        sample.reduceFiles( to=1)
        sample.scale /= sample.normalization

if args.recoil:
    from Analysis.Tools.RecoilCorrector import RecoilCorrector
    if args.recoil == "nvtx":
        recoilCorrector = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine_nvtx_loop", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )
    elif args.recoil == "VUp":
        recoilCorrector     = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine_VUp", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )
        recoilCorrector_raw = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v4.3_fine_raw_VUp", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )

def get_quantiles( histo, quantiles = [1-0.9545, 1-0.6826, 0.5, 0.6826, 0.9545]):
    thresholds = array.array('d', [ROOT.Double()] * len(quantiles) )
    histo.GetQuantiles( len(quantiles), thresholds, array.array('d', quantiles) )
    return thresholds 

def splitMetMC(mc):
    dy = mc[-1]
    dy_1 = copy.deepcopy( dy )
    dy_1.name += "_1"
    dy_1.addSelectionString( "met_pt<40" )
    dy_1.texName += " (MET<40)"
    dy_1.color   = ROOT.kGreen + 1 
    dy_2 = copy.deepcopy( dy )
    dy_2.name += "_2"
    dy_2.addSelectionString( "met_pt>40&&met_pt<80" )
    dy_2.texName += " (40<MET<80)"
    dy_2.color   = ROOT.kGreen + 2
    dy_3 = copy.deepcopy( dy )
    dy_3.name += "_3"
    dy_3.addSelectionString( "met_pt>80" )
    dy_3.texName += " (80<MET)"
    dy_3.color   = ROOT.kGreen + 3
    tt = mc[0]
    tt_1 = copy.deepcopy( tt )
    tt_1.name += "_1"
    tt_1.addSelectionString( "met_pt<40" )
    tt_1.texName += " (MET<40)"
    tt_1.color   = ROOT.kAzure + 1 
    tt_2 = copy.deepcopy( tt )
    tt_2.name += "_2"
    tt_2.addSelectionString( "met_pt>40&&met_pt<80" )
    tt_2.texName += " (40<MET<80)"
    tt_2.color   = ROOT.kAzure + 2
    tt_3 = copy.deepcopy( tt )
    tt_3.name += "_3"
    tt_3.addSelectionString( "met_pt>80" )
    tt_3.texName += " (80<MET)"
    tt_3.color   = ROOT.kAzure + 3

    return [ dy_1, dy_2, dy_3, tt_1, tt_2, tt_3] + mc[1:-1]

def splitMetSigMC(mc):
    dy = mc[-1]
    dy_1 = copy.deepcopy( dy )
    dy_1.name += "_1"
    dy_1.addSelectionString( "MET_significance<6" )
    dy_1.texName += " (S<6)"
    dy_1.color   = ROOT.kGreen + 1 
    dy_2 = copy.deepcopy( dy )
    dy_2.name += "_2"
    dy_2.addSelectionString( "MET_significance>6&&MET_significance<12" )
    dy_2.texName += " (6<S<12)"
    dy_2.color   = ROOT.kGreen + 2
    dy_3 = copy.deepcopy( dy )
    dy_3.name += "_3"
    dy_3.addSelectionString( "MET_significance>12" )
    dy_3.texName += " (12<S)"
    dy_3.color   = ROOT.kGreen + 3
    tt = mc[0]
    tt_1 = copy.deepcopy( tt )
    tt_1.name += "_1"
    tt_1.addSelectionString( "MET_significance<6" )
    tt_1.texName += " (S<6)"
    tt_1.color   = ROOT.kAzure + 1 
    tt_2 = copy.deepcopy( tt )
    tt_2.name += "_2"
    tt_2.addSelectionString( "MET_significance>6&&MET_significance<12" )
    tt_2.texName += " (6<S<12)"
    tt_2.color   = ROOT.kAzure + 2
    tt_3 = copy.deepcopy( tt )
    tt_3.name += "_3"
    tt_3.addSelectionString( "MET_significance>12" )
    tt_3.texName += " (12<S)"
    tt_3.color   = ROOT.kAzure + 3

    return [ dy_1, dy_2, dy_3, tt_1, tt_2, tt_3] + mc[1:-1]

data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
if args.signal == "T2tt":
    if year == 2016:
        postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import *
    else:
        postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import *
    T2tt                    = T2tt_650_0
    T2tt2                   = T2tt_500_250
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

      if ("u_para" in plot.name or "u_perp" in plot.name) and not args.noData:
          h_mc   = plot.histos_added[0][0].Clone()
          h_data = plot.histos_added[1][0].Clone()
          if h_mc.Integral()>0:
              h_mc.Scale(h_data.Integral()/h_mc.Integral())
          q_mc   = tuple(get_quantiles( h_mc ))
          q_data = tuple(get_quantiles( h_data ))
          median_shift = q_data[2]-q_mc[2]
          sigma1_ratio = (q_data[3]-q_data[1])/(q_mc[3]-q_mc[1]) if q_mc[3]-q_mc[1]!=0 else 0
          sigma2_ratio = (q_data[4]-q_data[0])/(q_mc[4]-q_mc[0]) if q_mc[4]-q_mc[0]!=0 else 0

          _drawObjects.append( tex.DrawLatex(0.22, 0.62, '#Delta(med): %+3.1f   1#sigma: %4.3f  2#sigma  %4.3f' % ( median_shift, sigma1_ratio, sigma2_ratio) ) )

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = not (args.splitMET or args.splitMETSig),
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {0:1} if args.dataMCScaling else {},
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "RawMET_pt/F", "RawMET_phi/F"]
read_variables += ["event/l", "luminosityBlock/I", "run/I"]

sequence = []

## veto list
#def make_veto( event, sample ):
#    if hasattr( sample, "vetoList" ):
#        event.passes_veto = sample.vetoList.passesVeto( event.run, event.luminosityBlock, event.event )
#        #event.passes_veto = event.event%2==0
#
#sequence.append( make_veto )

# recoil
def recoil_weight( var_bin, qt_bin):
    #if args.recoil == 'v4':
    def _weight_( event, sample):
        return event.weight*(event.dl_phi>var_bin[0])*(event.dl_phi<=var_bin[1])*(event.dl_pt>qt_bin[0])*(event.dl_pt<qt_bin[1]) 
    #elif args.recoil == 'v5':
    #    def _weight_( event, sample):
    #        return event.weight*(event.PV_npvsGood>var_bin[0])*(event.PV_npvsGood<=var_bin[1])*(event.dl_pt>qt_bin[0])*(event.dl_pt<qt_bin[1]) 
    return _weight_

if args.recoil:
    def corr_recoil( event, sample ):
        mt2Calculator.reset()
        if not sample.isData: 
            # Parametrisation vector - # define qt as GenMET + leptons
            qt_px = event.l1_pt*cos(event.l1_phi) + event.l2_pt*cos(event.l2_phi) + event.GenMET_pt*cos(event.GenMET_phi)
            qt_py = event.l1_pt*sin(event.l1_phi) + event.l2_pt*sin(event.l2_phi) + event.GenMET_pt*sin(event.GenMET_phi)

            qt = sqrt( qt_px**2 + qt_py**2 )
            qt_phi = atan2( qt_py, qt_px )

            #ref_phi = qt_phi
            ref_phi = event.dl_phi

            # recoil-correct met_pt, met_phi
            # compute fake MET 
            fakeMET_x = event.met_pt*cos(event.met_phi) - event.GenMET_pt*cos(event.GenMET_phi)
            fakeMET_y = event.met_pt*sin(event.met_phi) - event.GenMET_pt*sin(event.GenMET_phi)
            fakeMET = sqrt( fakeMET_x**2 + fakeMET_y**2 )
            fakeMET_phi = atan2( fakeMET_y, fakeMET_x )
            # project fake MET on qT
            fakeMET_para = fakeMET*cos( fakeMET_phi - ref_phi ) 
            fakeMET_perp = fakeMET*cos( fakeMET_phi - ( ref_phi - pi/2) ) 
            fakeMET_para_corr = - recoilCorrector.predict_para( ref_phi, qt, -fakeMET_para ) 
            fakeMET_perp_corr = - recoilCorrector.predict_perp( ref_phi, qt, -fakeMET_perp )
            # rebuild fake MET vector
            fakeMET_px_corr = fakeMET_para_corr*cos(ref_phi) + fakeMET_perp_corr*cos(ref_phi - pi/2) 
            fakeMET_py_corr = fakeMET_para_corr*sin(ref_phi) + fakeMET_perp_corr*sin(ref_phi - pi/2) 
            #print "%s qt: %3.2f para %3.2f->%3.2f perp %3.2f->%3.2f fakeMET(%3.2f,%3.2f) -> (%3.2f,%3.2f)" % ( sample.name, qt, fakeMET_para, fakeMET_para_corr, fakeMET_perp, fakeMET_perp_corr, fakeMET, fakeMET_phi, sqrt( fakeMET_px_corr**2+fakeMET_py_corr**2), atan2( fakeMET_py_corr, fakeMET_px_corr) )
            met_px_corr = event.met_pt*cos(event.met_phi) - fakeMET_x + fakeMET_px_corr 
            met_py_corr = event.met_pt*sin(event.met_phi) - fakeMET_y + fakeMET_py_corr
            event.met_pt_corr  = sqrt( met_px_corr**2 + met_py_corr**2 ) 
            event.met_phi_corr = atan2( met_py_corr, met_px_corr ) 

            # recoil-correct RawMET_pt, RawMET_phi
            # compute fake MET 
            rawFakeMET_x = event.RawMET_pt*cos(event.RawMET_phi) - event.GenMET_pt*cos(event.GenMET_phi)
            rawFakeMET_y = event.RawMET_pt*sin(event.RawMET_phi) - event.GenMET_pt*sin(event.GenMET_phi)
            rawFakeMET = sqrt( rawFakeMET_x**2 + rawFakeMET_y**2 )
            rawFakeMET_phi = atan2( rawFakeMET_y, rawFakeMET_x )
            # project fake MET on qT
            rawFakeMET_para = rawFakeMET*cos( rawFakeMET_phi - ref_phi ) 
            rawFakeMET_perp = rawFakeMET*cos( rawFakeMET_phi - ( ref_phi - pi/2) ) 
            rawFakeMET_para_corr = - recoilCorrector_raw.predict_para( ref_phi, qt, -rawFakeMET_para ) 
            rawFakeMET_perp_corr = - recoilCorrector_raw.predict_perp( ref_phi, qt, -rawFakeMET_perp )
            # rebuild fake MET vector
            rawFakeMET_px_corr = rawFakeMET_para_corr*cos(ref_phi) + rawFakeMET_perp_corr*cos(ref_phi - pi/2) 
            rawFakeMET_py_corr = rawFakeMET_para_corr*sin(ref_phi) + rawFakeMET_perp_corr*sin(ref_phi - pi/2) 
            RawMET_px_corr = event.RawMET_pt*cos(event.RawMET_phi) - rawFakeMET_x + rawFakeMET_px_corr 
            RawMET_py_corr = event.RawMET_pt*sin(event.RawMET_phi) - rawFakeMET_y + rawFakeMET_py_corr
            event.RawMET_pt_corr  = sqrt( RawMET_px_corr**2 + RawMET_py_corr**2 ) 
            event.RawMET_phi_corr = atan2( RawMET_py_corr, RawMET_px_corr ) 

        else:
            event.met_pt_corr     = event.met_pt 
            event.met_phi_corr    = event.met_phi
            event.RawMET_pt_corr  = event.RawMET_pt 
            event.RawMET_phi_corr = event.RawMET_phi

        mt2Calculator.setLeptons(event.l1_pt, event.l1_eta, event.l1_phi, event.l2_pt, event.l2_eta, event.l2_phi)
        mt2Calculator.setMet(event.met_pt_corr, event.met_phi_corr)
        event.dl_mt2ll_corr     = mt2Calculator.mt2ll()

        mt2Calculator.setMet(event.RawMET_pt, event.RawMET_phi)
        event.dl_mt2ll_raw      =  mt2Calculator.mt2ll()

        mt2Calculator.setMet(event.RawMET_pt_corr, event.RawMET_phi_corr)
        event.dl_mt2ll_raw_corr =  mt2Calculator.mt2ll()

        #print event.dl_mt2ll, event.dl_mt2ll_corr

    sequence.append( corr_recoil )
  
#
#
# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

# get nvtx reweighting histo
if args.reweightPU =='nvtx':
    logger.info( "Now obtain nvtx reweighting histo" )
    data_selectionString = "&&".join([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
    data_nvtx_histo = data_sample.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=data_selectionString, weightString = "weight" )
    data_nvtx_histo.Scale(1./data_nvtx_histo.Integral())

    mc_selectionString = "&&".join([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("SF"), cutInterpreter.cutString(args.nvtxReweightSelection)])
    mc_histos  = [ s.get1DHistoFromDraw( "PV_npvsGood", [100/5, 0, 100], selectionString=mc_selectionString, weightString = "weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF") for s in mc]
    mc_nvtx_histo     = mc_histos[0]
    for h in mc_histos[1:]:
        mc_nvtx_histo.Add( h )
    mc_nvtx_histo.Scale(1./mc_nvtx_histo.Integral())
    def nvtx_puRW( nvtx ):
        i_bin = mc_nvtx_histo.FindBin( nvtx )
        mc_val = mc_nvtx_histo.GetBinContent( i_bin)
        return data_nvtx_histo.GetBinContent( i_bin )/mc_val if mc_val>0 else 1

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
  weight_ = lambda event, sample: event.weight

  #data_sample_filtered = copy.deepcopy( data_sample )
  #data_sample_filtered.style = styles.errorStyle(ROOT.kRed)
  #data_sample_filtered.weight = lambda event, sample: event.weight*event.passes_veto
  #data_sample_filtered.name   += "_filtered"
  #data_sample_filtered.texName+= " (filtered)"

  for sample in mc + signals:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F']
    # Need individual pu reweighting functions for each sample in 2017, so nTrueInt_puRW is only defined here
    if args.reweightPU and args.reweightPU not in ["noPUReweighting", "nvtx"]:
        sample.read_variables.append( 'reweightPU%s/F'%args.reweightPU )
    #    if year == 2017:
    #        logger.info("Getting PU profile and weight for sample %s", sample.name)
    #        puProfiles = puProfile( source_sample = sample )
    #        mcHist = puProfiles.cachedTemplate( selection="( 1 )", weight='genWeight', overwrite=False ) # use genWeight for amc@NLO samples. No problems encountered so far
    #        nTrueInt_puRW = getReweightingFunction(data="PU_2017_41860_XSec%s"%args.reweightPU, mc=mcHist)

    if args.reweightPU == "noPUReweighting":
        sample.weight         = lambda event, sample: event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    elif args.reweightPU == "nvtx":
        sample.weight         = lambda event, sample: nvtx_puRW(event.PV_npvsGood) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    elif args.reweightPU:
        pu_getter = operator.attrgetter("reweightPU%s"%args.reweightPU)
        sample.weight         = lambda event, sample: pu_getter(event) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    else: #default
        sample.weight         = lambda event, sample: event.reweightPUCentral*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF

    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])

  for sample in signals:
      if args.signal == "T2tt" or args.signal == "T8bbllnunu" or args.signal == "compilation":
        sample.scale          = lumi_scale
        sample.read_variables = ['reweightPU36fb/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F']
        sample.weight         = lambda event, sample: event.reweightPU36fb*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
        sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
        #sample.read_variables = ['reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightLeptonFastSimSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F']
        #sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightLeptonFastSimSF*event.reweightBTag_SF*event.reweightDilepTriggerBackup*event.reweightLeptonTrackingSF
      elif args.signal == "DM":
        sample.scale          = lumi_scale
        sample.read_variables = ['reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F', 'reweightLeptonTrackingSF/F']
        sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightLeptonTrackingSF
        sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
      else:
        raise NotImplementedError
 
  if args.splitMET:
    mc_ = splitMetMC(mc)
  elif args.splitMETSig:
    mc_ = splitMetSigMC(mc)
  else:
    mc_ = mc 

  for sample in mc_: sample.style = styles.fillStyle(sample.color)

  if not args.noData:
    stack = Stack(mc_, data_sample)#, data_sample_filtered)
  else:
    stack = Stack(mc_)

  stack.extend( [ [s] for s in signals ] )

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

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

  plots.append(Plot( name = "met_pt_raw",
      texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "RawMET_pt/F" ),
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

  plots.append(Plot( name = "met_phi_corr",
      texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.met_phi_corr,
      binning=[10,-pi,pi],
  ))

  plots.append(Plot( name = "met_phi_raw",
      texX = 'raw #phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "RawMET_phi/F" ),
      binning=[10,-pi,pi],
  ))

  plots.append(Plot( name = "met_phi_raw_corr",
      texX = 'raw #phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.RawMET_phi_corr,
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
      binning=[300/20,0,300],
    ))
    plots.append(Plot( name = "dl_mt2ll_raw",
      texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = lambda event, sample: event.dl_mt2ll_raw,
      binning=[300/20,0,300],
    ))

  if args.recoil:
      plots.append(Plot( name = "met_pt_corr",
          texX = 'corr E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample: event.met_pt_corr,
          binning=[400/20,0,400],
      ))

      plots.append(Plot( name = "met_pt_raw_corr",
          texX = 'corr E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample: event.RawMET_pt_corr,
          binning=[400/20,0,400],
      ))
        
      plots.append(Plot( name = "dl_mt2ll_corr",
          texX = 'corr M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample: event.dl_mt2ll_corr,
          binning=[400/20,0,400],
      ))

      plots.append(Plot( name = "dl_mt2ll_raw_corr",
          texX = 'raw corr M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
          attribute = lambda event, sample: event.dl_mt2ll_raw_corr,
          binning=[400/20,0,400],
      ))

  plots.append(Plot( name = "qT",
    texX = 'q_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    attribute = lambda event, sample: sqrt((event.l1_pt*cos(event.l1_phi) + event.l2_pt*cos(event.l2_phi) + event.met_pt*cos(event.met_phi))**2 + (event.l1_pt*sin(event.l1_phi) + event.l2_pt*sin(event.l2_phi) + event.met_pt*sin(event.met_phi))**2),
    binning= [1000/50,0,1000]),
  )

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

  # Plots only when at least one jet:
  if args.selection.count('njet2') or args.selection.count('njet1') or args.selection.count('njet01'):
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_eta', attribute = lambda event, sample: abs(event.JetGood_eta[0]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet1phi',
      texX = 'Cos(#Delta#phi(Z, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ),
      read_variables =  ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    plots.append(Plot( name = "u_para", 
      texX = "u_{#parallel} (GeV)", texY = 'Number of Events / 30 GeV',
      attribute = lambda event, sample: - event.met_pt*cos(event.met_phi-event.dl_phi),
      binning=[80, -200,200],
    ))
    plots.append(Plot( name = "u_perp", 
      texX = "u_{#perp} (GeV)", texY = 'Number of Events / 30 GeV',
      attribute = lambda event, sample: - event.met_pt*cos(event.met_phi-(event.dl_phi-pi/2)),
      binning=[80, -200,200],
    ))
    plots.append(Plot( name = "u_para_raw", 
      texX = "u_{#parallel} (GeV)", texY = 'Number of Events / 30 GeV',
      attribute = lambda event, sample: - event.RawMET_pt*cos(event.RawMET_phi-event.dl_phi),
      binning=[80, -200,200],
    ))
    plots.append(Plot( name = "u_perp_raw", 
      texX = "u_{#perp} (GeV)", texY = 'Number of Events / 30 GeV',
      attribute = lambda event, sample: - event.RawMET_pt*cos(event.RawMET_phi-(event.dl_phi-pi/2)),
      binning=[80, -200,200],
    ))
    if args.recoil:
        plots.append(Plot( name = "u_para_corr", 
          texX = "u_{#parallel} corr. (GeV)", texY = 'Number of Events / 30 GeV',
          attribute = lambda event, sample: - event.met_pt_corr*cos(event.met_phi_corr-event.dl_phi),
          binning=[80, -200,200],
        ))
        plots.append(Plot( name = "u_perp_corr", 
          texX = "u_{#perp} corr. (GeV)", texY = 'Number of Events / 30 GeV',
          attribute = lambda event, sample: - event.met_pt_corr*cos(event.met_phi_corr-(event.dl_phi-pi/2)),
          binning=[80, -200,200],
        ))
        plots.append(Plot( name = "u_para_raw_corr", 
          texX = "u_{#parallel} corr. (GeV)", texY = 'Number of Events / 30 GeV',
          attribute = lambda event, sample: - event.RawMET_pt_corr*cos(event.RawMET_phi_corr-event.dl_phi),
          binning=[80, -200,200],
        ))
        plots.append(Plot( name = "u_perp_raw_corr", 
          texX = "u_{#perp} corr. (GeV)", texY = 'Number of Events / 30 GeV',
          attribute = lambda event, sample: - event.RawMET_pt_corr*cos(event.RawMET_phi_corr-(event.dl_phi-pi/2)),
          binning=[80, -200,200],
        ))

    if args.plotUPara:
        # u_para u_perp closure plots
        u_para_binning   =  [ i*20 for i in range(-10, 11) ]
        qt_binning    = [0, 50, 100, 150, 200, 300 ]
        qt_bins = [ (qt_binning[i],qt_binning[i+1]) for i in range(len(qt_binning)-1) ]
        #if args.recoil == 'v4':
        var_binning   = [ pi*(i-5)/5. for i in range(0,11) ]
        var_bins      = [ (var_binning[i],var_binning[i+1]) for i in range(len(var_binning)-1) ]
        #elif args.recoil == 'v5':
        #    var_binning   = [ 0, 20, 30, 40, 50, 100 ]
        #    var_bins      = [ (var_binning[i],var_binning[i+1]) for i in range(len(var_binning)-1) ]

        for var_bin in var_bins:
            for qt_bin in qt_bins:
                #if args.recoil=='v4':
                postfix = "phill_%3.2f_%3.2f_qt_%i_%i"%( var_bin[0], var_bin[1], qt_bin[0], qt_bin[1] )
                #elif args.recoil=='v5':
                #    postfix = "nvtx_%i_%i_qt_%i_%i"%( var_bin[0], var_bin[1], qt_bin[0], qt_bin[1] )
                plots.append(Plot( name = "u_para_" + postfix, 
                  texX = "u_{#parallel} (GeV)", texY = 'Number of Events / 30 GeV',
                  attribute = lambda event, sample: - event.met_pt*cos(event.met_phi-event.dl_phi),
                  weight = recoil_weight(var_bin, qt_bin),
                  binning=[80, -200,200],
                ))
                plots.append(Plot( name = "u_perp_" + postfix, 
                  texX = "u_{#perp} (GeV)", texY = 'Number of Events / 30 GeV',
                  attribute = lambda event, sample: - event.met_pt*cos(event.met_phi-(event.dl_phi-pi/2)),
                  weight = recoil_weight(var_bin, qt_bin),
                  binning=[80, -200,200],
                ))
                if args.recoil:
                    plots.append(Plot( name = "u_para_corr_" + postfix, 
                      texX = "u_{#parallel} corr. (GeV)", texY = 'Number of Events / 30 GeV',
                      attribute = lambda event, sample: - event.met_pt_corr*cos(event.met_phi_corr-event.dl_phi),
                      weight = recoil_weight(var_bin, qt_bin),
                      binning=[80, -200,200],
                    ))
                    plots.append(Plot( name = "u_perp_corr_" + postfix, 
                      texX = "u_{#perp} corr. (GeV)", texY = 'Number of Events / 30 GeV',
                      attribute = lambda event, sample: - event.met_pt_corr*cos(event.met_phi_corr-(event.dl_phi-pi/2)),
                      weight = recoil_weight(var_bin, qt_bin),
                      binning=[80, -200,200],
                    ))

#  # Plots only when at least two jets:
  if args.selection.count('njet2'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_eta', attribute = lambda event, sample: abs(event.JetGood_eta[1]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet2phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet2phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet2phi',
      texX = 'Cos(#Delta#phi(Z, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ),
      read_variables = ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

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

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc_)
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

