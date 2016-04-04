#!/usr/bin/env python
''' Analysis script for 1D 2l plots (RootTools)
'''
#Standard imports
import ROOT
from math import sqrt, cos, sin, pi
import itertools

# batch mode
ROOT.gROOT.SetBatch(True)

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

argParser.add_argument('--small',
    action='store_true',
#    default=True,
    help='Just a small subset?',
)

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='ttG',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

if args.mode=="doubleMu":
    leptonSelectionString = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0"
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2"
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"
    trigger    = "HLT_mue"
else:
    raise ValueError( "Mode %s not known"%args.mode )

# Extra requirements on data
filterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&vetoPassed&&jsonPassed&&weight>0)"


# Use data points for TTG
TTG_photonAsMet.style = styles.errorStyle( ROOT.kBlack )
TTG_photonAsMet.setSelectionString(["photonAsMet&&gamma_pt>50", trigger])   # select on photons

for mc in [TTZtoLLNuNu, TTZtoQQ]:
  mc.style = styles.fillStyle( mc.color)
  mc.setSelectionString(["abs(dl_mass-91.1876)<15&&dl_pt>50", trigger])     # select on Z bosons

stack = Stack([TTZtoLLNuNu, TTZtoQQ], TTG_photonAsMet)

# user data
from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda data:data.weight

cuts=[
    ("njet2", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
    ("nbtag1", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
    ("nbtag0", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)==0"),
    ("mll20", "dl_mass>20"),
    ("met80", "met_pt>80"),
    ("metSig5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
]
                
def drawObjects( scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
    (0.15, 0.95, 'CMS Preliminary'), 
    (0.45, 0.95, '13 TeV, Scale %3.2f'% ( scale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 


##for i_comb in [0]:
#for i_comb in [len(cuts)]:
for i_comb in reversed( range( len(cuts)+1 ) ):
#for i_comb in range(len(cuts)+1):
    for comb in itertools.combinations( cuts, i_comb ):
        for sample in stack.samples():
          sample.clear()  # Need a reload of the chain in order to avoid segFault

        presel = [("isOS","isOS")] 
        presel.extend( comb )

        prefix = '_'.join([args.mode, '-'.join([p[0] for p in presel])])
        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%path )
            continue

        if "nbtag1" in prefix and "nbtag0" in prefix: continue

        selectionString = "&&".join( [p[1] for p in presel] + [leptonSelectionString] )
        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

        logger.info( "Calculating normalization constants" )
        yield_TTG         = TTG_photonAsMet.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']
        yield_TTZtoLLNuNu = TTZtoLLNuNu.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']
        yield_TTZtoQQ     = TTZtoQQ.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']
        scale = yield_TTG/(yield_TTZtoLLNuNu+yield_TTZtoQQ)


        plots = []

        dl_mass  = Plot(
            texX = 'm(ll) (GeV)', texY = 'Number of Events / 3 GeV',
            stack = stack, 
            variable = Variable.fromString( "dl_mass/F" ),
            binning=[150/3,0,150],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mass )

        dl_pt  = Plot(
            texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            variable = Variable.fromString( "dl_pt/F" ),
            binning=[40,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_pt )

        dl_eta  = Plot(
            texX = '#eta(ll) ', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "dl_eta/F" ),
            binning=[30,-3,3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_eta )

        dl_phi  = Plot(
            texX = '#phi(ll) (GeV)', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "dl_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_phi )

        dl_mt2ll  = Plot(
            texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString( "dl_mt2ll/F" ),
            binning=[300/20,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2ll )

        dl_mt2bb  = Plot(
            texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString( "dl_mt2bb/F" ),
            binning=[300/20,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2bb )

        dl_mt2blbl  = Plot(
            texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString( "dl_mt2blbl/F" ),
            binning=[300/20,0,300],
            selectionString = selectionString,
            weight = weight,
            ) 
        plots.append( dl_mt2blbl )
         
        V_pt  = Plot(
            texX = 'p_{T}(Z or #gamma) (GeV)', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            variable = Variable.fromString( "V_pt/F" ).addFiller(
                helpers.uses(lambda data: data.gamma_pt[0] if data.photonAsMet else data.dl_pt , ["gamma[pt/F]","photonAsMet/O", "dl_pt/F"] )
            ), 
            binning=[60,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( V_pt )

        l1_pt  = Plot(
            texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            variable = Variable.fromString( "l1_pt/F" ),
            binning=[60,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_pt )


        l1_eta  = Plot(
            texX = '#eta(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l1_eta/F" ),
            binning=[36,-3.3,3.3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_eta )

        l1_phi  = Plot(
            texX = '#phi(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l1_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_phi )

        l1_pdgId  = Plot(
            texX = 'pdgId(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l1_pdgId/I" ),
            binning=[32,-16,16],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_pdgId )

        l2_pt  = Plot(
            texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
            stack = stack, 
            variable = Variable.fromString( "l2_pt/F" ),
            binning=[60,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_pt )

        l2_eta  = Plot(
            texX = '#eta(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l2_eta/F" ),
            binning=[30,-3,3],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_eta )

        l2_phi  = Plot(
            texX = '#phi(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l2_phi/F" ),
            binning=[30,-pi,pi],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_phi )

        l2_pdgId  = Plot(
            texX = 'pdgId(l_{1})', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "l2_pdgId/I" ),
            binning=[32,-16,16],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l2_pdgId )

        metZoomed  = Plot(
            name = "met_pt_zoomed",
            texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            variable = Variable.fromString( "met_pt/F" ),
            binning=[22,0,220],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( metZoomed )

        met  = Plot(
            texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
            stack = stack, 
            variable = Variable.fromString( "met_pt/F" ),
            binning=[1050/50,0,1050],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( met )


        JZB  = Plot(
            texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
            stack = stack, 
            variable = Variable.fromString('JZB/F').addFiller (
                helpers.uses( 
                    lambda data: sqrt( (data.met_pt*cos(data.met_phi)+data.dl_pt*cos(data.dl_phi))**2 + (data.met_pt*sin(data.met_phi)+data.dl_pt*sin(data.dl_phi))**2) - data.dl_pt, 
                    ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"])
            ), 
            binning=[25,-200,600],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( JZB )

        metSig  = Plot(
            texX = '#slash{E}_{T}/#sqrt(H_{T}) (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
            stack = stack, 
            variable = Variable.fromString('metSig/F').addFiller (
                helpers.uses( 
                    lambda data: data.met_pt/sqrt(data.ht) if data.ht>0 else float('nan') , 
                    ["met_pt/F", "ht/F"])
            ), 
            binning=[20,0,20],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( metSig )

        ht  = Plot(
            texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
            stack = stack, 
            variable = Variable.fromString( "ht/F" ),
            binning=[2600/100,0,2600],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( ht )

        ht_zoomed  = Plot(
            name = "ht_zoomed",
            texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
            stack = stack, 
            variable = Variable.fromString( "ht/F" ),
            binning=[390/15,0,390],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( ht_zoomed )

        cosMetJet0phi = Plot(\
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString('cosMetJet0phi/F').addFiller (
                helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
            ), 
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet0phi )

        cosMetJet1phi = Plot(\
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString('cosMetJet1phi/F').addFiller (
                helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
            ), 
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet1phi )

        jet0pt  = Plot(
            texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString('jet0pt/F').addFiller (
                helpers.uses(lambda data: data.JetGood_pt[0], "JetGood[pt/F]" )
            ), 
            binning=[980/20,0,980],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet0pt )

        jet1pt  = Plot(
            texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString('jet1pt/F').addFiller (
                helpers.uses(lambda data: data.JetGood_pt[1], "JetGood[pt/F]" )
            ), 
            binning=[980/20,0,980],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet1pt )

        jet2pt  = Plot(
            texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString('jet2pt/F').addFiller (
                helpers.uses(lambda data: data.JetGood_pt[2], "JetGood[pt/F]" )
            ), 
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet2pt )

        jet3pt  = Plot(
            texX = 'p_{T}(4^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString('jet3pt/F').addFiller (
                helpers.uses(lambda data: data.JetGood_pt[3], "JetGood[pt/F]" )
            ), 
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet3pt )

        jet4pt  = Plot(
            texX = 'p_{T}(5^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            variable = Variable.fromString('jet4pt/F').addFiller (
                helpers.uses(lambda data: data.JetGood_pt[4], "JetGood[pt/F]" )
            ), 
            binning=[400/20,0,400],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( jet4pt )

        nbtags  = Plot(
            texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString('nBTag/I'),
            binning=[8,0,8],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nbtags )

        njets  = Plot(
            texX = 'number of jets', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString('nJetGood/I'),
            binning=[14,0,14],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( njets )

        nVert  = Plot(
            texX = 'vertex multiplicity', texY = 'Number of Events',
            stack = stack, 
            variable = Variable.fromString( "nVert/I" ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nVert )

        read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]"]
        plotting.fill(plots, read_variables = read_variables)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )
        for plot in plots:
            plotting.draw(plot, 
                plot_directory = plot_path, ratio = {'yRange':(0.1,1.9)}, 
                logX = False, logY = False, sorting = True, 
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( scale )
            )
        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
