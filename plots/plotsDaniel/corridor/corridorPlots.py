import ROOT

from RootTools.core.standard import *
from Samples.nanoAOD.Autumn18_private_legacy_v1 import *
from StopsDilepton.tools.user   import plot_directory

## FullSim samples
FullSim_T2tt_175_1      = Sample.fromDirectory("FullSim_T2tt_175_1",    "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_175_mLSP_1/")
FullSim_T2tt_250_50     = Sample.fromDirectory("FullSim_T2tt_250_50",   "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_250_mLSP_50/")
FullSim_T2tt_250_75     = Sample.fromDirectory("FullSim_T2tt_250_75",   "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_250_mLSP_75/")
FullSim_T2tt_250_100    = Sample.fromDirectory("FullSim_T2tt_250_100",  "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_250_mLSP_100/")

## FastSim inclusive samples (not used here)
FastSim_T2tt_175_1      = Sample.fromDirectory("FastSim_T2tt_175_1",    "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_175_0/")
FastSim_T2tt_250_50     = Sample.fromDirectory("FastSim_T2tt_250_50",   "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_250_50/")
FastSim_T2tt_250_75     = Sample.fromDirectory("FastSim_T2tt_250_75",   "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_250_75/")
FastSim_T2tt_250_100    = Sample.fromDirectory("FastSim_T2tt_250_100",  "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_250_100/")

# FastSim dilep samples
FastSim_T2tt_175_1_dilep    = Sample.fromFiles("FastSim_T2tt_175_1_dilep",   ["/afs/hephy.at/data/cms07/nanoTuples/stops_2018_nano_v0p20/dilep/T2tt/T2tt_175_0.root"])
FastSim_T2tt_250_50_dilep   = Sample.fromFiles("FastSim_T2tt_250_50_dilep",  ["/afs/hephy.at/data/cms07/nanoTuples/stops_2018_nano_v0p20/dilep/T2tt/T2tt_250_50.root"])
FastSim_T2tt_250_75_dilep   = Sample.fromFiles("FastSim_T2tt_250_75_dilep",  ["/afs/hephy.at/data/cms07/nanoTuples/stops_2018_nano_v0p20/dilep/T2tt/T2tt_250_75.root"])
FastSim_T2tt_250_100_dilep  = Sample.fromFiles("FastSim_T2tt_250_100_dilep", ["/afs/hephy.at/data/cms07/nanoTuples/stops_2018_nano_v0p20/dilep/T2tt/T2tt_250_100.root"])

# sample selection
massPoint = 'T2tt_250_100'
fastSim = FastSim_T2tt_250_100_dilep
fullSim = FullSim_T2tt_250_100

# only need a loose preslection, it's MC anyway. use MuMu channel because that works well for full/fast
presel  = '(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0)'
presel += '&&(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2'
presel += '&&dl_mass>=20&&l1_pt>30&&nJetGood>=2&&nBTag>=1'

## plots of MET Significance, MT2ll and MT2blbl
h_mt2ll_reco    = fastSim.get1DHistoFromDraw('dl_mt2ll',       [10,0,200], selectionString=presel, addOverFlowBin='upper')
h_mt2ll_gen     = fastSim.get1DHistoFromDraw('dl_mt2ll_gen',   [10,0,200], selectionString=presel, addOverFlowBin='upper')
h_mt2ll_full    = fullSim.get1DHistoFromDraw('dl_mt2ll',       [10,0,200], selectionString=presel, addOverFlowBin='upper')

h_sig_reco    = fastSim.get1DHistoFromDraw('MET_significance',      [10,0,60], selectionString=presel, addOverFlowBin='upper')
h_sig_gen     = fastSim.get1DHistoFromDraw('GenMET_significance',   [10,0,60], selectionString=presel, addOverFlowBin='upper')
h_sig_full    = fullSim.get1DHistoFromDraw('MET_significance',      [10,0,60], selectionString=presel, addOverFlowBin='upper')

## styles
h_mt2ll_reco.legendText = 'FastSim Reco'
h_mt2ll_gen.legendText  = 'FastSim GenMET'
h_mt2ll_full.legendText = 'FullSim Reco'
h_mt2ll_reco.style      = styles.lineStyle(ROOT.kGreen+1,   width=2, errors=True)
h_mt2ll_gen.style       = styles.lineStyle(ROOT.kRed+1,     width=2, errors=True)
h_mt2ll_full.style      = styles.lineStyle(ROOT.kBlue+1,    width=2, errors=True)

h_sig_reco.legendText = 'FastSim Reco'
h_sig_gen.legendText  = 'FastSim GenMET'
h_sig_full.legendText = 'FullSim Reco'
h_sig_reco.style      = styles.lineStyle(ROOT.kGreen+1,   width=2, errors=True)
h_sig_gen.style       = styles.lineStyle(ROOT.kRed+1,     width=2, errors=True)
h_sig_full.style      = styles.lineStyle(ROOT.kBlue+1,    width=2, errors=True)


plot_path = plot_directory + '/corridor/recoGen/'

plotting.draw(
    Plot.fromHisto(name = massPoint+'_mt2ll', histos = [ [h_mt2ll_reco], [h_mt2ll_gen], [h_mt2ll_full] ], texX = "M_{T2}(ll) (GeV)", texY = "a.u."),
    plot_directory = plot_path,
    logX = False, logY = True, sorting = False,
    scaling = {1:0, 2:0},
    ratio = {'histos': [(1, 0), (2, 0)], 'texY': 'x / FS reco'},
)

plotting.draw(
    Plot.fromHisto(name = massPoint+'_MET_significance', histos = [ [h_sig_reco], [h_sig_gen], [h_sig_full] ], texX = "S", texY = "a.u."),
    plot_directory = plot_path,
    logX = False, logY = True, sorting = False,
    scaling = {1:0, 2:0},
    ratio = {'histos': [(1, 0), (2, 0)], 'texY': 'x / FS reco'},
    copyIndexPHP = True,
)
