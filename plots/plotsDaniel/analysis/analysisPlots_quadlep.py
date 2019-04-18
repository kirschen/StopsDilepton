#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools

from math                         import sqrt, cos, sin, pi, acos, cosh
from RootTools.core.standard      import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, getObjDict, getVarValue, deltaR, deltaR2
from Analysis.Tools.metFilters import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.triggerSelector import triggerSelector
from StopsDilepton.samples.color         import color

# for mt2ll
from StopsDilepton.tools.mt2Calculator   import mt2Calculator

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "ewkDM", "ttZ01j"], help="Add signal to plot")
argParser.add_argument('--onlyTTZ',            action='store_true', default=False,           help="Plot only ttZ")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',      action='store',      default='v0p5')
argParser.add_argument('--selection',           action='store',      default='lepSel-quadlep-njet1p-btag0-onZZ')
argParser.add_argument('--normalize',           action='store_true', default=False,             help="Normalize yields" )
argParser.add_argument('--year',                action='store',      default=2016,   type=int,  help="Which year?" )
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
if args.normalize: args.plot_directory += "_normalize"
#
# Make samples, will be searched for in the postProcessing directory
#

if args.year == 2016:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2016_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    postProcessing_directory = "stops_2016_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc          = [ TTXNoZ_16, TTZ_16, multiBoson_16, ZZ4l_16]
    data_sample = Run2016

elif args.year == 2017:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p6/dilep/"
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    postProcessing_directory = "stops_2017_nano_v0p6/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc          = [ TTXNoZ_17, TTZ_17, multiBoson_17, ZZ4l_17]
    data_sample = Run2017

elif args.year == 2018:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2018_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    postProcessing_directory = "stops_2018_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc          = [ TTXNoZ_18, TTZ_18, multiBoson_18, ZZ4l_18]
    data_sample = Run2018


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
    return [tex.DrawLatex(*l) for l in lines] 

scaling = { i+1:0 for i in range(len(signals)) }

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.selection, mode + ("_log" if log else ""), str(args.year))
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"
      extensions_ = ["pdf", "png", "root"] if mode == 'all' else ['png']

      plotting.draw(plot,
	    plot_directory = plot_directory_,
        extensions = extensions_,
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = True,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = scaling if args.normalize else {},
	    legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
        copyIndexPHP = True,
      )

# define 4l selections
offZ2 = "&&abs(Z2_mass-91.2)>20" if args.selection.count("offZ2") else ""
offZ2 = "&&met_pt > 80" if args.selection.count("offZ2met") else offZ2

minZ2mass12 = "&&Z2_mass>12" if args.selection.count("minZ2mass12") else ""

print offZ2

def getLeptonSelection( mode ):
    if   mode=="mumumumu":  return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==13)==4&&Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==11)==0" + offZ2 + minZ2mass12
    elif mode=="mumumue":   return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==13)==3&&Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==11)==1"
    elif mode=="mumuee":    return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==13)==2&&Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==11)==2" + offZ2 + minZ2mass12
    elif mode=="mueee":     return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==13)==1&&Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==11)==3"
    elif mode=="eeee":      return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==13)==0&&Sum$(lep_pt>10&&abs(lep_eta)<2.4&&abs(lep_pdgId)==11)==4" + offZ2 + minZ2mass12
    elif mode=='all':       return "Sum$(lep_pt>10&&abs(lep_eta)<2.4)==4"


#
# Read variables and sequences
#
read_variables =    ["weight/F",
                    #"jet[pt/F,eta/F,phi/F,btagCSV/F,DFb/F,DFbb/F,id/I]", "njet/I","nJetSelected/I",
                    "lep[pt/F,eta/F,phi/F,pdgId/I]", #"nlep/I",
                    "met_pt/F", "met_phi/F", "metSig/F", "ht/F", "nBTag/I", 
                    "Z1_l1_index/I", "Z1_l2_index/I", "nonZ1_l1_index/I", "nonZ1_l2_index/I", "Z2_l1_index/I", "Z2_l2_index/I", 
                    "Z1_phi/F","Z1_pt/F", "Z1_mass/F", "Z1_eta/F","Z1_lldPhi/F", "Z1_lldR/F", 
                    "Z2_phi/F","Z2_pt/F", "Z2_mass/F", "Z2_eta/F",
                    ]

sequence = []

def getMT2ll( event, sample ):
    mt2Calculator.reset()
    l1 = ROOT.TLorentzVector()
    l2 = ROOT.TLorentzVector()
    event.lep_pt[event.nonZ1_l1_index]
    l1.SetPtEtaPhiM(event.lep_pt[event.nonZ1_l1_index], event.lep_eta[event.nonZ1_l1_index], event.lep_phi[event.nonZ1_l1_index], 0 )
    l2.SetPtEtaPhiM(event.lep_pt[event.nonZ1_l2_index], event.lep_eta[event.nonZ1_l2_index], event.lep_phi[event.nonZ1_l2_index], 0 )
    mt2Calculator.setLeptons(l1.Pt(), l1.Eta(), l1.Phi(), l2.Pt(), l2.Eta(), l2.Phi())

    met         = ROOT.TLorentzVector()
    met.SetPtEtaPhiM( event.met_pt, 0, event.met_phi, 0)

    Z           = ROOT.TLorentzVector()
    Z.SetPtEtaPhiM( event.Z1_pt, event.Z1_eta, event.Z1_phi, 0)

    newMet = met+Z

    mt2Calculator.setMet(newMet.Pt(), newMet.Phi())
    event.dl_mt2ll_Z = mt2Calculator.mt2ll()

sequence += [ getMT2ll ]

#def getMinMLL( event, sample ):
#    

MW = 80.385
Mt = 172.5


#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumumumu','mumumue','mumuee', 'mueee', 'eeee']
for index, mode in enumerate(allModes):
    yields[mode] = {}
    logger.info("Working on mode %s", mode)
    if not args.noData:
        data_sample.texName = "data"

        data_sample.setSelectionString([getFilterCut(isData=True, year=args.year), getLeptonSelection(mode)])
        data_sample.name           = "data"
        data_sample.read_variables = ["event/I","run/I"]
        data_sample.style          = styles.errorStyle(ROOT.kBlack)
        lumi_scale                 = data_sample.lumi/1000

    if args.noData: lumi_scale = 35.9 if args.year == 2016 else 41.0
    weight_ = lambda event, sample: event.weight

    for sample in mc: sample.style = styles.fillStyle(sample.color)

    for sample in mc + signals:
      sample.scale          = lumi_scale
      sample.read_variables = ['reweightBTag_SF/F', 'reweightPU36fb/F', 'reweightDilepTrigger/F', 'reweightLeptonTrackingSF/F', 'reweightPU36fb/F', 'reweightLeptonSF/F']
      
      if args.year == 2016:
          sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightDilepTrigger*event.reweightLeptonTrackingSF*event.reweightPU36fb*event.reweightLeptonSF
      else:
          sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightDilepTrigger*event.reweightPU36fb*event.reweightLeptonSF
      sample.setSelectionString([getFilterCut(isData=False, year=args.year), getLeptonSelection(mode)])

    if not args.noData:
      stack = Stack(mc, data_sample)
    else:
      stack = Stack(mc)

    stack.extend( [ [s] for s in signals ] )

    if args.small:
        for sample in stack.samples:
            sample.reduceFiles( to = 1 )

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='both')

    plots = []
    
    plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + index,
      binning=[5, 0, 5],
    ))
    
    #plots.append(Plot(
    #  name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
    #  attribute = TreeVariable.fromString( "nVert/I" ),
    #  binning=[50,0,50],
    #))
    
    plots.append(Plot(
        texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "met_pt/F" ),
        binning=[400/20,0,400],
    ))
    
    plots.append(Plot(
        texX = 'H_{T} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "ht/F" ),
        binning=[800/20,0,800],
    ))
    
    plots.append(Plot(
        texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "met_phi/F" ),
        binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(
        texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[20,0,400],
    ))
    
    plots.append(Plot(
        name = 'Z1_pt_coarse', texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 50 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[16,0,800],
    ))
    
    plots.append(Plot(
        name = 'Z1_pt_superCoarse', texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[3,0,600],
    ))
    
    plots.append(Plot(
        name = 'Z1_pt_analysis', texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 100 GeV',
        attribute = TreeVariable.fromString( "Z1_pt/F" ),
        binning=[4,0,400],
    ))
    
    plots.append(Plot(
        texX = '#Delta#phi(ll)', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "Z1_lldPhi/F" ),
        binning=[10,0,pi],
    ))

    # plots of lepton variables

    plots.append(Plot(
        name = "lZ1_pt",
        texX = 'p_{T}(l_{1,Z}) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample:event.lep_pt[event.Z1_l1_index],
        binning=[30,0,300],
    ))

    plots.append(Plot(
        name = "lZ1_eta",
        texX = 'eta(l_{1,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_eta[event.Z1_l1_index],
        binning=[40,-4.,4.],
    ))

    plots.append(Plot(
        name = "lZ1_phi",
        texX = '#phi(l_{1,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_phi[event.Z1_l1_index],
        binning=[40,-3.2,3.2],
    ))

    plots.append(Plot(
        name = "lZ1_pdgId",
        texX = 'PDG ID (l_{1,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_pdgId[event.Z1_l1_index],
        binning=[30,-15,15],
    ))

    # lepton 2    
    plots.append(Plot(
        name = "lZ2_pt",
        texX = 'p_{T}(l_{2,Z}) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample:event.lep_pt[event.Z1_l2_index],
        binning=[20,0,200],
    ))


    plots.append(Plot(
        name = "lZ2_eta",
        texX = 'eta(l_{2,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_eta[event.Z1_l2_index],
        binning=[40,-4.,4.],
    ))

    plots.append(Plot(
        name = "lZ2_phi",
        texX = '#phi(l_{2,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_phi[event.Z1_l2_index],
        binning=[40,-3.2,3.2],
    ))

    plots.append(Plot(
        name = "lZ2_pdgId",
        texX = 'PDG ID (l_{2,Z})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_pdgId[event.Z1_l2_index],
        binning=[30,-15,15],
    ))
    
    # lepton 3
    plots.append(Plot(
        name = 'lnonZ1_pt',
        texX = 'p_{T}(l_{1,extra}) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample:event.lep_pt[event.nonZ1_l1_index],
        binning=[30,0,300],
    ))

    plots.append(Plot(
        name = "lnonZ1_eta",
        texX = 'eta(l_{1,extra})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_eta[event.nonZ1_l1_index],
        binning=[40,-4.,4.],
    ))

    plots.append(Plot(
        name = "lnonZ1_phi",
        texX = '#phi(l_{1,extra})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_phi[event.nonZ1_l1_index],
        binning=[40,-3.2,3.2],
    ))

    plots.append(Plot(
        name = "lnonZ1_pdgId",
        texX = 'PDG ID (l_{1,extra})', texY = 'Number of Events',
        attribute = lambda event, sample:event.lep_pdgId[event.nonZ1_l1_index],
        binning=[30,-15,15],
    ))

    # other plots


    plots.append(Plot(
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 2 GeV',
        attribute = TreeVariable.fromString( "Z1_mass/F" ),
        binning=[20,70,110],
    ))

    plots.append(Plot(
        texX = 'M(ll) 2nd OS pair (GeV)', texY = 'Number of Events / 8 GeV',
        attribute = TreeVariable.fromString( "Z2_mass/F" ),
        binning=[20,40,200],
    ))

    plots.append(Plot(
        texX = 'M(ll) 2nd OS pair (GeV)', texY = 'Number of Events / 5 GeV',
        name = "Z2_mass_wide",
        attribute = TreeVariable.fromString( "Z2_mass/F" ),
        binning=[40,0,200],
    ))
    
    plots.append(Plot(
        texX = 'M_{T2}(ll) Z estimated (GeV)', texY = 'Number of Events',
        name = "mt2ll_Z_estimated",
        attribute = lambda event, sample: event.dl_mt2ll_Z,
        binning=[4,0,320],
    ))
    
    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ), #nJetSelected
      binning=[8,-0.5,7.5],
    ))
    
    plots.append(Plot(
      texX = 'N_{b-tag}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nBTag/I" ),
      binning=[4,-0.5,3.5],
    ))
    
    plots.append(Plot(
      texX = 'p_{T}(leading l) (GeV)', texY = 'Number of Events / 20 GeV',
      name = 'lep1_pt', attribute = lambda event, sample: event.lep_pt[0],
      binning=[400/20,0,400],
    ))

    plots.append(Plot(
      texX = 'p_{T}(subleading l) (GeV)', texY = 'Number of Events / 10 GeV',
      name = 'lep2_pt', attribute = lambda event, sample: event.lep_pt[1],
      binning=[200/10,0,200],
    ))

    plots.append(Plot(
      texX = 'p_{T}(trailing l) (GeV)', texY = 'Number of Events / 10 GeV',
      name = 'lep3_pt', attribute = lambda event, sample: event.lep_pt[2],
      binning=[150/10,0,150],
    ))
    
    plotting.fill(plots, read_variables = read_variables, sequence = sequence)

    # Get normalization yields from yield histogram
    for plot in plots:
      if plot.name == "yield":
        for i, l in enumerate(plot.histos):
          for j, h in enumerate(l):
            yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
            h.GetXaxis().SetBinLabel(1, "#mu#mu#mu#mu")
            h.GetXaxis().SetBinLabel(2, "#mu#mu#mue")
            h.GetXaxis().SetBinLabel(3, "#mu#muee")
            h.GetXaxis().SetBinLabel(4, "#mueee")
            h.GetXaxis().SetBinLabel(5, "eeee")
    if args.noData: yields[mode]["data"] = 0

    yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
    dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

    drawPlots(plots, mode, dataMCScale)
    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["comb1","comb2","comb3","all"]:
    yields[mode] = {}
    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum(yields[c][y] for c in ['eeee','mueee','mumuee', 'mumumue', 'mumumumu'])
        except: yields[mode][y] = 0
    dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
    
    for plot in allPlots['mumumumu']:
        if mode=="comb1":
            tmp = allPlots['mumumue']
        elif mode=="comb2":
            tmp = allPlots['mumuee']
        elif mode=="comb3":
            tmp = allPlots['mueee']
        else:
            tmp = allPlots['eeee']
        for plot2 in (p for p in tmp if p.name == plot.name):
            for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                    if i==k:
                        j.Add(l)
    
    if mode == "all": drawPlots(allPlots['mumumumu'], mode, dataMCScale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

