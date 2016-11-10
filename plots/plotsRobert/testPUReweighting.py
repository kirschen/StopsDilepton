''' Analysis script for 1D 2l plots (RootTools)
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

argParser.add_argument('--small',
    action='store_true',
    #default = True,
    help='Small?',
)

argParser.add_argument('--reversed',
    action='store_true',
    help='Reversed?',
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

argParser.add_argument('--met',
    default='def',
    action='store',
    choices=['def', 'none', 'low'],
    help='met cut',
)

argParser.add_argument('--signals',
    action='store',
    nargs='*',
    type=str,
    default=[],
    help="Signals?"
    )

argParser.add_argument('--overwrite',
    #default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='pngPU',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
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
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *

if args.mode=="doubleMu":
    lepton_selection_string_mc   = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
elif args.mode=="doubleEle":
    lepton_selection_string_mc = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
elif args.mode=="muEle":
    lepton_selection_string_mc = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
elif args.mode=="dilepton":
    lepton_selection_string_mc = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"
elif args.mode=="sameFlavour":
    lepton_selection_string_mc = "&&".join([ "(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2)", getZCut(args.zMode)])
else:
    raise ValueError( "Mode %s not known"%args.mode )

dy      = DY_HT_LO
dy_Central = copy.deepcopy( dy )
dy_Up   = copy.deepcopy( dy )
dy_Down = copy.deepcopy( dy )

mc_samples = [dy, dy_Central, dy_Up, dy_Down]

if args.small:
    for sample in mc_samples:
        sample.reduceFiles(to = 1)

# 2016 PU reweighting
from StopsDilepton.tools.puReweighting import getNVTXReweightingFunction
pu_reweight = getNVTXReweightingFunction(filename = "dilepton_allZ_isOS_4000pb.pkl")

weight = lambda event: event.weight

for sample in mc_samples:
    sample.setSelectionString([ mcFilterCut, lepton_selection_string_mc])

#dy.weight = lambda event:pu_reweight( event.nVert )['reweight']
dy.style = styles.lineStyle( ROOT.kBlack )
dy_Central.weight = lambda event:pu_reweight( event.nVert )['reweight']
dy_Central.style = styles.lineStyle( ROOT.kBlue )
dy_Up.weight = lambda event:pu_reweight( event.nVert )['reweight_Up']
dy_Up.style = styles.lineStyle( ROOT.kRed )
dy_Down.weight = lambda event:pu_reweight( event.nVert )['reweight_Down']
dy_Down.style = styles.lineStyle( ROOT.kRed )

from StopsDilepton.tools.user import plot_directory

#from StopsDilepton.tools.objectSelection import multiIsoLepString
#multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))

basic_cuts=[
#    ("multiIsoWP", "l1_index>=0&&l1_index<1000&&l2_index>=0&&l2_index<1000&&"+multiIsoWP),
#    ("eleCutBasedTightID", "(abs(l1_pdgId)!=11 || LepGood_eleCutIdSpring15_25ns_v1[l1_index]>=4)&&((abs(l2_pdgId)!=11 || LepGood_eleCutIdSpring15_25ns_v1[l2_index]>=4))"),
    ("mll20", "dl_mass>20"),
    ("dPhiJet0-dPhiJet1", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )==0"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
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

def selection( ):
    res = [ \
        ("njet%s"%args.njet, "nJetGood%s"%mCutStr( args.njet )),
        ("nbtag%s"%args.nbtag, "nBTag%s"%mCutStr( args.nbtag ))]
    if args.met=='def': res.extend([\
        ("met80", "met_pt>80"),
        ("metSig5", "(met_pt/sqrt(ht)>5||nJetGood==0)")])
    elif args.met=='low':
        res.extend([  ("metSm80", "met_pt<80")] )
    elif args.met=='none':
        pass
    return res

cuts = selection()

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

stack = Stack([dy], [dy_Central], [dy_Up], [dy_Down])

if len(args.signals)>0:
    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_2l_postProcessed import *
    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *
    for s in args.signals:
        if "*" in s:
            split = s.split("*")
            sig, fac = split[0], int(split[1])
        else:
            sig, fac = s, 1
        try:
            stack.append( [eval(sig)] )
            if hasattr(stack[-1][0], "scale"): 
                stack[-1][0].scale*=fac
            elif fac!=1:
                stack[-1][0].scale = fac
            else: pass

            if fac!=1:
                stack[-1][0].name+=" x"+str(fac)                
            logger.info( "Adding sample %s with factor %3.2f", sig, fac)
        except NameError:
            logger.warning( "Could not add signal %s", s)

sequence = []

#from StopsDilepton.tools.helpers import deltaR
#from StopsDilepton.tools.objectSelection import getJets

rev = reversed if args.reversed else lambda x:x
#for i_comb in rev( range( len(cuts)+1 ) ):
for i_comb in [ len(cuts) ]:
    for comb in itertools.combinations( cuts, i_comb ):

        if args.charges=="OS":
            presel = [("isOS","isOS")]
        elif args.charges=="SS":
            presel = [("isSS","l1_pdgId*l2_pdgId>0")]
        else:
            raise ValueError

        # presel += [("highMiniRelIso","max(l1_miniRelIso,l2_miniRelIso)>0.4")]
 
        presel.extend( basic_cuts )
        presel.extend( comb )

        ppfixes = [args.mode, args.zMode]
        if args.small: ppfixes = ['small'] + ppfixes
        prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in presel ] ) ] )

        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%plot_path )
            continue

        selectionString = "&&".join( [p[1] for p in presel] )

        if  prefix.count('nbtag')>1: continue
        if  prefix.count('njet')>1: continue

        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

        plots = []
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

        nVert  = Plot(
            texX = 'vertex multiplicity', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "nVert/I" ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nVert )


        read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F,btagCSV/F,id/I]", "nJetGood/I"]
        plotting.fill(plots, read_variables = read_variables, sequence = sequence)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        for plot in plots:
            plotting.draw(
                plot,
                plot_directory = plot_path, ratio = None, 
                logX = False, logY = True, #sorting = True, 
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( None )
            )
        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
