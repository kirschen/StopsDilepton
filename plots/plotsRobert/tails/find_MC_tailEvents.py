import ROOT

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)
args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

postProcessing_directory = "postProcessed_80X_v23/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#Define chains for signals and backgrounds
samples = [
#    DY_HT_LO, 
    TTLep_pow, 
#    TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
#    TTbarDMJets_scalar_Mchi_1_Mphi_100,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_100,
#    TTbarDMJets_scalar_Mchi_1_Mphi_20,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20,
#    TTbarDMJets_scalar_Mchi_1_Mphi_50,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50,
]
#QCD_Mu5EMbcToE.name = 'QCD'

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

cuts=[
  #("==2 VT leptons (25/20)", "nGoodMuons+nGoodElectrons==2&&l1_mIsoWP>=5&&l2_mIsoWP>=5&&l1_pt>25"),
  ("filterCut", "Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter" ),
  ("==2 relIso03<0.12 leptons 25/20", "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12&&l1_pt>25"),
  ("opposite sign","isOS==1"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("MT2(ll) > 140", "dl_mt2ll>140"),
    ]

from StopsDilepton.samples.heppy_dpm_samples import mc_heppy_mapper

#invert map
heppy_sample_map = {v:k for k,v in mc_heppy_mapper.sample_map.iteritems()}

selection = "&&".join(c[1] for c in cuts)
for s in samples:
    print "Sample: s.name"
    s.setSelectionString( selection )
    r=s.treeReader(variables = map( TreeVariable.fromString, ["evt/l", "run/I", "lumi/I"]), selectionString = "(1)")
    s.chain.SetBranchStatus("*",1)
    r.start()
    while r.run():
        print "%i:%i:%i"%( r.event.run, r.event.lumi, r.event.evt )
