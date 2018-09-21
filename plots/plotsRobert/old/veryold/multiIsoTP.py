''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos, cosh, atan2
import itertools

#RootTools
from RootTools.core.standard import *

#StopsDilepton
from StopsDilepton.tools.objectSelection import getGoodAndOtherLeptons, leptonVars, eleSelector, muonSelector, getLeptons, getOtherLeptons, getGoodLeptons
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator() 


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
    default='doubleMu',
    action='store',
    choices=['doubleMu', 'doubleEle', 'muEle'])

argParser.add_argument('--small',
    #default = True,
    action='store_true',
    help='small?',
)

argParser.add_argument('--plot_directory',
    default='multiIsoTP',
    action='store',
)

argParser.add_argument('--pu',
    default="reweightPU12fb",
    action='store',
    choices=["None", "reweightPU12fb", "reweightPU12fbUp", "reweightPU12fbDown"],
    help='PU weight',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadron&&Flag_badMuon"
dataFilterCut = mcFilterCut+"&&weight>0"
postProcessing_directory = "postProcessed_80X_v12/dilep/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v12/dilep/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *

if args.mode=="doubleMu":
    lepton_selection_string_data = "&&".join(["nGoodMuons>=1"])
    lepton_selection_string_mc   = "&&".join(["nGoodMuons>=1"])
    data_samples = [DoubleMuon_Run2016BCD_backup]
    DoubleMuon_Run2016BCD_backup.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (2 #mu)"
    #qcd_sample = QCD_Mu5 #FIXME

elif args.mode=="doubleEle":
    lepton_selection_string_data = "&&".join(["nGoodElectrons>=1"])
    lepton_selection_string_mc   = "&&".join(["nGoodElectrons>=1"])
    data_samples = [DoubleEG_Run2016BCD_backup]
    DoubleEG_Run2016BCD_backup.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE

elif args.mode=="muEle":
    lepton_selection_string_data = "&&".join(["nGoodElectrons+nGoodMuons>=1"])
    lepton_selection_string_mc   = "&&".join(["nGoodElectrons+nGoodMuons>=1"])
    data_samples = [MuonEG_Run2016BCD_backup]
    MuonEG_Run2016BCD_backup.setSelectionString([dataFilterCut, lepton_selection_string_data])
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE

else:
    raise ValueError( "Mode %s not known"%args.mode )

mc = [ DY_HT_LO, Top, multiBoson, TTZ, TTXNoZ]

for d in data_samples:
    d.style = styles.errorStyle( ROOT.kBlack )
    if args.small:
        d.reduceFiles(to = 1) 

#Averaging lumi
lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000

logger.info( "Lumi scale for mode %s is %3.2f", args.mode, lumi_scale )
for sample in mc:
    sample.style = styles.fillStyle(sample.color)
    sample.setSelectionString( lepton_selection_string_mc )
    if args.small:
        sample.reduceFiles(to = 1)

# user data
from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event, sample: event.weight

for sample in mc:
    sample.read_variables = [args.pu+'/F', 'reweightDilepTriggerBackup/F', 'reweightBTag_SF/F', 'reweightLeptonSF/F', 'reweightLeptonHIPSF/F']
    sample.weight = lambda event, sample: getattr( event, args.pu )*event.reweightDilepTriggerBackup*event.reweightBTag_SF*event.reweightLeptonSF*event.reweightLeptonHIPSF

sequence = []    

loose_muon_selector = muonSelector( iso = 0.4, absEtaCut = 2.4)
loose_ele_selector = eleSelector( iso = 0.4, eleId = 4, absEtaCut = 2.4 )

def makeNonIsoLeptons( event ):

    event.mll                     = float('nan')
    event.mt2ll                   = float('nan')
    event.tag_pt                  = float('nan')
    event.tag_eta                 = float('nan')
    event.tag_phi                 = float('nan')
    event.tag_jetPtRelv2          = float('nan')
    event.tag_jetPtRatiov2        = float('nan')
    event.tag_miniRelIso          = float('nan')
    event.probe_pt                = float('nan')
    event.probe_eta               = float('nan')
    event.probe_phi               = float('nan')
    event.probe_jetPtRelv2        = float('nan')
    event.probe_jetPtRatiov2      = float('nan')
    event.probe_miniRelIso        = float('nan')

    goodLeptons = getGoodLeptons( event, collVars = leptonVars )
    tag = goodLeptons[0] if len(goodLeptons)>0 else None

    if not tag: return
    # check mode
    if ( abs(tag['pdgId'])==11 and args.mode=='doubleMu' ) or ( abs(tag['pdgId'])==13 and args.mode=='doubleEle' ): return

    extraLeptons = filter( 
            lambda p: (p!=tag) and ( (abs(p['pdgId'])==13 and loose_muon_selector(p)) or (abs(p['pdgId'])==11 and loose_ele_selector(p)) ),
            sorted( getGoodAndOtherLeptons(event, ptCut = 20, collVars=leptonVars, mu_selector = loose_muon_selector, ele_selector = loose_ele_selector), key=lambda l: -l['pt'] )
        )
    #for p in extraLeptons:
    #    print p['miniRelIso'], p['pt']
    probe = extraLeptons[0] if len(extraLeptons)>0 else None
    if not probe:
        return

    mll = sqrt(2.*tag['pt']*probe['pt']*(cosh(tag['eta']-probe['eta']) - cos(tag['phi']-probe['phi'])))

    if args.mode.startswith('double'):
        #OSSF
        if not tag['pdgId'] == -probe['pdgId']:return
        #T&P mass
        #on Z
        if abs(mll-91.2)>15: return

    if args.mode=='muEle':
        #OSOF
        if abs(tag['pdgId']) == abs(probe['pdgId']):return
        if not tag['pdgId']*probe['pdgId'] < 0: return 

    mt2Calc.reset()
    mt2Calc.setMet(event.met_pt, event.met_phi)

    mt2Calc.setLeptons(tag['pt'], tag['eta'], tag['phi'], probe['pt'], probe['eta'], probe['phi'])

    event.mt2ll                   = mt2Calc.mt2ll()
    event.mll                     = mll

    event.tag_pt                  = tag["pt"]
    event.tag_eta                 = tag["eta"]
    event.tag_phi                 = tag["phi"]
    event.tag_jetPtRelv2          = tag["jetPtRelv2"]
    event.tag_jetPtRatiov2        = tag["jetPtRatiov2"]
    event.tag_miniRelIso          = tag["miniRelIso"]
    event.probe_pt                = probe["pt"]
    event.probe_eta               = probe["eta"]
    event.probe_phi               = probe["phi"]
    event.probe_jetPtRelv2        = probe["jetPtRelv2"]
    event.probe_jetPtRatiov2      = probe["jetPtRatiov2"]
    event.probe_miniRelIso        = probe["miniRelIso"]

    return

sequence.append( makeNonIsoLeptons )

cuts=[
    ("mll20", "dl_mass>20"),
    ("njet2p", "nJetGood>=2"),
    ("nbtag1p", "nBTag>=1"),
    ("met80", "met_pt>80"),
    ("metSig5", "(met_pt/sqrt(ht)>5||nJetGood==0)"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),  
]
                
def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
    (0.15, 0.95, 'CMS Preliminary'), 
    (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

stack = Stack(mc, data_samples)

presel = cuts

prefix = '_'.join([args.mode, '-'.join([p[0] for p in presel])])

if args.small: prefix = 'small_'+prefix

plot_path = os.path.join(plot_directory, args.plot_directory, prefix)

selectionString = "&&".join( [p[1] for p in presel] )

plots = []
tag_pt  = Plot(
    name = "tag_pt",
    texX = 'p_{T}(tag) (GeV)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_pt,
    binning=[60,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_pt )

tag_eta  = Plot(
    name = "tag_eta",
    texX = '#eta(tag)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_eta,
    binning=[36,-3.3,3.3],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_eta )

tag_phi  = Plot(
    name = "tag_phi",
    texX = '#phi(tag)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_phi,
    binning=[30,-pi,pi],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_phi )

tag_miniRelIso  = Plot(
    name = "tag_miniRelIso",
    texX = 'I_{rel.mini}(tag)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_miniRelIso,
    binning=[40,0,2],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_miniRelIso )

tag_jetPtRelv2  = Plot(
    name = "tag_jetPtRelv2",
    texX = 'jetPtRelv2(tag)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_jetPtRelv2,
    binning=[50,0,50],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_jetPtRelv2 )

tag_jetPtRatiov2  = Plot(
    name = "tag_jetPtRatiov2",
    texX = 'jetPtRatiov2(tag)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.tag_jetPtRatiov2,
    binning=[28,0,1.4],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tag_jetPtRatiov2 )

probe_pt  = Plot(
    name = "probe_pt",
    texX = 'p_{T}(probe) (GeV)', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.probe_pt,
    binning=[60,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_pt )

probe_eta  = Plot(
    name = "probe_eta",
    texX = '#eta(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_eta,
    binning=[36,-3.3,3.3],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_eta )

probe_phi  = Plot(
    name = "probe_phi",
    texX = '#phi(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_phi,
    binning=[30,-pi,pi],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_phi )

probe_miniRelIso  = Plot(
    name = "probe_miniRelIso",
    texX = 'I_{rel.mini}(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_miniRelIso,
    binning=[40,0,2],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_miniRelIso )

probe_jetPtRelv2  = Plot(
    name = "probe_jetPtRelv2",
    texX = 'jetPtRelv2(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_jetPtRelv2,
    binning=[50,0,50],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_jetPtRelv2 )

probe_jetPtRelv2_miniRelIsoVT  = Plot(
    name = "probe_jetPtRelv2_miniRelIsoVT",
    texX = 'jetPtRelv2(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_jetPtRelv2 if event.probe_miniRelIso<0.09 else float('nan'),
    binning=[50,0,50],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_jetPtRelv2_miniRelIsoVT )

probe_jetPtRatiov2  = Plot(
    name = "probe_jetPtRatiov2",
    texX = 'jetPtRatiov2(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_jetPtRatiov2,
    binning=[28,0,1.4],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_jetPtRatiov2 )

probe_jetPtRatiov2_miniRelIsoVT  = Plot(
    name = "probe_jetPtRatiov2_miniRelIsoVT",
    texX = 'jetPtRatiov2(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_jetPtRatiov2 if event.probe_miniRelIso<0.09 else float('nan'),
    binning=[28,0,1.4],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_jetPtRatiov2_miniRelIsoVT )

probe_jetPtRatiov2_miniRelIsoVT_ptRel07  = Plot(
    name = "probe_jetPtRatiov2_miniRelIsoVT_ptRel07",
    texX = 'jetPtRatiov2(probe)', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:event.probe_jetPtRatiov2 if (event.probe_miniRelIso<0.09 and event.probe_jetPtRelv2<7.2) else float('nan'),
    binning=[28,0,1.4],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( probe_jetPtRatiov2_miniRelIsoVT_ptRel07 )

tp_mass  = Plot(
    name = "tp_mass",
    texX = 'm(ll) (GeV)', texY = 'Number of Events / 3 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.mll,
    binning=[150/3,0,150],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tp_mass )

tp_mt2ll  = Plot(
    name = "mt2ll",
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.mt2ll,
    binning=[300/20,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( tp_mt2ll )


read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "met_pt/F", "met_phi/F"]

read_variables.extend([\
    "nLepGood/I",  "LepGood[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I,etaSc/F]",
    "nLepOther/I", "LepOther[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I,etaSc/F]",
])

plotting.fill(plots, read_variables = read_variables, sequence = sequence)

if not os.path.exists( plot_path ): os.makedirs( plot_path )

for plot in plots:
    try:
        scale = plot.histos_added[1][0].Integral()/plot.histos_added[0][0].Integral()
    except ZeroDivisionError:
        scale = 1.

    plotting.draw(plot, 
        plot_directory = plot_path, ratio = {'yRange':(0.1,1.9)}, 
        logX = False, logY = False, sorting = True, 
        yRange = (0.03, "auto"), 
        scaling = {0:1},
        drawObjects = drawObjects(plot.histos_added[1][0].Integral()/(lumi_scale*plot.histos_added[0][0].Integral()) )
    )

    plotting.draw(plot, 
        plot_directory = plot_path+'/log/', ratio = {'yRange':(0.1,1.9)}, 
        logX = False, logY = True, sorting = True, 
        yRange = (0.03, "auto"), 
        scaling = {0:1},
        drawObjects = drawObjects(plot.histos_added[1][0].Integral()/(lumi_scale*plot.histos_added[0][0].Integral()) )
    )
logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
