''' Analysis script for 1D 2l plots (RootTools)
'''

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
      default='DEBUG',
      help="Log level for logging"
)

argParser.add_argument('--small',
    action='store_true',
    #default = True,
    help='Small?',
)

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='png25ns_jet250',
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
postProcessing_directory = "postProcessed_Fall15_mAODv2/jet250/" 

from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_jet250_postProcessed import *
jetHT = Sample.fromDirectory(name="jetHT", treeName="Events", texName="JetHT (Run2015D)",       directory=os.path.join(data_directory,postProcessing_directory,"JetHT_Run2015D_16Dec") ) 
jetHT.lumi = 1000*(2.165)

data_sample = jetHT 
qcd_sample = QCD_Pt
trigger     = "(1)"

# Extra requirements on data
dataFilterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

data_sample.style = styles.errorStyle( ROOT.kBlack )
data_sample.setSelectionString([dataFilterCut, trigger])
lumi_scale = data_sample.lumi/1000

TTJets_sample = TTJets

mc = [ qcd_sample, TTJets_sample, WJetsToLNu, singleTop, DY, DYToNuNu]
for sample in mc:
    sample.style = styles.fillStyle( sample.color)
    sample.setSelectionString([mcFilterCut, trigger])
if args.small:
    for sample in mc + [data_sample]:
        sample.reduceFiles(to = 1)


from StopsDilepton.tools.user import plot_directory

## official PU reweighting
#weight = lambda data:data.weight

cuts=[
    ("dijet500", "nJetGood>=1&&JetGood_pt[1]>500"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==0"),
]
                
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

stack = Stack(mc)
stack.append( [data_sample] )

sequence = []
ppfixes = []
 
if args.small: ppfixes = ['small'] + ppfixes
prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in cuts ] ) ] )

plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
if os.path.exists(plot_path) and not args.overwrite:
    logger.info( "Path %s not empty. Skipping."%path )
    sys.exit(0)


selectionString = "&&".join( [p[1] for p in cuts] )

logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

logger.info( "Calculating normalization constants" )        
yield_mc    = sum(s.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val'] for s in mc)
yield_data  = data_sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']

for sample in mc:
    dataMCScale = yield_data/(yield_mc*lumi_scale)
    sample.scale = lumi_scale*dataMCScale

plots = []

met  = Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack, 
    variable = Variable.fromString( "met_pt/F" ),
    binning=[1050/50,0,1050],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( met )

metSig  = Plot(
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    variable = Variable.fromString('metSig/F'),
    binning=[30,0,30],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( metSig )

ht  = Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    variable = Variable.fromString( "ht/F" ),
    binning=[2600/100,0,2600],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( ht )

ht_zoomed  = Plot(
    name = "ht_zoomed",
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    stack = stack, 
    variable = Variable.fromString( "ht/F" ),
    binning=[390/15,0,390],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( ht_zoomed )

#cosMetJet0phi = Plot(\
#    texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
#    stack = stack, 
#    variable = Variable.fromString('cosMetJet0phi/F').addFiller (
#        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
#    ), 
#    binning = [10,-1,1], 
#    selectionString = selectionString,
#    # weight = weight,
#)
#plots.append( cosMetJet0phi )
#
#cosMetJet1phi = Plot(\
#    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
#    stack = stack, 
#    variable = Variable.fromString('cosMetJet1phi/F').addFiller (
#        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
#    ), 
#    binning = [10,-1,1], 
#    selectionString = selectionString,
#    # weight = weight,
#)
#plots.append( cosMetJet1phi )
#
#jet0pt  = Plot(
#    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = Variable.fromString('jet0pt/F').addFiller (
#        helpers.uses(lambda data: data.JetGood_pt[0], "JetGood[pt/F]" )
#    ), 
#    binning=[980/20,0,980],
#    selectionString = selectionString,
#    # weight = weight,
#    )
#plots.append( jet0pt )
#
#jet1pt  = Plot(
#    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = Variable.fromString('jet1pt/F').addFiller (
#        helpers.uses(lambda data: data.JetGood_pt[1], "JetGood[pt/F]" )
#    ), 
#    binning=[980/20,0,980],
#    selectionString = selectionString,
#    # weight = weight,
#    )
#plots.append( jet1pt )
#
#jet2pt  = Plot(
#    texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = Variable.fromString('jet2pt/F').addFiller (
#        helpers.uses(lambda data: data.JetGood_pt[2], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    # weight = weight,
#    )
#plots.append( jet2pt )
#
#jet3pt  = Plot(
#    texX = 'p_{T}(4^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = Variable.fromString('jet3pt/F').addFiller (
#        helpers.uses(lambda data: data.JetGood_pt[3], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    # weight = weight,
#    )
#plots.append( jet3pt )
#
#jet4pt  = Plot(
#    texX = 'p_{T}(5^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
#    stack = stack, 
#    variable = Variable.fromString('jet4pt/F').addFiller (
#        helpers.uses(lambda data: data.JetGood_pt[4], "JetGood[pt/F]" )
#    ), 
#    binning=[400/20,0,400],
#    selectionString = selectionString,
#    # weight = weight,
#    )
#plots.append( jet4pt )

nbtags  = Plot(
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = stack, 
    variable = Variable.fromString('nBTag/I'),
    binning=[8,0,8],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( nbtags )

njets  = Plot(
    texX = 'number of jets', texY = 'Number of Events',
    stack = stack, 
    variable = Variable.fromString('nJetGood/I'),
    binning=[14,0,14],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( njets )

nVert  = Plot(
    texX = 'vertex multiplicity', texY = 'Number of Events',
    stack = stack, 
    variable = Variable.fromString( "nVert/I" ),
    binning=[50,0,50],
    selectionString = selectionString,
    # weight = weight,
    )
plots.append( nVert )

#read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]"]
#plotting.fill(plots, read_variables = read_variables, sequence = sequence)
plotting.fill_with_draw(plots, weight_string = 'weight')
if not os.path.exists( plot_path ): os.makedirs( plot_path )

ratio = {'yRange':(0.1,1.9)}

for plot in plots:
    plotting.draw(plot, 
        plot_directory = plot_path, ratio = ratio, 
        logX = False, logY = True, sorting = True, 
        yRange = (0.03, "auto"), 
        drawObjects = drawObjects( dataMCScale )
    )
logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
