import copy, os, sys
from StopsDilepton.tools.user import data_output_directory
from RootTools.core.Sample import Sample 
import ROOT

dirs = {}
dirs['DoubleEG']       = ["DoubleEG_Run2015D_16Dec"]
dirs['DoubleMuon']     = ["DoubleMuon_Run2015D_16Dec"]
dirs['MuonEG']         = ["MuonEG_Run2015D_16Dec"]
dirs['SingleElectron'] = ["SingleElectron_Run2015D_16Dec"]
dirs['SingleMuon']     = ["SingleMuon_Run2015D_16Dec"]

for key in dirs:
  dirs[key] = [ os.path.join( data_output_directory, 'postProcessed_Fall15_mAODv2/dilepTiny', dir) for dir in dirs[key]]

lumi = {}
lumi['DoubleEG']       = 1000*(2.517)
lumi['DoubleMuon']     = 1000*(2.517)
lumi['MuonEG']         = 1000*(2.517)
lumi['SingleElectron'] = 1000*(2.517)
lumi['SingleMuon']     = 1000*(2.517)

DoubleEG_Run2015D       = Sample.fromDirectory(name="DoubleEG_Run2015D",       treeName="Events", texName="DoubleEG (Run2015D)",       directory=dirs["DoubleEG"])
DoubleMuon_Run2015D     = Sample.fromDirectory(name="DoubleMuon_Run2015D",     treeName="Events", texName="DoubleMuon (Run2015D)",     directory=dirs["DoubleMuon"])
#MuonEG_Run2015D         = Sample.fromDirectory(name="MuonEG_Run2015D",         treeName="Events", texName="MuonEG (Run2015D)",         directory=dirs["MuonEG"])
#SingleElectron_Run2015D = Sample.fromDirectory(name="SingleElectron_Run2015D", treeName="Events", texName="SingleElectron (Run2015D)", directory=dirs["SingleElectron"])
#SingleMuon_Run2015D     = Sample.fromDirectory(name="SingleMuon_Run2015D",     treeName="Events", texName="SingleMuon (Run2015D)",     directory=dirs["SingleMuon"])

#allSamples_Data25ns = [DoubleEG_Run2015D, MuonEG_Run2015D, DoubleMuon_Run2015D, SingleElectron_Run2015D, SingleMuon_Run2015D]
allSamples_Data25ns = [DoubleEG_Run2015D]
for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True
