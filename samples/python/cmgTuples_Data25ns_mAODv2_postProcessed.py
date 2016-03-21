import copy, os, sys
from StopsDilepton.tools.user import data_directory
from RootTools.core.Sample import Sample 
import ROOT

dirs = {}
dirs['DoubleEG']       = ["DoubleEG_Run2015D_16Dec"]
dirs['DoubleMuon']     = ["DoubleMuon_Run2015D_16Dec"]
dirs['MuonEG']         = ["MuonEG_Run2015D_16Dec"]
dirs['SingleElectron'] = ["SingleElectron_Run2015D_16Dec"]
dirs['SingleMuon']     = ["SingleMuon_Run2015D_16Dec"]

for key in dirs:
  dirs[key] = [ os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/dilepTiny', dir) for dir in dirs[key]]

lumi = {}
lumi['DoubleEG']       = 1000*(2.165)
lumi['DoubleMuon']     = 1000*(2.165)
lumi['MuonEG']         = 1000*(2.137)
lumi['SingleElectron'] = 1000*(2.162)
lumi['SingleMuon']     = 1000*(2.024)

DoubleEG_Run2015D       = Sample.fromDirectory(name="DoubleEG_Run2015D",       treeName="Events", texName="DoubleEG (Run2015D)",       directory=dirs["DoubleEG"])
DoubleMuon_Run2015D     = Sample.fromDirectory(name="DoubleMuon_Run2015D",     treeName="Events", texName="DoubleMuon (Run2015D)",     directory=dirs["DoubleMuon"])
MuonEG_Run2015D         = Sample.fromDirectory(name="MuonEG_Run2015D",         treeName="Events", texName="MuonEG (Run2015D)",         directory=dirs["MuonEG"])
SingleElectron_Run2015D = Sample.fromDirectory(name="SingleElectron_Run2015D", treeName="Events", texName="SingleElectron (Run2015D)", directory=dirs["SingleElectron"])
SingleMuon_Run2015D     = Sample.fromDirectory(name="SingleMuon_Run2015D",     treeName="Events", texName="SingleMuon (Run2015D)",     directory=dirs["SingleMuon"])

DoubleEG_Run2015D      .lumi =  1000*(2.165)
DoubleMuon_Run2015D    .lumi =  1000*(2.136)
MuonEG_Run2015D        .lumi =  1000*(2.137)
SingleElectron_Run2015D.lumi =  1000*(2.165)
SingleMuon_Run2015D    .lumi =  1000*(2.129)

allSamples_Data25ns = [DoubleEG_Run2015D, MuonEG_Run2015D, DoubleMuon_Run2015D, SingleElectron_Run2015D, SingleMuon_Run2015D]
for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True
