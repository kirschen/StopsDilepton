#!/usr/bin/env python
''' analysis script for standard plots with systematic errors
'''

# quick marks
#NN     implementation of input uncertainties
#

# Standard imports and batch mode
import ROOT
ROOT.gROOT.SetBatch(True)
import operator
import pickle
import os, time, sys, copy
from math                                import sqrt, cos, sin, pi, atan2

# RootTools
from RootTools.core.standard             import *

#Analysis / StopsDilepton / Samples
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, add_histos
from Analysis.Tools.metFilters           import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.RecoilCorrector import RecoilCorrector
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puReweighting        import getReweightingFunction
from Analysis.Tools.DirDB                import DirDB

# JEC corrector
from JetMET.JetCorrector.JetCorrector    import JetCorrector, correction_levels_data, correction_levels_mc
corrector_data     = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_data )
corrector_mc       = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_mc )


# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',          action='store',      default='INFO',     nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',            action='store',      default=None,        nargs='?', choices=['None', "T2tt",'DM'], help="Add signal to plot")
argParser.add_argument('--plot_directory',    action='store',      default='v1')
argParser.add_argument('--selection',         action='store',      default='lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1')
# Scalings
argParser.add_argument('--scaling',           action='store',      default=None, choices = [None, 'mc', 'top'],     help='Scale top to data in mt2ll<100?')
argParser.add_argument('--variation_scaling', action='store_true', help='Scale the variations individually to mimick bkg estimation?')
argParser.add_argument('--normalize',         action='store_true', help='Perform area normalization mc to data?')
argParser.add_argument('--beta',              action='store',      default=None, help="Add an additional directory label for minor changes to the plots")
argParser.add_argument('--small',             action='store_true',     help='Run only on a small subset of the data?')
argParser.add_argument('--directories',       action='store',         nargs='*',  type=str, default=[],                  help="Input" )


args = argParser.parse_args()

# Logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
import Analysis.Tools.logger as logger_an
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)
logger_an = logger_an.get_logger(args.logLevel, logFile = None)


# Define all systematic variations
variations = {
    'central'           : {},
    'jesTotalUp'        : {}, 
    'jesTotalDown'      : {}, 
    'jerUp'             : {}, 
    'jerDown'           : {}, 
    'unclustEnUp'       : {}, 
    'unclustEnDown'     : {}, 
    'PUUp'              : {}, 
    'PUDown'            : {}, 
    'BTag_SF_b_Down'    : {}, 
    'BTag_SF_b_Up'      : {}, 
    'BTag_SF_l_Down'    : {}, 
    'BTag_SF_l_Up'      : {}, 
    'DilepTriggerDown'  : {}, 
    'DilepTriggerUp'    : {}, 
    'LeptonSFDown'      : {}, 
    'LeptonSFUp'        : {}, 
    'LeptonHit0SFDown'  : {}, 
    'LeptonHit0SFUp'    : {}, 
    'LeptonSip3dSFDown' : {},
    'LeptonSip3dSFUp'   : {}, 
    'L1PrefireDown'     : {}, 
    'L1PrefireUp'       : {}, 
#NN
#    'DYInputUp'             : {'addSampleWeight':(DY_HT_LO, '1.25', '(1)'),                                               'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'DYInputDown'           : {'addSampleWeight':(DY_HT_LO, '0.75', '(1)'),                                               'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTInputUp'             : {'addSampleWeight':(Top_pow, '1.25', '(1)'),                                                'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTInputDown'           : {'addSampleWeight':(Top_pow, '0.75', '(1)'),                                                'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'MBInputUp'             : {'addSampleWeight':(multiBoson, '1.25', '(1)'),                                             'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'MBInputDown'           : {'addSampleWeight':(multiBoson, '0.75', '(1)'),                                             'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTZInputUp'            : {'addSampleWeight':(TTZ_LO, '1.2', '(1)'),                                                 'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTZInputDown'          : {'addSampleWeight':(TTZ_LO, '0.8', '(1)'),                                                 'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'OtherInputUp'          : {'addSampleWeight':(TTXNoZ, '1.25', '(1)'),                                                'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'OtherInputDown'        : {'addSampleWeight':(TTXNoZ, '0.75', '(1)'),                                                'read_variables' : ['%s/F'%v for v in nominalMCWeights] },

#
#    'TT1JetMismInputUp'     : {'addSampleWeight':(Top_pow, '1.3', '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) >=1)'), 'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TT1JetMismInputDown'   : {'addSampleWeight':(Top_pow, '0.7', '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) >=1)'), 'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTTotJetMismInputUp'   : {'addSampleWeight':(Top_pow, '1.15', 
#                              '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) >= 40)'), 
#                                                                                                                         'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTTotJetMismInputDown' : {'addSampleWeight':(Top_pow, '0.85',
#                              '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) >= 40)'), 
#                                                                                                                         'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTNonPromptInputUp'    : {'addSampleWeight':(Top_pow, '1.5',
#                              '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && ((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1)))'), 
#                                                                                                                         'read_variables' : ['%s/F'%v for v in nominalMCWeights] },
#    'TTNonPromptInputDown'  : {'addSampleWeight':(Top_pow, '0.5',
#                              '(Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && ((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1)))'),
#
#    'TopPt':{},
}

# Systematic pairs:( 'name', 'up', 'down' )
systematics = [\
    {'name':'JEC',          'correlated':True, 'pair':('jesTotalUp', 'jesTotalDown')},
    {'name':'Unclustered',  'correlated':True, 'pair':('unclustEnUp', 'unclustEnDown')},
    {'name':'PU',           'correlated':True, 'pair':('PUUp', 'PUDown')},
    {'name':'BTag_b',       'correlated':True, 'pair':('BTag_SF_b_Down', 'BTag_SF_b_Up' )},
    {'name':'BTag_l',       'correlated':True, 'pair':('BTag_SF_l_Down', 'BTag_SF_l_Up')},
    {'name':'trigger',      'correlated':True, 'pair':('DilepTriggerDown', 'DilepTriggerUp')},
    {'name':'leptonSF',     'correlated':True, 'pair':('LeptonSFDown', 'LeptonSFUp')},
    {'name':'leptonHit0SF', 'correlated':True, 'pair':('LeptonHit0SFDown', 'LeptonHit0SFUp')},
    {'name':'leptonSip3dSF','correlated':True, 'pair':('LeptonSip3dSFDown', 'LeptonSip3dSFUp')},
    #{'name': 'TopPt',      'correlated':True, 'pair':(  'TopPt', 'central')},
    {'name': 'JER',         'correlated':True, 'pair':('jerUp', 'jerDown')},
    {'name': 'L1Prefire',   'correlated':True, 'pair':('L1PrefireUp', 'L1PrefireDown')},
#NN
#    {'name': 'DYInput',           'pair':('DYInputUp', 'DYInputDown')},
#    {'name': 'TTInput',           'pair':('TTInputUp', 'TTInputDown')},
#    {'name': 'MBInput',           'pair':('MBInputUp', 'MBInputDown')},
#    {'name': 'TTZInput',          'pair':('TTZInputUp', 'TTZInputDown')},
#    {'name': 'OtherInput',        'pair':('OtherInputUp', 'OtherInputDown')},
#
#    {'name': 'TT1JetMismInput',   'pair':('TT1JetMismUp', 'TT1JetMismDown')},
#    {'name': 'TTTotJetMismInput', 'pair':('TTTotJetMismUp', 'TTTotJetMismDown')},
#    {'name': 'TTNonPromptInput',  'pair':('TTNonPromptInputUp', 'TTNonPromptInputDown')},
]


# store everything in the dir_db
lumi_scale = 137
#args.directories=\
#    [
#        "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/systematicPlots/Run2016/v0p19_small_T2tt_reweightPUCentral/lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
#        "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/systematicPlots/Run2016/v0p19_small_T2tt_reweightPUCentral/lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
#        "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/systematicPlots/Run2016/v0p19_small_T2tt_reweightPUCentral/lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
#        "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/systematicPlots/Run2017/v0p19_small_T2tt_reweightPUCentral/lepSel-badEEJetVeto-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
#        "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/systematicPlots/Run2018/v0p19_small_T2tt_reweightPUVUp/lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
#    ]

dirdb_key =   'variation_data_scaling_%s'%(args.scaling if args.scaling is not None else "None")
dirdb_key += "_variation_scaling_%s"%bool(args.variation_scaling)
dirdb_key += "_normalize_%s"%bool(args.normalize)

variation_data = {}
plots          = {}
for i_directory, directory in enumerate(args.directories):

    dirDB = DirDB(os.path.join(directory, 'cache'))
    v_data, v_plots, stack_mc, stack_data, stack_signal = dirDB.get(dirdb_key)
    variation_data[directory] = v_data
    plots[directory] = v_plots 
    if variation_data[directory] is None: 
        logger.error( "Did not find %s in %s", dirdb_key, directory )
    else:
        logger.info( "Found %s in %s", dirdb_key, directory )
# just take the first one for the plots. They must all be the same
plots = plots.values()[0]     

def drawObjects( scaling ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      ]
    #if scaling == 'mc':
    #  lines += [(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) SF(mc)=%3.2f'% ( lumi_scale, scaleFactor ) )]
    #elif scaling == 'top':
    #  lines += [(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) SF(top)=%3.2f'% ( lumi_scale, scaleFactor ) )]
    #elif scaling is None and args.normalize:
    #  lines += [(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) scale=%3.2f'% ( lumi_scale, scaleFactor ) )]
    #else:
    #  lines += [(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% ( lumi_scale) )]
    lines += [(0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% ( lumi_scale) )]
    #if "mt2ll100" in args.selection: lines += [(0.55, 0.65, 'M_{T2}(ll) > 100 GeV')] # Manually put the mt2ll > 100 GeV label
    return [tex.DrawLatex(*l) for l in lines]

def accumulate_level_2( lists_of_lists ):
    res = copy.deepcopy( lists_of_lists[0] )
    for stack_histos in lists_of_lists[1:]:
        for i_histos, histos in enumerate(stack_histos):
            for i_histo,histo in enumerate(histos):
                res[i_histos][i_histo].Add( histo )
    return res

# arguments & directory
plot_subdirectory = args.plot_directory

# We plot now. 
if args.normalize: plot_subdirectory += "_normalized"
if args.beta:      plot_subdirectory += "_%s"%args.beta
for mode in ['mumu', 'ee', 'mue', 'SF', 'all']:
    for i_plot, plot in enumerate(plots):
        
        # for central (=no variation), we store plot_data_1, plot_mc_1, plot_data_2, plot_mc_2, ...
        if args.signal:
            data_histo_list     = accumulate_level_2( [variation_data[directory][(mode, 'central')]['histos'][3*i_plot] for directory in args.directories] )
            signal_histo_list   = accumulate_level_2( [variation_data[directory][(mode, 'central')]['histos'][3*i_plot+1]  for directory in args.directories] )
            mc_histo_list       = {'central': accumulate_level_2( [variation_data[directory][(mode, 'central')]['histos'][3*i_plot+2] for directory in args.directories]) }
        else:
            data_histo_list     = accumulate_level_2( [variation_data[directory][(mode, 'central')]['histos'][2*i_plot]  for directory in args.directories] )
            signal_histo_list   = []
            mc_histo_list       = {'central': accumulate_level_2( [variation_data[directory][(mode, 'central')]['histos'][2*i_plot+1] for directory in args.directories]) }

        data_histo_list[0][0].style = styles.errorStyle(ROOT.kBlack)
        for i_mc, mc in enumerate(stack_mc[0]):
            mc_histo_list['central'][0][i_mc].legendText = mc.texName
        if args.signal:
            for i_sig, sig in enumerate(stack_signal):
                signal_histo_list[i_sig][0].legendText = sig[0].texName

        # for the other variations, there is no data
        for variation in variations.keys():
            if variation=='central': continue
            mc_histo_list[variation] = accumulate_level_2( [variation_data[directory][(mode, variation)]['histos'][i_plot] for directory in args.directories ] )
        for directory in args.directories:
            mc_histo_list[directory] = {variation: variation_data[directory][(mode, variation)]['histos'][i_plot] for variation in variations.keys()}

        # Add histos, del the stack (which refers to MC only )
        if args.signal:
            plot.histos =  mc_histo_list['central'] + data_histo_list + signal_histo_list
        else:
            plot.histos =  mc_histo_list['central'] + data_histo_list
        #plot.stack  = Stack( mc, [data_sample] )
        #if args.signal != None: 
        #    plot.histos += signal_histo_list
        #    plot.stack.extend( [ [s] for s in signals ] ) 
        
        # Make boxes and ratio boxes
        boxes           = []
        ratio_boxes     = []
        # Compute all variied MC sums
        total_mc_histo  = {variation:add_histos( mc_histo_list[variation][0]) for variation in variations.keys() }
        # store also per directory
        for directory in args.directories:
            total_mc_histo[directory]  = {variation:add_histos( mc_histo_list[directory][variation][0]) for variation in variations.keys() }

        # loop over bins & compute shaded uncertainty boxes
        boxes   = []
        r_boxes = []
        for i_b in range(1, 1 + total_mc_histo['central'].GetNbinsX() ):
            # Only positive yields
            total_central_mc_yield = total_mc_histo['central'].GetBinContent(i_b)
            # include overflow bin for the last bin
            overflowBin = True
            if i_b==total_mc_histo['central'].GetNbinsX() and overflowBin:
                total_central_mc_yield += total_mc_histo['central'].GetBinContent(i_b+1)
            if total_central_mc_yield<=0: continue
            variance = 0.
            for systematic in systematics:
                # Use 'central-variation' (factor 1) and 0.5*(varUp-varDown)
                if 'central' in systematic['pair']: 
                    factor = 1
                else:
                    factor = 0.5
                # sum in quadrature
                if systematic['correlated']:
                    variance += ( factor*(total_mc_histo[systematic['pair'][0]].GetBinContent(i_b) - total_mc_histo[systematic['pair'][1]].GetBinContent(i_b)) )**2
                else:
                    for directory in args.directories:
                        variance += ( factor*(total_mc_histo[directory][systematic['pair'][0]].GetBinContent(i_b) - total_mc_histo[directory][systematic['pair'][1]].GetBinContent(i_b)) )**2

            sigma     = sqrt(variance)
            sigma_rel = sigma/total_central_mc_yield 

            box = ROOT.TBox( 
                    total_mc_histo['central'].GetXaxis().GetBinLowEdge(i_b),
                    max([0.03, (1-sigma_rel)*total_central_mc_yield]),
                    total_mc_histo['central'].GetXaxis().GetBinUpEdge(i_b), 
                    max([0.03, (1+sigma_rel)*total_central_mc_yield]) )
            box.SetLineColor(ROOT.kBlack)
            box.SetFillStyle(3444)
            box.SetFillColor(ROOT.kBlack)
            boxes.append(box)

            r_box = ROOT.TBox( 
                total_mc_histo['central'].GetXaxis().GetBinLowEdge(i_b),  
                max(0.1, 1-sigma_rel), 
                total_mc_histo['central'].GetXaxis().GetBinUpEdge(i_b), 
                min(1.9, 1+sigma_rel) )
            r_box.SetLineColor(ROOT.kBlack)
            r_box.SetFillStyle(3444)
            r_box.SetFillColor(ROOT.kBlack)
            ratio_boxes.append(r_box)

        for log in [False, True]:
            plot_directory_ = os.path.join(plot_directory, 'systematicPlots', 'combined', plot_subdirectory, args.selection, mode + ("_log" if log else ""))
            #if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
            texMode = "#mu#mu" if mode == "mumu" else "#mue" if mode == "mue" else mode
            if    mode == "all": plot.histos[1][0].legendText = "data (RunII)"
            else:                plot.histos[1][0].legendText = "data (%s, %s)"%("RunII", texMode)

            _drawObjects = []

            plotting.draw(plot,
              plot_directory = plot_directory_,
              ratio = {'yRange':(0.1,1.9), 'drawObjects':ratio_boxes},
              logX = False, logY = log, sorting = False,
              yRange = (0.03, "auto") if log else (0.001, "auto"),
              scaling = {0:1} if args.normalize else {},
              legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
              drawObjects = drawObjects( args.scaling ) + boxes,
              copyIndexPHP = True, extensions = ["png", "pdf"],
            )
