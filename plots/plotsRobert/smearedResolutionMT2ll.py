''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos, atan2
import itertools

#RootTools
from RootTools.core.standard import *
# StopsDilepton
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

argParser.add_argument('--ttjets',
    default='LO',
    action='store',
    choices=['LO', 'NLO'])

argParser.add_argument('--noData',
    action='store_true',
    help='Skip data',
)

argParser.add_argument('--small',
    action='store_true',
    # default = True,
    help='Small?',
)

argParser.add_argument('--reversed',
    action='store_true',
    help='Reversed?',
)

argParser.add_argument('--signals',
    action='store',
    nargs='*',
    type=str,
    default=[],
    help="Signals?"
    )

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='png25ns_2l_mAODv2_2100_noPU_VTVT_smeared',
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
postProcessing_directory = "postProcessed_Fall15_mAODv2/dilep/" 

from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

if args.mode=="doubleMu":
    leptonSelectionString = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    data_sample = DoubleMuon_Run2015D if not args.noData else None
    qcd_sample = QCD_Mu5 #FIXME
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    data_sample = DoubleEG_Run2015D if not args.noData else None
    qcd_sample = QCD_EMbcToE
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    data_sample = MuonEG_Run2015D if not args.noData else None
    qcd_sample = QCD_Mu5EMbcToE
    trigger    = "HLT_mue"
else:
    raise ValueError( "Mode %s not known"%args.mode )

# Extra requirements on data
dataFilterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

if args.ttjets == "NLO":
    TTJets_sample = TTJets
elif args.ttjets == "LO":
    TTJets_sample = TTJets_Lep 
else:
    raise ValueError

#mc = [ DY, TTJets, qcd_sample, singleTop, TTX, diBoson, triBoson, WJetsToLNu]
#mc = [ DY, TTJets, qcd_sample, TTZ]
mc = [ DY_HT_LO, TTJets_sample, singleTop, qcd_sample, TTZ, TTXNoZ, diBoson, WZZ]
#mc = [ TTX]
if args.small:
    for sample in mc:
        sample.reduceFiles(to = 1)

if not args.noData:
    data_sample.style = styles.errorStyle( ROOT.kBlack )
    lumi_scale = data_sample.lumi/1000
    data_sample.read_variables = ["LepGood[pt/F,phi/F,eta/F,pdgId/I]"]
for sample in mc:
    sample.style = styles.fillStyle( sample.color)
    sample.read_variables = ["LepGood[pt/F,phi/F,eta/F,pdgId/I,mcPt/F]","met_genPt/F", "met_genPhi/F"]

from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event, sample:event.weight

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))

cuts=[
#    ("leadingLepIsTight", "l1_miniRelIso<0.4"),
#    ("EE", "abs(l1_eta)>1.5&&abs(l2_eta)>1.5"),
#    ("EB", "(abs(l1_eta)<1.5&&abs(l2_eta)>1.5||abs(l1_eta)>1.5&&abs(l2_eta)<1.5)"),
#    ("BB", "abs(l1_eta)<1.5&&abs(l2_eta)<1.5"),
    ("njet2", "nJetGood>=2"),
    ("nbtag1", "nBTag>=1"),
    ("mll20", "dl_mass>20"),
    ("met80", "met_pt>80"),
    ("metSig5", "met_pt/sqrt(ht)>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),

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
if not args.noData:
    stack.append( [data_sample] )

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

def mt2llSmeared( data ):

    # Get selected leptons
    l1 = {'pt':event.l1_pt, 'eta':event.l1_eta, 'phi':event.l1_phi, 'pdgId':event.l1_pdgId} 
    l2 = {'pt':event.l2_pt, 'eta':event.l2_eta, 'phi':event.l2_phi, 'pdgId':event.l2_pdgId} 

    try:
        l1['mcPt'] = event.LepGood_mcPt[event.l1_index]
        l2['mcPt'] = event.LepGood_mcPt[event.l2_index]
    except AttributeError:
        # Data
        l1['mcPt'] = l1['pt'] 
        l2['mcPt'] = l2['pt']
        
    # Stretch data/MC difference by 10%
    l1['ptScaled'] = l1['pt'] + 0.1*(l1['pt'] - l1['mcPt']) if l1['mcPt']>0 and abs(l1['pdgId'])==11 else l1['pt']
    l2['ptScaled'] = l2['pt'] + 0.1*(l2['pt'] - l2['mcPt']) if l2['mcPt']>0 and abs(l2['pdgId'])==11 else l2['pt']

    mt2Calc.reset()
    # Correcting MET
    met_px = event.met_pt*cos( event.met_phi ) + (l1['pt'] - l1['ptScaled'])*cos(l1['phi']) + (l2['pt'] - l2['ptScaled'])*cos(l2['phi'])
    met_py = event.met_pt*sin( event.met_phi ) + (l1['pt'] - l1['ptScaled'])*sin(l1['phi']) + (l2['pt'] - l2['ptScaled'])*sin(l2['phi'])
    mt2Calc.setMet(sqrt( met_px**2 + met_py**2), atan2(met_py, met_px) )
    # leptons
    mt2Calc.setLeptons(l1['ptScaled'], l1['eta'], l1['phi'], l2['ptScaled'], l2['eta'], l2['phi'] )

    setattr(event, "dl_mt2ll_ele_smeared", mt2Calc.mt2ll() )

    try:
        met_genPt, met_genPhi = event.met_genPt, event.met_genPhi
    except AttributeError:
        # Data
        met_genPt, met_genPhi = event.met_pt, event.met_phi
    mt2Calc.reset()
    # Correcting MET
    met_px = event.met_pt*cos( event.met_phi ) + 0.1*(event.met_pt*cos(event.met_phi) - met_genPt*cos(met_genPhi)) 
    met_py = event.met_pt*sin( event.met_phi ) + 0.1*(event.met_pt*sin(event.met_phi) - met_genPt*sin(met_genPhi)) 
    mt2Calc.setMet(sqrt( met_px**2 + met_py**2), atan2(met_py, met_px) )
    # leptons
    mt2Calc.setLeptons(l1['pt'], l1['eta'], l1['phi'], l2['pt'], l2['eta'], l2['phi'] )

    setattr(event, "dl_mt2ll_met_smeared", mt2Calc.mt2ll() )

    
#    print
#    print l1,l2
#    print event.met_pt, event.met_phi, sqrt( met_px**2 + met_py**2), atan2(met_py, met_px)
#    print event.dl_mt2ll_ele_smeared, event.dl_mt2ll
    

sequence.append( mt2llSmeared )

for i_comb in [len(cuts)]:
    for comb in itertools.combinations( cuts, i_comb ):

        if not args.noData: data_sample.setSelectionString([dataFilterCut, trigger])
        for sample in mc:
            sample.setSelectionString([ mcFilterCut, trigger ])

        if args.charges=="OS":
            presel = [("isOS","isOS")]
        elif args.charges=="SS":
            presel = [("isSS","l1_pdgId*l2_pdgId>0")]
        else:
            raise ValueError

        # presel += [("highMiniRelIso","max(l1_miniRelIso,l2_miniRelIso)>0.4")]
 
        presel.extend( comb )

        ppfixes = [args.mode, args.zMode]
        if args.ttjets == "NLO": ppfixes.append( "TTJetsNLO" )
        if args.ttjets == "LO": ppfixes.append( "TTJetsLO" )
        if args.small: ppfixes = ['small'] + ppfixes
        prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in presel ] ) ] )

        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%path )
            continue

        if "nbtag1" in prefix and "nbtag0" in prefix: continue

        selectionString = "&&".join( [p[1] for p in presel] + [leptonSelectionString] )

        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

        if not args.noData:
            logger.info( "Calculating normalization constants" )        
            yield_mc    = sum(s.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val'] for s in mc)
            yield_data  = data_sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']

            for sample in mc:
                dataMCScale = yield_data/(yield_mc*lumi_scale)
                sample.scale = lumi_scale*dataMCScale

            logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc, yield_data, lumi_scale )
        else:
            dataMCScale = None 

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

        dl_mt2ll_ele_smeared  = Plot(
            name = "dl_mt2ll_ele_smeared",
            texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 15 GeV',
            stack = stack, 
            attribute = lambda event, sample:abs(event.dl_mt2ll_ele_smeared),
            binning=[300/15,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2ll_ele_smeared )

        dl_mt2ll_met_smeared  = Plot(
            name = "dl_mt2ll_met_smeared",
            texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 15 GeV',
            stack = stack, 
            attribute = lambda event, sample:abs(event.dl_mt2ll_met_smeared),
            binning=[300/15,0,300],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( dl_mt2ll_met_smeared )

        read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]", "met_phi/F", "met_pt/F"]
        read_variables += [ "l1_pt/F", "l1_phi/F", "l1_eta/F", "l1_index/I", "l1_pdgId/I"]
        read_variables += [ "l2_pt/F", "l2_phi/F", "l2_eta/F", "l2_index/I", "l2_pdgId/I"]
        plotting.fill(plots, read_variables = read_variables, sequence = sequence)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        ratio = {'yRange':(0.1,1.9)} if not args.noData else None

        for plot in plots:
            plotting.draw(plot, 
                plot_directory = plot_path, ratio = ratio, 
                logX = False, logY = True, sorting = True, 
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( dataMCScale )
            )
        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
