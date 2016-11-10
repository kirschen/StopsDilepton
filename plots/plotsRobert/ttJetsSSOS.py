''' Analysis script for SS/OS comparison (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import copy

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
    default='doubleMu',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle'])

argParser.add_argument('--charges',
    default='OS',
    action='store',
    choices=['OS', 'SS'])

argParser.add_argument('--zMode',
    default='offZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)

argParser.add_argument('--small',
    action='store_true',
#    default = True,
    help='Small?',
)

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='SSOS',
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
postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepLoose/" 
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
#from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

# Extra requirements on data
dataFilterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

#if      n_t and n_W and not n_B and not n_D and not n_tau:
#    print "t->W->l"
#elif    n_t and not n_W and n_B and not n_D and not n_tau:
#    print "t->b->B->l"
#elif    n_t and not n_W and n_B and n_D and not n_tau:
#    print "t->b->B->D->l"
#elif    n_t and n_W and n_tau:
#    print "t->W->tau->l"
#elif    n_t and n_W and not n_B and n_D and not n_tau:
#    print "t->W->c->D->l"

top_W       = "GenLep_n_t>0&&GenLep_n_W>0&&GenLep_n_B==0&&GenLep_n_D==0&&GenLep_n_tau==0"
top_b       = "GenLep_n_t>0&&GenLep_n_W==0&&GenLep_n_B>0&&GenLep_n_D==0&&GenLep_n_tau==0"
top_b_c     = "GenLep_n_t>0&&GenLep_n_W==0&&GenLep_n_B>0&&GenLep_n_D>0&&GenLep_n_tau==0"
top_W_c     = "GenLep_n_t>0&&GenLep_n_W>0&&GenLep_n_B==0&&GenLep_n_D>0&&GenLep_n_tau==0"
top_W_tau   = "GenLep_n_t>0&&GenLep_n_W>0&&GenLep_n_B==0&&GenLep_n_D==0&&GenLep_n_tau>0"
other_HF    = "GenLep_n_t==0&&GenLep_n_W==0&&(GenLep_n_B>0||GenLep_n_D>0)&&GenLep_n_tau==0"
other = "&&".join("(!(%s))"%x for x in [top_W, top_b, top_b_c, top_W_c, top_W_tau, other_HF])

def Sum(s):
    return "Sum$(%s)"%s

TTJets_sample = TTJets_Lep

TTJets_top_W = copy.deepcopy(TTJets_sample)
TTJets_top_W.setSelectionString( Sum(top_W)+"==2&&"+Sum(top_b)+"==0")
TTJets_top_W.name = "TTJets_top_W"
TTJets_top_W.texName = 't#bar{t} + Jets (2g.l from W)'
TTJets_top_W.style = styles.lineStyle( ROOT.kBlack )

TTJets_top_b = copy.deepcopy(TTJets_sample)
TTJets_top_b.setSelectionString( Sum(top_b)+">=1")
TTJets_top_b.name = "TTJets_top_b"
TTJets_top_b.texName = 't#bar{t} + Jets (>=1 g.l from b)'
TTJets_top_b.style = styles.lineStyle( ROOT.kBlue )

TTJets_top_b_c = copy.deepcopy(TTJets_sample)
TTJets_top_b_c.setSelectionString( Sum(top_b_c)+">=1")
TTJets_top_b_c.name = "TTJets_top_b_c"
TTJets_top_b_c.texName = 't#bar{t} + Jets (>=1 g.l from b->c)'
TTJets_top_b_c.style = styles.lineStyle( ROOT.kGreen )

TTJets_top_W_c = copy.deepcopy(TTJets_sample)
TTJets_top_W_c.setSelectionString( Sum(top_W_c)+">=1")
TTJets_top_W_c.name = "TTJets_top_W_c"
TTJets_top_W_c.texName = 't#bar{t} + Jets (>=1 g.l from W->c)'
TTJets_top_W_c.style = styles.lineStyle( ROOT.kMagenta )

samples = [ TTJets_top_W, TTJets_top_b, TTJets_top_b_c, TTJets_top_W_c  ]
if args.small:
    for s in samples:
        s.reduceFiles(to = 1)

for s in samples:
    s.scale = 10 #10/fb 

from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event:event.weight

cuts=[
    ("njet2", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
    ("nbtag1", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
#    ("nbtag0", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)==0"),
    ("mll20", "dl_mass>20"),
#    ("met80", "met_pt>80"),
#    ("metSig5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
#    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
]

if args.charges   == "OS":
    cuts =  [("isOS", "isOS")] + cuts
elif args.charges == "SS":
    cuts =  [("isSS", "l1_pdgId*l2_pdgId>0")] + cuts
else:
    raise ValueError

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

if args.mode=="doubleMu":
    leptonSelectionString = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    trigger    = "HLT_mue"
else:
    raise ValueError( "Mode %s not known"%args.mode )

stack = Stack(samples)

prefix = '_'.join([args.mode, args.zMode, '-'.join([p[0] for p in cuts])])
plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
if os.path.exists(plot_path) and not args.overwrite:
    logger.info( "Path %s not empty. Exiting."%path )
    sys.exit(0)

selectionString = "&&".join( [p[1] for p in cuts] + [leptonSelectionString] + [trigger] )

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

#dl_pt  = Plot(
#    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "dl_pt/F" ),
#    binning=[40,0,400],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( dl_pt )
#
#dl_eta  = Plot(
#    texX = '#eta(ll) ', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "dl_eta/F" ),
#    binning=[30,-3,3],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( dl_eta )
#
#dl_phi  = Plot(
#    texX = '#phi(ll) (GeV)', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "dl_phi/F" ),
#    binning=[30,-pi,pi],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( dl_phi )
dl_mt2ll  = Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_mt2ll )

dl_mt2bb  = Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    )
plots.append( dl_mt2bb )

dl_mt2blbl  = Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    weight = weight,
    ) 
plots.append( dl_mt2blbl )
 
#l1_pt  = Plot(
#    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l1_pt/F" ),
#    binning=[60,0,300],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l1_pt )
#
#l1_eta  = Plot(
#    texX = '#eta(l_{1})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l1_eta/F" ),
#    binning=[36,-3.3,3.3],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l1_eta )
#
#l1_phi  = Plot(
#    texX = '#phi(l_{1})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l1_phi/F" ),
#    binning=[30,-pi,pi],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l1_phi )
#
#l1_pdgId  = Plot(
#    texX = 'pdgId(l_{1})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l1_pdgId/I" ),
#    binning=[32,-16,16],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l1_pdgId )
#
#l2_pt  = Plot(
#    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 5 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l2_pt/F" ),
#    binning=[60,0,300],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l2_pt )
#
#l2_eta  = Plot(
#    texX = '#eta(l_{2})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l2_eta/F" ),
#    binning=[30,-3,3],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l2_eta )
#
#l2_phi  = Plot(
#    texX = '#phi(l_{2})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l2_phi/F" ),
#    binning=[30,-pi,pi],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l2_phi )
#
#l2_pdgId  = Plot(
#    texX = 'pdgId(l_{2})', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "l2_pdgId/I" ),
#    binning=[32,-16,16],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( l2_pdgId )
#
#metZoomed  = Plot(
#    name = "met_pt_zoomed",
#    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 10 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "met_pt/F" ),
#    binning=[22,0,220],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( metZoomed )
#
#met  = Plot(
#    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "met_pt/F" ),
#    binning=[1050/50,0,1050],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( met )
#
#JZB  = Plot(
#    texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('JZB/F').addFiller (
#        helpers.uses( 
#            lambda event: sqrt( (event.met_pt*cos(event.met_phi)+event.dl_pt*cos(event.dl_phi))**2 + (event.met_pt*sin(event.met_phi)+event.dl_pt*sin(event.dl_phi))**2) - event.dl_pt, 
#            ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"])
#    ), 
#    binning=[25,-200,600],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( JZB )
#
#metSig  = Plot(
#    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('metSig/F').addFiller (
#        helpers.uses( 
#            lambda event: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan') , 
#            ["met_pt/F", "ht/F"])
#    ), 
#    binning=[30,0,30],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( metSig )
#
#ht  = Plot(
#    texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "ht/F" ),
#    binning=[2600/100,0,2600],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( ht )
#
#ht_zoomed  = Plot(
#    name = "ht_zoomed",
#    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString( "ht/F" ),
#    binning=[390/15,0,390],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( ht_zoomed )
#
#cosMetJet0phi = Plot(\
#    texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString('cosMetJet0phi/F').addFiller (
#        helpers.uses(lambda event: cos( event.met_phi - event.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
#    ), 
#    binning = [10,-1,1], 
#    selectionString = selectionString,
#    weight = weight,
#)
#plots.append( cosMetJet0phi )
#
#cosMetJet1phi = Plot(\
#    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString('cosMetJet1phi/F').addFiller (
#        helpers.uses(lambda event: cos( event.met_phi - event.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
#    ), 
#    binning = [10,-1,1], 
#    selectionString = selectionString,
#    weight = weight,
#)
#plots.append( cosMetJet1phi )
#
#jet0pt  = Plot(
#    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('jet0pt/F').addFiller (
#        helpers.uses(lambda event: event.JetGood_pt[0], "JetGood[pt/F]" )
#    ), 
#    binning=[980/20,0,980],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( jet0pt )
#
#jet1pt  = Plot(
#    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('jet1pt/F').addFiller (
#        helpers.uses(lambda event: event.JetGood_pt[1], "JetGood[pt/F]" )
#    ), 
#    binning=[980/20,0,980],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( jet1pt )
#
#jet2pt  = Plot(
#    texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('jet2pt/F').addFiller (
#        helpers.uses(lambda event: event.JetGood_pt[2], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( jet2pt )
#
#jet3pt  = Plot(
#    texX = 'p_{T}(4^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('jet3pt/F').addFiller (
#        helpers.uses(lambda event: event.JetGood_pt[3], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( jet3pt )
#
#jet4pt  = Plot(
#    texX = 'p_{T}(5^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = TreeVariable.fromString('jet4pt/F').addFiller (
#        helpers.uses(lambda event: event.JetGood_pt[4], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( jet4pt )
#
#nbtags  = Plot(
#    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString('nBTag/I'),
#    binning=[8,0,8],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( nbtags )
#
#njets  = Plot(
#    texX = 'number of jets', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString('nJetGood/I'),
#    binning=[14,0,14],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( njets )
#
#nVert  = Plot(
#    texX = 'vertex multiplicity', texY = 'Number of Events',
#    stack = stack, 
#    variable = TreeVariable.fromString( "nVert/I" ),
#    binning=[50,0,50],
#    selectionString = selectionString,
#    weight = weight,
#    )
#plots.append( nVert )


read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]"]
plotting.fill(plots, read_variables = read_variables)
if not os.path.exists( plot_path ): os.makedirs( plot_path )

ratio =  None

for plot in plots:
    plotting.draw(plot, 
        plot_directory = plot_path, ratio = ratio, 
        logX = False, logY = True, sorting = True, 
        yRange = (0.03, "auto"), 
        #drawObjects = drawObjects( dataMCScale )
    )
logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
