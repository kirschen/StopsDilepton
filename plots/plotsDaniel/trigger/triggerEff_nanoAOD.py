#!/usr/bin/env python
import os, sys
import ROOT
import array

ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from StopsDilepton.tools.triggerSelector import *

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',             nargs='?',      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],      default='INFO',      help="Log level for logging")
argParser.add_argument('--small',               action='store_true',        help='Small?')
argParser.add_argument('--plot_directory',      default='trigger_nanoAOD',  type=str,    action='store')
argParser.add_argument('--mode',                default='doubleMu',            action='store',    choices=['doubleMu', 'doubleEle',  'muEle'])
argParser.add_argument('--year',                default=2016,               action='store')
args = argParser.parse_args()

year = int(args.year)

class TriggerAnalysis(Module):
    def __init__(self, probeTriggers):
        self.writeHistFile = True
        self.probeTriggers = probeTriggers

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        pt_thresholds = range(0,30,2)+range(30,50,5)+range(50,210,10)
        self.h_passEvents   = ROOT.TH1F("pass","pass", len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_totalEvents  = ROOT.TH1F("total","total", len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_MET_pt       = ROOT.TH1F("MET", "MET", 50, 0, 1000)
        self.h_HT           = ROOT.TH1F("HT", "HT", 50, 0, 1000)
        self.addObject(self.h_passEvents )
        self.addObject(self.h_totalEvents )
        self.addObject(self.h_MET_pt )
        self.addObject(self.h_HT )


    def muonSelector(self, muon):
        return abs(muon.eta)<2.4 and muon.pfRelIso03_all < 0.120 and muon.sip3d < 4.0 and abs(muon.dxy) < 0.05 and abs(muon.dz) < 0.1 and muon.mediumId > 0

    def passTriggers(self, event):
        for trigger, lower, upper in self.probeTriggers:
            if event.run >= lower and (event.run < upper or upper < 0):
                if getattr(event, trigger) > 0: return True

    def analyze(self, event):
        electrons   = Collection(event, "Electron")
        muons       = Collection(event, "Muon")
        jets        = Collection(event, "Jet")

        nGoodMuons  = 0
        leadingPt   = 0
        for muon in muons:
            if self.muonSelector(muon):
                muon.goodMuon = 1
                nGoodMuons += 1
                if muon.pt > leadingPt: leadingPt = muon.pt
            else:
                muon.goodMuon = 0

        ht = 0.
        for jet in jets:
            if jet.pt>30 and abs(jet.eta)<2.4 and jet.jetId>0:
                ht += jet.pt

        if nGoodMuons > 1:
            self.h_totalEvents.Fill(leadingPt)
            if self.passTriggers(event):
                self.h_passEvents.Fill(leadingPt)

            self.h_MET_pt.Fill(event.MET_pt)
            self.h_HT.Fill(ht)

        return True


    def endJob(self):
        self.eff    = ROOT.TEfficiency(self.h_passEvents, self.h_totalEvents)
        self.addObject(self.eff)


if year == 2016:

    tag_triggers  = ['HLT_MET200','HLT_MET250', 'HLT_MET300', 'HLT_MET600', 'HLT_MET700','HLT_PFMET300','HLT_PFMET400','HLT_PFMET500','HLT_PFMET600','HLT_PFMET90_PFMHT90_IDTight','HLT_PFMET100_PFMHT100_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight']
    tag_triggers += ['HLT_HT200','HLT_HT275','HLT_HT325','HLT_HT425','HLT_HT575','HLT_HT410to430','HLT_HT430to450','HLT_HT450to470','HLT_HT470to500','HLT_HT500to550','HLT_HT550to650','HLT_HT650','HLT_PFHT300_PFMET100','HLT_PFHT300_PFMET110','HLT_DiPFJetAve15_HFJEC','HLT_DiPFJetAve25_HFJEC','HLT_DiPFJetAve35_HFJEC','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500']
    tag_triggers += ['HLT_AK8PFJet360_TrimMass30','HLT_AK8PFHT700_TrimR0p1PT0p03Mass50','HLT_AK8PFHT650_TrimR0p1PT0p03Mass50','HLT_AK8PFHT600_TrimR0p1PT0p03Mass50_BTagCSV_p20','HLT_PFHT550_4JetPt50','HLT_PFHT650_4JetPt50','HLT_PFHT750_4JetPt50','HLT_PFJet15_NoCaloMatched','HLT_PFJet25_NoCaloMatched','HLT_DiPFJet15_NoCaloMatched','HLT_DiPFJet25_NoCaloMatched','HLT_DiPFJet15_FBEta3_NoCaloMatched']
    tag_triggers += ['HLT_DiPFJet25_FBEta3_NoCaloMatched','HLT_DiPFJetAve40','HLT_DiPFJetAve60','HLT_DiPFJetAve80','HLT_DiPFJetAve140','HLT_DiPFJetAve200','HLT_DiPFJetAve260','HLT_DiPFJetAve320','HLT_DiPFJetAve400','HLT_DiPFJetAve500']
    tag_triggers += ['HLT_DiCentralPFJet55_PFMET110','HLT_PFHT125','HLT_PFHT200','HLT_PFHT250','HLT_PFHT300','HLT_PFHT350','HLT_PFHT400','HLT_PFHT475','HLT_PFHT600','HLT_PFHT650','HLT_PFHT800','HLT_PFHT900']
    tag_triggers += ['HLT_AK8DiPFJet280_200_TrimMass30','HLT_AK8DiPFJet250_200_TrimMass30','HLT_PFHT400_SixJet30','HLT_PFHT450_SixJet40','HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_HT2000','HLT_HT2500']

elif year == 2017:

    from Samples.nanoAOD.Run2017_14Dec2018 import *
    data_samples = MET_Run2017
    #data_samples = JetHT_Run2017
    
    tag_triggers  = ['HLT_PFHT500_PFMET100_PFMHT100_IDTight','HLT_PFHT500_PFMET110_PFMHT110_IDTight','HLT_PFHT700_PFMET85_PFMHT85_IDTight','HLT_PFHT700_PFMET95_PFMHT95_IDTight','HLT_PFHT800_PFMET75_PFMHT75_IDTight','HLT_PFHT800_PFMET85_PFMHT85_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight']
    tag_triggers += ['HLT_PFHT430', 'HLT_PFHT510', 'HLT_PFHT590', 'HLT_PFHT680', 'HLT_PFHT780', 'HLT_PFHT890', 'HLT_PFHT1050', 'HLT_PFJet40', 'HLT_PFJet60', 'HLT_PFJet80', 'HLT_PFJet140', 'HLT_PFJet200','HLT_PFJet260', 'HLT_PFJet320', 'HLT_PFJet400', 'HLT_PFJet450', 'HLT_PFJet500', 'HLT_PFJet550', 'HLT_DiPFJetAve15_HFJEC', 'HLT_DiPFJetAve25_HFJEC', 'HLT_DiPFJetAve35_HFJEC']
    tag_triggers += ['HLT_CaloJet500_NoJetID','HLT_CaloJet550_NoJetID','HLT_DiPFJet15_NoCaloMatched','HLT_DiPFJet25_NoCaloMatched','HLT_DiPFJet15_FBEta3_NoCaloMatched','HLT_DiPFJet25_FBEta3_NoCaloMatched','HLT_AK8PFJet40','HLT_AK8PFJet60','HLT_AK8PFJet80','HLT_AK8PFJet140','HLT_AK8PFJet200','HLT_AK8PFJet260','HLT_AK8PFJet320','HLT_AK8PFJet400','HLT_AK8PFJet450','HLT_AK8PFJet500','HLT_AK8PFJet550']
    tag_triggers += ['HLT_PFHT180','HLT_PFHT250','HLT_PFHT370','HLT_PFMETTypeOne110_PFMHT110_IDTight','HLT_PFMETTypeOne120_PFMHT120_IDTight','HLT_PFMETTypeOne130_PFMHT130_IDTight','HLT_PFMETTypeOne140_PFMHT140_IDTight']
    tag_triggers += ['HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4CaloJet120','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_AK4PFJet120']
#    tag_triggers += ['HLT_PFMET200_HBHE_BeamHaloCleaned']

    preselection = "Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_mediumId>0)>1"
    preselection += "&&(%s)"%'||'.join(tag_triggers)

elif year == 2018:
    
    from Samples.nanoAOD.Run2018_17Sep2018_private import *
    data_samples = MET

    tag_triggers   = ['HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFMET200_NotCleaned','HLT_PFMET200_HBHECleaned','HLT_PFMET250_HBHECleaned','HLT_PFMET300_HBHECleaned','HLT_PFMET200_HBHE_BeamHaloCleaned','HLT_CaloMET250_HBHECleaned','HLT_CaloMET300_HBHECleaned','HLT_CaloMET350_HBHECleaned']
    tag_triggers  += ['HLT_PFJet15','HLT_PFJet25','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500','HLT_PFJet550','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFHT180','HLT_PFHT250','HLT_PFHT370','HLT_PFHT430','HLT_PFHT510','HLT_PFHT590','HLT_PFHT680','HLT_PFHT780','HLT_PFHT890','HLT_PFHT1050']
    tag_triggers  += ['HLT_AK8PFJet360_TrimMass30','HLT_AK8PFJet380_TrimMass30','HLT_AK8PFJet400_TrimMass30','HLT_AK8PFJet420_TrimMass30','HLT_AK8PFHT750_TrimMass50','HLT_AK8PFHT800_TrimMass50','HLT_AK8PFHT850_TrimMass50','HLT_AK8PFHT900_TrimMass50','HLT_CaloJet500_NoJetID','HLT_CaloJet550_NoJetID','HLT_HT450_Beamspot','HLT_HT300_Beamspot','HLT_DiPFJetAve40','HLT_DiPFJetAve60']
    tag_triggers  += ['HLT_DiPFJetAve80','HLT_DiPFJetAve140','HLT_DiPFJetAve200','HLT_DiPFJetAve260','HLT_DiPFJetAve320','HLT_DiPFJetAve400','HLT_DiPFJetAve500','HLT_DiPFJetAve15_HFJEC','HLT_DiPFJetAve25_HFJEC','HLT_DiPFJetAve60_HFJEC','HLT_DiPFJetAve80_HFJEC','HLT_DiPFJetAve100_HFJEC','HLT_DiPFJetAve160_HFJEC','HLT_DiPFJetAve220_HFJEC','HLT_DiPFJetAve300_HFJEC']
    tag_triggers  += ['HLT_AK8PFJet15','HLT_AK8PFJet25','HLT_AK8PFJet40','HLT_AK8PFJet60','HLT_AK8PFJet80','HLT_AK8PFJet140','HLT_AK8PFJet200','HLT_AK8PFJet260','HLT_AK8PFJet320','HLT_AK8PFJet400','HLT_AK8PFJet450','HLT_AK8PFJet500','HLT_AK8PFJet550','HLT_PFJetFwd15','HLT_PFJetFwd25','HLT_PFJetFwd40','HLT_PFJetFwd60','HLT_PFJetFwd80','HLT_PFJetFwd140','HLT_PFJetFwd200','HLT_PFJetFwd260','HLT_PFJetFwd320','HLT_PFJetFwd400','HLT_PFJetFwd450','HLT_PFJetFwd500']
    tag_triggers  += ['HLT_AK8PFJetFwd15','HLT_AK8PFJetFwd25','HLT_AK8PFJetFwd40','HLT_AK8PFJetFwd60','HLT_AK8PFJetFwd80','HLT_AK8PFJetFwd140','HLT_AK8PFJetFwd200','HLT_AK8PFJetFwd260','HLT_AK8PFJetFwd320','HLT_AK8PFJetFwd400','HLT_AK8PFJetFwd450','HLT_AK8PFJetFwd500','HLT_PFHT500_PFMET100_PFMHT100_IDTight','HLT_PFHT500_PFMET110_PFMHT110_IDTight','HLT_PFHT700_PFMET85_PFMHT85_IDTight','HLT_PFHT700_PFMET95_PFMHT95_IDTight','HLT_PFHT800_PFMET75_PFMHT75_IDTight','HLT_PFHT800_PFMET85_PFMHT85_IDTight']
    tag_triggers  += ['HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFMET120_PFMHT120_IDTight_PFHT60']
    tag_triggers  += ['HLT_DiJet110_35_Mjj650_PFMET110','HLT_DiJet110_35_Mjj650_PFMET120','HLT_DiJet110_35_Mjj650_PFMET130','HLT_TripleJet110_35_35_Mjj650_PFMET110','HLT_TripleJet110_35_35_Mjj650_PFMET120','HLT_TripleJet110_35_35_Mjj650_PFMET130','HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5','HLT_PFHT330PT30_QuadPFJet_75_60_45_40']
    tag_triggers  += ['HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4CaloJet120','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_AK4PFJet120']

tr = triggerSelector(year)

if args.mode == "muEle":
    dileptonTrigger = tr.e + tr.m + tr.em
    triggerName = "HLT_muEle"
    preselection = "(Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_mediumId>0) + Sum$(Electron_pt>5&&abs(Electron_eta)<2.4&&Electron_cutBased>=4)) >1"
elif args.mode == "doubleEle":
    dileptonTrigger = tr.e + tr.ee
    triggerName = "HLT_ee"
    preselection = "Sum$(Electron_pt>5&&abs(Electron_eta)<2.4&&Electron_cutBased>=4)>1"
elif args.mode == "doubleMu":
    dileptonTrigger = tr.m + tr.mm
    triggerName = "HLT_mm"
    preselection = "Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_mediumId>0)>1"

preselection += "&&(%s)"%'||'.join(tag_triggers) #+ "&&MET_pt<100"

data = Sample.combine( "Run%s"%year, data_samples )
data.files = [ 'root://hephyse.oeaw.ac.at///store' + f.split('store')[1] for f in data.files ]

files = data.files[:30]

p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[TriggerAnalysis(dileptonTrigger)],noOut=True,histFileName="histOut.root",histDirName="plots")

p.run()

outFile = p.histFile

TDir            = outFile.Get('plots')
h_passEvents    = outFile.Get('pass')
h_totalEvents   = outFile.Get('total')
h_MET_pt        = outFile.Get('MET')
h_HT            = outFile.Get('HT')

eff    = ROOT.TEfficiency(h_passEvents, h_totalEvents)

