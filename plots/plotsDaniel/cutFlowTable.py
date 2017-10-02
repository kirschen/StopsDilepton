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

#postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
#from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import VVTo2L2Nu as VVTo2L2Nu_old

postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *

postProcessing_directory = "postProcessed_80X_v31/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *

postProcessing_directory = "postProcessed_80X_v40/dilepTiny"
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *

T2tt                    = T2tt_750_1
T2tt2                   = T2tt_600_300
TTbarDM                 = TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
TTbarDM2                = TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10
signals = [ T2tt, T2tt2, TTbarDM, TTbarDM2]

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#Define chains for signals and backgrounds
samples = [
#    TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
#    DY_HT_LO,
    #VVTo2L2Nu,
    #VVTo2L2Nu_old,
    #TTbarDMJets_scalar_Mchi_1_Mphi_100,
    #TTbarDMJets_pseudoscalar_Mchi_1_Mphi_100,
#    TTbarDMJets_scalar_Mchi_1_Mphi_20,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20,
#    TTbarDMJets_scalar_Mchi_1_Mphi_50,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50,
#    Top_pow, 
    T2tt_750_1,
    T2tt_600_300,
    TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10,
    TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10
]
#QCD_Mu5EMbcToE.name = 'QCD'

for s in samples:
    if s.texName.count("#"):
        s.texName = "$"+s.texName.replace("#", "\\")+"$"

#T2tt_750_1.texName = "750/0"
#T2tt_600_300.texName = "600/300"
#Top_pow.texName = "$t\overline{t}/t$"

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

for s in samples:
    if 'TTbarDM' in s.name:
        tp = 'PS' if 'pseudoscalar' in s.name else 'S'
        s.name = "%i/%i(%s)"%(s.mChi, s.mPhi, tp)

relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

lumiFac = 35.9

presel = '&&Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadronSummer2016'

cuts=[
  ("entry point",                "entry point", "(1)"), 
  ("SFs and 2l skim",            "SF + loose 2l skim", "(1)"),
  ("==2 relIso03<0.12 leptons",  "$n_{\\textrm{lep.}==2}$",       "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12&&l1_pt>25"+presel),
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


cutFlowFile = "cutflow_signal_preFR.tex"
with open(cutFlowFile, "w") as cf:

    cf.write("\\begin{tabular}{r|"+"|l"*len(samples)+"} \n")
    cf.write( 30*" "+"& "+ " & ".join([ "%13s"%s.texName for s in samples ] )+"\\\\\\hline\n" )
    print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )
    firstLine = True
    for i in range(len(cuts)):
        r=[]
        for s in samples:
            selection = "&&".join(c[2] for c in cuts[:i+1])
            #selection = "&&".join(c[2] for c in cuts)
            if selection=="":selection="(1)"
            if firstLine:
                weight_string = 'weight'
            else:
                if 'T2tt' in s.name:
                    weight_string = 'weight * reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightTopPt * reweightLeptonTrackingSF * reweightLeptonFastSimSF'
                else:
                    weight_string = 'weight * reweightDilepTriggerBackup * reweightLeptonSF * reweightPU36fb * reweightBTag_SF * reweightTopPt * reweightLeptonTrackingSF'


            y = lumiFac*getYieldFromChain(s.chain, selection, weight_string)
            n = getYieldFromChain(s.chain, selection, '(1)')
            r.append(y)
        cf.write("%30s"%cuts[i][1]+ "& "+" & ".join([ " %12.1f"%r[j] for j in range(len(r))] )+"\\\\\n")
        print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )
        firstLine = False
    cf.write("\\end{tabular} \n")
    cf.write("\\caption{ Cutflow.} \n")
