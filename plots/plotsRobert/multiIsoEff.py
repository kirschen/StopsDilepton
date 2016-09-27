#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

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

argParser.add_argument('--mode',
    default='muEle',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle', 'dilepton', 'sameFlavour']
)

argParser.add_argument('--zMode',
    default='allZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)


argParser.add_argument('--njet',
    default='2p',
    type=str,
    action='store',
    choices=['0', '0p', '1', '1p', '2', '2p', '01']
)

argParser.add_argument('--nbtag',
    default='1p',
    action='store',
    choices=['0', '0p', '1', '1p',]
)

argParser.add_argument('--pu',
    default="reweightPU12fb",
    action='store',
    choices=["None", "reweightPU12fb", "reweightPU12fbUp", "reweightPU12fbDown"],
    help='PU weight',
)

argParser.add_argument('--small',
    action='store_true',
    #default = True,
    help='Small?',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"


# Extra requirements on data
mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadron&&Flag_badMuon"
dataFilterCut = mcFilterCut+"&&weight>0"
postProcessing_directory = "postProcessed_80X_v12/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v12/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *

sample_DoubleMuon  = DoubleMuon_Run2016BCD_backup
sample_DoubleEG    = DoubleEG_Run2016BCD_backup
sample_MuonEG      = MuonEG_Run2016BCD_backup

if args.mode=="doubleMu":
    lepton_selection_string_data = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    lepton_selection_string_mc   = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    data_samples = [sample_DoubleMuon]
    sample_DoubleMuon.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (2 #mu)"
    #qcd_sample = QCD_Mu5 #FIXME
elif args.mode=="doubleEle":
    lepton_selection_string_data = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    data_samples = [sample_DoubleEG]
    sample_DoubleEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE
elif args.mode=="muEle":
    lepton_selection_string_data = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    data_samples = [sample_MuonEG]
    sample_MuonEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (1 #mu, 1 e)"
    #qcd_sample = QCD_Mu5EMbcToE
elif args.mode=="dilepton":
    doubleMu_selectionString    = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&abs(dl_mass-91.2)>15"
    doubleEle_selectionString   = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&abs(dl_mass-91.2)>15"
    muEle_selectionString       = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"
    lepton_selection_string_mc = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"
    data_samples = [sample_DoubleMuon, sample_DoubleEG, sample_MuonEG]
    sample_DoubleMuon.setSelectionString([dataFilterCut, doubleMu_selectionString])
    sample_DoubleEG.setSelectionString([dataFilterCut, doubleEle_selectionString])
    sample_MuonEG.setSelectionString([dataFilterCut, muEle_selectionString])

    data_sample_texName = "Data"
    #qcd_sample = QCD_Mu5EMbcToE

elif args.mode=="sameFlavour":
    doubleMu_selectionString =  "&&".join([ "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    doubleEle_selectionString = "&&".join([ "isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join([ "(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2)", getZCut(args.zMode)])

    data_samples = [sample_DoubleMuon, sample_DoubleEG]
    sample_DoubleMuon.setSelectionString([dataFilterCut, doubleMu_selectionString])
    sample_DoubleEG.setSelectionString([dataFilterCut, doubleEle_selectionString])

    data_sample_texName = "Data (SF)"
    #qcd_sample = QCD_Mu5EMbcToE

else:
    raise ValueError( "Mode %s not known"%args.mode )

diBoson_samples = [diBoson]
TTJets_sample = Top
mc_samples = [ TTJets_sample] + diBoson_samples + [DY_HT_LO, TTZ_LO, TTW, triBoson]

for sample in mc_samples:
    sample.setSelectionString([ mcFilterCut, lepton_selection_string_mc])
    sample.style = styles.fillStyle( sample.color)

if args.small:
    for s in data_samples + mc_samples:
        s.reduceFiles( to = 1 )

#Averaging lumi
lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000
logger.info( "Lumi scale for mode %s is %3.2f", args.mode, lumi_scale )

for s in data_samples:
    s.scale = 1
for s in mc_samples:
    s.scale = lumi_scale


mc_weight_string = "weight*reweightDilepTriggerBackup*reweightBTag_SF*reweightLeptonSF*reweightLeptonHIPSF"
if args.pu != "None":
    mc_weight_string+="*"+args.pu
data_weight_string = "weight"


def mCutStr( arg ):
    if not arg in ['0', '0p', '1', '1p', '2', '2p', '01']: raise ValueError( "Don't know what to do with cut %s" % arg )

    if arg=='0':
        return '==0'
    elif arg=='0p':
        return '>=0'
    elif arg=='1':
        return '==1'
    elif arg=='1p':
        return '>=1'
    elif arg=='2':
        return '==2'
    elif arg=='2p':
        return '>=2'
    elif arg=='01':
        return '<=1'


cuts=[
    ("isOS","isOS"),
    ("mll20", "dl_mass>20"),
    ("l1pt25", "l1_pt>25"),
    #("mIsoVT", "l1_mIsoWP>=5&&l2_mIsoWP>=5"),
    ("mIsoVTleading", "l1_mIsoWP>=5"),
    ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("met80", "met_pt>80"),
    ("metSig5", "(met_pt/sqrt(ht)>5||nJetGood==0)"),
    ("njet%s"%args.njet, "nJetGood%s"%mCutStr( args.njet )),
    ("nbtag%s"%args.nbtag, "nBTag%s"%mCutStr( args.nbtag ))
]

selectionString = "&&".join( [p[1] for p in cuts] )


wpStr = { 5: "VT", 4: "T", 3: "M" , 2: "L" , 1: "VL", 0:"None"}

ratio = {}
for nvtxl, nvtxh in [[-1, 12], [12, 18], [18,100], [-1,100]]:
    nvtxcut = "nVert>%i&&nVert<=%i"%(nvtxl, nvtxh)
    for wp in [0,1,2,3,4,5]:

        yield_mc    = {s.name: s.scale*s.getYieldFromDraw( selectionString = selectionString+"&&"+nvtxcut+"&&dl_mt2ll<100&&l2_mIsoWP>=%i"%wp, weightString = mc_weight_string)['val'] for s in mc_samples}
        yield_mc = sum(yield_mc.values())
        yield_data  = sum(s.getYieldFromDraw( selectionString = selectionString+"&&"+nvtxcut+"&&dl_mt2ll<100&&l2_mIsoWP>=%i"%wp, weightString = data_weight_string)['val'] for s in data_samples)

        ratio[wp] = yield_data/yield_mc
        logger.info( "nVert: %s MultiIso WP trailing %i %6s data %5.2f mc %5.2f ratio %3.2f", nvtxcut, wp, wpStr[wp], yield_data, yield_mc, ratio[wp] )
