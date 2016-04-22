''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.tools.objectSelection import getLeptons, getOtherLeptons, getGoodLeptons, looseEleIDString, looseMuIDString, leptonVars

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
    choices=['doubleMu', 'doubleEle',  'muEle']
)

argParser.add_argument('--noData',
    action='store_true',
    help='Skip data',
)

argParser.add_argument('--small',
    action='store_true',
    help='Small?',
)

argParser.add_argument('--overwrite',
#    default = False,
    default = True,
    action='store_true',
    help='overwrite?',
)

argParser.add_argument('--plot_directory',
    default='png25ns_3rdLep',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#make samples
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed_dilep import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

if args.mode=="doubleMu":
    leptonSelectionString = "&&".join([looseMuIDString()+"==2", looseEleIDString()+"==0"])
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "&&".join([looseMuIDString()+"==0", looseEleIDString()+"==2"])
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "&&".join([looseMuIDString()+"==1", looseEleIDString()+"==1"])
    trigger    = "HLT_mue"
else:
    raise ValueError( "Mode %s not known"%args.mode )

# Extra requirements on data
#dataFilterCut = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"
filterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

import StopsDilepton.tools.user as user
from StopsDilepton.samples.helpers import fromHeppySample
maxN = 5 if args.small else -1

TTJets = fromHeppySample("TTJets", data_path = user.cmg_directory, maxN = maxN)
DYJetsToLL_M50 = fromHeppySample("DYJetsToLL_M50", data_path = user.cmg_directory, maxN = maxN)

TToLeptons_tch_amcatnlo  = fromHeppySample("TToLeptons_tch_amcatnlo", data_path = user.cmg_directory, maxN = maxN)
TBarToLeptons_tch_powheg = fromHeppySample("TBarToLeptons_tch_powheg", data_path = user.cmg_directory, maxN = maxN)
#TToLeptons_sch_amcatnlo  = fromHeppySample("TToLeptons_sch_amcatnlo", data_path = user.cmg_directory, maxN = maxN)
TBar_tWch                = fromHeppySample("TBar_tWch", data_path = user.cmg_directory, maxN = maxN)
T_tWch                   = fromHeppySample("T_tWch", data_path = user.cmg_directory, maxN = maxN)

if not args.noData:

    if args.mode=="doubleMu":
        data_sample = fromHeppySample("DoubleMuon_Run2015D_16Dec", data_path = '/scratch/rschoefbeck/cmgTuples/763', maxN = maxN)
    elif args.mode=="doubleEle":
        data_sample = fromHeppySample("DoubleEG_Run2015D_16Dec", data_path = '/scratch/rschoefbeck/cmgTuples/763', maxN = maxN)
    elif args.mode=="muEle":
        data_sample = fromHeppySample("MuonEG_Run2015D_16Dec", data_path = '/scratch/rschoefbeck/cmgTuples/763', maxN = maxN)

    data_sample.style = styles.errorStyle( ROOT.kBlack )
    #lumi_scale = data_sample.lumi/1000

    import StopsDilepton.tools.vetoList as vetoList_

    # MET group veto lists from 74X
    fileNames  = ['Run2015D/csc2015_Dec01.txt.gz', 'Run2015D/ecalscn1043093_Dec01.txt.gz']
    vetoList = vetoList_.vetoList( [os.path.join(user.veto_lists, f) for f in fileNames] )

    from FWCore.PythonUtilities.LumiList import LumiList
    # Apply golden JSON
    json = '$CMSSW_BASE/src/CMGTools/TTHAnalysis/data/json/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt'
    lumiList = LumiList(os.path.expandvars(json))


DYJetsToLL_M50.color = 8
TTJets.color = 7
TToLeptons_tch_amcatnlo.color  = 40
TBarToLeptons_tch_powheg.color = 40
TBar_tWch.color = 40
T_tWch.color    = 40

noTT = [ TToLeptons_tch_amcatnlo, TBarToLeptons_tch_powheg, TBar_tWch, T_tWch ]

noTT_stack = Stack(noTT)
TTJets_stack = Stack([TTJets])

if not args.noData:
    data_stack = Stack( [data_sample] )

from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = None #lambda data:data.weight
dataMCScale = None 

cuts=[
    ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
    ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"),
#    ("nbtag0", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)==0"),
#    ("mll20", "dl_mass>20"),
    ("met80", "met_pt>80"),
    ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
]

for sample in noTT + [TTJets] + [data_sample]:
    sample.style = styles.fillStyle(sample.color)
    sample.setSelectionString([ filterCut, trigger ])

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
    

##for i_comb in [0]:
for i_comb in [len(cuts)]:
#for i_comb in reversed( range( len(cuts)+1 ) ):
#for i_comb in range(len(cuts)+1):
    for comb in itertools.combinations( cuts, i_comb ):

        presel = [] 
        presel.extend( comb )

        prefix = '_'.join([args.mode, '-'.join([p[0] for p in presel])])
        if args.small: prefix = 'small_'+prefix
        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            logger.info( "Path %s not empty. Skipping."%path )
            continue

        if "nbtag1" in prefix and "nbtag0" in prefix: continue

        selectionString = "&&".join( [p[1] for p in presel] + [leptonSelectionString] )

        logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

        # Normalization
        def setWeight(data, sample):
            #print data.evt, data.genWeight, sample.name, sample.normalization
            if sample.isData: setattr(data, "weight", 1)
            else: setattr(data, "weight", data.genWeight/sample.normalization )
        sequence = [ setWeight ]

        # Compute leptons
        extraLepVars = ['relIso04', 'mcMatchAny']
        def makeLeptons( data ):
            goodLeptons = getGoodLeptons( data, collVars = leptonVars + extraLepVars )
            extraLeptons = sorted( \
                [l for l in getLeptons( data, collVars = leptonVars + extraLepVars) if l not in goodLeptons] \
                + getOtherLeptons( data , collVars = leptonVars + extraLepVars), 
                            key=lambda l: -l['pt'] )
            setattr( data, "goodLeptons", goodLeptons )
            setattr( data, "extraLeptons", extraLeptons )
        sequence.append( makeLeptons )

        def extraLep_pt( pdgId , lepton_criterion = lambda l:True):
            def filler( data ):

                selectedExtraLep = filter(lambda l: abs(l['pdgId'])==pdgId and l['relIso04']>0.5 and lepton_criterion(l), data.extraLeptons )
#                print len(data.goodLeptons), len(getLeptons( data )), len([l for l in getLeptons( data ) if l not in data.goodLeptons]), len(data.extraLeptons), len(selectedExtraLep)
#                print [l['pt'] for l in selectedExtraLep]
                if len(selectedExtraLep)==0:
                    return float('nan')
                else:
                    return selectedExtraLep[-1]['pt']
            return filler

        sequence.append( lambda data: setattr(data, "extraMu_pt",  extraLep_pt( pdgId = 13 )(data) )
        sequence.append( lambda data: setattr(data, "extraEle_pt", extraLep_pt( pdgId = 11 )(data) )

        plots = []
        fill_only = []

        extraMu_data_pt  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            variable = Variable.fromString('extraMu_pt/F').addFiller ( extraLep_pt( pdgId = 13 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraMu_data_pt )

        extraEle_data_pt  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            variable = Variable.fromString('extraEle_pt/F').addFiller ( extraLep_pt( pdgId = 11 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraEle_pt )

        extraMu_noTT_pt  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            variable = Variable.fromString('extraMu_pt/F').addFiller ( extraLep_pt( pdgId = 13 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraMu_pt )

        extraEle_noTT_pt  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            variable = Variable.fromString('extraEle_pt/F').addFiller ( extraLep_pt( pdgId = 11 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraEle_pt )

        extraMu_TT_pt  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraMu_pt/F').addFiller ( extraLep_pt( pdgId = 13 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraMu_pt )

        extraEle_TT_pt  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraEle_pt/F').addFiller ( extraLep_pt( pdgId = 11 ) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        plots.append( extraEle_pt )

        extraMu_pt_TT_matched  = Plot(
            texX = 'extraMu_pt_TT_matched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraMu_pt/F').addFiller ( extraLep_pt( pdgId = 13 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        fill_only.append( extraMu_pt_TT_matched )

        extraEle_pt_TT_matched  = Plot(
            texX = 'extraEle_pt_TT_matched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraEle_pt/F').addFiller ( extraLep_pt( pdgId = 11 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        fill_only.append( extraEle_pt_TT_matched )

        extraMu_pt_TT_nonMatched  = Plot(
            texX = 'extraMu_pt_TT_nonMatched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraMu_pt/F').addFiller ( extraLep_pt( pdgId = 13 , lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        fill_only.append( extraMu_pt_TT_nonMatched )

        extraEle_pt_TT_nonMatched  = Plot(
            texX = 'extraEle_pt_TT_nonMatched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            variable = Variable.fromString('extraEle_pt/F').addFiller ( extraLep_pt( pdgId = 11 , lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ),
            binning=[50,0,50],
            selectionString = selectionString,
            weight = weight,
            #addOverFlowBin = "both",
            )
        fill_only.append( extraEle_pt_TT_nonMatched )

        read_variables = [
            "genWeight/F", "evt/l",
             "Jet[pt/F,eta/F,phi/F]", 
             "nLepGood/I", "LepGood[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,mcMatchAny/I]", 
             "nLepOther/I", "LepOther[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,mcMatchAny/I]",
            ]

        plotting.fill(plots + fill_only, read_variables = read_variables, sequence = sequence)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        ratio = {'yRange':(0.1,1.9)} if not args.noData else None

#        for plot in plots:
#            plotting.draw(plot, 
#                plot_directory = plot_path, ratio = ratio, 
#                logX = False, logY = True, sorting = True, 
#                yRange = (0.03, "auto"), 
#                scaling = {0:1},
#                drawObjects = drawObjects( dataMCScale )
#            )
#
#            plot_comb = Plot.fromHisto(name = plot.name+'_STComb', histos = singleTopHistoComb( plot.histos ), texX = plot.texX, texY = plot.texY)
#            plotting.draw(plot_comb, 
#                plot_directory = plot_path, ratio = ratio, 
#                logX = False, logY = True, sorting = True, 
#                yRange = (0.03, "auto"), 
#                scaling = {0:1},
#                drawObjects = drawObjects( dataMCScale )
#            )

        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
