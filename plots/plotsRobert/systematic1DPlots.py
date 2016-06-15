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
    choices=['doubleMu', 'doubleEle',  'muEle', 'dilepton'])

argParser.add_argument('--charges',
    default='OS',
    action='store',
    choices=['OS', 'SS'])

argParser.add_argument('--zMode',
    default='offZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)

argParser.add_argument('--ttjets',
    default='LO',
    action='store',
    choices=['LO', 'NLO'])

argParser.add_argument('--small',
    action='store_true',
    #default=True,
    help='Small?',
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
    default = False,
    #default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='png25ns_2l_mAODv2_2100_v3_systematics',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples
data_directory = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
postProcessing_directory = "postProcessed_Fall15_v3/dilep/"

from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

# Extra requirements on data
dataFilterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"


if args.mode=="doubleMu":
    lepton_selection_string = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&HLT_mumuIso", getZCut(args.zMode)])
    data_samples = [DoubleMuon_Run2015D]
    data_sample_texName = "Data (2 #mu)"
    qcd_sample = QCD_Mu5 #FIXME
    DoubleMuon_Run2015D.setSelectionString([dataFilterCut, lepton_selection_string])
elif args.mode=="doubleEle":
    lepton_selection_string = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&HLT_ee_DZ", getZCut(args.zMode)])
    data_samples = [DoubleEG_Run2015D]
    data_sample_texName = "Data (2 e)"
    qcd_sample = QCD_EMbcToE
    DoubleEG_Run2015D.setSelectionString([dataFilterCut, lepton_selection_string])
elif args.mode=="muEle":
    lepton_selection_string = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1&&HLT_mue", getZCut(args.zMode)])
    data_samples = [MuonEG_Run2015D]
    data_sample_texName = "Data (1 #mu, 1 e)"
    qcd_sample = QCD_Mu5EMbcToE
    MuonEG_Run2015D.setSelectionString([dataFilterCut, lepton_selection_string])
elif args.mode=="dilepton":
    doubleMu_selectionString = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&HLT_mumuIso&&abs(dl_mass-91.2)>15"
    doubleEle_selectionString = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&HLT_ee_DZ&&abs(dl_mass-91.2)>15"
    muEle_selectionString = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1&&HLT_mue"
    lepton_selection_string = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1&&HLT_mue|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&HLT_mumuIso || isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&HLT_ee_DZ ) && abs(dl_mass-91.2)>15)"

    data_samples = [DoubleMuon_Run2015D, DoubleEG_Run2015D, MuonEG_Run2015D] 
    data_sample_texName = "Data"
    qcd_sample = QCD_Mu5EMbcToE

    DoubleMuon_Run2015D.setSelectionString([dataFilterCut, doubleMu_selectionString])
    DoubleEG_Run2015D.setSelectionString([dataFilterCut, doubleEle_selectionString])
    MuonEG_Run2015D.setSelectionString([dataFilterCut, muEle_selectionString])
else:
    raise ValueError( "Mode %s not known"%args.mode )


if args.ttjets == "NLO":
    TTJets_sample = TTJets
elif args.ttjets == "LO":
    TTJets_sample = TTJets_Lep
else:
    raise ValueError

mc_samples = [ DY_HT_LO, TTJets_sample, singleTop, qcd_sample, TTZ, TTXNoZ, diBoson, WZZ]
#mc_samples = [ TTJets_sample ]

DY_HT_LO.texName  = "DY + jets"
qcd_sample.texName = "QCD (multi-jet)"

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

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))

common_selection=[
#    ("multiIsoWP", "l1_index>=0&&l1_index<1000&&l2_index>=0&&l2_index<1000&&"+multiIsoWP),
    ("dPhiJet0-dPhiJet1", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )==0"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("mll20", "dl_mass>20"),
]

jet_systematics = ['JECUp', 'JECDown', 'JERUp', 'JERDown']
met_systematics = ['UnclusteredEnUp', 'UnclusteredEnDown']
weight_systematics = ['PUUp', 'PUDown', 'TopPt', 'BTag_SF', 'BTag_SF_b_Down', 'BTag_SF_b_Up', 'BTag_SF_l_Down', 'BTag_SF_l_Up']

sys_pairs = [\
    ('JEC', 'JECUp', 'JECDown'),
#    ('JER', 'JERUp', 'JERDown'),
    ('Unclustered', 'UnclusteredEnUp', 'UnclusteredEnDown'),
    ('PU', 'PUUp', 'PUDown'),
    ('TopPt', 'TopPt', None),
    ('BTag_b', 'BTag_SF_b_Down', 'BTag_SF_b_Up' ),
    ('BTag_l', 'BTag_SF_l_Down', 'BTag_SF_l_Up'),
]


#jet_systematics = []
#met_systematics = []
#weight_systematics = []
#sys_pairs = []

jme_systematics = jet_systematics + met_systematics

def systematic_selection( sys = None ):

    if sys is None: return [ \
        ("njet2", "nJetGood>=2"),
        ("nbtag1", "nBTag>=1"),
        ("met80", "met_pt>80"),
        ("metSig5", "met_pt/sqrt(ht)>5"),
        ]
    elif sys in jet_systematics: return [\
        ("njet2", "nJetGood_"+sys+">=2"),
        ("nbtag1", "nBTag_"+sys+">=1"),
        ("met80", "met_pt_"+sys+">80"),
        ("metSig5", "metSig_"+sys+">5"),
        ]
    elif sys in met_systematics: return [\
        ("njet2", "nJetGood>=2"),
        ("nbtag1", "nBTag>=1"),
        ("met80", "met_pt_"+sys+">80"),
        ("metSig5", "metSig_"+sys+">5"),
        ]
    elif sys in weight_systematics:
        return systematic_selection( sys = None )
    else: raise ValueError( "Systematic %s not known"%sys )

def weight( sys = None ):
    if sys is None:
        return (lambda data:data.weight, "weight")
    elif sys in weight_systematics:
        return (lambda data:data.weight*getattr(data, "reweight"+sys), "weight*reweight"+sys)
    elif sys in jme_systematics :
        return weight( sys = None )
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

#signals = []
#if len(args.signals)>0:
#    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_2l_postProcessed import *
#    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *
#    for s in args.signals:
#        if "*" in s:
#            split = s.split("*")
#            sig, fac = split[0], int(split[1])
#        else:
#            sig, fac = s, 1
#        try:
#            signals.append( [eval(sig)] )
#            if hasattr(signals[-1][0], "scale"):
#                signals[-1][0].scale*=fac
#            elif fac!=1:
#                signals[-1][0].scale = fac
#            else: pass
#
#            if fac!=1:
#                signals[-1][0].name+=" x"+str(fac)
#            logger.info( "Adding sample %s with factor %3.2f", sig, fac)
#        except NameError:
#            logger.warning( "Could not add signal %s", s)

sequence = []

for sample in mc_samples:
    sample.read_variables = ["reweight%s/F"%s for s in weight_systematics]
    sample.read_variables += ["dl_mt2ll_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["dl_mt2bb_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["dl_mt2blbl_%s/F"%s for s in jme_systematics]
    sample.read_variables += ["nJetGood_%s/I"%s for s in jet_systematics]
    sample.read_variables += ["nBTag_%s/I"%s for s in jet_systematics]

# Charge requirements
if args.charges=="OS":
    selection = [("isOS","isOS")]
elif args.charges=="SS":
    selection = [("isSS","l1_pdgId*l2_pdgId>0")]
else:
    raise ValueError

selection.extend( common_selection )

ppfixes = [args.mode, args.zMode] if not args.mode=='dilepton' else [args.mode]
if args.ttjets == "NLO": ppfixes.append( "TTJetsNLO" )
if args.ttjets == "LO": ppfixes.append( "TTJetsLO" )
if args.small: ppfixes = ['small'] + ppfixes
prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in selection ] ) ] )

plot_path = os.path.join(plot_directory, args.plot_directory, prefix)

result_file = os.path.join(plot_path, 'results.pkl')

common_selection_string = "&&".join( p[1] for p in selection )

logger.info( "Prefix %s common_selection_string %s", prefix, common_selection_string )

data_selection_string = "&&".join( s[1] for s in systematic_selection( sys = None ) )
data_weight_func, data_weight_string = weight( sys = None )

sys_stacks = {sys:copy.deepcopy(stack_mc) for sys in [None] + weight_systematics + jme_systematics }

roottools_plots = []
dl_mt2ll_data  = Plot(
    name = "dl_mt2ll_data",
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    binning=Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2ll/F" ),
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    )
roottools_plots.append( dl_mt2ll_data )

dl_mt2ll_mc  = { sys:Plot(\
    name = "dl_mt2ll" if sys is None else "dl_mt2ll_mc_%s" % sys,
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    binning=Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2ll/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2ll_%s/F" % sys ),
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2ll_mc.values() )

dl_mt2bb_data  = Plot( 
    name = "dl_mt2bb_data",
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2bb/F" ),
    binning=Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450]),
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    ) 
roottools_plots.append( dl_mt2bb_data )

dl_mt2bb_mc  = {sys: Plot(
    name = "dl_mt2bb" if sys is None else "dl_mt2bb_mc_%s" % sys,
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2bb/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2bb_%s/F" % sys ),
    binning=Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450]),
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2bb_mc.values() )

dl_mt2blbl_data  = Plot( 
    name = "dl_mt2blbl_data",
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack_data,
    variable = Variable.fromString( "dl_mt2blbl/F" ),
    binning=Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350]),
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    ) 
roottools_plots.append( dl_mt2blbl_data )

dl_mt2blbl_mc  = {sys: Plot(
    name = "dl_mt2blbl" if sys is None else "dl_mt2blbl_mc_%s" % sys,
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = sys_stacks[sys],
    variable = Variable.fromString( "dl_mt2blbl/F" ) if sys is None or sys in weight_systematics else Variable.fromString( "dl_mt2blbl_%s/F" % sys ),
    binning=Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350]),
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( dl_mt2blbl_mc.values() )

nbtags_data  = Plot( 
    name = "nbtags_data",
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = stack_data,
    variable = Variable.fromString('nBTag/I'),
    binning=[5,1,6],
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
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
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( nbtags_mc.values() )

njets_data  = Plot( 
    name = "njets_data",
    texX = 'number of jets', texY = 'Number of Events',
    stack = stack_data,
    variable = Variable.fromString('nJetGood/I'),
    binning=[8,2,10],
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
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
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( njets_mc.values() )

met_data  = Plot( 
    name = "met_data",
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack_data, 
    variable = Variable.fromString( "met_pt/F" ),
    binning=Binning.fromThresholds([80,130,180,230,280,320,420,520,800]),
    selectionString = "&&".join([ common_selection_string, data_selection_string] ),
    weight = data_weight_func,
    addOverFlowBin = "upper",
    )
roottools_plots.append( met_data )

met_mc  = {sys: Plot(
    name = "met_pt" if sys is None else "met_pt_mc_%s" % sys,
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = sys_stacks[sys],
    variable = Variable.fromString('met_pt/F') if sys not in met_systematics else Variable.fromString( "met_pt_%s/F" % sys ),
    binning=Binning.fromThresholds([80,130,180,230,280,320,420,520,800]),
    selectionString = "&&".join( [common_selection_string] + [ s[1] for s in systematic_selection( sys = sys ) ] ),
    weight = weight( sys = sys )[0],
    addOverFlowBin = "upper",
    ) for sys in [None] + weight_systematics + jme_systematics }
roottools_plots.extend( met_mc.values() )

plots = [\
         [ dl_mt2ll_mc, dl_mt2ll_data , (0,100), 20],
         [ dl_mt2bb_mc, dl_mt2bb_data , (70,170), 20],
         [ dl_mt2blbl_mc, dl_mt2blbl_data, (0,100), 20],
         [ njets_mc, njets_data, (3,3), -1],
         [ nbtags_mc, nbtags_data, (1,1), -1],
         [ met_mc, met_data, (80,80), 50],
    ]

if os.path.exists(result_file) and not args.overwrite:

    #(dl_mt2ll_data_histos, dl_mt2ll_mc_histos, dataMCScale) = pickle.load(file( result_file ))
    (all_histos,  dataMCScale) = pickle.load(file( result_file ))
    logger.info( "Loaded plots from %s", result_file )
    for i_plot, plot_ in enumerate(plots):
        p_mc, p_data, x_norm, bin_width = plot_
        for k in p_mc.keys():
            p_mc[k].histos = all_histos[i_plot][0][k] 
        p_data.histos = all_histos[i_plot][1]
else:
    # Applying systematic variation

    mc_selection_string = "&&".join( s[1] for s in systematic_selection( sys = None ) )
    mc_weight_func, mc_weight_string = weight( sys = None )

    logger.info( "Calculating normalization constants:" )
    logger.info( "data_selection_string: %s", data_selection_string  )
    logger.info( "mc_selection_string:   %s", mc_selection_string  )
    logger.info( "data_weight_string:    %s", data_weight_string  )
    logger.info( "mc_weight_string:      %s", mc_weight_string  )

    normalization_region_cut = "dl_mt2ll<100"

    yield_mc    = sum(s.getYieldFromDraw( selectionString = "&&".join([ common_selection_string, mc_selection_string, normalization_region_cut ] ), weightString = mc_weight_string)['val'] for s in mc_samples)
    yield_data  = sum(s.getYieldFromDraw( selectionString = "&&".join([ common_selection_string, data_selection_string, normalization_region_cut ] ), weightString = data_weight_string)['val'] for s in data_samples )

    dataMCScale = yield_data/(yield_mc*lumi_scale)

    for sys in dl_mt2ll_mc.values():
        for sample in sys.stack.samples(): 
            sample.scale = lumi_scale*dataMCScale

    logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc, yield_data, lumi_scale )

    read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]"]
    plotting.fill(roottools_plots, read_variables = read_variables, sequence = sequence)

    if not os.path.exists(os.path.dirname( result_file )):
        os.makedirs(os.path.dirname( result_file ))

    all_histos = []
    for p_mc, p_data, x_norm, bin_width in plots:
        mc_histos = {k:p_mc[k].histos for k in p_mc.keys()}
        data_histos = p_data.histos
        all_histos.append( (mc_histos, data_histos) )

    pickle.dump( (all_histos, dataMCScale), file( result_file, 'w' ) )
    logger.info( "Written %s", result_file)

if not os.path.exists( plot_path ): os.makedirs( plot_path )

for plot_mc, plot_data, x_norm, bin_width in plots:
    if args.normalizeBinWidth and bin_width>0:
            for p in plot_mc.values() + [plot_data]:
                for histo in sum(p.histos, []): 
                    for ib in range(histo.GetXaxis().GetNbins()+1):
                        val = histo.GetBinContent( ib )
                        err = histo.GetBinError( ib )
                        width = histo.GetBinWidth( ib )
                        histo.SetBinContent(ib, val / (width / bin_width)) 
                        histo.SetBinError(ib, err / (width / bin_width)) 

    #Calculating systematics
    h_summed = {k: plot_mc[k].histos_added[0][0].Clone() for k in plot_mc.keys()}

    #Normalize systematic shapes
    for k in h_summed.keys():
        if k is None: continue
        try:
            bin_low  = h_summed[None].FindBin(x_norm[0])
            bin_high = h_summed[None].FindBin(x_norm[1])
            # if 'njet' in plot_mc[k].name.lower(): print "before", k,h_summed[k], bin_low, bin_high, h_summed[k].Integral(bin_low, bin_high), [ h_summed[k][i] for i in range(10) ]
            h_summed[k].Scale(
                h_summed[None].Integral(bin_low, bin_high) / h_summed[k].Integral(bin_low, bin_high)
            )
            # if 'njet' in plot_mc[k].name.lower(): print "after", k,h_summed[k], bin_low, bin_high, h_summed[k].Integral(bin_low, bin_high), [ h_summed[k][i] for i in range(10) ]
        except ZeroDivisionError:
            logger.warning( "Found zero for variation %s of variable %s", k, plot_mc[k].name )


    h_rel_err = h_summed[None].Clone()
    h_rel_err.Reset()

    h_sys = {}
    for k, s1, s2 in sys_pairs:
        h_sys[k] = h_summed[s1].Clone()
        h_sys[k].Scale(-1)
        h_sys[k].Add(h_summed[s2])
        # h_sys[k].Divide(h_summed[None])

    h_rel_err = h_summed[None].Clone()
    h_rel_err.Reset()

    # Adding in quadrature
    for k in h_sys.keys():
        for ib in range( 1 + h_rel_err.GetNbinsX() ):
            h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + h_sys[k].GetBinContent(ib)**2 )

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
        drawObjects = drawObjects( dataMCScale ) + boxes
    )
