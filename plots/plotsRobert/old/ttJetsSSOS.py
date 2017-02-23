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
weight = lambda event, sample:event.weight

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
