#!/usr/bin/env python
''' Simple plot script for JER-related variables
    using badEEJetVeto for 2017, although it is not stated on the plot directory!!!
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
from StopsDilepton.tools.helpers         import deltaPhi, deltaR
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--dpm',               action='store_true',     help='Use dpm?', )

argParser.add_argument('--small',                                 action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')

argParser.add_argument('--sample',             action='store',      default="TTbar",    choices=["TTbar", "DY_HT", "DY", "multiBoson"])
argParser.add_argument('--variation',          action='store',      default="nom",      choices=["nom", "jer", "jerUp", "jerDown"])
argParser.add_argument('--weight',             action='store',      default="noWeight", choices=["lumi", "allMCWeights", "weight", "noWeight"])

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

#
# Make samples, will be searched for in the postProcessing directory
#
from RootTools.core.Sample import Sample
from StopsDilepton.samples.color import color

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

mc = []
dirs = {}

dirs['Top_pow'] = ["TTLep_pow"]

###################################################################### 2016 ######################################################################

#data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
#postProcessing_directory    = "stops_2016_nano_v0p16/dilep/"
#data_directory              = "/afs/hephy.at/data/rschoefbeck02/nanoTuples/"
postProcessing_directory    = "stops_2016_nano_v0p15/dilep/"

dirs['DY_LO']    = ["DYJetsToLL_M50_LO_ext1_comb", "DYJetsToLL_M10to50_LO"]
dirs['DY_HT_LO'] = [
            "DYJetsToLL_M5to50_HT70to100",
            "DYJetsToLL_M5to50_HT100to200_comb",
            "DYJetsToLL_M5to50_HT200to400_comb",
            "DYJetsToLL_M5to50_HT400to600_comb",
            "DYJetsToLL_M5to50_HT600toInf",
            "DYJetsToLL_M50_LO_ext1_comb_lheHT70", 
            "DYJetsToLL_M50_HT70to100",
            "DYJetsToLL_M50_HT100to200_ext",
            "DYJetsToLL_M50_HT200to400_comb",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ]

dirs['WW']               = ["WWToLNuQQ"]
dirs['VVTo2L2Nu']        = ["VVTo2L2Nu_comb"]
dirs['WZ']               = ["WZTo1L1Nu2Q",  "WZTo1L3Nu", "WZTo2L2Q", "WZTo3LNu_ext"]
dirs['ZZ']               = ["ZZTo2L2Q", "ZZTo2Q2Nu"]
dirs['ZZ4l']             = ["ZZTo4L"]
dirs['ZZTo2L2Nu']        = ["ZZTo2L2Nu"]
dirs['diBoson']          = dirs['WW'] + dirs['WZ'] + dirs['ZZ']+ dirs['VVTo2L2Nu']
dirs['triBoson']         = ["WWW_4F","WWZ","WZZ","ZZZ"]
dirs['multiBoson']       = dirs['diBoson'] + dirs['triBoson']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}
Top_pow_16      = Sample.fromDirectory(name="Top_pow",          treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t}/single-t",                 directory=directories['Top_pow'])
DY_HT_LO_16        = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_HT_LO'])
DY_LO_16        = Sample.fromDirectory(name="DY_LO",               treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_LO'])
multiBoson_16      = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])

###################################################################### 2017 ######################################################################

#data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
#postProcessing_directory    = "stops_2017_nano_v0p16/dilep/"
#data_directory              = "/afs/hephy.at/data/cms06/nanoTuples/"
postProcessing_directory    = "stops_2017_nano_v0p15/dilep/"

dirs['DY_LO']    = ["DYJetsToLL_M50_LO_comb", "DYJetsToLL_M10to50_LO"]
dirs['DY_HT_LO'] = [
            "DYJetsToLL_M10to50_LO_lheHT100", 
            "DYJetsToLL_M4to50_HT100to200_comb",
            "DYJetsToLL_M4to50_HT200to400_comb",
            "DYJetsToLL_M4to50_HT400to600_comb",
            "DYJetsToLL_M4to50_HT600toInf_comb",
            "DYJetsToLL_M50_LO_comb_lheHT70", 
            "DYJetsToLL_M50_HT70to100",
            "DYJetsToLL_M50_HT100to200",
            "DYJetsToLL_M50_HT200to400_comb",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ] 

dirs['WW']               = ["WWToLNuQQ"]
dirs['VVTo2L2Nu']        = ["VVTo2L2Nu"]
dirs['WZ']               = ["WZTo1L1Nu2Q", "WZTo2L2Q", "WZTo1L3Nu", "WZTo3LNu_amcatnlo"]
dirs['ZZ']               = ["ZZTo2L2Q"] # "ZZTo2Q2Nu"
dirs['ZZ4l']             = ["ZZTo4L"] # "ZZTo2Q2Nu"
dirs['diBoson']          = dirs['WW'] + dirs['WZ'] + dirs['ZZ'] + dirs['VVTo2L2Nu']
dirs['triBoson']         = ["WWW_4F","WWZ_4F","WZZ","ZZZ"] 
dirs['multiBoson']       = dirs['diBoson'] + dirs['triBoson']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}
Top_pow_17      = Sample.fromDirectory(name="Top_pow",          treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t}/single-t",                 directory=directories['Top_pow'])
DY_HT_LO_17        = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_HT_LO'])
DY_LO_17        = Sample.fromDirectory(name="DY_LO",               treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_LO'])
multiBoson_17      = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])

###################################################################### 2018 ######################################################################

#data_directory              = "/afs/hephy.at/data/cms05/nanoTuples/"
#postProcessing_directory    = "stops_2018_nano_v0p16/dilep/"
#data_directory              = "/afs/hephy.at/data/rschoefbeck02/nanoTuples/"
postProcessing_directory    = "stops_2018_nano_v0p15/dilep/"

dirs['DY_LO']    = ["DYJetsToLL_M50_LO", "DYJetsToLL_M10to50_LO"]
dirs['DY_HT_LO'] = [
            "DYJetsToLL_M10to50_LO_lheHT70", 
            "DYJetsToLL_M4to50_HT70to100",
            "DYJetsToLL_M4to50_HT100to200",
            "DYJetsToLL_M4to50_HT200to400",
            "DYJetsToLL_M4to50_HT400to600",
            "DYJetsToLL_M4to50_HT600toInf",
            "DYJetsToLL_M50_LO_lheHT70", 
            "DYJetsToLL_M50_HT70to100",
            "DYJetsToLL_M50_HT100to200",
            "DYJetsToLL_M50_HT200to400",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ]

dirs['WW']              = ["WWToLNuQQ"]
dirs['WZ']              = ["WZTo1L3Nu", "WZTo2L2Q", "WZTo3LNu_amcatnlo"] # no miniAOD of WZTo1L1Nu2Q yet
dirs['ZZ']              = ["ZZTo2L2Q_redBy5", "ZZTo2Q2Nu"]
dirs['ZZ4l']            = ['ZZTo4L']
dirs['diBoson']         = dirs['VVTo2L2Nu'] + dirs['WW'] + dirs['WZ'] + dirs['ZZ']
dirs['triBoson']        = ["WWZ","WZZ","ZZZ"] # WWW_4F to be added in the next round
dirs['multiBoson']      = dirs['diBoson'] + dirs['triBoson']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}
Top_pow_18         = Sample.fromDirectory(name="Top_pow",          treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t}/single-t",                 directory=directories['Top_pow'])
DY_HT_LO_18        = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_HT_LO'])
DY_LO_18        = Sample.fromDirectory(name="DY_LO",               treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_LO'])
multiBoson_18      = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])

# append samples
if args.sample == "DY":
    mc=[DY_LO_16, DY_LO_17, DY_LO_18]
    kColor = ROOT.kGreen
elif args.sample == "DY_HT":
    mc=[DY_HT_LO_16, DY_HT_LO_17, DY_HT_LO_18]
    kColor = ROOT.kGreen
elif args.sample == "multiBoson":
    mc=[multiBoson_16, multiBoson_17, multiBoson_18]
    kColor = ROOT.kOrange
elif args.sample == "TTbar":
    mc=[Top_pow_16, Top_pow_17, Top_pow_18]
    kColor = ROOT.kCyan

if args.small:
    for sample in mc:
        sample.reduceFiles( factor = 40 )

# lepton selection
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ

replacementStrings = {
"MET_pt": ["met_pt", "0.5*(MET_pt_jerUp+MET_pt_jerDown)" , "MET_pt_jerUp", "MET_pt_jerDown"],
"MET_phi": ["met_phi", "0.5*(MET_phi_jerUp+MET_phi_jerDown)" , "MET_phi_jerUp", "MET_phi_jerDown"],
"met_pt": ["met_pt", "0.5*(met_pt_jerUp+met_pt_jerDown)" , "met_pt_jerUp", "met_pt_jerDown"],
"met_phi": ["met_phi", "0.5*(met_phi_jerUp+met_phi_jerDown)" , "met_phi_jerUp", "met_phi_jerDown"],
"Jet_pt": ["Jet_pt", "0.5*(Jet_pt_jerUp+Jet_pt_jerDown)" , "Jet_pt_jerUp", "Jet_pt_jerDown"],
"nBTag": ["nBTag", "0.5*(nBTag_jerUp+nBTag_jerDown)" , "nBTag_jerUp", "nBTag_jerDown"],
"nJetGood": ["nJetGood", "0.5*(nJetGood_jerUp+nJetGood_jerDown)" , "nJetGood_jerUp", "nJetGood_jerDown"],
"MET_significance": ["MET_significance", "0.5*(MET_significance_jerUp+MET_significance_jerDown)" , "MET_significance_jerUp", "MET_significance_jerDown"],
"dl_mt2ll": ["dl_mt2ll", "0.5*(dl_mt2ll_jerUp+dl_mt2ll_jerDown)" , "dl_mt2ll_jerUp", "dl_mt2ll_jerDown"],
"dl_mt2bb": ["dl_mt2bb", "0.5*(dl_mt2bb_jerUp+dl_mt2bb_jerDown)" , "dl_mt2bb_jerUp", "dl_mt2bb_jerDown"],
"dl_mt2blbl": ["dl_mt2blbl", "0.5*(dl_mt2blbl_jerUp+dl_mt2blbl_jerDown)" , "dl_mt2blbl_jerUp", "dl_mt2blbl_jerDown"],
}

#v = 0 # nom
#if "jer"== args.variation:
#    v = 1
#elif "jerUp"== args.variation:
#    v = 2
#elif "jerDown"== args.variation:
#    v = 3
 
selectionForYear = {}
for year in [2016, 2017, 2018]:
    preSel = [getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection("mumu")]
    if year == 2017:
        selection = args.selection.replace("lepSel", "lepSel-badEEJetVeto")
    else:
        selection = args.selection
    cutInterpreterString = cutInterpreter.cutString(selection)
    selectionForYear[year] = {}
    for v, variation in enumerate(["nom", "jer", "jerUp", "jerDown"]):
        selectionStringForYear = "&&".join(preSel + [cutInterpreterString])
        if variation is not "nom":
            for var, replacement in replacementStrings.iteritems():
                # var -> replacement
                selectionStringForYear = selectionStringForYear.replace(var, replacement[v])
        selectionForYear[year][variation] = selectionStringForYear

if args.weight == "weight":
    weightString = "weight"
elif args.weight == "noWeight":
    weightString = "(1)"
else:
    weightString = "weight*reweightPU*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF*reweightL1Prefire*reweightHEM"

plotVariables = {"MET": ["MET_pt", "0.5*(MET_pt_jerUp+MET_pt_jerDown)", "MET_pt_jerUp", "MET_pt_jerDown"], 
                "mt2ll": ["dl_mt2ll", "0.5*(dl_mt2ll_jerUp+dl_mt2ll_jerDown)", "dl_mt2ll_jerUp", "dl_mt2ll_jerDown"], 
                "mt2blbl": ["dl_mt2blbl", "0.5*(dl_mt2blbl_jerUp+dl_mt2blbl_jerDown)", "dl_mt2blbl_jerUp", "dl_mt2blbl_jerDown"]}
plots = []

for y, year in enumerate([2016, 2017, 2018]):
    # lumi scale
    if year   == 2016: lumi_scale = 35.9
    elif year == 2017: lumi_scale = 41.9
    elif year == 2018: lumi_scale = 60.0

    # loop over variables
    for plotVar, plotList in plotVariables.iteritems():

        if plotVar == "mt2ll": # mt2ll binning
            plotBinning = [0,20,40,60,80,100,140,240,340]
        elif plotVar == "mt2blbl": # mt2blbl binning
            plotBinning = [0,20,40,60,80,100,120,140,160,200,250,300,350]
        else:
            #plotBinning = [0,80,130,180,230,280,320,420,520,800]
            plotBinning = [0,80,100,120,140,160,200,500]

        if year == 2018:
            weight = weightString.replace("reweightPU", "reweightPUVUp")
        else:
            weight = weightString

        #print "\n weight: \n", weight, "\n"
        #print "nom selection: \n", selectionForYear[year]["nom"], "\n"
        #print "jer selection: \n", selectionForYear[year]["jer"], "\n"
        #print "jerUp selection: \n", selectionForYear[year]["jerUp"], "\n"
        #print "jerDown selection: \n", selectionForYear[year]["jerDown"], "\n"

        plotNom     = mc[y].get1DHistoFromDraw(plotList[0], selectionString = selectionForYear[year]["nom"],     weightString = weight+"*"+str(lumi_scale), binning = plotBinning, binningIsExplicit = True)
        plotJer     = mc[y].get1DHistoFromDraw(plotList[1], selectionString = selectionForYear[year]["jer"],     weightString = weight+"*"+str(lumi_scale), binning = plotBinning, binningIsExplicit = True)
        plotJerUp   = mc[y].get1DHistoFromDraw(plotList[2], selectionString = selectionForYear[year]["jerUp"],   weightString = weight+"*"+str(lumi_scale), binning = plotBinning, binningIsExplicit = True)
        plotJerDown = mc[y].get1DHistoFromDraw(plotList[3], selectionString = selectionForYear[year]["jerDown"], weightString = weight+"*"+str(lumi_scale), binning = plotBinning, binningIsExplicit = True)
        hList = [plotNom, plotJer, plotJerUp, plotJerDown]

        histos = [ [h] for h in hList ]
        histos[0][0].style = styles.lineStyle( ROOT.kGray )
        histos[0][0].legendText = plotVar+"_nom"
        histos[1][0].style = styles.lineStyle( ROOT.kGray+3 )
        histos[1][0].legendText = plotVar+"_jer (+ selection)"
        histos[2][0].style = styles.lineStyle( kColor-3 )
        histos[2][0].legendText = plotVar+"_jerUp (+ selection)"
        histos[3][0].style = styles.lineStyle( kColor )
        histos[3][0].legendText = plotVar+"_jerDown (+ selection)"

        plots.append(Plot.fromHisto(name = plotVar+"_"+str(year)+("_small" if args.small else ""), histos = histos, texX = plotVar + " ("+str(year)+")", texY = "Events") )
        plotting.draw(plots[len(plots)-1], plot_directory = "/afs/hephy.at/user/m/mdoppler/www/stopsDileptonLegacy/JER/"+args.sample+"/"+args.selection+"/"+args.weight+"/", ratio = None, logY = True, logX = False)







