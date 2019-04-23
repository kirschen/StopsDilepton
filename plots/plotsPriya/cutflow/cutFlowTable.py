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
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--year',               action='store', type=int,      default=2016)
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

if args.year == 2016:
    data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]

#from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
#data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
#postProcessing_directory = "postProcessed_80X_v31/dilepTiny"
#from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *
#data_directory = "/afs/hephy.at/data/dspitzbart02/cmgTuples/"
#postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
#postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
    #from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    #mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
elif args.year == 2017:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    postProcessing_directory = "stops_2017_nano_v0p4/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
elif args.year == 2018:
    data_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2018_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    postProcessing_directory = "stops_2018_nano_v0p5/dilep/"
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]

#from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
#T2tt                    = T2tt_650_1
#T2tt2                   = T2tt_500_250
#signals = [ T2tt, T2tt2]

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#Define chains for signals and backgrounds
samples = [ mc

#    Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16
 
   #Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17
    #TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
    #DY_HT_LO, 
#    TTbarDMJets_scalar_Mchi_1_Mphi_20,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20,
#    TTbarDMJets_scalar_Mchi_1_Mphi_50,
#    TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50,
    #Top_pow, 
#    TTLep_pow,
#    singleTop,
    #T2tt_650_1,
    #T2tt_500_250,
    #TTbarDMJets_scalar_Mchi_1_Mphi_10_ext1,
    #TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10,

]
#QCD_Mu5EMbcToE.name = 'QCD'

for s in samples:
    if s.texName.count("#"):
        s.texName = "$"+s.texName.replace("#", "\\")+"$"

if args.small:
    for sample in samples:
        sample.reduceFiles( factor = 10)

data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
if args.signal == "T2tt":
    if args.year == 2016:
        postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import *
    else:
        postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
        from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import *

#    postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
#   from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import *

    T2tt                    = T2tt_650_0
    T2tt2                   = T2tt_500_250
    T2tt2.style             = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3 )
    signals = [ T2tt, T2tt2]
elif args.signal == "T8bbllnunu":
    postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
    T8bbllnunu              = T8bbllnunu_XCha0p5_XSlep0p95_1300_1
    T8bbllnunu2             = T8bbllnunu_XCha0p5_XSlep0p95_1300_300
    T8bbllnunu3             = T8bbllnunu_XCha0p5_XSlep0p95_1300_600
    T8bbllnunu3.style       = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
    T8bbllnunu2.style       = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T8bbllnunu.style        = styles.lineStyle( ROOT.kBlack, width=3 )
    signals = [ T8bbllnunu, T8bbllnunu2, T8bbllnunu3 ]
elif args.signal == "compilation":
    postProcessing_directory = "postProcessed_80X_v30/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
    postProcessing_directory = "postProcessed_80X_v30/dilepTiny"
    from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
    T2tt                    = T2tt_800_1
    T8bbllnunu              = T8bbllnunu_XCha0p5_XSlep0p05_800_1
    T8bbllnunu2             = T8bbllnunu_XCha0p5_XSlep0p5_800_1
    T8bbllnunu3             = T8bbllnunu_XCha0p5_XSlep0p95_800_1
    T2tt.style              = styles.lineStyle( ROOT.kGreen-3, width=3 )
    T8bbllnunu.style        = styles.lineStyle( ROOT.kBlack, width=3 )
    T8bbllnunu2.style        = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T8bbllnunu3.style       = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
    signals = [ T2tt, T8bbllnunu, T8bbllnunu2, T8bbllnunu3 ]
else:
    signals = []



#T2tt_650_1.texName = "650/0"
#T2tt_500_250.texName = "500/250"
#Top_pow.texName = "$t\overline{t}/t$"

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

#for s in samples:
#    if 'TTbarDM' in s.name:
#        tp = 'PS' if 'pseudoscalar' in s.name else 'S'
#        s.name = "%i/%i(%s)"%(s.mChi, s.mPhi, tp)

#from StopsDilepton.tools.objectSelection import multiIsoLepString
#multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
#multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string = 'weight*reweightLeptonTrackingSF*reweightBTag_SF*reweightLeptonSF*reweightDilepTrigger*reweightPU36fb'
lumiFac = 150

cuts=[
  ("==2 relIso03<0.12 leptons",  "$n_{\\textrm{lep.}==2}$",       "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12&&l1_pt>25"),
  ("opposite sign",              "opposite charge",       "isOS==1"),
  ("looseLeptonVeto",            "loose lepton veto",       "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2"),
  ("m(ll)>20",                   "$M(ll)>20$ GeV",       "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF",     "$|M(ll)-M_{Z}| > 15$ GeV (SF)",       "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)>=15 || isEMu==1 )"),
  (">=2 jets",                   "$n_{jet}>=2$",       "nJetGood>=2"),
  (">=1 b-tags (CSVv2)",         "$n_{b-tag}>=1$",       "nBTag>=1"),
  ("MET>80",                     "$\\ETmiss>80$ GeV",       "met_pt>80"),
  ("MET/sqrt(HT)>5",             "$\\ETmiss/\\sqrt{H_{T}}>5$",       "met_pt/sqrt(ht)>5."),
  ("dPhiJetMET",                 "$\\phi(\\ETmiss, jets)$ veto",       "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("MT2(ll) > 140",              "$M_{T2}(ll)>140$ GeV",       "dl_mt2ll>140"),
    ]

cutFlowFile = "/afs/hephy.at/user/p/phussain/www/stopsDilepton/analysisPlots/2016/cutflowmod.tex"
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
    if args.year == 2016:
        cf.write("\\2016{ Cutflow.} \n")
    elif args.year == 2017:
        cf.write("\\2017{ Cutflow.} \n")
    else:
        cf.write("\\2018{ Cutflow.} \n")


