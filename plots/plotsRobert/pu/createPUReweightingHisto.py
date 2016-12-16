import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

import os
import pickle

from RootTools.core.standard import *
from StopsDilepton.tools.user import *

logLevel = "INFO"
# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(logLevel, logFile = None )


#preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = '(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1 || isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 )'
mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadron&&Flag_badMuon"
dataFilterCut = mcFilterCut+"&&weight>0"
prefix="dilepton_allZ_isOS_5300pb"

maxN = -1
prefix = prefix+"_maxN_%i_"%maxN if maxN>0 else prefix
#load all the samples
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *

mc   = Sample.combine("mc", [ TTJets_Lep, singleTop, diBoson, DY_HT_LO, TTZ, TTW, triBoson ] )
mc.setSelectionString( "&&".join([mcFilterCut, preselection]) )

if maxN>0:
    mc.reduceFiles(to=maxN)
    DoubleEG_Run2016B     .reduceFiles(to=maxN)
    DoubleMuon_Run2016B   .reduceFiles(to=maxN)
    MuonEG_Run2016B       .reduceFiles(to=maxN)

#Get true PU from data
from StopsDilepton.tools.helpers import getObjFromFile
nTrueInt_data_XSecVUp = getObjFromFile("$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/PU_2016_5300_XSecVUp.root", "pileup")
nTrueInt_data_XSecUp = getObjFromFile("$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/PU_2016_5300_XSecUp.root", "pileup")
nTrueInt_data_XSecVDown = getObjFromFile("$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/PU_2016_5300_XSecVDown.root", "pileup")
nTrueInt_data_XSecDown = getObjFromFile("$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/PU_2016_5300_XSecDown.root", "pileup")
nTrueInt_data_XSecCentral = getObjFromFile("$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/PU_2016_5300_XSecCentral.root", "pileup")

nTrueInt_data_XSecDown.Scale(nTrueInt_data_XSecCentral.Integral()/nTrueInt_data_XSecDown.Integral())
nTrueInt_data_XSecVDown.Scale(nTrueInt_data_XSecCentral.Integral()/nTrueInt_data_XSecVDown.Integral())
nTrueInt_data_XSecUp.Scale(nTrueInt_data_XSecCentral.Integral()/nTrueInt_data_XSecUp.Integral())
nTrueInt_data_XSecVUp.Scale(nTrueInt_data_XSecCentral.Integral()/nTrueInt_data_XSecVUp.Integral())

#Get true PU from MC
h_nTrueInt_mc = mc.get1DHistoFromDraw( "nTrueInt", binning = [40,0,40], selectionString = "(1)", weightString = "weight" )
h_nTrueInt_mc.Scale(nTrueInt_data_XSecCentral.Integral()/h_nTrueInt_mc.Integral())

nTrueInt_data_XSecVUp.style = styles.lineStyle(ROOT.kMagenta)
nTrueInt_data_XSecVDown.style = styles.lineStyle(ROOT.kMagenta)
nTrueInt_data_XSecUp.style = styles.lineStyle(ROOT.kRed)
nTrueInt_data_XSecDown.style = styles.lineStyle(ROOT.kRed)
h_nTrueInt_mc.style = styles.lineStyle(ROOT.kBlue)

plotting.draw(
    Plot.fromHisto(name = prefix+"nTrueInt_mc", histos = [ [h_nTrueInt_mc], [nTrueInt_data_XSecCentral], [nTrueInt_data_XSecDown], [nTrueInt_data_XSecUp], [nTrueInt_data_XSecVUp], [nTrueInt_data_XSecVDown] ], texX = "Number of interactions", texY = "Number of Events"),
    plot_directory = '/afs/hephy.at/user/r/rschoefbeck/www/pngPU/', #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.0003, "auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

#Apply difference in true PU in data as uncertainty on MC (but don't do the true PU reweighting)
ratio_DownToCentral = nTrueInt_data_XSecDown.Clone()
ratio_DownToCentral.Divide(nTrueInt_data_XSecCentral)
ratio_UpToCentral = nTrueInt_data_XSecUp.Clone()
ratio_UpToCentral.Divide(nTrueInt_data_XSecCentral)
ratio_VDownToCentral = nTrueInt_data_XSecVDown.Clone()
ratio_VDownToCentral.Divide(nTrueInt_data_XSecCentral)
ratio_VUpToCentral = nTrueInt_data_XSecVUp.Clone()
ratio_VUpToCentral.Divide(nTrueInt_data_XSecCentral)

plotting.draw(
    Plot.fromHisto(name = prefix+"nTrueInt_ratio", histos = [ [ratio_UpToCentral], [ratio_DownToCentral], [ratio_VUpToCentral], [ratio_VDownToCentral] ], texX = "Number of interactions", texY = "Number of Events"),
    plot_directory = '/afs/hephy.at/user/r/rschoefbeck/www/pngPU/', #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.0003, "auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

#Now get the reco-vertex shapes with the x-sec uncertainty applied
reader = mc.treeReader( \
    variables = map( TreeVariable.fromString, ["nTrueInt/F","nVert/I","weight/F"])
    )
reader.activateAllBranches()
event_list = mc.getEventList( mc.selectionString )
reader.setEventList( event_list )

reader.start()

h_nVert           = ROOT.TH1D("nVert", "nVert", 50,0,50)
h_nVert_rwUp      = ROOT.TH1D("nVert_rwUp", "nVert_rwUp", 50,0,50)
h_nVert_rwDown    = ROOT.TH1D("nVert_rwDown", "nVert_rwDown", 50,0,50)
h_nVert_rwUp.style = styles.lineStyle(ROOT.kRed)
h_nVert_rwDown.style = styles.lineStyle(ROOT.kRed)
h_nVert_rwVUp      = ROOT.TH1D("nVert_rwVUp", "nVert_rwVUp", 50,0,50)
h_nVert_rwVDown    = ROOT.TH1D("nVert_rwVDown", "nVert_rwVDown", 50,0,50)
h_nVert_rwVUp.style = styles.lineStyle(ROOT.kBlue)
h_nVert_rwVDown.style = styles.lineStyle(ROOT.kBlue)

while reader.run():
    if reader.event.nTrueInt>39:reader.event.nTrueInt=39
    h_nVert.Fill(reader.event.nVert, reader.event.weight) 
    ib = ratio_UpToCentral.FindBin(reader.event.nTrueInt)
    h_nVert_rwUp.Fill(reader.event.nVert, reader.event.weight*ratio_UpToCentral.GetBinContent(ib)) 
    h_nVert_rwDown.Fill(reader.event.nVert, reader.event.weight*ratio_DownToCentral.GetBinContent(ib)) 
    h_nVert_rwVUp.Fill(reader.event.nVert, reader.event.weight*ratio_VUpToCentral.GetBinContent(ib)) 
    h_nVert_rwVDown.Fill(reader.event.nVert, reader.event.weight*ratio_VDownToCentral.GetBinContent(ib)) 

h_nVert_rwUp.Scale(h_nVert.Integral()/h_nVert_rwUp.Integral())
h_nVert_rwDown.Scale(h_nVert.Integral()/h_nVert_rwDown.Integral())
h_nVert_rwVUp.Scale(h_nVert.Integral()/h_nVert_rwVUp.Integral())
h_nVert_rwVDown.Scale(h_nVert.Integral()/h_nVert_rwVDown.Integral())

plotting.draw(
    Plot.fromHisto(name = prefix+"nVtx_rw", histos = [ [h_nVert], [h_nVert_rwUp], [h_nVert_rwDown], [h_nVert_rwVDown], [h_nVert_rwVUp] ], texX = "Number of vertices", texY = "Number of Events"),
    plot_directory = '/afs/hephy.at/user/r/rschoefbeck/www/pngPU/', #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.3, "auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

#Loading Data
DoubleEG_Run2016B     .setSelectionString( "&&".join([dataFilterCut, "isEE==1&&nGoodMuons==0&&nGoodElectrons==2" ]) ) 
DoubleMuon_Run2016B   .setSelectionString( "&&".join([dataFilterCut, "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0" ]) ) 
MuonEG_Run2016B       .setSelectionString( "&&".join([dataFilterCut, "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1" ]) )

#h_nVert = mc.get1DHistoFromDraw( "nVert", binning = [50,0,50], selectionString = "(1)", weightString = "weight" )
h_EE = DoubleEG_Run2016B.get1DHistoFromDraw( "nVert", binning = [50,0,50], selectionString = "(1)", weightString = "weight" )
h_EMu = MuonEG_Run2016B.get1DHistoFromDraw( "nVert", binning = [50,0,50], selectionString = "(1)", weightString = "weight" )
h_MuMu = DoubleMuon_Run2016B.get1DHistoFromDraw( "nVert", binning = [50,0,50], selectionString = "(1)", weightString = "weight" )

h_data = h_EE.Clone()
h_event.Add(h_EMu)
h_event.Add(h_MuMu)
h_nVert.Scale(h_event.Integral()/h_nVert.Integral())

plotting.draw(
    Plot.fromHisto(name = prefix+"nVtx", histos = [[h_nVert], [h_data] ], texX = "Number of vertices", texY = "Number of Events"),
    plot_directory = '/afs/hephy.at/user/r/rschoefbeck/www/pngPU/', #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.3, "auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

reweightingHisto = h_event.Clone()
reweightingHisto.Divide(h_nVert)

reweightingHisto_Up = h_event.Clone()
h_nVert_rwUp.Scale(h_event.Integral()/h_nVert_rwUp.Integral())
reweightingHisto_Up.Divide(h_nVert_rwUp)
reweightingHisto_Up.style = styles.lineStyle(ROOT.kRed)

reweightingHisto_Down = h_event.Clone()
h_nVert_rwDown.Scale(h_event.Integral()/h_nVert_rwDown.Integral())
reweightingHisto_Down.Divide(h_nVert_rwDown)
reweightingHisto_Down.style = styles.lineStyle(ROOT.kRed)

reweightingHisto_VUp = h_event.Clone()
h_nVert_rwVUp.Scale(h_event.Integral()/h_nVert_rwVUp.Integral())
reweightingHisto_VUp.Divide(h_nVert_rwVUp)
reweightingHisto_VUp.style = styles.lineStyle(ROOT.kBlue)

reweightingHisto_VDown = h_event.Clone()
h_nVert_rwVDown.Scale(h_event.Integral()/h_nVert_rwVDown.Integral())
reweightingHisto_VDown.Divide(h_nVert_rwVDown)
reweightingHisto_VDown.style = styles.lineStyle(ROOT.kBlue)

plotting.draw(
    Plot.fromHisto(name =prefix+"_reweighting", histos = [ [reweightingHisto], [reweightingHisto_Up], [reweightingHisto_Down], [reweightingHisto_VDown], [reweightingHisto_VUp] ], texX = "Number of vertices", texY = "Number of Events"),
    plot_directory = '/afs/hephy.at/user/r/rschoefbeck/www/pngPU/', #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.003, "auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

pickle.dump({'rw':reweightingHisto, 'up':reweightingHisto_Up, 'down':reweightingHisto_Down, 'vup':reweightingHisto_VUp, 'vdown':reweightingHisto_VDown}, file("/afs/hephy.at/data/rschoefbeck01/StopsDilepton/puReweightingData2016/"+prefix+".pkl", "w") )
