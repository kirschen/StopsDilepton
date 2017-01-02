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

postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v16/dilepTiny"
data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#Define chains for signals and backgrounds
samples = [
    DY_HT_LO, 
    Top_pow, 
    TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
    TTbarDMJets_scalar_Mchi_1_Mphi_100,
    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_100,
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

for s in samples:
    if 'TTbarDM' in s.name:
        tp = 'PS' if 'pseudoscalar' in s.name else 'S'
        s.name = "%i/%i(%s)"%(s.mChi, s.mPhi, tp)

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string = 'weight*reweightDilepTriggerBackup*reweightLeptonSF'
lumiFac = 36.5

cuts=[
  #("==2 VT leptons (25/20)", "nGoodMuons+nGoodElectrons==2&&l1_mIsoWP>=5&&l2_mIsoWP>=5&&l1_pt>25"),
  ("==2 relIso03<0.12 leptons", "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12"),
  ("opposite sign","isOS==1"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("MT2(ll) < 100", "dl_mt2ll<100"),
#  ("multiIso M(Mu), T(Ele)", multiIsoWPMT),
#  ("multiIso VT(Mu), VT(Ele)", multiIsoWPVTVT),
#  ("filterCut", "Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter" ),
# ("relIso04<0.12", relIso04sm12Cut),
# ("MT2(ll) > 240", "dl_mt2ll>240"),
    ]

print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )
#for i in reversed(range(len(cuts))):
for i in range(len(cuts)):
    r=[]
    for s in samples:
        selection = "&&".join(c[1] for c in cuts[:i+1])
        if selection=="":selection="(1)"
        y = lumiFac*getYieldFromChain(s.chain, selection, weight_string)
        n = getYieldFromChain(s.chain, selection, '(1)')
        r.append(y)
    print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )
