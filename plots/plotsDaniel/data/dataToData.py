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

from math                         import sqrt, cos, sin, pi
from RootTools.core.standard      import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaR, deltaPhi, getObjDict, getVarValue
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='StopsDilepton_dataVsData_v1')
argParser.add_argument('--selection',          action='store',      default='lepSel-OS-looseLeptonVeto-njet2p-relIso0.12-mll20')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory
#

data_directory           = "/afs/hephy.at/data/dspitzbart01/nanoTuples"


postProcessing_directory = "2016_nano_v1/dilep"
from StopsDilepton.samples.nanoTuples_Run2016_05Feb2018 import *

postProcessing_directory = "2017_nano_v1/dilep/"
from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018 import *

postProcessing_directory = "2018_nano_v1/dilep/"
from StopsDilepton.samples.nanoTuples_Run2018_PromptReco import *


# define 2l selections
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0"
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2"
  elif mode=='all':  return "nGoodMuons+nGoodElectrons==2"

# Read variables and sequences
#
read_variables =    ["weight/F",
                    "JetGood[pt/F,eta/F,phi/F,btagCSVV2/F,btagDeepB/F,rawFactor/F]", "nJetGood/I",
                    "Jet[pt/F,eta/F,phi/F,btagCSVV2/F,btagDeepB/F,rawFactor/F]", "nJet/I",
                    "l1[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "l2[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "MET_pt/F", "MET_phi/F", "metSig/F", "ht/F", "nBTag/I", 
                    "RawMET_pt/F", "RawMET_phi/F", 
                    ]


sequence = []

def getUpdatedMET( event, sample ):
    MET = ROOT.TVector3()
    MET.SetPtEtaPhi(event.MET_pt, 0., event.MET_phi)

    jetVars = ['eta','pt','phi','rawFactor']
    jets = [getObjDict(event, 'Jet_', jetVars, i) for i in range(int(getVarValue(event, 'nJet')))]

    JetsEtaM4     = [ jet for jet in jets if        jet['eta'] <= -4.0 and jet['pt']>25 ]
    JetsEtaM3     = [ jet for jet in jets if -4.0 < jet['eta'] <= -3.0 and jet['pt']>25 ]
    JetsEtaM2p5   = [ jet for jet in jets if -3.0 < jet['eta'] <= -2.5 and jet['pt']>25 ]
    JetsEtaM2     = [ jet for jet in jets if -2.5 < jet['eta'] <= -2.0 and jet['pt']>25 ]
    JetsEtaM1     = [ jet for jet in jets if -2.0 < jet['eta'] <= -1.0 and jet['pt']>25 ]
    JetsEta0      = [ jet for jet in jets if -1.0 < jet['eta'] <=  0.0 and jet['pt']>25 ]
    JetsEta1      = [ jet for jet in jets if  0.0 < jet['eta'] <=  1.0 and jet['pt']>25 ]
    JetsEta2      = [ jet for jet in jets if  1.0 < jet['eta'] <=  2.0 and jet['pt']>25 ]
    JetsEta2p5    = [ jet for jet in jets if  2.0 < jet['eta'] <=  2.5 and jet['pt']>25 ]
    JetsEta3      = [ jet for jet in jets if  2.5 < jet['eta'] <=  3.0 and jet['pt']>25 ]
    JetsEta4      = [ jet for jet in jets if  3.0 < jet['eta'] <=  4.0 and jet['pt']>25 ]
    JetsEtaInf    = [ jet for jet in jets if  4.0 < jet['eta']         and jet['pt']>25 ]

    event.nJetEtaM4     = len( JetsEtaM4 )
    event.nJetEtaM3     = len( JetsEtaM3 )
    event.nJetEtaM2p5   = len( JetsEtaM2p5 )
    event.nJetEtaM2     = len( JetsEtaM2 )
    event.nJetEtaM1     = len( JetsEtaM1 )
    event.nJetEta0      = len( JetsEta0 )
    event.nJetEta1      = len( JetsEta1 )
    event.nJetEta2      = len( JetsEta2 )
    event.nJetEta2p5    = len( JetsEta2p5 )
    event.nJetEta3      = len( JetsEta3 )
    event.nJetEta4      = len( JetsEta4 )
    event.nJetEtaInf    = len( JetsEtaInf )

    event.Jet_pt_EtaM4     = JetsEtaM4[0]['pt']     if len(JetsEtaM4)>0     else -99.
    event.Jet_pt_EtaM3     = JetsEtaM3[0]['pt']     if len(JetsEtaM3)>0     else -99.
    event.Jet_pt_EtaM2p5   = JetsEtaM2p5[0]['pt']   if len(JetsEtaM2p5)>0   else -99.
    event.Jet_pt_EtaM2     = JetsEtaM2[0]['pt']     if len(JetsEtaM2)>0     else -99.
    event.Jet_pt_EtaM1     = JetsEtaM1[0]['pt']     if len(JetsEtaM1)>0     else -99.
    event.Jet_pt_Eta0      = JetsEta0[0]['pt']      if len(JetsEta0)>0      else -99.
    event.Jet_pt_Eta1      = JetsEta1[0]['pt']      if len(JetsEta1)>0      else -99.
    event.Jet_pt_Eta2      = JetsEta2[0]['pt']      if len(JetsEta2)>0      else -99.
    event.Jet_pt_Eta2p5    = JetsEta2p5[0]['pt']    if len(JetsEta2p5)>0    else -99.
    event.Jet_pt_Eta3      = JetsEta3[0]['pt']      if len(JetsEta3)>0      else -99.
    event.Jet_pt_Eta4      = JetsEta4[0]['pt']      if len(JetsEta4)>0      else -99.
    event.Jet_pt_EtaInf    = JetsEtaInf[0]['pt']    if len(JetsEtaInf)>0    else -99.

    event.nJetRawEtaM4     = len( [ jet for jet in jets if        jet['eta'] <= -4.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEtaM3     = len( [ jet for jet in jets if -4.0 < jet['eta'] <= -3.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEtaM2p5   = len( [ jet for jet in jets if -3.0 < jet['eta'] <= -2.5 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEtaM2     = len( [ jet for jet in jets if -2.5 < jet['eta'] <= -2.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEtaM1     = len( [ jet for jet in jets if -2.0 < jet['eta'] <= -1.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta0      = len( [ jet for jet in jets if -1.0 < jet['eta'] <=  0.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta1      = len( [ jet for jet in jets if  0.0 < jet['eta'] <=  1.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta2      = len( [ jet for jet in jets if  1.0 < jet['eta'] <=  2.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta2p5    = len( [ jet for jet in jets if  2.0 < jet['eta'] <=  2.5 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta3      = len( [ jet for jet in jets if  2.5 < jet['eta'] <=  3.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEta4      = len( [ jet for jet in jets if  3.0 < jet['eta'] <=  4.0 and jet['pt']*jet['rawFactor']>25 ] )
    event.nJetRawEtaInf    = len( [ jet for jet in jets if  4.0 < jet['eta']         and jet['pt']*jet['rawFactor']>25 ] )

    jetsToUncorrect = [ jet for jet in jets if ( jet['pt'] < 75 and 2.7 < abs(jet['eta']) < 3.0 ) ]

    for jet in jetsToUncorrect:
        jetVector = ROOT.TVector3()
        jetVector.SetPtEtaPhi(jet['pt']*jet['rawFactor'], jet['eta'], jet['phi'])
        MET = MET - jetVector

    event.UpdatedMET_pt = MET.Pt()
    event.UpdatedMET_phi = MET.Phi()    

sequence += [getUpdatedMET]

#
# Text on the plots
#
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS #bf{#it{Preliminary}}' ), 
      (0.68, 0.95, '#bf{%3.1f fb{}^{-1} (13 TeV)}'% lumi_scale )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, lumi_scale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'data_to_data', args.plot_directory, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if mode == "all": 
        for s in plot.stack:
            s[0].texName = s[0].texName.replace('(2#mu)', '(all)')

      #if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      l  = len(plot.histos)
      #scaling = {2*i+1:2*i for i in range(l/2)} 
      scaling = {i:0 for i in range(1,5)}
      #scaling = {1:2, 2:2} #scale to 2018
      #ratio_histos = [ (2*i,2*i+1) for i in range(l/2) ] 
      ratio_histos = [(i,1) for i in [0]+range(2,5) ] #ratio wrt 2016
      #ratio_histps = [(1,0), (2,0)]
      plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio = {'yRange':(0.1,1.9), 'histos':ratio_histos, 'texY': '17(18) / 16'},
        logX = False, logY = log, sorting = True,
        yRange = (0.03, "auto") if log else (0.001, "auto"),
        scaling = scaling,
        legend = [ (0.20,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2],
        drawObjects = drawObjects( lumi_scale ),
        copyIndexPHP = True
      )

def get_nVtx_reweight( histo ):
    def get_histo_reweight( event, sample) :
        return histo.GetBinContent(sample.nVert_histo.FindBin( event.PV_npvsGood ))/sample.nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.PV_npvsGood ) )
    return get_histo_reweight

colors = [ROOT.kBlue, ROOT.kMagenta, ROOT.kGreen, ]

#
# Loop over channels
#
yields     = {}
allPlots   = {}
#allModes   = ['mumu','mue','ee']
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
    yields[mode] = {}
    if mode == "mumu":
        data_2016_sample            = DoubleMuon_Run2016 
        data_2016_sample.texName    = "data 2016 (2#mu)"
        data_2016_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])

        data_2017B_sample            = DoubleMuon_Run2017B 
        data_2017B_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2017B_sample.texName    = "data 2017 B (2#mu)"
        data_2017CDE_sample            = DoubleMuon_Run2017CDE
        data_2017CDE_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2017CDE_sample.texName    = "data 2017 CDE (2#mu)"
        data_2017F_sample            = DoubleMuon_Run2017F
        data_2017F_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2017F_sample.texName    = "data 2017 F (2#mu)"

        data_2018_sample            = DoubleMuon_Run2018
        data_2018_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2018_sample.texName    = "data 2018 (2#mu)"
        data_2017_samples           = [data_2017B_sample, data_2017CDE_sample, data_2017F_sample ]
        data_2018_samples           = [copy.deepcopy(data_2018_sample) for x in data_2017_samples]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    elif mode == "ee":
        data_2016_sample            = DoubleEG_Run2016
        data_2016_sample.texName    = "data 2016 (2e)"
        data_2016_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])

        data_2017B_sample            = DoubleEG_Run2017B 
        data_2017B_sample.texName    = "data 2017 B (2e)"
        data_2017B_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017CDE_sample            = DoubleEG_Run2017CDE
        data_2017CDE_sample.texName    = "data 2017 CDE (2e)"
        data_2017CDE_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017F_sample            = DoubleEG_Run2017F
        data_2017F_sample.texName    = "data 2017 F (2e)"
        data_2017F_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])

        data_2018_sample            = EGamma_Run2018
        data_2018_sample.texName    = "data 2018 (2e)"
        data_2018_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])

        data_2017_samples           = [data_2017B_sample, data_2017CDE_sample, data_2017F_sample]#, data_2017D_sample, DoubleEG_Run2017EF]
        data_2018_samples           = [copy.deepcopy(data_2018_sample) for x in data_2017_samples]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    elif mode == 'mue':
        data_2016_sample            = MuonEG_Run2016
        data_2016_sample.texName    = "data 2016 (1#mu, 1e)"
        data_2016_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL||HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL"])

        data_2017B_sample            = MuonEG_Run2017B 
        data_2017B_sample.texName    = "data 2017 B (1#mu, 1e)"
        data_2017B_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017CDE_sample            = MuonEG_Run2017CDE
        data_2017CDE_sample.texName    = "data 2017 CDE (1#mu, 1e)"
        data_2017CDE_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017F_sample            = MuonEG_Run2017F
        data_2017F_sample.texName    = "data 2017 F (1#mu, 1e)"
        data_2017F_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])

        data_2018_sample            = MuonEG_Run2018
        data_2018_sample.texName    = "data 2018 (1#mu, 1e)"
        data_2018_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017_samples           = [data_2017B_sample, data_2017CDE_sample, data_2017F_sample]
        data_2018_samples           = [copy.deepcopy(data_2018_sample) for x in data_2017_samples]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    else: raise ValueError    

    colors2017 = [ROOT.kGreen+1, ROOT.kYellow+1, ROOT.kCyan+1]
    for i_s, data_2017_sample in enumerate(data_2017_samples):
        data_2017_sample.addSelectionString([getFilterCut(isData=True, year=2017), getLeptonSelection(mode)])
        data_2017_sample.read_variables = ["event/I","run/I"]
        data_2017_sample.style          = styles.errorStyle(colors2017[i_s], markerStyle=21+i_s, width=2)
        lumi_2017_scale                 = data_2017_sample.lumi/1000

    colors2016 = [ROOT.kOrange+1]*3
    for i_s, data_2016_sample in enumerate(data_2016_samples):
        data_2016_sample.addSelectionString([getFilterCut(isData=True, year=2016), getLeptonSelection(mode)])
        data_2016_sample.read_variables = ["event/I","run/I"]
        data_2016_sample.style          = styles.lineStyle(colors2016[i_s], errors=True, width=2)
        lumi_2016_scale                 = data_2016_sample.lumi/1000

    colors2018 = [ROOT.kBlue+1]*3
    for i_s, data_2018_sample in enumerate(data_2018_samples):
        data_2018_sample.addSelectionString([getFilterCut(isData=True, year=2018), getLeptonSelection(mode)])
        data_2018_sample.read_variables = ["event/I","run/I"]
        data_2018_sample.style          = styles.errorStyle(colors2018[i_s], markerStyle=20, width=2)
        lumi_2018_scale                 = data_2018_sample.lumi/1000

    weight_ = lambda event, sample: event.weight
    stack_samples = []
    stack_samples.append( [data_2018_samples[0]] )
    stack_samples.append( [data_2016_samples[0]] )
    for i in range(len(data_2017_samples)):
        #stack_samples.append( [data_2016_samples[i]] )
        stack_samples.append( [data_2017_samples[i]] )
        #stack_samples.append( [data_2018_samples[i]] )

    stack = Stack( *stack_samples )

    if args.small:
        for sample in stack.samples:
            sample.reduceFiles( to = 3 )

    print len(data_2018_samples), len(data_2016_samples)

    reweight_binning = [3*i for i in range(10)]+[30,35,40,50,100]
    for i_s, data_2017_sample in enumerate(data_2017_samples):

        logger.info('nVert Histo for %s', data_2018_sample.name)
        data_2018_samples[i_s].nVert_histo     = data_2018_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2018_samples[i_s].nVert_histo.Scale(1./data_2018_samples[i_s].nVert_histo.Integral())
        
        logger.info('nVert Histo for %s', data_2017_sample.name)
        data_2017_sample.nVert_histo     = data_2017_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2017_sample.nVert_histo.Scale(1./data_2017_sample.nVert_histo.Integral())
    
        data_2016_sample = data_2016_samples[i_s]
        logger.info('nVert Histo for %s', data_2016_sample.name)
        data_2016_samples[i_s].nVert_histo     = data_2016_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2016_samples[i_s].nVert_histo.Scale(1./data_2016_samples[i_s].nVert_histo.Integral())

        #data_2016_sample.weight         = lambda event, sample: data_2017_samples[i_s].nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.nVert ))/sample.nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.nVert ) )
        data_2016_sample.weight = get_nVtx_reweight(data_2018_samples[i_s].nVert_histo)
        data_2017_sample.weight = get_nVtx_reweight(data_2018_samples[i_s].nVert_histo)

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin=None)

    plots = []
    
    plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + index,
      binning=[3, 0, 3],
    ))
    
    plots.append(Plot(
      name = 'PV_npvsGood', texX = 'number of good PVs', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
      binning=[80,0,80],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "MET_pt/F" ),
        binning=[400/20,0,400],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        texX = 'E_{T}^{miss} (raw) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "RawMET_pt/F" ),
        binning=[400/20,0,400],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(name = "UpdatedMET_pt",
        texX = 'E_{T}^{miss} (updated) (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = lambda event, sample: event.UpdatedMET_pt,
        binning=[400/20,0,400],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        texX = '#phi(E_{T}^{miss})', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "MET_phi/F" ),
        binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(
        texX = '#phi(E_{T}^{miss} (raw))', texY = 'Number of Events',
        attribute = TreeVariable.fromString( "RawMET_phi/F" ),
        binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(name = "UpdatedMET_phi",
        texX = '#phi(E_{T}^{miss} (updated)) (GeV)', texY = 'Number of Events',
        attribute = lambda event, sample: event.UpdatedMET_phi,
        binning=[10,-pi,pi],
    ))  
    
    plots.append(Plot(
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = TreeVariable.fromString( "dl_mass/F" ),
        binning=[30,0,300],
    ))

    plots.append(Plot(name = "Z_mass_EE",
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample: event.dl_mass if ( abs(event.l1_eta[0])>1.479 and abs(event.l2_eta[0])>1.479) else float('nan'),
        binning=[20,71,111],
    ))

    plots.append(Plot(name = "Z_mass_EB",
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample: event.dl_mass if ( ((abs(event.l1_eta[0])<1.479 and abs(event.l2_eta[0])>1.479) or (abs(event.l1_eta[0])>1.479 and abs(event.l2_eta[0])<1.479))) else float('nan'),
        binning=[20,71,111],
    ))

    plots.append(Plot(name = "Z_mass_BB",
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample: event.dl_mass if ( abs(event.l2_eta[0])<1.479 and abs(event.l2_eta[0])<1.479) else float('nan'),
        binning=[20,71,111],
    ))

    plots.append(Plot(
      texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
      attribute = TreeVariable.fromString('metSig/F'),
      binning= [30,0,30],
    ))
    
    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ),
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot( name = 'nJetEtaM4',
      texX = 'N_{jets}, #eta#leq -4.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaM4,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEtaM3',
      texX = 'N_{jets}, -4.0 <#eta#leq -3.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaM3,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEtaM2p5',
      texX = 'N_{jets}, -3.0 <#eta#leq -2.5', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaM2p5,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEtaM2',
      texX = 'N_{jets}, -2.5 <#eta#leq -2.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaM2,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEtaM1',
      texX = 'N_{jets}, -2.0 <#eta#leq -1.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaM1,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta0',
      texX = 'N_{jets}, -1.0 <#eta#leq 0.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta0,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta1',
      texX = 'N_{jets}, 0.0 <#eta#leq 1.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta1,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta2',
      texX = 'N_{jets}, 1.0 <#eta#leq 2.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta2,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta2p5',
      texX = 'N_{jets}, 2.0 <#eta#leq 2.5', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta2p5,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta3',
      texX = 'N_{jets}, 2.5 <#eta#leq 3.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta3,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEta4',
      texX = 'N_{jets}, 3.0 <#eta#leq 4.0', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEta4,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = 'nJetEtaInf',
      texX = 'N_{jets}, 4.0 <#eta', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJetEtaInf,
      binning=[8,-0.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "nBTagDeepCSV",
      texX = 'number of medium b-tags (deepCSV)', texY = 'Number of Events',
      attribute = TreeVariable.fromString('nBTag/I'),
      binning=[8,0,8],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaM4",
      texX = 'p_{T}(leading jet, #eta#leq -4.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaM4,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaM3",
      texX = 'p_{T}(leading jet, -4.0 <#eta#leq -3.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaM3,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaM2p5",
      texX = 'p_{T}(leading jet, -3.0 <#eta#leq -2.5) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaM2p5,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaM2",
      texX = 'p_{T}(leading jet, -2.5 <#eta#leq -2.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaM2,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaM1",
      texX = 'p_{T}(leading jet, -2.0 <#eta#leq -1.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaM1,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta0",
      texX = 'p_{T}(leading jet, -1.0 <#eta#leq 0.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta0,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta1",
      texX = 'p_{T}(leading jet, 0.0 <#eta#leq 1.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta1,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta2",
      texX = 'p_{T}(leading jet, 1.0 <#eta#leq 2.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta2,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta2p5",
      texX = 'p_{T}(leading jet, 2.0 <#eta#leq 2.5) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta2p5,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta3",
      texX = 'p_{T}(leading jet, 2.5 <#eta#leq 3.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta3,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_Eta4",
      texX = 'p_{T}(leading jet, 3.0 <#eta#leq 4.0) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_Eta4,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "jet_pt_EtaInf",
      texX = 'p_{T}(leading jet, 4.0 <#eta) (GeV)', texY = 'Number of Events',
      attribute = lambda event, sample: event.Jet_pt_EtaInf,
      binning=[30,0,300],
      addOverFlowBin='upper',
    ))



    #plots.append(Plot( name = "nBTagDeepCSV",
    #  texX = 'number of medium b-tags (DeepCSV)', texY = 'Number of Events',
    #  attribute = TreeVariable.fromString('nBTagDeepCSV/I'),
    #  binning=[8,0,8],
    #  addOverFlowBin='upper',
    #))

    plots.append(Plot(
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 25 GeV',
      attribute = TreeVariable.fromString( "ht/F" ),
      binning=[500/25,0,600],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot( name = "ht_zoom",
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 3 GeV',
      attribute = TreeVariable.fromString( "ht/F" ),
      binning=[50,0,150],
      addOverFlowBin='upper',
    ))
    
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
      texX = 'leading jet b-tag Disc. CSVv2', texY = 'Number of Events',
      name = 'jet1_CSVv2', attribute = lambda event, sample: event.JetGood_btagCSVV2[0],
      binning=[40,0,1],
    ))

    plots.append(Plot(
      texX = 'leading jet b-tag Disc. DeepCSV', texY = 'Number of Events',
      name = 'jet1_DeepCSV', attribute = lambda event, sample: event.JetGood_btagDeepB[0],
      binning=[40,0,1],
    ))
    
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
      texX = '2nd leading jet b-tag Disc. CSVv2', texY = 'Number of Events',
      name = 'jet2_CSVv2', attribute = lambda event, sample: event.JetGood_btagCSVV2[1],
      binning=[40,0,1],
    ))

    plots.append(Plot(
      texX = '2nd leading jet b-tag Disc. DeepCSV', texY = 'Number of Events',
      name = 'jet2_DeepCSV', attribute = lambda event, sample: event.JetGood_btagDeepB[1],
      binning=[40,0,1],
    ))

    plots.append(Plot( name = "l1_pt",
      texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
      attribute = lambda event, sample: event.l1_pt[0], 
      binning=[20,0,300],
    ))
  
    plots.append(Plot( name = "l1_dxy",
      texX = 'd_{xy}(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_dxy[0], 
      binning=[40,-0.2,0.2],
    ))

    plots.append(Plot( name = "l1_dz",
      texX = 'd_{z}(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_dz[0], 
      binning=[40,-0.2,0.2],
    ))
  
    plots.append(Plot( name = "l1_eta",
      texX = '#eta(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_eta[0], 
      binning=[30,-3,3],
    ))
  
    plots.append(Plot( name = "l1_phi",
      texX = '#phi(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_phi[0], 
      binning=[10,-pi,pi],
    ))
 
    #plots.append(Plot( name = "l1_etaSc",
    #  texX = '#etaSc(l_{1})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.lep_etaSc[0], 
    #  binning=[30,-3,3],
    #))

    plots.append(Plot( name = "l1_relIso03",
      texX = 'relIso03(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_relIso03[0], 
      binning=[30,0,1],
    ))

    #plots.append(Plot( name = "l1_sip3d",
    #  texX = 'sip3d(l_{1})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.l1_sip3d, 
    #  binning=[50,0,5],
    #))
 
    plots.append(Plot( name = "l2_pt",
      texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
      attribute = lambda event, sample: event.l2_pt[0], 
      binning=[20,0,300],
    ))
  
    plots.append(Plot( name = "l2_dxy",
      texX = 'd_{xy}(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_dxy[0], 
      binning=[40,-0.2,0.2],
    ))

    plots.append(Plot( name = "l2_dz",
      texX = 'd_{z}(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_dz[0], 
      binning=[40,-0.2,0.2],
    ))
  
    plots.append(Plot( name = "l2_eta",
      texX = '#eta(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_eta[0], 
      binning=[30,-3,3],
    ))
  
    plots.append(Plot( name = "l2_phi",
      texX = '#phi(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_phi[0], 
      binning=[10,-pi,pi],
    ))

    #plots.append(Plot( name = "l2_etaSc",
    #  texX = '#etaSc(l_{2})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.lep_etaSc[1], 
    #  binning=[30,-3,3],
    #))

    plots.append(Plot( name = "l2_relIso03",
      texX = 'relIso03(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_relIso03[0], 
      binning=[30,0,1],
    ))

    #plots.append(Plot( name = "l2_sip3d",
    #  texX = 'sip3d(l_{2})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.l2_sip3d, 
    #  binning=[50,0,5],
    #))
 
    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[0]), 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[0] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosMetJet2phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[1] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet2phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[1] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plotting.fill(plots, read_variables = read_variables, sequence = sequence)

    # Get normalization yields from yield histogram
    for plot in plots:
      if plot.name == "yield":
        for i, l in enumerate(plot.histos):
          for j, h in enumerate(l):
            yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
            h.GetXaxis().SetBinLabel(1, "#mu#mu")
            h.GetXaxis().SetBinLabel(2, "#mue")
            h.GetXaxis().SetBinLabel(3, "ee")

    drawPlots(plots, mode, lumi_2018_scale)
    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["comb1","comb2","all"]:
    yields[mode] = {}
    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum(yields[c][y] for c in allModes)
        except: yields[mode][y] = 0
    
    for plot in allPlots['mumu']:
        if mode=="comb1":
            tmp = allPlots['mue'] if 'mue' in allModes else []
        elif mode=="comb2":
            tmp = allPlots['ee']
        for plot2 in (p for p in tmp if p.name == plot.name):
            for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                    if i==k:
                        j.Add(l)
    
    if mode == "all": drawPlots(allPlots['mumu'], mode, lumi_2018_scale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )

