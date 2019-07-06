# Standard imports
import ROOT
from   math import sqrt, cos, sin, pi, acos, atan2
import itertools
import pickle
import operator

#RootTools
from RootTools.core.standard import *

#StopsDilepton
from StopsDilepton.tools.helpers import getCollection, deltaR
from StopsDilepton.tools.user import plot_directory
from StopsDilepton.tools.objectSelection import muonSelector, eleSelector, getGoodMuons, getGoodElectrons, getGoodJets, getAllJets
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

# Samples
from Samples.Tools.metFilters            import getFilterCut

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',  action='store',  nargs='?',  choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],  default='INFO', help="Log level for logging")
argParser.add_argument('--mode',      default='ee',    action='store', choices=['mumu', 'ee',  'mue'])
#argParser.add_argument('--isolation', default='standard',  action='store',  choices=['VeryLoose', 'VeryLooseInverted', 'VeryLoosePt10', 'standard'])
argParser.add_argument('--charges',   default='OS',        action='store',choices=['OS', 'SS'])
argParser.add_argument('--era',       action='store', type=str,      default="Run2016")
argParser.add_argument('--DYInc',     action='store_true',  help='Use Inclusive DY sample?', )
argParser.add_argument('--small',     action='store_true',  help='Small?')
argParser.add_argument('--reversed',  action='store_true',  help='Reversed?',)
argParser.add_argument('--dpm',                                   action='store_true',     help='Use dpm?', )
argParser.add_argument('--overwrite', action='store_true',  help='overwrite?',)
argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp', 'noPUReweighting', 'nvtx'])
argParser.add_argument('--plot_directory',  default='v0',  action='store',)
argParser.add_argument('--selection', action='store', default='lepSel-njet2p-btag1p-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')

args = argParser.parse_args()

if args.small:                        args.plot_directory += "_small"
if args.DYInc:                        args.plot_directory += "_DYInc"
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples

if "2016" in args.era:
    year = 2016
elif "2017" in args.era:
    year = 2017
elif "2018" in args.era:
    year = 2018

logger.info( "Working in year %i", year )

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    TTJets_1l, TTJets = Top_pow_1l_16, Top_pow_16
    if args.DYInc:
        mc             = [ TTXNoZ_16, TTZ_16, multiBoson_16, DY_16]
    else:
        mc             = [ TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    TTJets_1l, TTJets = Top_pow_1l_17, Top_pow_17
    if args.DYInc:
        mc             = [ TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
    else:
        mc             = [ TTXNoZ_17, TTZ_17, multiBoson_17, DY_HT_LO_17]
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    TTJets_1l, TTJets = Top_pow_1l_18, Top_pow_18
    if args.DYInc:
        mc             = [ TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]
    else:
        mc             = [ TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18]

try:
  data_sample = eval(args.era)
except Exception as e:
  logger.error( "Didn't find %s", args.era )
  raise e

offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

TTJets_1l.name = "TTJets_1l"
TTJets_1l.texName = "TTJets 1l"
TTJets_1l.color = ROOT.kAzure - 2

TTJets_l2_prompt    = copy.deepcopy(TTJets)
TTJets_l2_prompt.name = "TTJets_l2_prompt"
TTJets_l2_prompt.texName = "TTJets 2l (prompt)"
TTJets_l2_prompt.weight = lambda event, sample: not event.l2_matched_nonPrompt

TTJets_l2_nonPrompt = copy.deepcopy(TTJets)
TTJets_l2_nonPrompt.name = "TTJets_l2_nonPrompt"
TTJets_l2_nonPrompt.texName = "TTJets 2l (non-prompt)"
TTJets_l2_nonPrompt.weight = lambda event, sample: event.l2_matched_nonPrompt
TTJets_l2_nonPrompt.color = ROOT.kAzure + 9

mc = [ TTJets_l2_prompt, TTJets_1l] +  mc + [ TTJets_l2_nonPrompt ]
mc_for_normalization = [ TTJets, TTJets_1l] + mc

if args.small:
    for s in mc + mc_for_normalization + [data_sample]:
        s.reduceFiles(to = 1)

data_sample.style = styles.errorStyle( ROOT.kBlack )
lumi_scale = data_sample.lumi/1000
for sample in mc:
    sample.style = styles.fillStyle(sample.color)

# official PU reweighting
weight = lambda event, sample:event.weight

def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if dataMCScale is not None: 
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(data_sample.lumi/100)/10., dataMCScale ) ) )
    else:
        lines.append( (0.50, 0.95, '13 TeV' ) )
    return [tex.DrawLatex(*l) for l in lines] 

stack = Stack(mc, [data_sample] )

#def fromTau( gen_lepton ):
#    return gen_lepton['n_tau']>0
#def prompt( gen_lepton ):
#    return not fromTau( gen_lepton) and gen_lepton['n_B']==0 and gen_lepton['n_D']==0
#def nonPrompt( gen_lepton ):
#    return not fromTau( gen_lepton) and not ( gen_lepton['n_B']==0 and gen_lepton['n_D']==0 ) 
#
#gen_ttbar_sequence = []
#
## Match l1 and l2
#def matchLeptons( event, sample ):
#    # Get Gen leptons
#    gen_leps = getCollection(event, "GenLep", ["pt", "eta", "phi", "n_t", "n_W", "n_B", "n_D", "n_tau", "pdgId"], "nGenLep" )
#    non_prompt = filter(lambda l: nonPrompt(l), gen_leps )
#    # Get selected leptons
#    l1 = {'pt':event.l1_pt, 'eta':event.l1_eta, 'phi':event.l1_phi, 'pdgId':event.l1_pdgId} 
#    l2 = {'pt':event.l2_pt, 'eta':event.l2_eta, 'phi':event.l2_phi, 'pdgId':event.l2_pdgId} 
#    # match l1 and l2 
#    event.l1_matched_nonPrompt = False 
#    event.l2_matched_nonPrompt = False 
#    for gl in non_prompt:
#        if gl['pdgId']==l1['pdgId'] and deltaR(gl, l1)<0.2 and abs(1-gl['pt']/l1['pt'])<0.5:
#            event.l1_matched_nonPrompt = True
#        if gl['pdgId']==l2['pdgId'] and deltaR(gl, l2)<0.2 and abs(1-gl['pt']/l2['pt'])<0.5:
#            event.l2_matched_nonPrompt = True
#    return
#
#gen_ttbar_sequence.append( matchLeptons )

read_variables = [\
    "weight/F" , "JetGood[pt/F,eta/F,phi/F]", 
    "l1_pt/F", "l1_eta/F", "l1_phi/F", "l1_pdgId/I",
    "l2_pt/F", "l2_eta/F", "l2_phi/F", "l2_pdgId/I",
    TreeVariable.fromString('nElectron/I'),
    VectorTreeVariable.fromString('Electron[pt/F,eta/F,phi/F,pdgId/I,cutBased/I,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,lostHits/b,convVeto/O,dxy/F,dz/F,charge/I,deltaEtaSC/F]'),
    TreeVariable.fromString('nMuon/I'),
    VectorTreeVariable.fromString('Muon[pt/F,eta/F,phi/F,pdgId/I,mediumId/O,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,dxy/F,dz/F,charge/I]'),
#    TreeVariable.fromString('nJet/I'),
#    VectorTreeVariable.fromString('Jet[%s]'% ( ','.join(jetVars) ) ),
]

def fs(pdgId):
    if abs(pdgId)==11:
        return "e"
    elif abs(pdgId)==13:
        return "m"
    else: raise ValueError

ele_selector_noIso = eleSelector( "tightNoIso", year = year, ptCut = 7)
mu_selector_noIso = muonSelector( "tightNoIso", year = year, ptCut = 5)
ele_selector = eleSelector( "tight", year = year )
mu_selector = muonSelector( "tight", year = year )

sequence = []

def initSwappedMT2ll( event, sample ):
    # initial values
    for fh in ["leadingLepIso", "leadingLepNonIso"]:
        for swap in ["L1", "L2"]:
            for fs in ["mm","me","em","ee"]:
                setattr(event, "dl_mt2ll_%s_swap%s_%s"%(fh, swap, fs), float('nan') )
                # print "dl_mt2ll_%s_swap%s_%s"%(fh, swap, fs)

sequence.append( initSwappedMT2ll )

verbose = False
def makeSwappedMT2ll(event, l1, l2, nonIsoLep, verbose = False):
    mt2Calculator.reset()

    # swap l1
    final_hierarchy = "leadingLepNonIso" if nonIsoLep['pt']>l2['pt'] else "leadingLepIso"
    l1p, l2p = (nonIsoLep, l2) if nonIsoLep['pt']>l2['pt'] else (l2, nonIsoLep)
    finalState = "".join(fs(p['pdgId']) for p in [l1p, l2p])
    pfix = "_".join([final_hierarchy, "swapL1", finalState])
    mt2Calculator.setLeptons(l1p['pt'], l1p['eta'], l1p['phi'], l2p['pt'], l2p['eta'], l2p['phi'])
    mt2Calculator.setMet(event.met_pt, event.met_phi)
    setattr(event, "dl_mt2ll_"+pfix, mt2Calculator.mt2ll() )

    if verbose: print "dl_mt2ll_"+pfix, mt2Calculator.mt2ll()

    # swap l2
    final_hierarchy = "leadingLepNonIso" if nonIsoLep['pt']>l1['pt'] else "leadingLepIso"
    l1p, l2p = (nonIsoLep, l1) if nonIsoLep['pt']>l1['pt'] else (l1, nonIsoLep)
    finalState = "".join(fs(p['pdgId']) for p in [l1p, l2p])
    pfix = "_".join([final_hierarchy, "swapL2", finalState])
    mt2Calculator.setLeptons(l1p['pt'], l1p['eta'], l1p['phi'], l2p['pt'], l2p['eta'], l2p['phi'])
    mt2Calculator.setMet(event.met_pt, event.met_phi)

    setattr(event, "dl_mt2ll_"+pfix, mt2Calculator.mt2ll() )

    if verbose: print "dl_mt2ll_"+pfix, mt2Calculator.mt2ll() 

#verbose = False
def makeNonIsoLeptons( event, sample ):

    electrons_lowPt_noIso  = getGoodElectrons(event, ele_selector = ele_selector_noIso)
    muons_lowPt_noIso      = getGoodMuons(event, mu_selector = mu_selector_noIso )
    
    print muons_lowPt_noIso
    extra_electrons_lowPt_noIso = [ l for l in electrons_lowPt_noIso if l['pt'] not in [ event.l1_pt, event.l2_pt] ]
    extra_muons_lowPt_noIso     = [ l for l in muons_lowPt_noIso     if l['pt'] not in [ event.l1_pt, event.l2_pt] ]

    if len( electrons_lowPt_noIso ) + len( muons_lowPt_noIso ) - len( extra_electrons_lowPt_noIso ) - len( extra_muons_lowPt_noIso) != 2:
        logger.warning( "Analysis leptons not found!" )

    #goodLeptons = getGoodLeptons( event,  mu_selector = mu_selector, ele_selector = ele_selector)
    #allExtraLeptons = sorted( \
    #    [l for l in getLeptons( event, collVars = leptonVars_data ) if l not in goodLeptons] + getOtherLeptons( event , collVars = leptonVars_data ), 
    #                key=lambda l: -l['pt'] )

    #for l in goodLeptons:
    #    print "good", l
    #for l in allExtraLeptons:
    #    print "extra", l
    #print len(goodLeptons), len(allExtraLeptons) 
    #assert len(goodLeptons)==2, "Analysis leptons not found!"

    l1 = {'pt':event.l1_pt, 'phi':event.l1_phi, 'eta':event.l1_eta, 'pdgId':event.l1_pdgId}
    l2 = {'pt':event.l2_pt, 'phi':event.l2_phi, 'eta':event.l2_eta, 'pdgId':event.l2_pdgId}

    nonIsoEles = filter(lambda l: abs(l['pdgId'])==11 and l['pfRelIso03_all']>0.12 and l['pt']>7, extra_electrons_lowPt_noIso )
    nonIsoMus  = filter(lambda l: abs(l['pdgId'])==13 and l['pfRelIso03_all']>0.12 and l['pt']>5, extra_muons_lowPt_noIso )
    #print nonIsoMus, nonIsoEles

    event.nonIsoMu  = nonIsoMus[-1] if len(nonIsoMus)>0 else None 
    event.nonIsoEle = nonIsoEles[-1] if len(nonIsoEles)>0 else None 

    # extra ele
    if event.nonIsoEle is not None:
        makeSwappedMT2ll( event, l1, l2, event.nonIsoEle, verbose = verbose)
    # extra mu
    if event.nonIsoMu is not None:
        makeSwappedMT2ll( event, l1, l2, event.nonIsoMu, verbose = verbose)
    if verbose: print

sequence.append( makeNonIsoLeptons )

#for sample in [TTJets_l2_prompt, TTJets_l2_nonPrompt]:
    #sample.sequence = gen_ttbar_sequence        
    #sample.read_variables = [ "nGenLep/I", "GenLep[pt/F,eta/F,phi/F,n_t/I,n_W/I,n_B/I,n_D/I,n_tau/I,pdgId/I]"]

data_sample.setSelectionString([getFilterCut(isData=True, year=year), getLeptonSelection(args.mode)])
data_sample.name           = "data"
data_sample.read_variables = ["event/I","run/I"]
data_sample.style          = styles.errorStyle(ROOT.kBlack)

for sample in mc:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F']
    # Need individual pu reweighting functions for each sample in 2017, so nTrueInt_puRW is only defined here
    if args.reweightPU and args.reweightPU not in ["noPUReweighting", "nvtx"]:
        sample.read_variables.append( 'reweightPU/F' if args.reweightPU=='Central' else 'reweightPU%s/F'%args.reweightPU )

    if args.reweightPU == "noPUReweighting":
        sample.weight         = lambda event, sample: event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    elif args.reweightPU == "nvtx":
        sample.weight         = lambda event, sample: nvtx_puRW(event.PV_npvsGood) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    elif args.reweightPU:
        pu_getter = operator.attrgetter( 'reweightPU' if args.reweightPU=='Central' else 'reweightPU%s'%args.reweightPU )
        sample.weight         = lambda event, sample: pu_getter(event) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    else: #default
        sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF

    sample.setSelectionString([getFilterCut(isData=False, year=year), getLeptonSelection(args.mode)])

plot_directory = os.path.join(plot_directory, 'looseIsoPlots', args.plot_directory, args.era, args.selection, args.mode)

selectionString = cutInterpreter.cutString(args.selection)
logger.info( "SelectionString: %s, translates to %s", args.selection, selectionString )

#logger.info( "Calculating normalization constants" ) 
#weight_string_mc  = 'weight*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF*' + ( 'reweightPU' if args.reweightPU=='Central' else 'reweightPU%s'%args.reweightPU )
#yield_mc    = sum(s.getYieldFromDraw( selectionString = selectionString, weightString = weight_string_mc)['val'] for s in mc_for_normalization)
#yield_data  = data_sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']
#
#for sample in mc:
#    dataMCScale = yield_data/(yield_mc*lumi_scale)
#    sample.scale = lumi_scale*dataMCScale
#
#logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc, yield_data, lumi_scale )


plots = []

dl_mass  = Plot(
    texX = 'm(ll) (GeV)', texY = 'Number of Events / 3 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[150/3,0,150],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_mass )

dl_pt  = Plot(
    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_pt/F" ),
    binning=[40,0,400],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_pt )

dl_eta  = Plot(
    texX = '#eta(ll) ', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_eta/F" ),
    binning=[30,-3,3],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_eta )

dl_phi  = Plot(
    texX = '#phi(ll) (GeV)', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_phi/F" ),
    binning=[30,-pi,pi],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_phi )

dl_mt2ll  = Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_mt2ll )

mt2ll_leadingLepIso_swapL1_mm  = Plot(
    name = "mt2ll_leadingLepIso_swapL1_mm",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l1, mm)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL1_mm,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL1_mm )

mt2ll_leadingLepIso_swapL2_mm  = Plot(
    name = "mt2ll_leadingLepIso_swapL2_mm",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l2, mm)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL2_mm,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL2_mm )

mt2ll_leadingLepIso_swapL1_me  = Plot(
    name = "mt2ll_leadingLepIso_swapL1_me",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l1, me)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL1_me,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL1_me )

mt2ll_leadingLepIso_swapL2_me  = Plot(
    name = "mt2ll_leadingLepIso_swapL2_me",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l2, me)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL2_me,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL2_me )

mt2ll_leadingLepIso_swapL1_em  = Plot(
    name = "mt2ll_leadingLepIso_swapL1_em",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l1, em)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL1_em,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL1_em )

mt2ll_leadingLepIso_swapL2_em  = Plot(
    name = "mt2ll_leadingLepIso_swapL2_em",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l2, em)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL2_em,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL2_em )

mt2ll_leadingLepIso_swapL1_ee  = Plot(
    name = "mt2ll_leadingLepIso_swapL1_ee",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l1, ee)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL1_ee,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL1_ee )

mt2ll_leadingLepIso_swapL2_ee  = Plot(
    name = "mt2ll_leadingLepIso_swapL2_ee",
    texX = 'MT_{2}^{ll}(l.l. Iso, swap l2, ee)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.dl_mt2ll_leadingLepIso_swapL2_ee,
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( mt2ll_leadingLepIso_swapL2_ee )

extra_mu_pt  = Plot(
    name = "extra_mu_pt",
    texX = 'p_{T}(extra #mu) (GeV)', texY = 'Number of Events / 1 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.nonIsoMu['pt'] if event.nonIsoMu is not None else float('nan'),
    binning=[30,0,30],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( extra_mu_pt )

extra_ele_pt  = Plot(
    name = "extra_ele_pt",
    texX = 'p_{T}(extra e) (GeV)', texY = 'Number of Events / 1 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.nonIsoEle['pt'] if event.nonIsoEle is not None else float('nan'),
    binning=[30,0,30],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( extra_ele_pt )

dl_mt2bb  = Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_mt2bb )

dl_mt2blbl  = Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 15 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    ) 
plots.append( dl_mt2blbl )
 
l1_pt  = Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[60,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_pt )

l1_eta  = Plot(
    texX = '#eta(l_{1})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l1_eta/F" ),
    binning=[36,-3.3,3.3],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_eta )

l1_phi  = Plot(
    texX = '#phi(l_{1})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l1_phi/F" ),
    binning=[30,-pi,pi],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_phi )

l1_relIso03  = Plot(
    texX = 'I_{rel.}', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "l1_relIso03/F" ),
    binning=[40,0,2],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_relIso03 )

l1_dxy  = Plot(
    name = "l1_dxy",
    texX = '|d_{xy}|', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:abs(event.l1_dxy), 
    read_variables = ["l1_dxy/F"],
    binning=[40,0,1],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_dxy )

l1_dz  = Plot(
    name = "l1_dz",
    texX = '|d_{z}|', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:abs(event.l1_dz), 
    read_variables = ["l1_dz/F"],
    binning=[40,0,0.15],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_dz )

l1_pdgId  = Plot(
    texX = 'pdgId(l_{1})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l1_pdgId/I" ),
    binning=[32,-16,16],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l1_pdgId )

l2_pt  = Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[60,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_pt )

l2_eta  = Plot(
    texX = '#eta(l_{2})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l2_eta/F" ),
    binning=[30,-3,3],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_eta )

l2_phi  = Plot(
    texX = '#phi(l_{2})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l2_phi/F" ),
    binning=[30,-pi,pi],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_phi )

l2_relIso03  = Plot(
    texX = 'I_{rel.}', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "l2_relIso03/F" ),
    binning=[40,0,2],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_relIso03 )

l2_dxy  = Plot(
    name = "l2_dxy",
    texX = '|d_{xy}|', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:abs(event.l2_dxy), 
    read_variables = ["l2_dxy/F"],
    binning=[40,0,1],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_dxy )

l2_dz  = Plot(
    name = "l2_dz",
    texX = '|d_{z}|', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample:abs(event.l2_dz), 
    read_variables = ["l2_dz/F"],
    binning=[40,0,0.15],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_dz )

l2_pdgId  = Plot(
    texX = 'pdgId(l_{2})', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "l2_pdgId/I" ),
    binning=[32,-16,16],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( l2_pdgId )

metZoomed  = Plot(
    name = "met_pt_zoomed",
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 10 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[22,0,220],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( metZoomed )

met  = Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[1050/50,0,1050],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( met )

JZB  = Plot(
    name = "JZB",
    texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
    stack = stack, 
    attribute = lambda event, sample: sqrt( (event.met_pt*cos(event.met_phi)+event.dl_pt*cos(event.dl_phi))**2 + (event.met_pt*sin(event.met_phi)+event.dl_pt*sin(event.dl_phi))**2) - event.dl_pt, 
    read_variables =  ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"],
    binning=[25,-200,600],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( JZB )

metSig  = Plot(
    name = "metSig",
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    attribute = lambda event, sample: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan'), 
    read_variables = ["met_pt/F", "ht/F"],
    binning=[30,0,30],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( metSig )

ht  = Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[2600/100,0,2600],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( ht )

ht_zoomed  = Plot(
    name = "ht_zoomed",
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[390/15,0,390],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( ht_zoomed )

nbtags  = Plot(
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString('nBTag/I'),
    binning=[8,0,8],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( nbtags )

njets  = Plot(
    texX = 'number of jets', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( njets )

nVert  = Plot(
    texX = 'vertex multiplicity', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
    binning=[50,0,50],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( nVert )

plotting.fill(plots, read_variables = read_variables, sequence = sequence)
if not os.path.exists( plot_directory ): os.makedirs( plot_directory )

ratio = {'yRange':(0.1,1.9)}

for plot in plots:
    plotting.draw(plot, 
        plot_directory = plot_directory, ratio = ratio, 
        logX = False, logY = True, sorting = True, 
        yRange = (0.03, "auto"), 
        drawObjects = drawObjects( None ),
        scaling = {0:1},
    )

# Dump dl_mt2ll extra lepton histos
for fh in ["leadingLepIso"]:
    for swap in ["L1", "L2"]:
        for fs in ["mm","me","em","ee"]:
            ofile = os.path.join(plot_directory, "dl_mt2ll_%s_swap%s_%s.pkl"%(fh, swap, fs))
            pickle.dump(getattr( eval("mt2ll_%s_swap%s_%s"%(fh, swap, fs)), "histos"), file( ofile, 'w') )
            logger.info( "Written %s", ofile )
#elif 'Loose' in args.isolation:
#    # load mt2ll extra lepton histos (same directory but with isolation 'standard')
#    histos = {}
#    for m in ['doubleMu', 'doubleEle', 'muEle']:
#        for fh in ["leadingLepIso"]:
#            for swap in ["L1", "L2"]:
#                for fs in ["mm","me","em","ee"]:
#                    ofile = os.path.join(plot_directory, args.plot_directory, prefix.replace(args.isolation, "standard").replace("small_","").replace(args.mode, m), "dl_mt2ll_%s_swap%s_%s.pkl"%(fh, swap, fs))
#                    if os.path.isfile(ofile):
#                        logger.info( "Loading %s", ofile )
#                        histos["%s_mt2ll_%s_swap%s_%s"%(m, fh, swap, fs)] = pickle.load( file( ofile) )
#                    else:
#                        logger.warning( "File not found: %s", ofile)
#
#    # construct shape of swapped leptons
#    if args.mode == 'doubleMu':
#        fss = ["mm"]
#    elif args.mode == 'doubleEle':
#        fss = ['ee']
#    elif args.mode== 'muEle':
#        fss = ['em', 'me']
#    else: raise ValueError( "Unknown mode %s"%args.mode )
#
#    # sum up all contributions
#    shape_histos = []
#    for m in ['doubleMu', 'doubleEle', 'muEle']:
#        for fh in ["leadingLepIso"]:
#            for swap in ["L1", "L2"]:
#                for fs in fss:
#                    logger.info( "Adding %s_mt2ll_%s_swap%s_%s"%(m, fh, swap, fs) )
#                    shape_histos.extend( histos["%s_mt2ll_%s_swap%s_%s"%(m, fh, swap, fs)][0] )
#
#    shape = add_histos( shape_histos )
#    #shape.Scale( dl_mt2ll.histos[0][ mc.index( TTJets_l2_nonPrompt  ) ].Integral() / shape.Integral() )
#    bin_low, bin_high = shape.FindBin( 90 ), shape.FindBin( 290 )
#    h_TTJets_l2_nonPrompt = dl_mt2ll.histos[0][ mc.index( TTJets_l2_nonPrompt  ) ] 
#    shape.Scale( h_TTJets_l2_nonPrompt.Integral( bin_low, bin_high ) / shape.Integral( bin_low, bin_high ) )
#    shape.style = styles.lineStyle( ROOT.kRed )
#
#    plotting.draw(
#        Plot.fromHisto(name = "dl_mt2ll_comp", histos = dl_mt2ll.histos + [[ shape ]], texX = dl_mt2ll.texX, texY = dl_mt2ll.texY),
#        plot_directory = plot_directory, #ratio = ratio, 
#        logX = False, logY = True, sorting = False,
#         yRange = (0.003, "auto"), legend = None ,
#        # scaling = {0:1},
#         drawObjects = drawObjects( None )
#    )
#    plotting.draw(
#        Plot.fromHisto(name = "dl_mt2ll_shape", histos = [[h_TTJets_l2_nonPrompt]] + [[ shape ]], texX = dl_mt2ll.texX, texY = dl_mt2ll.texY),
#        plot_directory = plot_directory, #ratio = ratio, 
#        logX = False, logY = True, sorting = False,
#         yRange = (0.003, "auto"), legend = None ,
#        # scaling = {0:1},
#         drawObjects = drawObjects( dataMCScale )
#    )
#     
#logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )

