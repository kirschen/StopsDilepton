''' Tail Scanner
'''
import ROOT
from Samples.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',      action='store', type=int, default=2018)
argParser.add_argument('--selection', action='store',           default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12')
argParser.add_argument('--mode',      action='store',           default='ee', choices=['mumu', 'mue', 'ee'])
args = argParser.parse_args()

# import data sample
if args.year == 2016:
    data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    dataSample = Run2016
elif args.year == 2017:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p6/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    dataSample = Run2017
elif args.year == 2018:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2018_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    dataSample = Run2018

# mode selections
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection(mode):
  if mode=="mumu":
      return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":
      return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":
      return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ

# set filter cuts
selectionList = [getFilterCut(isData=True, year=args.year, skipBadPFMuon=False, skipBadChargedCandidate=False), getLeptonSelection(args.mode), cutInterpreter.cutString(args.selection), "dl_mt2ll>140"]

cutSelection =  "&&".join(selectionList)
# print cutSelection

dataSample.chain.SetScanField(1000)
dataSample.chain.Scan("run:luminosityBlock:event", cutSelection, "colsize=15") 
