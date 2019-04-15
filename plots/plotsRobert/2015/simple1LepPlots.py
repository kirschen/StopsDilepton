''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos, cosh, atan2
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.tools.mt2Calculator import mt2Calculator

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
    default='singleMu',
    action='store',
    choices=['singleMu', 'singleEle'])

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='png25ns_1l',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_1l_postProcessed import *

data_directory = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
SingleElectron_Run2015D = Sample.fromDirectory(name="SingleElectron_Run2015D", treeName="Events", texName="SingleElectron (Run2015D)", directory=os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/singlelepTiny/SingleElectron_Run2015D_16Dec') ) 
SingleMuon_Run2015D     = Sample.fromDirectory(name="SingleMuon_Run2015D",     treeName="Events", texName="SingleMuon (Run2015D)",     directory=os.path.join( data_directory, 'postProcessed_Fall15_mAODv2/singlelepTiny/SingleMuon_Run2015D_16Dec') )
SingleElectron_Run2015D.lumi =  1000*(2.165)
SingleMuon_Run2015D    .lumi =  1000*(2.129)

if args.mode=="singleMu":
    leptonSelectionString = "&&".join(["nGoodMuons==1&&nGoodElectrons==0"])
    data_sample = SingleMuon_Run2015D
    qcd_sample = QCD_Mu5 #FIXME
#    trigger     = "HLT_SingleMu"
    trigger     = "1"
elif args.mode=="singleEle":
    leptonSelectionString = "&&".join(["nGoodMuons==0&&nGoodElectrons==1"])
    data_sample = SingleEG_Run2015D
    qcd_sample = QCD_EMbcToE
    trigger   = "1"
#    trigger   = "HLT_IsoEle32"
else:
    raise ValueError( "Mode %s not known"%args.mode )

# Extra requirements on data
filterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"

data_sample.style = styles.errorStyle( ROOT.kBlack )

#mc = [ TTJets_Lep, WJetsToLNu, DY, qcd_sample]# diBoson, triBoson]

TTJets.reduceFiles(10)
DY.reduceFiles(3)
WJetsToLNu.reduceFiles(2)

mc = [ TTJets, WJetsToLNu, DY, qcd_sample]# diBoson, triBoson]

lumi_scale = data_sample.lumi/1000
for sample in mc:
    sample.style = styles.fillStyle(sample.color)

# user data
from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event, sample:event.weight

cuts=[
    ("njet4", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=4"),
    ("nbtag2", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=2"),
    ("met30", "met_pt>30"),
    ("m3peak", "abs(m3-174)<75."),
]
                
def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
    (0.15, 0.95, 'CMS Preliminary'), 
    (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(data_sample.lumi/100)/10., dataMCScale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

stack = Stack(mc, [data_sample])

##for i_comb in [0]:
for i_comb in [len(cuts)]:
#for i_comb in reversed( range( len(cuts)+1 ) ):
#for i_comb in range(len(cuts)+1):
    for comb in itertools.combinations( cuts, i_comb ):

        data_sample.setSelectionString([filterCut, trigger])
        for sample in mc:
            sample.setSelectionString([ trigger ])

        presel = [] 
        presel.extend( comb )

        prefix = '_'.join([args.mode, '-'.join([p[0] for p in presel])])
        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%path )
            continue

        selectionString = "&&".join( [p[1] for p in presel] + [leptonSelectionString] )

        logger.info( "Calculating normalization constants" )        
        yield_mc    = 0.
        for sample in mc:
            yield_s = sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']
            yield_mc += yield_s*sample.reduce_files_factor if hasattr(sample, "reduce_files_factor") else yield_s 
        yield_data  = data_sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']

        for sample in mc:
            dataMCScale = yield_data/(yield_mc*lumi_scale)
            sample.scale = lumi_scale*dataMCScale
            if hasattr(sample, "reduce_files_factor"): sample.scale*=sample.reduce_files_factor

        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )
        logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc, yield_data, lumi_scale )

        plots = []

        m3  = Plot(
            texX = 'M_{3} (GeV)', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            attribute = TreeVariable.fromString( "m3/F" ),
            binning=[400/10,0,400],
            selectionString = selectionString,
            weight = weight,
            addOverFlowBin = "both",
            )
        plots.append( m3 )

        maxM3BTag  = Plot(
            name = "maxM3BTag",
            texX = 'max. b-disc of M_{3} sub jets', texY = 'Number of Events',
            stack = stack, 
            attribute =  lambda event, sample: max([ event.JetGood_btagCSV[k] for k in [event.m3_ind1, event.m3_ind2, event.m3_ind3] if k>=0] + [-1]), 
            read_variables = ["m3_ind1/I", "m3_ind2/I", "m3_ind3/I"],
            binning=[30,-1,2],
            selectionString = selectionString,
            weight = weight,
            addOverFlowBin = "both",
            )
        plots.append( maxM3BTag )

        def m3_mW(data):
            subjets = [ (event.JetGood_btagCSV[k], k) for k in [event.m3_ind1, event.m3_ind2, event.m3_ind3] if k>=0]
            if not len(subjets)==3:
                print "len(subjets)",len(subjets) 
                return float('nan')
            subjets.sort()
            bj  = subjets[0][1]
            lj1 = subjets[1][1]
            lj2 = subjets[2][1]
            mW = sqrt(2.*event.JetGood_pt[lj1]*event.JetGood_pt[lj2]*(cosh(event.JetGood_eta[lj1] - event.JetGood_eta[lj2]) - cos(event.JetGood_phi[lj1] - event.JetGood_phi[lj2]) ) ) 
            return mW
 
        m3_mW  = Plot(
            name = "m3_mW",
            texX = 'm3_mW', texY = 'Number of Events / 10 GeV',
            stack = stack, 
            attribute =  m3_mW,
            binning=[400/10,0,400],
            selectionString = selectionString,
            weight = weight,
            addOverFlowBin = "both",
            )
        plots.append( m3_mW )

        def mt2ll_Pred(data):
            subjets = [ (event.JetGood_btagCSV[k], k) for k in [event.m3_ind1, event.m3_ind2, event.m3_ind3] if k>=0]
            if not len(subjets)==3:
                print "len(subjets)",len(subjets) 
                return float('nan')
            subjets.sort()
            bj  = subjets[0][1]
            lj1 = subjets[1][1]
            lj2 = subjets[2][1]
            
            mt2Calculator.reset()
            # treat one jet as a lepton
            mt2Calculator.setLeptons( event.l1_pt, event.l1_eta, event.l1_phi, event.JetGood_pt[lj1], event.JetGood_eta[lj1], event.JetGood_phi[lj1] )
            # the other one as MET
            met_Pred_x = event.met_pt*cos(event.met_phi) - event.JetGood_pt[lj2]*cos(event.JetGood_phi[lj2])
            met_Pred_y = event.met_pt*sin(event.met_phi) - event.JetGood_pt[lj2]*sin(event.JetGood_phi[lj2])
            mt2Calculator.setMet( sqrt(met_Pred_x**2 + met_Pred_y**2), atan2( met_Pred_y, met_Pred_x ) )
            return mt2Calculator.mt2ll()

        mt2ll_Pred  = Plot(
            name = "mt2ll_Pred",
            texX = 'mt2ll_Pred', texY = 'Number of Events / 20 GeV',
            stack = stack, 
            attribute = mt2ll_Pred,
            binning=[300/15,0,300],
            selectionString = selectionString,
            weight = weight,
            addOverFlowBin = "both",
            )
        plots.append( mt2ll_Pred )
 
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

        l1_pdgId  = Plot(
            texX = 'pdgId(l_{1})', texY = 'Number of Events',
            stack = stack, 
            attribute = TreeVariable.fromString( "l1_pdgId/I" ),
            binning=[32,-16,16],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( l1_pdgId )


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

        metSig  = Plot(
            name = "metSig",
            texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
            stack = stack, 
            attribute = lambda event, sample: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan'), 
            read_variables = [["met_pt/F", "ht/F"],
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

        cosMetJet0phi = Plot(\
            name = "cosMetJet0phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
            stack = stack, 
            attribute =  lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ),  
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet0phi )

        cosMetJet1phi = Plot(\
            name = "cosMetJet1phi",
            texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
            stack = stack, 
            attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) 
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
        )
        plots.append( cosMetJet1phi )

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
            attribute = TreeVariable.fromString( "nVert/I" ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            )
        plots.append( nVert )

        read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F,btagCSV/F]"]

        plotting.fill(plots, read_variables = read_variables)

        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        for plot in plots:
            plotting.draw(plot, 
                plot_directory = plot_path, ratio = {'yRange':(0.1,1.9)}, 
                logX = False, logY = True, sorting = True, 
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( dataMCScale )
            )
        for plot in plots:
            plotting.draw(plot, 
                plot_directory = plot_path+'/lin', ratio = {'yRange':(0.1,1.9)}, 
                logX = False, logY = False, sorting = True, 
                yRange = (0.03, "auto"), 
                drawObjects = drawObjects( dataMCScale )
            )
        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
