#!/usr/bin/env python
import os, sys
import ROOT
import array
import json

ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from StopsDilepton.tools.triggerSelector import *
from StopsDilepton.tools.helpers import checkRootFile, nonEmptyFile, deltaR, deltaR2

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',             nargs='?',      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],      default='INFO',      help="Log level for logging")
argParser.add_argument('--small',               action='store_true',        help='Small?')
argParser.add_argument('--globalRedirector',               action='store_true',        help='Small?')
argParser.add_argument('--local',               action='store_true',        help='Use local files?')
argParser.add_argument('--plot_directory',      default='trigger_nanoAOD',  type=str,    action='store')
argParser.add_argument('--mode',                default='doubleMu',            action='store',    choices=['doubleMu', 'doubleEle',  'muEle'])
argParser.add_argument('--sample',              default='MET',              action='store',    choices=['MET', 'JetHT'])
argParser.add_argument('--year',                default=2016,               action='store')
args = argParser.parse_args()

import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

year = int(args.year)

def _dasPopen(dbs):
    #logger.info('DAS query\t: %s',  dbs)
    return os.popen(dbs)

def checkLocalityOfFile(f, locality="T2_AT_Vienna"):
    fileNoRedirector ='/store' + f.split('store')[1]
    dbs='dasgoclient -query="site file=%s" --json'%(fileNoRedirector)
    jdata = json.load(_dasPopen(dbs))
    found = False
    for j in jdata:
        if j['site'][0]['name'] == locality:
            found = True
    return found
    
if 'cern' in os.environ['HOSTNAME']:
  redirector = 'root://cms-xrd-global.cern.ch/'

def fixUncertainties(teff, heff, x_binning, y_binning):
    for x in x_binning:
        for y in y_binning:
            x_bin = heff.GetXaxis().FindBin(x)
            y_bin = heff.GetYaxis().FindBin(y)
            n_bin = teff.FindFixBin(x,y)
            err   = (teff.GetEfficiencyErrorUp(n_bin) + teff.GetEfficiencyErrorLow(n_bin) ) / 2.
            heff.SetBinError(x_bin, y_bin, err)
    return heff
            

class TriggerAnalysis(Module):
    def __init__(self, probeTriggers):
        self.writeHistFile = True
        self.probeTriggers = probeTriggers

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        pt_thresholds           = range(0,30,2)+range(30,50,5)+range(50,210,10)
        eta_thresholds          = [x/10. for x in range(-25,26,1) ]
        pt_thresholds_coarse    = range(5,25,10)+range(25,130,15)+range(130,330,50)
        pt_thresholds_veryCoarse = [20,25,35] + range(50,200,50)+[250]
        eta_thresholds_coarse   = [x/10. for x in range(-25,26,5) ]

        # 1D hists
        self.h_pt_dummy         = ROOT.TH1F("pt_dummy","",    len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_pt1_passEvents   = ROOT.TH1F("pt1_pass","",    len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_pt1_totalEvents  = ROOT.TH1F("pt1_total","",   len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_pt2_passEvents   = ROOT.TH1F("pt2_pass","",    len(pt_thresholds)-1, array.array('d',pt_thresholds))
        self.h_pt2_totalEvents  = ROOT.TH1F("pt2_total","",   len(pt_thresholds)-1, array.array('d',pt_thresholds))

        self.h_eta_dummy         = ROOT.TH1F("eta_dummy","",  len(eta_thresholds)-1, array.array('d',eta_thresholds))
        self.h_eta1_passEvents   = ROOT.TH1F("eta1_pass","",  len(eta_thresholds)-1, array.array('d',eta_thresholds))
        self.h_eta1_totalEvents  = ROOT.TH1F("eta1_total","", len(eta_thresholds)-1, array.array('d',eta_thresholds))
        self.h_eta2_passEvents   = ROOT.TH1F("eta2_pass","",  len(eta_thresholds)-1, array.array('d',eta_thresholds))
        self.h_eta2_totalEvents  = ROOT.TH1F("eta2_total","", len(eta_thresholds)-1, array.array('d',eta_thresholds))


        # 2D hists
        self.h_pt1_pt2_pass   = ROOT.TH2D("pt1_pt2_pass","",   len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
        self.h_pt1_pt2_total  = ROOT.TH2D("pt1_pt2_total","",  len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))

        self.h_pt1_pt2_highEta1_pass  = ROOT.TH2D("pt1_pt2_highEta1_pass","",   len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
        self.h_pt1_pt2_highEta1_total = ROOT.TH2D("pt1_pt2_highEta1_total","",  len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
        self.h_pt1_pt2_lowEta1_pass   = ROOT.TH2D("pt1_pt2_lowEta1_pass","",   len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
        self.h_pt1_pt2_lowEta1_total  = ROOT.TH2D("pt1_pt2_lowEta1_total","",  len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))

        self.h_pt1_eta1_pass  = ROOT.TH2D("pt1_eta1_pass","",  len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))
        self.h_pt1_eta1_total = ROOT.TH2D("pt1_eta1_total","", len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))
        self.h_pt2_eta2_pass  = ROOT.TH2D("pt2_eta2_pass","",  len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))
        self.h_pt2_eta2_total = ROOT.TH2D("pt2_eta2_total","", len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))

        self.h_MET_pt       = ROOT.TH1F("MET", "MET", 50, 0, 1000)
        self.h_HT           = ROOT.TH1F("HT", "HT", 50, 0, 1000)

        for o in [self.h_pt_dummy, self.h_pt1_passEvents, self.h_pt1_totalEvents, self.h_pt2_passEvents, self.h_pt2_passEvents, self.h_pt2_totalEvents, self.h_eta_dummy, self.h_eta1_passEvents, self.h_eta1_totalEvents, self.h_eta2_passEvents, self.h_eta2_totalEvents, self.h_MET_pt, self.h_HT]:
            self.addObject(o)

        for o in [self.h_pt1_pt2_pass,self.h_pt1_pt2_total,self.h_pt1_pt2_highEta1_pass,self.h_pt1_pt2_highEta1_total,self.h_pt1_pt2_lowEta1_pass,self.h_pt1_pt2_lowEta1_total,self.h_pt1_eta1_pass,self.h_pt1_eta1_total,self.h_pt2_eta2_pass,self.h_pt2_eta2_total]:
            self.addObject(o)

        #self.addObject(self.h_passEvents )
        #self.addObject(self.h_totalEvents )
        #self.addObject(self.h_MET_pt )
        #self.addObject(self.h_HT )


    def muonSelector(self, muon):
        return abs(muon.eta)<2.4 and muon.pfRelIso03_all < 0.120 and muon.sip3d < 4.0 and abs(muon.dxy) < 0.05 and abs(muon.dz) < 0.1 and muon.mediumId > 0

    def electronSelector(self, electron):
        return abs(electron.eta)<2.4 and electron.pfRelIso03_all < 0.120 and electron.sip3d < 4.0 and abs(electron.dxy) < 0.05 and abs(electron.dz) < 0.1 and electron.cutBased >=4 and electron.convVeto and electron.lostHits==0

    def passTriggers(self, event):
        for trigger, lower, upper in self.probeTriggers:
            #print "Trigger:", trigger
            if event.run >= lower and (event.run < upper or upper < 0):
                if getattr(event, trigger) > 0: return True

    def analyze(self, event):
        electrons   = Collection(event, "Electron")
        muons       = Collection(event, "Muon")
        jets        = Collection(event, "Jet")


        # muons
        goodMuons   = []
        for muon in muons:
            if self.muonSelector(muon):
                goodMuons.append({'pt':muon.pt, 'eta':muon.eta, 'phi':muon.phi})

        # electrons
        goodElectrons = []
        for electron in electrons:
            if self.electronSelector(electron):
                goodElectrons.append({'pt':electron.pt, 'eta':electron.eta})
        
        # total
        goodLeptons = goodMuons + goodElectrons
        goodLeptons.sort( key = lambda x: -x['pt'] )

        ht = 0.
        for jet in jets:
            if jet.pt>30 and abs(jet.eta)<2.4 and jet.jetId>0:
                ht += jet.pt

        #if len(goodMuons)>1:
        #    if deltaR(goodMuons[0], goodMuons[1]) < 0.4:
        #        return True

        if len(goodLeptons) > 1:
            leadingPt       = goodLeptons[0]['pt']
            subleadingPt    = goodLeptons[1]['pt']
            leadingEta      = goodLeptons[0]['eta']
            subleadingEta   = goodLeptons[1]['eta']

            self.h_pt1_totalEvents.Fill(leadingPt)
            self.h_pt2_totalEvents.Fill(subleadingPt)
            self.h_eta1_totalEvents.Fill(leadingEta)
            self.h_eta2_totalEvents.Fill(subleadingEta)
            
            self.h_pt1_pt2_total.Fill(leadingPt,subleadingPt)
            self.h_pt1_eta1_total.Fill(leadingPt,leadingEta)
            self.h_pt2_eta2_total.Fill(subleadingPt,subleadingEta)
            if leadingEta > 1.5:
                self.h_pt1_pt2_highEta1_total.Fill(leadingPt,subleadingPt)
            else:
                self.h_pt1_pt2_lowEta1_total.Fill(leadingPt,subleadingPt)

            if self.passTriggers(event):
                self.h_pt1_passEvents.Fill(leadingPt)
                self.h_pt2_passEvents.Fill(subleadingPt)
                self.h_eta1_passEvents.Fill(leadingEta)
                self.h_eta2_passEvents.Fill(subleadingEta)

                self.h_pt1_pt2_pass.Fill(leadingPt,subleadingPt)
                self.h_pt1_eta1_pass.Fill(leadingPt,leadingEta)
                self.h_pt2_eta2_pass.Fill(subleadingPt,subleadingEta)
                if leadingEta > 1.5:
                    self.h_pt1_pt2_highEta1_pass.Fill(leadingPt,subleadingPt)
                else:
                    self.h_pt1_pt2_lowEta1_pass.Fill(leadingPt,subleadingPt)

            self.h_MET_pt.Fill(event.MET_pt)
            self.h_HT.Fill(ht)

        return True


    def endJob(self):
        self.eff    = ROOT.TEfficiency(self.h_pt1_passEvents, self.h_pt1_totalEvents)
        self.addObject(self.eff)


logger.info("Loading samples")

from Samples.Tools.config import redirector_global, redirector

if args.globalRedirector:
    #redirector = redirector_global
    redirector = "root://xrootd-cms.infn.it/"

if year == 2016:

    from Samples.nanoAOD.Run2016_14Dec2018 import *
    data_samples = MET_Run2016 if args.sample == 'MET' else JetHT_Run2016

    tag_triggers  = ['HLT_MET200','HLT_MET250', 'HLT_MET300', 'HLT_MET600', 'HLT_MET700','HLT_PFMET300','HLT_PFMET400','HLT_PFMET500','HLT_PFMET600','HLT_PFMET90_PFMHT90_IDTight','HLT_PFMET100_PFMHT100_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight']
    tag_triggers += ['HLT_HT200','HLT_HT275','HLT_HT325','HLT_HT425','HLT_HT575','HLT_HT410to430','HLT_HT430to450','HLT_HT450to470','HLT_HT470to500','HLT_HT500to550','HLT_HT550to650','HLT_HT650','HLT_PFHT300_PFMET100','HLT_PFHT300_PFMET110','HLT_DiPFJetAve15_HFJEC','HLT_DiPFJetAve25_HFJEC','HLT_DiPFJetAve35_HFJEC','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500']
    tag_triggers += ['HLT_AK8PFJet360_TrimMass30','HLT_AK8PFHT700_TrimR0p1PT0p03Mass50','HLT_AK8PFHT650_TrimR0p1PT0p03Mass50','HLT_AK8PFHT600_TrimR0p1PT0p03Mass50_BTagCSV_p20','HLT_PFHT550_4JetPt50','HLT_PFHT650_4JetPt50','HLT_PFHT750_4JetPt50','HLT_PFJet15_NoCaloMatched','HLT_PFJet25_NoCaloMatched','HLT_DiPFJet15_NoCaloMatched','HLT_DiPFJet25_NoCaloMatched','HLT_DiPFJet15_FBEta3_NoCaloMatched']
    tag_triggers += ['HLT_DiPFJet25_FBEta3_NoCaloMatched','HLT_DiPFJetAve40','HLT_DiPFJetAve60','HLT_DiPFJetAve80','HLT_DiPFJetAve140','HLT_DiPFJetAve200','HLT_DiPFJetAve260','HLT_DiPFJetAve320','HLT_DiPFJetAve400','HLT_DiPFJetAve500']
    tag_triggers += ['HLT_DiCentralPFJet55_PFMET110','HLT_PFHT125','HLT_PFHT200','HLT_PFHT250','HLT_PFHT300','HLT_PFHT350','HLT_PFHT400','HLT_PFHT475','HLT_PFHT600','HLT_PFHT650','HLT_PFHT800','HLT_PFHT900']
    tag_triggers += ['HLT_AK8DiPFJet280_200_TrimMass30','HLT_AK8DiPFJet250_200_TrimMass30','HLT_PFHT400_SixJet30','HLT_PFHT450_SixJet40','HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_HT2000','HLT_HT2500']

elif year == 2017:

    from Samples.nanoAOD.Run2017_14Dec2018 import *
    data_samples = MET_Run2017 if args.sample == 'MET' else JetHT_Run2017
    #data_samples = [MET_Run2017C_14Dec2018, MET_Run2017D_14Dec2018, MET_Run2017E_14Dec2018, MET_Run2017F_14Dec2018] if args.sample == 'MET' else []
    
    tag_triggers  = ['HLT_PFHT500_PFMET100_PFMHT100_IDTight','HLT_PFHT500_PFMET110_PFMHT110_IDTight','HLT_PFHT700_PFMET85_PFMHT85_IDTight','HLT_PFHT700_PFMET95_PFMHT95_IDTight','HLT_PFHT800_PFMET75_PFMHT75_IDTight','HLT_PFHT800_PFMET85_PFMHT85_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight']
    tag_triggers += ['HLT_PFHT430', 'HLT_PFHT510', 'HLT_PFHT590', 'HLT_PFHT680', 'HLT_PFHT780', 'HLT_PFHT890', 'HLT_PFHT1050', 'HLT_PFJet40', 'HLT_PFJet60', 'HLT_PFJet80', 'HLT_PFJet140', 'HLT_PFJet200','HLT_PFJet260', 'HLT_PFJet320', 'HLT_PFJet400', 'HLT_PFJet450', 'HLT_PFJet500', 'HLT_PFJet550', 'HLT_DiPFJetAve15_HFJEC', 'HLT_DiPFJetAve25_HFJEC', 'HLT_DiPFJetAve35_HFJEC']
    tag_triggers += ['HLT_CaloJet500_NoJetID','HLT_CaloJet550_NoJetID','HLT_DiPFJet15_NoCaloMatched','HLT_DiPFJet25_NoCaloMatched','HLT_DiPFJet15_FBEta3_NoCaloMatched','HLT_DiPFJet25_FBEta3_NoCaloMatched','HLT_AK8PFJet40','HLT_AK8PFJet60','HLT_AK8PFJet80','HLT_AK8PFJet140','HLT_AK8PFJet200','HLT_AK8PFJet260','HLT_AK8PFJet320','HLT_AK8PFJet400','HLT_AK8PFJet450','HLT_AK8PFJet500','HLT_AK8PFJet550']
    tag_triggers += ['HLT_PFHT180','HLT_PFHT250','HLT_PFHT370','HLT_PFMETTypeOne110_PFMHT110_IDTight','HLT_PFMETTypeOne120_PFMHT120_IDTight','HLT_PFMETTypeOne130_PFMHT130_IDTight','HLT_PFMETTypeOne140_PFMHT140_IDTight']
    tag_triggers += ['HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4CaloJet120','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_AK4PFJet120']
#    tag_triggers += ['HLT_PFMET200_HBHE_BeamHaloCleaned']

    preselection = "Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_mediumId>0)>1"
    preselection += "&&(%s)"%'||'.join(tag_triggers)

elif year == 2018:
    
    if args.local:
        from Samples.nanoAOD.Run2018_17Sep2018_private import *
        data_samples = MET if args.sample == 'MET' else JetHT
    else:
        from Samples.nanoAOD.Run2018_14Dec2018 import *
        data_samples = MET_Run2018 if args.sample == 'MET' else JetHT_Run2018

    tag_triggers   = ['HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFMET200_NotCleaned','HLT_PFMET200_HBHECleaned','HLT_PFMET250_HBHECleaned','HLT_PFMET300_HBHECleaned','HLT_PFMET200_HBHE_BeamHaloCleaned','HLT_CaloMET250_HBHECleaned','HLT_CaloMET300_HBHECleaned','HLT_CaloMET350_HBHECleaned']
    tag_triggers  += ['HLT_PFJet15','HLT_PFJet25','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500','HLT_PFJet550','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFHT180','HLT_PFHT250','HLT_PFHT370','HLT_PFHT430','HLT_PFHT510','HLT_PFHT590','HLT_PFHT680','HLT_PFHT780','HLT_PFHT890','HLT_PFHT1050']
    tag_triggers  += ['HLT_AK8PFJet360_TrimMass30','HLT_AK8PFJet380_TrimMass30','HLT_AK8PFJet400_TrimMass30','HLT_AK8PFJet420_TrimMass30','HLT_AK8PFHT750_TrimMass50','HLT_AK8PFHT800_TrimMass50','HLT_AK8PFHT850_TrimMass50','HLT_AK8PFHT900_TrimMass50','HLT_CaloJet500_NoJetID','HLT_CaloJet550_NoJetID','HLT_HT450_Beamspot','HLT_HT300_Beamspot','HLT_DiPFJetAve40','HLT_DiPFJetAve60']
    tag_triggers  += ['HLT_DiPFJetAve80','HLT_DiPFJetAve140','HLT_DiPFJetAve200','HLT_DiPFJetAve260','HLT_DiPFJetAve320','HLT_DiPFJetAve400','HLT_DiPFJetAve500']
    tag_triggers  += ['HLT_AK8PFJet15','HLT_AK8PFJet25','HLT_AK8PFJet40','HLT_AK8PFJet60','HLT_AK8PFJet80','HLT_AK8PFJet140','HLT_AK8PFJet200','HLT_AK8PFJet260','HLT_AK8PFJet320','HLT_AK8PFJet400','HLT_AK8PFJet450','HLT_AK8PFJet500','HLT_AK8PFJet550','HLT_PFJetFwd15','HLT_PFJetFwd25','HLT_PFJetFwd40','HLT_PFJetFwd60','HLT_PFJetFwd80','HLT_PFJetFwd140','HLT_PFJetFwd200','HLT_PFJetFwd260','HLT_PFJetFwd320','HLT_PFJetFwd400','HLT_PFJetFwd450','HLT_PFJetFwd500']
    tag_triggers  += ['HLT_AK8PFJetFwd15','HLT_AK8PFJetFwd25','HLT_AK8PFJetFwd40','HLT_AK8PFJetFwd60','HLT_AK8PFJetFwd80','HLT_AK8PFJetFwd140','HLT_AK8PFJetFwd200','HLT_AK8PFJetFwd260','HLT_AK8PFJetFwd320','HLT_AK8PFJetFwd400','HLT_AK8PFJetFwd450','HLT_AK8PFJetFwd500','HLT_PFHT500_PFMET100_PFMHT100_IDTight','HLT_PFHT500_PFMET110_PFMHT110_IDTight','HLT_PFHT700_PFMET85_PFMHT85_IDTight','HLT_PFHT700_PFMET95_PFMHT95_IDTight','HLT_PFHT800_PFMET75_PFMHT75_IDTight','HLT_PFHT800_PFMET85_PFMHT85_IDTight']
    tag_triggers  += ['HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFMET120_PFMHT120_IDTight_PFHT60']
    tag_triggers  += ['HLT_DiJet110_35_Mjj650_PFMET110','HLT_DiJet110_35_Mjj650_PFMET120','HLT_DiJet110_35_Mjj650_PFMET130','HLT_TripleJet110_35_35_Mjj650_PFMET110','HLT_TripleJet110_35_35_Mjj650_PFMET120','HLT_TripleJet110_35_35_Mjj650_PFMET130','HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5','HLT_PFHT330PT30_QuadPFJet_75_60_45_40']
    tag_triggers  += ['HLT_AK4CaloJet30','HLT_AK4CaloJet40','HLT_AK4CaloJet50','HLT_AK4CaloJet80','HLT_AK4CaloJet100','HLT_AK4CaloJet120','HLT_AK4PFJet30','HLT_AK4PFJet50','HLT_AK4PFJet80','HLT_AK4PFJet100','HLT_AK4PFJet120']

tr = triggerSelector(year, era='B') # era F to get all triggers

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
    triggerName = "HLT_mm_tight"
    #dileptonTrigger = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"]
    #triggerName = "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"
    preselection = "Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_mediumId>0&&Muon_pfRelIso03_all<0.15)>1"

dileptonTrigger = [(t, 0, -1) for t in dileptonTrigger]
if year == 2017 and args.mode == "doubleMu":
    dileptonTrigger += [("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", 299337, -1), ("HLT_Mu37_TkMu27", 302026, -1)]

print "Dilepton triggers:"
print dileptonTrigger

preselection += "&&(%s)"%'||'.join(tag_triggers) #+ "&&MET_pt<100"

logger.info("Combining samples")

data = Sample.combine( "Run%s"%year, data_samples )

# single files might be missing, need to avoid this
localFiles = []

print "Checking files"
for f in data.files:
    if year == 2018 and args.local:
        if nonEmptyFile(f):
            localFiles.append(f)
    elif not args.globalRedirector:
        print "Checking if file %s is in Vienna"%sf
        if checkLocalityOfFile(f):
            localFiles.append(f)
        print "done"
    else:
        localFiles.append(f)

#data.files = [ 'root://hephyse.oeaw.ac.at///store' + f.split('store')[1] for f in data.files ]

files = localFiles[:2] if args.small else localFiles

logger.info("Starting post-processor")

p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[TriggerAnalysis(dileptonTrigger)],noOut=True,histFileName="histOut.root",histDirName="plots")

print "Run"

p.run()

print "Done"

outFile = p.histFile

logger.info("Plotting")

TDir                = outFile.Get('plots')

## 1D

h_pt_dummy          = outFile.Get('pt_dummy')
h_pt1_passEvents    = outFile.Get('pt1_pass')
h_pt1_totalEvents   = outFile.Get('pt1_total')
h_pt2_passEvents    = outFile.Get('pt2_pass')
h_pt2_totalEvents   = outFile.Get('pt2_total')

h_eta_dummy          = outFile.Get('eta_dummy')
h_eta1_passEvents    = outFile.Get('eta1_pass')
h_eta1_totalEvents   = outFile.Get('eta1_total')
h_eta2_passEvents    = outFile.Get('eta2_pass')
h_eta2_totalEvents   = outFile.Get('eta2_total')

h_MET_pt            = outFile.Get('MET')
h_HT                = outFile.Get('HT')

eff_pt1   = ROOT.TEfficiency(h_pt1_passEvents, h_pt1_totalEvents)
eff_pt2   = ROOT.TEfficiency(h_pt2_passEvents, h_pt2_totalEvents)

eff_eta1  = ROOT.TEfficiency(h_eta1_passEvents, h_eta1_totalEvents)
eff_eta2  = ROOT.TEfficiency(h_eta2_passEvents, h_eta2_totalEvents)

## 2D

h_pt1_pt2_pass  = outFile.Get('pt1_pt2_pass')
h_pt1_pt2_total = outFile.Get('pt1_pt2_total')
h_pt1_eta1_pass  = outFile.Get('pt1_eta1_pass')
h_pt1_eta1_total = outFile.Get('pt1_eta1_total')
h_pt2_eta2_pass  = outFile.Get('pt2_eta2_pass')
h_pt2_eta2_total = outFile.Get('pt2_eta2_total')
h_pt1_pt2_highEta1_pass  = outFile.Get('pt1_pt2_highEta1_pass')
h_pt1_pt2_highEta1_total = outFile.Get('pt1_pt2_highEta1_total')
h_pt1_pt2_lowEta1_pass  = outFile.Get('pt1_pt2_lowEta1_pass')
h_pt1_pt2_lowEta1_total = outFile.Get('pt1_pt2_lowEta1_total')

pt_thresholds_coarse    = range(5,25,10)+range(25,130,15)+range(130,330,50)
pt_thresholds_veryCoarse = [20,25,35] + range(50,200,50)+[250]
eta_thresholds_coarse   = [x/10. for x in range(-25,26,5) ]

eff_pt1_pt2 = ROOT.TEfficiency(h_pt1_pt2_pass, h_pt1_pt2_total)
h_eff_pt1_pt2 = eff_pt1_pt2.CreateHistogram('eff_pt1_pt2')
h_eff_pt1_pt2.SetName('eff_pt1_pt2')
h_eff_pt1_pt2 = fixUncertainties(eff_pt1_pt2, h_eff_pt1_pt2, pt_thresholds_veryCoarse, pt_thresholds_veryCoarse)

eff_pt1_eta1 = ROOT.TEfficiency(h_pt1_eta1_pass, h_pt1_eta1_total)
h_eff_pt1_eta1 = eff_pt1_eta1.CreateHistogram('eff_pt1_eta1')
h_eff_pt1_eta1.SetName('eff_pt1_eta1')
h_eff_pt1_eta1 = fixUncertainties(eff_pt1_eta1, h_eff_pt1_eta1, pt_thresholds_coarse, eta_thresholds_coarse)

eff_pt2_eta2 = ROOT.TEfficiency(h_pt2_eta2_pass, h_pt2_eta2_total)
h_eff_pt2_eta2 = eff_pt2_eta2.CreateHistogram('eff_pt2_eta2')
h_eff_pt2_eta2.SetName('eff_pt2_eta2')
h_eff_pt2_eta2 = fixUncertainties(eff_pt2_eta2, h_eff_pt2_eta2, pt_thresholds_coarse, eta_thresholds_coarse)

eff_pt1_pt2_lowEta1 = ROOT.TEfficiency(h_pt1_pt2_lowEta1_pass, h_pt1_pt2_lowEta1_total)
h_eff_pt1_pt2_lowEta1 = eff_pt1_pt2_lowEta1.CreateHistogram('eff_pt1_pt2_lowEta1')
h_eff_pt1_pt2_lowEta1.SetName('eff_pt1_pt2_lowEta1')
h_eff_pt1_pt2_lowEta1 = fixUncertainties(eff_pt1_pt2_lowEta1, h_eff_pt1_pt2_lowEta1, pt_thresholds_veryCoarse, pt_thresholds_veryCoarse)

eff_pt1_pt2_highEta1 = ROOT.TEfficiency(h_pt1_pt2_highEta1_pass, h_pt1_pt2_highEta1_total)
h_eff_pt1_pt2_highEta1 = eff_pt1_pt2_highEta1.CreateHistogram('eff_pt1_pt2_highEta1')
h_eff_pt1_pt2_highEta1.SetName('eff_pt1_pt2_highEta1')
h_eff_pt1_pt2_highEta1 = fixUncertainties(eff_pt1_pt2_highEta1, h_eff_pt1_pt2_highEta1, pt_thresholds_veryCoarse, pt_thresholds_veryCoarse)

preprefix   = "Run%s"%year
prefix      = preprefix+"_%s_measuredIn%s" % ( triggerName, args.sample)
if args.small: prefix = "small_" + prefix

from RootTools.core.standard import *
from StopsDilepton.tools.user import plot_directory
plot_path = os.path.join(plot_directory, args.plot_directory, prefix)

## momenta

plotting.draw(
    Plot.fromHisto(name = 'pt1_'+triggerName, histos = [[ h_pt_dummy ]], texX = "p_{T} of leading lepton", texY = triggerName),
    drawObjects = [eff_pt1],
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1.05), legend = None ,
)

plotting.draw(
    Plot.fromHisto(name = 'pt2_'+triggerName, histos = [[ h_pt_dummy ]], texX = "p_{T} of subleading lepton", texY = triggerName),
    drawObjects = [eff_pt2],
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1.05), legend = None ,
)


## rap

plotting.draw(
    Plot.fromHisto(name = 'eta1_'+triggerName, histos = [[ h_eta_dummy ]], texX = "#eta of leading lepton", texY = triggerName),
    drawObjects = [eff_eta1],
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1.05), legend = None ,
)

plotting.draw(
    Plot.fromHisto(name = 'eta2_'+triggerName, histos = [[ h_eta_dummy ]], texX = "#eta of subleading lepton", texY = triggerName),
    drawObjects = [eff_eta2],
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1.05), legend = None ,
    copyIndexPHP = True,
)


plotting.draw(
    Plot.fromHisto(name = 'MET_pt_'+triggerName, histos = [[ h_MET_pt ]], texX = "E_{T}^{miss} (GeV)", texY = "Events"),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
    legend = None ,
)

plotting.draw(
    Plot.fromHisto(name = 'HT_'+triggerName, histos = [[ h_HT ]], texX = "H_{T} (GeV)", texY = "Events"),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
    legend = None ,
)

ROOT.gStyle.SetPaintTextFormat("1.2f")

## 2D
h_eff_pt1_pt2.GetXaxis().SetNdivisions(712)
h_eff_pt1_pt2.GetXaxis().SetMoreLogLabels()
h_eff_pt1_pt2.GetXaxis().SetNoExponent()
h_eff_pt1_pt2.GetYaxis().SetNdivisions(712)
h_eff_pt1_pt2.GetYaxis().SetMoreLogLabels()
h_eff_pt1_pt2.GetYaxis().SetNoExponent()

plot = Plot.fromHisto(name = 'pt1_pt2_'+triggerName, histos = [[ h_eff_pt1_pt2 ]], texX = "p_{T} of leading lepton", texY = "p_{T} of subleading lepton")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = plot_path, #ratio = ratio, 
    logX = True, logY = True, logZ=False,
     zRange = (0,1.05),
)

plot = Plot.fromHisto(name = 'pt1_pt2_highEta1'+triggerName, histos = [[ h_eff_pt1_pt2_highEta1 ]], texX = "p_{T} of leading lepton", texY = "p_{T} of subleading lepton")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = plot_path, #ratio = ratio, 
    logX = True, logY = True, logZ=False,
     zRange = (0,1.05),
)

plot = Plot.fromHisto(name = 'pt1_pt2_lowEta1'+triggerName, histos = [[ h_eff_pt1_pt2_lowEta1 ]], texX = "p_{T} of leading lepton", texY = "p_{T} of subleading lepton")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = plot_path, #ratio = ratio, 
    logX = True, logY = True, logZ=False,
     zRange = (0,1.05),
)

plot = Plot.fromHisto(name = 'pt1_eta1_'+triggerName, histos = [[ h_eff_pt1_eta1 ]], texX = "p_{T} of leading lepton", texY = "#eta of leading lepton")
#plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, logZ=False,
     zRange = (0,1.05),
)

plot = Plot.fromHisto(name = 'pt2_eta2_'+triggerName, histos = [[ h_eff_pt2_eta2 ]], texX = "p_{T} of subleading lepton", texY = "#eta of subleading lepton")
#plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, logZ=False,
     zRange = (0,1.05),
)

ofile = ROOT.TFile.Open(os.path.join(plot_path, prefix+'.root'), 'recreate')
h_eff_pt1_pt2.Write()
h_eff_pt1_pt2_highEta1.Write()
h_eff_pt1_pt2_lowEta1.Write()
h_eff_pt1_eta1.Write()
h_eff_pt2_eta2.Write()
ofile.Close()
