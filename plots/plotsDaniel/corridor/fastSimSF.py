#!/usr/bin/env python
import os, sys
import ROOT
import array
import json
import random
import glob
import textwrap     # for CutBased Ele ID
import operator

ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from RootTools.core.standard import *

#from StopsDilepton.tools.helpers import checkRootFile, nonEmptyFile, deltaR, deltaR2

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',             nargs='?',      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],      default='INFO',      help="Log level for logging")
argParser.add_argument('--small',               action='store_true',        help='Small?')
argParser.add_argument('--plot_directory',      default='trigger_nanoAOD',  type=str,    action='store')
argParser.add_argument('--sample',              default='MET',              action='store',    choices=['MET', 'JetHT'])
argParser.add_argument('--year',                default=2016,               action='store')
args = argParser.parse_args()

year = int(args.year)

def _dasPopen(dbs):
    #logger.info('DAS query\t: %s',  dbs)
    return os.popen(dbs)


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

def writeObjToFile(fname, obj, update=False):
    gDir = ROOT.gDirectory.GetName()
    if update:
        f = ROOT.TFile(fname, 'UPDATE')
    else:
        f = ROOT.TFile(fname, 'recreate')
    objw = obj.Clone()
    objw.Write()
    f.Close()
    ROOT.gDirectory.cd(gDir+':/')
    return

pt_thresholds_coarse    = [20,30,50,75,100,500]
eta_thresholds_coarse   = [-2.5, -1.4, -0.8, 0., 0.8, 1.4, 2.5]

class TnPAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True
        self.vidNestedWPBitMap           = { 'fail':0, 'veto':1, 'loose':2, 'medium':3, 'tight':4 }  # Bitwise (Electron vidNestedWPBitMap ID flags (3 bits per cut), '000'=0 is fail, '001'=1 is veto, '010'=2 is loose, '011'=3 is medium, '100'=4 is tight)
        self.vidNestedWPBitMapNamingList = \
            ['GsfEleMissingHitsCut',
             'GsfEleConversionVetoCut',
             'GsfEleRelPFIsoScaledCut',
             'GsfEleEInverseMinusPInverseCut',
             'GsfEleHadronicOverEMEnergyScaledCut',
             'GsfEleFull5x5SigmaIEtaIEtaCut',
             'GsfEleDPhiInCut',
             'GsfEleDEtaInSeedCut',
             'GsfEleSCEtaMultiRangeCut',
             'MinPtCut']


    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        pt_thresholds_coarse    = [20,30,50,75,100,500]
        eta_thresholds_coarse   = [-2.5, -1.4, -0.8, 0., 0.8, 1.4, 2.5]


        # 2D hists
        self.h_pt_eta_pass  = ROOT.TH2D("pt_eta_pass","",  len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse), len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse))
        self.h_pt_eta_total = ROOT.TH2D("pt_eta_total","", len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse), len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse))

        for o in [self.h_pt_eta_pass, self.h_pt_eta_total]:
            self.addObject(o)

    def muonSelector(self, muon):
        return abs(muon.eta)<2.4 and muon.pfRelIso03_all < 0.120 and muon.sip3d < 4.0 and abs(muon.dxy) < 0.05 and abs(muon.dz) < 0.1 and muon.mediumId > 0

    def cutBasedEleBitmap(self, integer ):
        return [int( x, 2 ) for x in textwrap.wrap("{0:030b}".format(integer),3) ]

    def cbEleSelector( self, quality, removeCuts = [] ):
        if quality not in self.vidNestedWPBitMap.keys():
            raise Exception( "Don't know about quality %r" % quality )
        if type( removeCuts ) == str:
            removeCuts = [removeCuts]

        # construct a list of thresholds the electron has to satisfy
        thresholds = []
        for cut in removeCuts:
            if cut not in self.vidNestedWPBitMapNamingList:
                raise Exception( "Don't know about ele cut %r" % cut )
        for cut in self.vidNestedWPBitMapNamingList:
            if cut not in removeCuts:
                thresholds.append( self.vidNestedWPBitMap[quality] )
            else:
                thresholds.append( 0 )

        # construct the selector
        def _selector( integer ):
            return all(map( lambda x: operator.ge(*x), zip( self.cutBasedEleBitmap(integer), thresholds ) ))
        return _selector

    def electronSelector(self, electron):
        cbEleSelector_ = self.cbEleSelector( 'tight', removeCuts = ['GsfEleRelPFIsoScaledCut'] )
        return cbEleSelector_(electron.vidNestedWPBitmap) and abs(electron.eta)<2.5 and electron.miniPFRelIso_all < 0.20

    def electronSelectorTight(self, electron):
        cbEleSelector_ = self.cbEleSelector( 'tight', removeCuts = ['GsfEleRelPFIsoScaledCut'] )
        return cbEleSelector_(electron.vidNestedWPBitmap) and abs(electron.eta)<2.5 and electron.miniPFRelIso_all < 0.20 and electron.sip3d < 4.0 and electron.lostHits==0

    def passTriggers(self, event):
        for trigger, lower, upper in self.probeTriggers:
            #print "Trigger:", trigger
            if event.run >= lower and (event.run < upper or upper < 0):
                if getattr(event, trigger) > 0: return True

    def getMLL(self, o1, o2):
        l1 = ROOT.TLorentzVector()
        l2 = ROOT.TLorentzVector()
        l1.SetPtEtaPhiM(o1['pt'], o1['eta'], o1['phi'], 0.)
        l2.SetPtEtaPhiM(o2['pt'], o2['eta'], o2['phi'], 0.)
        return (l1+l2).M()

    def analyze(self, event):
        electrons   = Collection(event, "Electron")
        muons       = Collection(event, "Muon")
        jets        = Collection(event, "Jet")



        # electrons
        goodElectrons = []
        tightElectrons = []
        for electron in electrons:
            if self.electronSelector(electron):
                goodElectrons.append({'pt':electron.pt, 'eta':electron.eta+electron.deltaEtaSC, 'phi':electron.phi})
            if self.electronSelectorTight(electron):
                tightElectrons.append({'pt':electron.pt, 'eta':electron.eta+electron.deltaEtaSC, 'phi':electron.phi})

        if len(goodElectrons) == 2 and len(tightElectrons)>=1:
            mll = self.getMLL(goodElectrons[0], goodElectrons[1])
            if not abs(mll-91.2)<15: return True
            randIndex = random.randint(0,1) # get the index of the probe electron
            self.h_pt_eta_total.Fill(goodElectrons[randIndex]['eta'], goodElectrons[randIndex]['pt'])
            if len(tightElectrons)>1:
                self.h_pt_eta_pass.Fill(tightElectrons[randIndex]['eta'], tightElectrons[randIndex]['pt'])

        return True


    def endJob(self):
        self.eff    = ROOT.TEfficiency(self.h_pt_eta_pass, self.h_pt_eta_total)
        self.addObject(self.eff)


# load samples
if year == 2016:
    DY_full = Sample.fromFiles("DY_full", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8__RunIISummer16NanoAODv4-PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6_ext1-v1/*.root"))
    DY_fast = Sample.fromFiles("DY_fast", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8__RunIISummer16NanoAODv4-PUSummer16v3Fast_Nano14Dec2018_lhe_102X_mcRun2_asymptotic_v6_ext1-v1/*.root"))
elif year == 2017:
    DY_full = Sample.fromFiles("DY_full", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8__RunIIFall17NanoAODv4-PU2017RECOSIMstep_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/*.root"))
    DY_fast = Sample.fromFiles("DY_fast", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCP2_13TeV-madgraphMLM-pythia8__RunIIFall17NanoAODv4-PUFall17Fast_Nano14Dec2018_pilot_102X_mc2017_realistic_v6_ext1-v1/*.root"))
elif year == 2018:
    DY_full = Sample.fromFiles("DY_full", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8__RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v2/*.root"))
    DY_fast = Sample.fromFiles("DY_fast", glob.glob("/hadoop/cms/store/user/dspitzba/nanoAOD/DYJetsToLL_M-50_TuneCP2_13TeV-madgraphMLM-pythia8__RunIIAutumn18NanoAODv4-PUFall18Fast_Nano14Dec2018_lhe_102X_upgrade2018_realistic_v16-v1/*.root"))

preselection = 'Sum$(Electron_pt>20&&abs(Electron_eta)<2.4&&Electron_miniPFRelIso_all<0.2)>1'

### run full sim ###
print "Run Full Sim"
files = DY_full.files if not args.small else DY_full.files[:1]
p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[TnPAnalysis()],noOut=True,histFileName="eff_full.root",histDirName="plots")
p.run()

outFile             = p.histFile
h_pt_eta_pass       = outFile.Get('pt_eta_pass')
h_pt_eta_total      = outFile.Get('pt_eta_total')
eff_pt_eta          = ROOT.TEfficiency(h_pt_eta_pass, h_pt_eta_total)
h_eff_pt_eta_full   = eff_pt_eta.CreateHistogram('eff_pt_eta')
h_eff_pt_eta_full   = fixUncertainties(eff_pt_eta, h_eff_pt_eta_full, pt_thresholds_coarse, eta_thresholds_coarse)
h_eff_pt_eta_full.SetName('eff_pt_eta')

## 2D
h_eff_pt_eta_full.GetYaxis().SetNdivisions(712)
h_eff_pt_eta_full.GetYaxis().SetMoreLogLabels()
h_eff_pt_eta_full.GetYaxis().SetNoExponent()

plot = Plot.fromHisto(name = 'pt_eta_fullSim_%s'%year, histos = [[ h_eff_pt_eta_full ]], texX = "super-cluster-#eta", texY = "lepton p_{T} (GeV)")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = './plots/', #ratio = ratio,
    logX = False, logY = True, logZ=False,
     zRange = (0,1.05),
)

print "Done with Full Sim"
outFile.Close()

### Fast Sim ###

print "Run Fast Sim"
files = DY_fast.files if not args.small else DY_fast.files[:1]
p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[TnPAnalysis()],noOut=True,histFileName="eff_fast.root",histDirName="plots")
p.run()

outFile             = p.histFile
h_pt_eta_pass       = outFile.Get('pt_eta_pass')
h_pt_eta_total      = outFile.Get('pt_eta_total')
eff_pt_eta          = ROOT.TEfficiency(h_pt_eta_pass, h_pt_eta_total)
h_eff_pt_eta_fast   = eff_pt_eta.CreateHistogram('eff_pt_eta')
h_eff_pt_eta_fast   = fixUncertainties(eff_pt_eta, h_eff_pt_eta_fast, pt_thresholds_coarse, eta_thresholds_coarse)
h_eff_pt_eta_fast.SetName('eff_pt_eta')

## 2D
h_eff_pt_eta_fast.GetYaxis().SetNdivisions(712)
h_eff_pt_eta_fast.GetYaxis().SetMoreLogLabels()
h_eff_pt_eta_fast.GetYaxis().SetNoExponent()

plot = Plot.fromHisto(name = 'pt_eta_fastSim_%s'%year, histos = [[ h_eff_pt_eta_fast ]], texX = "super-cluster-#eta", texY = "lepton p_{T} (GeV)")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = './plots/', #ratio = ratio,
    logX = False, logY = True, logZ=False,
     zRange = (0,1.05),
)

print "Done with Fast Sim"

scaleFactor = h_eff_pt_eta_full.Clone()
scaleFactor.Divide(h_eff_pt_eta_fast)

writeObjToFile('fastSimSF_%s.root'%year, scaleFactor, update=False)


plot = Plot.fromHisto(name = 'pt_eta_SF_%s'%year, histos = [[ scaleFactor ]], texX = "super-cluster-#eta", texY = "lepton p_{T} (GeV)")
plot.drawOption="colz texte"
plotting.draw2D(
    plot,
    plot_directory = './plots/', #ratio = ratio,
    logX = False, logY = True, logZ=False,
     zRange = (0,1.05),
)

