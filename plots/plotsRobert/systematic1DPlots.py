''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import copy
import pickle

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
    #default='muEle',
    default='dilepton',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle', 'dilepton', 'sameFlavour'])

argParser.add_argument('--charges',
    default='OS',
    action='store',
    choices=['OS', 'SS'])

argParser.add_argument('--zMode',
    default='offZ',
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

argParser.add_argument('--small',
    action='store_true',
    default=True,
    help='Small?',
)

argParser.add_argument('--met',
    default='def',
    action='store',
    choices=['def', 'none', 'low'],
    help='met cut',
)

argParser.add_argument('--normalizeBinWidth',
    action='store_true',
    help='normalize wider bins?',
)

argParser.add_argument('--signals',
    action='store',
    nargs='*',
    type=str,
    default=[ "T2tt_450_0" ],
    help="Signals?"
    )

argParser.add_argument('--overwrite',
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='80X_v10_systematics',
    action='store',
)

argParser.add_argument('--analysisSelection',
    default='',
    action='store',
)

argParser.add_argument('--sysScaling',
    action='store_true',
    #default=True,
    help='sysScaling?',
)

argParser.add_argument('--dataMCScaling',
    action='store_true',
    #default=True,
    help='dataMCScaling?',
)


args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples

mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadron&&Flag_badMuon"
dataFilterCut = mcFilterCut+"&&weight>0"
postProcessing_directory = "postProcessed_80X_v10/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v10/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

if args.mode=="doubleMu":
    lepton_selection_string = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    trigger = "HLT_mumuIso"
    data_samples = [DoubleMuon_Run2016B]
    data_sample_texName = "Data (2 #mu)"
    #qcd_sample = QCD_Mu5 #FIXME
    DoubleMuon_Run2016B.setSelectionString([dataFilterCut, lepton_selection_string, trigger])
elif args.mode=="doubleEle":
    lepton_selection_string = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    trigger = "HLT_ee_DZ"
    data_samples = [DoubleEG_Run2016B]
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE
    DoubleEG_Run2016B.setSelectionString([dataFilterCut, lepton_selection_string, trigger])
elif args.mode=="muEle":
    lepton_selection_string = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    trigger = "HLT_mue"
    data_samples = [MuonEG_Run2016B]
    data_sample_texName = "Data (1 #mu, 1 e)"
    #qcd_sample = QCD_Mu5EMbcToE
    MuonEG_Run2016B.setSelectionString([dataFilterCut, lepton_selection_string, trigger])
elif args.mode=="dilepton":
    doubleMu_selectionString = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&HLT_mumuIso&&abs(dl_mass-91.2)>15"
    doubleEle_selectionString = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&HLT_ee_DZ&&abs(dl_mass-91.2)>15"
    muEle_selectionString = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1&&HLT_mue"
    lepton_selection_string = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"

    data_samples = [DoubleMuon_Run2016B, DoubleEG_Run2016B, MuonEG_Run2016B] 
    data_sample_texName = "Data"
    #qcd_sample = QCD_Mu5EMbcToE

    DoubleMuon_Run2016B.setSelectionString([dataFilterCut, doubleMu_selectionString])
    DoubleEG_Run2016B.setSelectionString([dataFilterCut, doubleEle_selectionString])
    MuonEG_Run2016B.setSelectionString([dataFilterCut, muEle_selectionString])

elif args.mode=="sameFlavour":
    doubleMu_selectionString =  "&&".join([ "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&HLT_mumuIso", getZCut(args.zMode)])
    doubleEle_selectionString = "&&".join([ "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&HLT_ee_DZ", getZCut(args.zMode)])
    lepton_selection_string = "&&".join([ "(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2)", getZCut(args.zMode)])

    data_samples = [DoubleMuon_Run2016B, DoubleEG_Run2016B] 
    data_sample_texName = "Data (SF)"
    #qcd_sample = QCD_Mu5EMbcToE

    DoubleMuon_Run2016B.setSelectionString([dataFilterCut, doubleMu_selectionString])
    DoubleEG_Run2016B.setSelectionString([dataFilterCut, doubleEle_selectionString])
else:
    raise ValueError( "Mode %s not known"%args.mode )


mc_samples = [ DY_HT_LO, Top, TTZ_LO, TTXNoZ, multiBoson]
DY_HT_LO.texName  = "DY + jets"

if args.small:
    for sample in mc_samples+ data_samples:
        sample.reduceFiles(to = 1)
    
for d in data_samples:
    d.style = styles.errorStyle( ROOT.kBlack )

#Averaging lumi
lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000
logger.info( "Lumi scale for mode %s is %3.2f", args.mode, lumi_scale )
for sample in mc_samples:
    sample.setSelectionString([ mcFilterCut, lepton_selection_string])
    sample.style = styles.fillStyle( sample.color)

from StopsDilepton.tools.user import plot_directory

common_selection=[
    ("l1pt25", "l1_pt>25"),
    ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("mll20", "dl_mass>20"),
]

analysis_selection=[
]

if "mt2ll100" in args.analysisSelection:
    analysis_selection.append( ("mt2ll100", "dl_mt2ll>100") )

jet_systematics = ['JECUp','JECDown']# 'JERDown','JECVUp','JECVDown']
met_systematics = ['UnclusteredEnUp', 'UnclusteredEnDown']
weight_systematics = ['PUUp', 'PUDown', 'TopPt', 'BTag_SF_b_Down', 'BTag_SF_b_Up', 'BTag_SF_l_Down', 'BTag_SF_l_Up']

sys_pairs = [\
    ('JEC', 'JECUp', 'JECDown'),
#    ('JECV', 'JECVUp', 'JECVDown'),

    ('Unclustered', 'UnclusteredEnUp', 'UnclusteredEnDown'),
    ('PU', 'PUUp', 'PUDown'),
    ('TopPt', 'TopPt', None),

#    ('JER', 'JERUp', 'JERDown'),
    ('BTag_b', 'BTag_SF_b_Down', 'BTag_SF_b_Up' ),
    ('BTag_l', 'BTag_SF_l_Down', 'BTag_SF_l_Up'),
]

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

jme_systematics = jet_systematics + met_systematics

def systematic_selection( sys = None ):
    if sys is None: 
        res = [ \
            ("njet%s"%args.njet, "nJetGood%s"%mCutStr( args.njet )),
            ("nbtag%s"%args.nbtag, "nBTag%s"%mCutStr( args.nbtag ))]
        if args.met=='def': res.extend([\
            ("met80", "met_pt>80"),
            ("metSig5", "met_pt/sqrt(ht)>5")])
        elif args.met=='low':
            res.extend([  ("metSm80", "met_pt<80")] )
        elif args.met=='none':
            pass
        return res
    elif sys in jet_systematics: 
        res = [\
            ("njet%s"%args.njet, "nJetGood_%s%s"%( sys, mCutStr(args.njet) )),
            ("nbtag%s"%args.nbtag, "nBTag_%s%s"%( sys, mCutStr(args.nbtag) ))]
        if args.met=='def': res.extend([\
            ("met80", "met_pt_"+sys+">80"),
            ("metSig5", "metSig_"+sys+">5")])
        elif args.met=='low':
            res.extend([  ("metSm80", "met_pt_"+sys+"<80")] )
        elif args.met=='none':
            pass
        return res
    elif sys in met_systematics: 
        res = [\
            ("njet%s"%args.njet, "nJetGood%s"%mCutStr( args.njet )),
            ("nbtag%s"%args.nbtag, "nBTag%s"%mCutStr( args.nbtag ))]
        if args.met=='def': res.extend([\
            ("met80", "met_pt_"+sys+">80"),
            ("metSig5", "metSig_"+sys+">5")])
        elif args.met=='low':
            res.extend([  ("metSm80", "met_pt_"+sys+"<80")] )
        elif args.met=='none':
            pass
        return res
    elif sys in weight_systematics:
        return systematic_selection( sys = None )
    else: raise ValueError( "Systematic %s not known"%sys )


def weightMC( sys = None ):
    if sys is None:
        return (lambda data:data.weight*data.reweightPU*data.reweightDilepTrigger*data.reweightBTag_SF, "weight*reweightDilepTrigger*reweightPU*reweightBTag_SF")
    elif 'PU' in sys:
        return (lambda data:data.weight*getattr(data, "reweight"+sys)*data.reweightDilepTrigger*data.reweightBTag_SF, "weight*reweightDilepTrigger*reweight"+sys+"*reweightBTag_SF")
    elif 'BTag' in sys:
        return (lambda data:data.weight*data.reweightPU*data.reweightDilepTrigger*getattr(data, "reweight"+sys), "weight*reweightDilepTrigger*reweightPU*reweight"+sys)
    elif sys in weight_systematics:
        return (lambda data:data.weight*data.reweightDilepTrigger*data.reweightPU*data.reweightBTag_SF*getattr(data, "reweight"+sys), "weight*reweightDilepTrigger*reweightPU*reweightBTag_SF*reweight"+sys)
    elif sys in jme_systematics :
        return weightMC( sys = None )
    else: raise ValueError( "Systematic %s not known"%sys )

def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if dataMCScale is not None:
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*10)/10., dataMCScale ) ) )
    else:
        lines.append( (0.50, 0.95, '13 TeV' ) )
    return [tex.DrawLatex(*l) for l in lines]

stack_mc = Stack( mc_samples )
stack_data = Stack( data_samples )

sequence = []

for sample in mc_samples:
    sample.read_variables = ["reweight%s/F"%s for s in weight_systematics]
    sample.read_variables += ["dl_mt2ll_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["dl_mt2bb_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["dl_mt2blbl_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["nJetGood_%s/I"%s for s in jet_systematics]
    sample.read_variables += ["nBTag_%s/I"%s for s in jet_systematics]
    #if args.pu is not None: sample.read_variables += [args.pu+'/F']
    sample.read_variables += ['reweightPU/F', 'reweightDilepTrigger/F', 'reweightBTag_SF/F']

# Charge requirements
if args.charges=="OS":
    selection = [("isOS","isOS")]
elif args.charges=="SS":
    selection = [("isSS","l1_pdgId*l2_pdgId>0")]
else:
    raise ValueError

selection.extend( common_selection )

ppfixes = [args.mode, args.zMode] if not args.mode=='dilepton' else [args.mode]
#if args.pu is not None: ppfixes = [args.pu] + ppfixes
if args.dataMCScaling: ppfixes.append( "dataMCScaled" )
if args.sysScaling: ppfixes.append( "sysScaled" )
ppfixes.append('triggerSF')
if args.small: ppfixes = ['small'] + ppfixes
prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in selection + analysis_selection + systematic_selection( sys = None )] ) ] )

plot_path = os.path.join(plot_directory, args.plot_directory, prefix)

result_file = os.path.join(plot_path, 'results.pkl')

common_selection_string = "&&".join( p[1] for p in selection )

logger.info( "Prefix %s common_selection_string %s", prefix, common_selection_string )

data_selection_string = "&&".join( s[1] for s in systematic_selection( sys = None ) )
analysis_selection_string = "&&".join( s[1] for s in analysis_selection ) if len(analysis_selection)>0 else "1"

data_weight_func, data_weight_string = lambda data:data.weight, "weight"

sys_stacks = {sys:copy.deepcopy(stack_mc) for sys in [None] + weight_systematics + jme_systematics }

roottools_plots = []
dl_mt2ll_data  = Plot(
    name = "dl_mt2ll_data",
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    binning=Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2ll/F" ),
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    )
roottools_plots.append( dl_mt2ll_data )

dl_mt2ll_mc  = { sys:Plot(\
    name = "dl_mt2ll" if sys is None else "dl_mt2ll_mc_%s" % sys,
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    binning=Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2ll/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2ll_%s/F" % sys ),
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2ll_mc.values() )

dl_mt2bb_data  = Plot( 
    name = "dl_mt2bb_data",
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2bb/F" ),
    binning=Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450]),
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    ) 
roottools_plots.append( dl_mt2bb_data )

dl_mt2bb_mc  = {sys: Plot(
    name = "dl_mt2bb" if sys is None else "dl_mt2bb_mc_%s" % sys,
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2bb/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2bb_%s/F" % sys ),
    binning=Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450]),
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2bb_mc.values() )

dl_mt2blbl_data  = Plot( 
    name = "dl_mt2blbl_data",
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2blbl/F" ),
    binning=Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350]),
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    ) 
roottools_plots.append( dl_mt2blbl_data )

dl_mt2blbl_mc  = {sys: Plot(
    name = "dl_mt2blbl" if sys is None else "dl_mt2blbl_mc_%s" % sys,
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2blbl/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2blbl_%s/F" % sys ),
    binning=Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350]),
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2blbl_mc.values() )

nbtags_data  = Plot( 
    name = "nbtags_data",
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = stack_data,
    variable = Variable.fromString('nBTag/I'),
    binning=[5,1,6],
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    ) 
roottools_plots.append( nbtags_data )

nbtags_mc  = {sys: Plot(
    name = "nbtags" if sys is None else "nbtags_mc_%s" % sys,
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = sys_stacks[sys],
    variable = Variable.fromString('nBTag/I') if sys is None or sys in weight_systematics or sys in met_systematics else Variable.fromString( "nBTag_%s/I" % sys ),
    binning=[5,1,6],
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( nbtags_mc.values() )

njets_data  = Plot( 
    name = "njets_data",
    texX = 'number of jets', texY = 'Number of Events',
    stack = stack_data,
    variable = Variable.fromString('nJetGood/I'),
    binning=[8,2,10],
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    )
roottools_plots.append( njets_data )

njets_mc  = {sys: Plot(
    name = "njets" if sys is None else "njets_mc_%s" % sys,
    texX = 'number of jets', texY = 'Number of Events',
    stack = sys_stacks[sys],
    variable = Variable.fromString('nJetGood/I') if sys is None or sys in weight_systematics or sys in met_systematics else Variable.fromString( "nJetGood_%s/I" % sys ),
    binning=[8,2,10],
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( njets_mc.values() )

met_data  = Plot( 
    name = "met_data",
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = stack_data, 
    variable = Variable.fromString( "met_pt/F" ),
    binning=Binning.fromThresholds( [0,80,130,180,230,280,320,420,520,800] if args.met != 'def' else [80,130,180,230,280,320,420,520,800]),
    selectionString = "&&".join([ analysis_selection_string, common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    )
roottools_plots.append( met_data )

met_mc  = {sys: Plot(
    name = "met_pt" if sys is None else "met_pt_mc_%s" % sys,
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV' if args.normalizeBinWidth else "Number of Event",
    stack = sys_stacks[sys],
    variable = Variable.fromString('met_pt/F') if sys not in met_systematics else Variable.fromString( "met_pt_%s/F" % sys ),
    binning=Binning.fromThresholds( [0,80,130,180,230,280,320,420,520,800] if args.met != 'def'  else [80,130,180,230,280,320,420,520,800]),
    selectionString = "&&".join( [analysis_selection_string, common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weightMC( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( met_mc.values() )

plots = [\
#         [ dl_mt2ll_mc, dl_mt2ll_data, (0,100), 20],
#         [ dl_mt2bb_mc, dl_mt2bb_data, (70,170), 20],
#         [ dl_mt2blbl_mc, dl_mt2blbl_data,  (0,100), 20],
#         [ njets_mc, njets_data, (3,3), -1],
#         [ nbtags_mc, nbtags_data, (1,1), -1],
#         [ met_mc, met_data , (80,80), 50],
         [ dl_mt2ll_mc, dl_mt2ll_data, 20],
         [ dl_mt2bb_mc, dl_mt2bb_data, 20],
         [ dl_mt2blbl_mc, dl_mt2blbl_data, 20],
         [ njets_mc, njets_data, -1],
         [ nbtags_mc, nbtags_data, -1],
         [ met_mc, met_data, 50],
    ]

if os.path.exists(result_file) and not args.overwrite:

    (all_histos, top_sf) = pickle.load(file( result_file ))
    logger.info( "Loaded plots from %s", result_file )
    for i_plot, plot_ in enumerate(plots):
        #p_mc, p_data, x_norm, bin_width = plot_
        p_mc, p_data, bin_width = plot_
        for k in p_mc.keys():
            p_mc[k].histos = all_histos[i_plot][0][k] 
        p_data.histos = all_histos[i_plot][1]
else:
    # Applying systematic variation

    mc_selection_string = "&&".join( s[1] for s in systematic_selection( sys = None ) )
    mc_weight_func, mc_weight_string = weightMC( sys = None )

    logger.info( "Calculating normalization constants:" )
    logger.info( "data_selection_string: %s", data_selection_string  )
    logger.info( "mc_selection_string:   %s", mc_selection_string  )
    logger.info( "data_weight_string:    %s", data_weight_string  )
    logger.info( "mc_weight_string:      %s", mc_weight_string  )

    for s in data_samples:
        s.scale = 1
    for s in mc_samples:
        s.scale = lumi_scale
    #for s in diBoson_samples:
    #    s.scale*=args.diBosonScaleFactor

    #Scaling MC to data in MT2ll<100 region
    normalization_region_cut = "dl_mt2ll<100"
    top_sf = {}
    if args.dataMCScaling or args.sysScaling:
        #for s in mc_samples:
        yield_mc    = {s.name:s.scale*s.getYieldFromDraw( selectionString = "&&".join([ common_selection_string, mc_selection_string, normalization_region_cut ] ), weightString = mc_weight_string)['val'] for s in mc_samples}
    if args.dataMCScaling:
        yield_data  = sum(s.getYieldFromDraw( selectionString = "&&".join([ common_selection_string, data_selection_string, normalization_region_cut ] ), weightString = data_weight_string)['val'] for s in data_samples )
        yield_non_top = sum(yield_mc[s.name] for s in mc_samples if s.name != Top.name)
        top_sf[None]  = (yield_data - yield_non_top)/yield_mc[Top.name]
        total = yield_data
        logger.info( "Data: %i MC TT %3.2f MC other %3.2f SF %3.2f", yield_data, yield_mc[Top.name], yield_non_top, top_sf[None] )
    elif args.sysScaling:
        top_sf[None] = 1
        total = sum(yield_mc.values())
    else:
        top_sf[None] = 1

    #Scaling systematic shapes to MT2ll<100 region
    for sys_pair in sys_pairs:
        for sys in sys_pair[1:]:
            if not top_sf.has_key( sys ):
                if args.sysScaling:
                    mc_sys_selection_string = "&&".join( s[1] for s in systematic_selection( sys = sys ) )
                    mc_sys_weight_func, mc_sys_weight_string = weightMC( sys = sys )
                    yield_sys_mc = {s.name:s.scale*s.getYieldFromDraw( selectionString = "&&".join([ common_selection_string, mc_sys_selection_string, normalization_region_cut ] ), weightString = mc_sys_weight_string)['val'] for s in mc_samples}
                    non_top = sum(yield_sys_mc[s.name] for s in mc_samples if s.name != Top.name)
                    top_sf[sys]  = (total - non_top)/yield_sys_mc[Top.name]
                    logger.info( "Total: %i sys %s MC TT %3.2f MC other %3.2f SF %3.2f", total, sys, yield_sys_mc[Top.name], non_top, top_sf[sys] )
                else:
                     top_sf[sys] = top_sf[None]

    read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]"]
    plotting.fill(roottools_plots, read_variables = read_variables, sequence = sequence)

    
    if not os.path.exists(os.path.dirname( result_file )):
        os.makedirs(os.path.dirname( result_file ))

    all_histos = []
    #for p_mc, p_data, x_norm, bin_width in plots:
    for p_mc, p_data, bin_width in plots:
        mc_histos = {k:p_mc[k].histos for k in p_mc.keys()}
        data_histos = p_data.histos
        all_histos.append( (mc_histos, data_histos) )

    pickle.dump( (all_histos, top_sf), file( result_file, 'w' ) )
    logger.info( "Written %s", result_file)

if not os.path.exists( plot_path ): os.makedirs( plot_path )

### Ad Hoc
#for i_plot, plot_ in enumerate(plots):
#    p_mc, p_data, bin_width = plot_
#    for k in p_mc.keys():
#        for h in p_mc[k].histos[0]:
#            if 'DY' in h.GetName():
#                scale = 2
#                logger.info("Add hoc scaling of scaling DY by %3.2f for %s in plot %s", scale, k, p_mc[k].name)
#                h.Scale(scale)
#            if 'TTZ' in h.GetName():
#                scale = 1.3
#                logger.info("Add hoc scaling of scaling TTZ by %3.2f for %s in plot %s", scale, k, p_mc[k].name)
#                h.Scale(scale)
#
#for plot_mc, plot_data, x_norm, bin_width in plots:
for plot_mc, plot_data, bin_width in plots:
    if args.normalizeBinWidth and bin_width>0:
            for p in plot_mc.values() + [plot_data]:
                for histo in sum(p.histos, []): 
                    for ib in range(histo.GetXaxis().GetNbins()+1):
                        val = histo.GetBinContent( ib )
                        err = histo.GetBinError( ib )
                        width = histo.GetBinWidth( ib )
                        histo.SetBinContent(ib, val / (width / bin_width)) 
                        histo.SetBinError(ib, err / (width / bin_width)) 

    # Scaling Top
    for k in plot_mc.keys():
        for s in plot_mc[k].histos:
            for h in s:
                h.Scale(lumi_scale)
            pos_top = [i for i,x in enumerate(mc_samples) if x == Top][0]
            plot_mc[k].histos[0][pos_top].Scale(top_sf[k]) 
                    
    #Calculating systematics
    h_summed = {k: plot_mc[k].histos_added[0][0].Clone() for k in plot_mc.keys()}

    ##Normalize systematic shapes
    #if args.sysScaling:
    #    for k in h_summed.keys():
    #        if k is None: continue
    #        h_summed[k].Scale( top_sf[ k ] )

    h_rel_err = h_summed[None].Clone()
    h_rel_err.Reset()

    #MC statistical error
    for ib in range( 1 + h_rel_err.GetNbinsX() ):
        h_rel_err.SetBinContent(ib, h_summed[None].GetBinError(ib)**2 )

    h_sys = {}
    for k, s1, s2 in sys_pairs:
        h_sys[k] = h_summed[s1].Clone()
        h_sys[k].Scale(-1)
        h_sys[k].Add(h_summed[s2])

    # Adding in quadrature
    for k in h_sys.keys():
        for ib in range( 1 + h_rel_err.GetNbinsX() ):
            h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + h_sys[k].GetBinContent(ib)**2 )

    # take sqrt
    for ib in range( 1 + h_rel_err.GetNbinsX() ):
        h_rel_err.SetBinContent(ib, sqrt( h_rel_err.GetBinContent(ib) ) )

    # Divide
    h_rel_err.Divide(h_summed[None])

    plot = plot_mc[None]
    if args.normalizeBinWidth: plot.name += "_normalizeBinWidth"
    data_histo =  plot_data.histos_added[0][0]
    data_histo.style = styles.errorStyle( ROOT.kBlack )
    plot.histos += [[ data_histo ]]
    plot_data.stack[0][0].texName = data_sample_texName 
    plot.stack += [[ plot_data.stack[0][0] ]]

    boxes = []
    ratio_boxes = []
    for ib in range(1, 1 + h_rel_err.GetNbinsX() ):
        val = h_summed[None].GetBinContent(ib)
        if val<0: continue
        sys = h_rel_err.GetBinContent(ib)
        box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max([0.03, (1-sys)*val]), h_rel_err.GetXaxis().GetBinUpEdge(ib), max([0.03, (1+sys)*val]) )
        box.SetLineColor(ROOT.kBlack)
        box.SetFillStyle(3444)
        box.SetFillColor(ROOT.kBlack)
        r_box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max(0.1, 1-sys), h_rel_err.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys) )
        r_box.SetLineColor(ROOT.kBlack)
        r_box.SetFillStyle(3444)
        r_box.SetFillColor(ROOT.kBlack)

        boxes.append( box )
        ratio_boxes.append( r_box )

    ratio = {'yRange':(0.1,1.9), 'drawObjects':ratio_boxes}

    plotting.draw(plot,
        plot_directory = plot_path, ratio = ratio,
        logX = False, logY = True, sorting = True,
        yRange = (0.03, "auto"),
        drawObjects = drawObjects( top_sf[None] ) + boxes
    )
