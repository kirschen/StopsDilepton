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

data_directory = "/afs/hephy.at/data/dspitzbart02/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
#data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
#postProcessing_directory = "postProcessed_80X_v31/dilepTiny"
#from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *
data_directory = "/afs/hephy.at/data/dspitzbart02/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
#T2tt                    = T2tt_650_1
#T2tt2                   = T2tt_500_250
#signals = [ T2tt, T2tt2]

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#Define chains for signals and backgrounds
samples = [
    TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
    DY_HT_LO, 
#    TTbarDMJets_scalar_Mchi_1_Mphi_20,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20,
#    TTbarDMJets_scalar_Mchi_1_Mphi_50,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50,
    Top_pow, 
#    TTLep_pow,
#    singleTop,
#    T2tt_650_1,
#    T2tt_500_250,
    TTbarDMJets_scalar_Mchi_1_Mphi_10_ext1,
    TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10,
]
#QCD_Mu5EMbcToE.name = 'QCD'

for s in samples:
    if s.texName.count("#"):
        s.texName = "$"+s.texName.replace("#", "\\")+"$"

T2tt_650_1.texName = "650/0"
T2tt_500_250.texName = "500/250"
Top_pow.texName = "$t\overline{t}/t$"

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

for s in samples:
    if 'TTbarDM' in s.name:
        tp = 'PS' if 'pseudoscalar' in s.name else 'S'
        s.name = "%i/%i(%s)"%(s.mChi, s.mPhi, tp)

#from StopsDilepton.tools.objectSelection import multiIsoLepString
#multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
#multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string = 'weight*reweightTopPt*reweightBTag_SF*reweightLeptonSF*reweightDilepTriggerBackup*reweightPU36fb'
lumiFac = 36.5

cuts=[
  ("==2 relIso03<0.12 leptons",  "$n_{\\textrm{lep.}==2}$",       "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12&&l1_pt>25"),
  ("opposite sign",              "opposite charge",       "isOS==1"),
  ("looseLeptonVeto",            "loose lepton veto",       "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
  ("m(ll)>20",                   "$M(ll)>20$ GeV",       "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF",     "$|M(ll)-M_{Z}| > 15$ GeV (SF)",       "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)>=15 || isEMu==1 )"),
  (">=2 jets",                   "$n_{jet}>=2$",       "nJetGood>=2"),
  (">=1 b-tags (CSVv2)",         "$n_{b-tag}>=1$",       "nBTag>=1"),
  ("MET>80",                     "$\\ETmiss>80$ GeV",       "met_pt>80"),
  ("MET/sqrt(HT)>5",             "$\\ETmiss/\\sqrt{H_{T}}>5$",       "met_pt/sqrt(ht)>5."),
  ("dPhiJetMET",                 "$\\phi(\\ETmiss, jets)$ veto",       "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("MT2(ll) > 140",              "$M_{T2}(ll)>140$ GeV",       "dl_mt2ll>140"),
    ]

cutFlowFile = "/afs/hephy.at/user/r/rschoefbeck/www/etc/cutflow.tex"
with open(cutFlowFile, "w") as cf:

    cf.write("\\begin{tabular}{r|"+"|l"*len(samples)+"} \n")
    cf.write( 30*" "+"& "+ " & ".join([ "%13s"%s.texName for s in samples ] )+"\\\\\\hline\n" )
    print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )

    for i in range(len(cuts)):
        r=[]
        for s in samples:
            selection = "&&".join(c[2] for c in cuts[:i+1])
            #selection = "&&".join(c[2] for c in cuts)
            if selection=="":selection="(1)"
            y = lumiFac*getYieldFromChain(s.chain, selection, weight_string)
            n = getYieldFromChain(s.chain, selection, '(1)')
            r.append(y)
        cf.write("%30s"%cuts[i][1]+ "& "+" & ".join([ " %12.1f"%r[j] for j in range(len(r))] )+"\\\\\n")
        print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )

    cf.write("\\end{tabular} \n")
    cf.write("\\caption{ Cutflow.} \n")
