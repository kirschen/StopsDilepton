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

# for smearing
import numpy as np

from math                         import sqrt, cos, sin, pi, atan2
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
argParser.add_argument('--plot_directory',     action='store',      default='SpecialData_HEM_v1')
argParser.add_argument('--selection',          action='store',      default='lepSel-OS-looseLeptonVeto-njet2p-relIso0.12-mll20-badJetSrEVeto')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# for mt2ll
from StopsDilepton.tools.mt2Calculator              import mt2Calculator
mt2Calc = mt2Calculator()

if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory
#

data_directory           = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
postProcessing_directory = "stops_2018_nano_v3/dilep/"

dirs = {}
dirs['MuonEG']                  = ['MuonEG_Run2018B_26Sep2018']
dirs['MuonEG_HEM']              = ['MuonEG_Run2018B_26Sep2018_HEM']
dirs['MuonEG_HEMmitigation']    = ['MuonEG_Run2018B_26Sep2018_HEMmitigation']

dirs['EGamma']                  = ['EGamma_Run2018B_26Sep2018']
dirs['EGamma_HEM']              = ['EGamma_Run2018B_26Sep2018_HEM']
dirs['EGamma_HEMmitigation']    = ['EGamma_Run2018B_26Sep2018_HEMmitigation']

dirs['DoubleMuon']                  = ['DoubleMuon_Run2018B_26Sep2018']
dirs['DoubleMuon_HEM']              = ['DoubleMuon_Run2018B_26Sep2018_HEM']
dirs['DoubleMuon_HEMmitigation']    = ['DoubleMuon_Run2018B_26Sep2018_HEMmitigation']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}
MuonEG   = Sample.fromDirectory(name="MuonEG", treeName="Events", isData=True, color=ROOT.kBlack, texName="MuonEG", directory=directories['MuonEG'])
MuonEG_HEM   = Sample.fromDirectory(name="MuonEG_HEM", treeName="Events", isData=True, color=ROOT.kBlack, texName="MuonEG HEM", directory=directories['MuonEG_HEM'])
MuonEG_HEMmitigation   = Sample.fromDirectory(name="MuonEG_HEMmitigation", treeName="Events", isData=True, color=ROOT.kBlack, texName="MuonEG HEM mit.", directory=directories['MuonEG_HEMmitigation'])

EGamma   = Sample.fromDirectory(name="EGamma", treeName="Events", isData=True, color=ROOT.kBlack, texName="EGamma", directory=directories['EGamma'])
EGamma_HEM   = Sample.fromDirectory(name="EGamma_HEM", treeName="Events", isData=True, color=ROOT.kBlack, texName="EGamma HEM", directory=directories['EGamma_HEM'])
EGamma_HEMmitigation   = Sample.fromDirectory(name="EGamma_HEMmitigation", treeName="Events", isData=True, color=ROOT.kBlack, texName="EGamma HEM mit.", directory=directories['EGamma_HEMmitigation'])

DoubleMuon   = Sample.fromDirectory(name="DoubleMuon", treeName="Events", isData=True, color=ROOT.kBlack, texName="DoubleMuon", directory=directories['DoubleMuon'])
DoubleMuon_HEM   = Sample.fromDirectory(name="DoubleMuon_HEM", treeName="Events", isData=True, color=ROOT.kBlack, texName="DoubleMuon HEM", directory=directories['DoubleMuon_HEM'])
DoubleMuon_HEMmitigation   = Sample.fromDirectory(name="DoubleMuon_HEMmitigation", treeName="Events", isData=True, color=ROOT.kBlack, texName="DoubleMuon HEM mit.", directory=directories['DoubleMuon_HEMmitigation'])

data_directory           = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
postProcessing_directory = "stops_HEM_nano_v3/dilep/"

dirs = {}
dirs['TTLep_100X_comb']             = ['TTLep_100X']
dirs['TTLep_100X_HEM_ext1_comb']    = ['TTLep_100X_HEM_ext1']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}
TTLep_100X_comb             = Sample.fromDirectory(name="TTLep_100X_comb", treeName="Events", isData=True, color=ROOT.kBlack, texName="t#bar{t}+jets", directory=directories['TTLep_100X_comb'])
TTLep_100X_HEM_ext1_comb    = Sample.fromDirectory(name="TTLep_100X_HEM_ext1_comb", treeName="Events", isData=True, color=ROOT.kBlack, texName="t#bar{t}+jets (HEM)", directory=directories['TTLep_100X_HEM_ext1_comb'])

def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0"
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2"
  elif mode=='all':  return "nGoodMuons+nGoodElectrons==2"


read_variables =    ["weight/F", "run/I",
                    "JetGood[pt/F,eta/F,phi/F,btagCSVV2/F,btagDeepB/F,rawFactor/F]", "nJetGood/I",
                    "Jet[pt/F,eta/F,phi/F,btagCSVV2/F,btagDeepB/F,rawFactor/F]", "nJet/I",
                    "l1[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "l2[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "MET_pt/F", "MET_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I",
                    "RawMET_pt/F", "RawMET_phi/F",
                    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ/I",
                    ]

variables = map( TreeVariable.fromString, ["run/I", "event/I", "MET_pt/F", "MET_phi/F", "MET_sumEt/F", "l1_pt/F", "l1_eta/F", "l1_phi/F", "l2_pt/F", "l2_eta/F", "l2_phi/F"])

sequence = []

def getMT2ll( event, sample ):
    l1 = ROOT.TLorentzVector()
    l2 = ROOT.TLorentzVector()
    l1.SetPtEtaPhiM(event.l1_pt, event.l1_eta, event.l1_phi, 0 )
    l2.SetPtEtaPhiM(event.l2_pt, event.l2_eta, event.l2_phi, 0 )
    mt2Calc.setLeptons(l1.Pt(), l1.Eta(), l1.Phi(), l2.Pt(), l2.Eta(), l2.Phi())

    met         = ROOT.TLorentzVector()
    met.SetPtEtaPhiM( event.MET_pt, 0, event.MET_phi, 0)
    met_shift   = ROOT.TLorentzVector()
    #met_shift.SetPtEtaPhiM( max(1, event.MET_sumEt*0.001), 0, -1.15, 0)
    met_shift.SetPtEtaPhiM( max(1, event.MET_sumEt*0.0015), 0, -1.15, 0)
    #met_shift.SetPtEtaPhiM( max(2.0, event.MET_sumEt*0.0025), 0, -1.15, 0)

    newMet = met - met_shift

    mt2Calc.setMet(newMet.Pt(), newMet.Phi())
    event.dl_mt2ll_shifted = mt2Calc.mt2ll()
    event.MET_phi_corr = newMet.Phi()

sequence += [ getMT2ll ]

colors = [ROOT.kBlue, ROOT.kMagenta, ROOT.kGreen, ]

#
# Loop over channels
#

selection = cutInterpreter.cutString("lepSel-OS-looseLeptonVeto-njet2p-relIso0.12-mll20-offZ-HEMJetVeto")

sample_nom = DoubleMuon
sample_HEM = DoubleMuon_HEM

#sample_nom = TTLep_100X_comb
#sample_HEM = TTLep_100X_HEM_ext1_comb


sample_nom.setSelectionString(selection)
sample_HEM.setSelectionString(selection)

histo_mt2ll_nom = sample_nom.get1DHistoFromDraw("dl_mt2ll", [20,0,200], selectionString=selection, weightString='(1)')
histo_metphi_nom = sample_nom.get1DHistoFromDraw("MET_phi", [16,-3.2,3.2], selectionString=selection, weightString='(1)')

histo_mt2ll_HEM = sample_HEM.get1DHistoFromDraw("dl_mt2ll", [20,0,200], selectionString=selection, weightString='(1)')
histo_metphi_HEM = sample_HEM.get1DHistoFromDraw("MET_phi", [16,-3.2,3.2], selectionString=selection, weightString='(1)')

reader = sample_HEM.treeReader(variables=variables, sequence=sequence)
reader.start()

histo_mt2ll_HEM_corr = ROOT.TH1F("histo_mt2ll_HEM_corr", "", 20,0,200)
histo_metphi_HEM_corr = ROOT.TH1F("histo_metphi_HEM_corr", "", 16,-3.2,3.2)

while reader.run():
    r = reader.event
    histo_metphi_HEM_corr.Fill(r.MET_phi_corr)
    histo_mt2ll_HEM_corr.Fill(r.dl_mt2ll_shifted)


histo_mt2ll_nom.style         = styles.lineStyle( ROOT.kGreen+1, width=2)
histo_mt2ll_HEM.style         = styles.errorStyle( ROOT.kRed+1, markerStyle=23 )
histo_mt2ll_HEM_corr.style    = styles.errorStyle( ROOT.kBlue+1, markerStyle=22 )

histo_mt2ll_nom.legendText        = "nominal"
histo_mt2ll_HEM.legendText        = "HEM"
histo_mt2ll_HEM_corr.legendText   = "HEM (shifted)"


histo_metphi_nom.style         = styles.lineStyle( ROOT.kGreen+1, width=2 )
histo_metphi_HEM.style         = styles.errorStyle( ROOT.kRed+1, markerStyle=23 )
histo_metphi_HEM_corr.style    = styles.errorStyle( ROOT.kBlue+1, markerStyle=22 )

histo_metphi_nom.legendText        = "nominal"
histo_metphi_HEM.legendText        = "HEM"
histo_metphi_HEM_corr.legendText   = "HEM (shifted)"

def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      (0.75, 0.95, ' (13 TeV)' )
    ]
    return [tex.DrawLatex(*l) for l in lines]

plots_mt2ll = [[histo_mt2ll_nom], [histo_mt2ll_HEM], [histo_mt2ll_HEM_corr]]
plots_metphi = [[histo_metphi_nom], [histo_metphi_HEM], [histo_metphi_HEM_corr]]

scaling = {1:0, 2:0}

plotting.draw(
    Plot.fromHisto("mt2ll",
                plots_mt2ll,
                texX = "MT2ll"
            ),
    plot_directory = "/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/HEM_correction/",
    logX = False, logY = True, sorting = False, 
    drawObjects = drawObjects(),
    ratio = {'histos':[(2,0),(1,0)]},
    scaling = scaling,
    copyIndexPHP = True
)

plotting.draw(
    Plot.fromHisto("MET_phi",
                plots_metphi,
                texX = "MET phi"
            ),
    plot_directory = "/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/HEM_correction/",
    logX = False, logY = True, sorting = False,
    drawObjects = drawObjects(),
    ratio = {'histos':[(2,0),(1,0)]},
    scaling = scaling,
    copyIndexPHP = True
)

