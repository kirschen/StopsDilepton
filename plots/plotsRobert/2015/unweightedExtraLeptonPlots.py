''' Analysis script for 1D 2l plots (RootTools)
'''
#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import os

#RootTools
from RootTools.core.standard import *

# StopsDilepton
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.objectSelection import getLeptons, getOtherLeptons, getGoodLeptons, eleSelectorString, muonSelectorString, leptonVars, getGenPartsAll
from StopsDilepton.tools.helpers import deltaR

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
    default = False,
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
#from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed_dilep import *
#from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

if args.mode=="doubleMu":
    leptonSelectionString = "&&".join([muonSelectorString()+"==2", eleSelectorString()+"==0"])
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "&&".join([muonSelectorString()+"==0", eleSelectorString()+"==2"])
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "&&".join([muonSelectorString()+"==1", eleSelectorString()+"==1"])
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

from StopsDilepton.samples.color import color
DYJetsToLL_M50.color = color.DY
TTJets.color = color.TTJets
TToLeptons_tch_amcatnlo.color  = color.singleTop
TBarToLeptons_tch_powheg.color = color.singleTop
TBar_tWch.color = color.singleTop
T_tWch.color    = color.singleTop

noTT = [ TToLeptons_tch_amcatnlo, TBarToLeptons_tch_powheg, TBar_tWch, T_tWch ]

noTT_stack = Stack(noTT)
TTJets_stack = Stack([TTJets])

if not args.noData:
    data_stack = Stack( [data_sample] )

from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event, sample:event.weight
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

        read_variables = [
            "genWeight/F", "evt/l",
             "Jet[pt/F,eta/F,phi/F]", 
             "nLepGood/I", "LepGood[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,mcMatchAny/I]", 
             "nLepOther/I", "LepOther[eta/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,mcMatchAny/I]",
            ]

        # Normalization
        def setWeight(event, sample):
            #print event.evt, event.genWeight, sample.name, sample.normalization
            if sample.isData: setattr(event, "weight", 1)
            else: setattr(event, "weight", event.genWeight/sample.normalization )
        sequence = [ setWeight ]

        # Compute leptons
        extraLepVars = ['relIso04', 'mcMatchAny']
        read_variables.extend( [ 'met_pt/F', 'met_phi/F' ] )
        def makeLeptons( data ):
            goodLeptons = getGoodLeptons( data, collVars = leptonVars + extraLepVars )
            extraLeptons = sorted( \
                [l for l in getLeptons( data, collVars = leptonVars + extraLepVars) if l not in goodLeptons] \
                + getOtherLeptons( data , collVars = leptonVars + extraLepVars), 
                            key=lambda l: -l['pt'] )
            #print len(goodLeptons), len(getLeptons( data, collVars = leptonVars + extraLepVars)), len(getOtherLeptons( data , collVars = leptonVars + extraLepVars)), len(extraLeptons) 
            if len(goodLeptons)==2: 
                setattr( data, "goodLeptons", goodLeptons )
                setattr( data, "extraLeptons", extraLeptons )

                extraMu  = filter(lambda l: abs(l['pdgId'])==13 and l['relIso04']>0.5, extraLeptons )
                extraEle = filter(lambda l: abs(l['pdgId'])==11 and l['relIso04']>0.5, extraLeptons )

                setattr( data, "extraMu", extraMu[-1] if len(extraMu)>0 else None )
                setattr( data, "extraEle", extraEle[-1] if len(extraEle)>0 else None )

                # MT2ll
                mt2Calc.reset()
                l1, l2 = goodLeptons[0], goodLeptons[1]
                mt2Calc.setLeptons(l1["pt"], l1["eta"], l1["phi"], l2["pt"], l2["eta"], l2["phi"])
                mt2Calc.setMet(event.met_pt, event.met_phi)
                setattr( data, "mt2ll", mt2Calc.mt2ll())
                #print event.mt2ll
            else:
                setattr( data, "goodLeptons", None)
                setattr( data, "extraLeptons", None)
                setattr( data, "extraMu", None)
                setattr( data, "extraEle", None)
                setattr( data, "mt2ll", None)

        sequence.append( makeLeptons )

        # functor for extra lepton plots
        def extraLep_pt( pdgId , lepton_criterion = lambda l:True):

            if not abs(pdgId) in [11, 13]: raise ValueError

            def filler( event, sample ):
                if abs(pdgId)==13 and event.extraMu is not None:
                    lep = event.extraMu
                elif abs(pdgId)==11 and event.extraEle is not None:
                    lep = event.extraEle
                else:
                    return float('nan')
                if lepton_criterion(lep):
                    return lep['pt']
                else:
                    return float('nan')
            return filler

        # neutrino generator information
        read_variables.extend(
            [  
              'ngenPartAll/I', 
              'genPartAll[eta/F,pt/F,phi/F,charge/I,status/I,pdgId/I,motherId/I,grandmotherId/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I,nMothers/I,motherIndex1/I,motherIndex2/I]' 
            ] )

        def makeGenNeutrinos( data ):
            setattr( data, "genNu", filter( lambda p:abs(p['pdgId']) in [12, 14, 16] and p['status']==1, getGenPartsAll( data ) ) )
    
        sequence.append( makeGenNeutrinos )
        
        # Calculate the neutrino pt in the vicinity of the extra leptons
        def makeNuPts( data ):
            for lepton in ["extraMu", "extraEle"]:
                lep = getattr(event, lepton)
                if not lep or lep is None:
                     res = float('nan')
                else:
                    nu = filter(lambda nu:abs(nu['motherId'])!=24 and deltaR(nu, lep) <0.5, event.genNu)
#                    for n in nu:
#                        print n['pdgId'], n['motherId']
                    if len(nu)==0:
                        res = 0.
                    else:
                        res =  sqrt( ( sum( [ n['pt']*cos(n['phi']) for n in nu]) )**2 + (sum( [ n['pt']*sin(n['phi']) for n in nu]))**2)
                setattr(event, lepton+"_nuPt", res)

        sequence.append( makeNuPts )

        plots = []
        plots2D = []
        fill_only = []

        Plot.setDefaults(weight = weight, selectionString = selectionString)

        extraMu_data  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            attribute = extraLep_pt( pdgId = 13 ),
            binning=[50,0,50],
            )
        plots.append( extraMu_data )

        extraEle_data  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            attribute = extraLep_pt( pdgId = 11 ) ,
            binning=[50,0,50],
            )
        plots.append( extraEle_data )

        extraMu_noTT_matched  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = extraLep_pt( pdgId = 13, lepton_criterion = lambda l:abs(l['mcMatchAny'])==5)  ,
            binning=[50,0,50],
            )
        plots.append( extraMu_noTT_matched )

        extraEle_noTT_matched  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = extraLep_pt( pdgId = 11, lepton_criterion = lambda l:abs(l['mcMatchAny'])==5)  ,
            binning=[50,0,50],
            )
        plots.append( extraEle_noTT_matched )

        extraMu_noTT_unmatched  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = extraLep_pt( pdgId = 13, lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ,
            binning=[50,0,50],
            )
        plots.append( extraMu_noTT_unmatched )

        extraEle_noTT_unmatched  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = extraLep_pt( pdgId = 11, lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ,
            binning=[50,0,50],
            )
        plots.append( extraEle_noTT_unmatched )

        extraMu_TT  = Plot(
            texX = 'extraMu_pt', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 13 ) ,
            binning=[50,0,50],
            )
        plots.append( extraMu_TT )

        extraEle_TT  = Plot(
            texX = 'extraEle_pt', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 11 ) ,
            binning=[50,0,50],
            )
        plots.append( extraEle_TT )

        extraMu_TT_matched  = Plot(
            texX = 'extraMu_TT_matched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 13 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ,
            binning=[50,0,50],
            )
        fill_only.append( extraMu_TT_matched )

        extraEle_TT_matched  = Plot(
            texX = 'extraEle_TT_matched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 11 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ,
            binning=[50,0,50],
            )
        fill_only.append( extraEle_TT_matched )

        extraMu_TT_nonMatched  = Plot(
            texX = 'extraMu_TT_nonMatched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 13 , lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ,
            binning=[50,0,50],
            )
        fill_only.append( extraMu_TT_nonMatched )

        extraEle_TT_nonMatched  = Plot(
            texX = 'extraEle_TT_nonMatched', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = extraLep_pt( pdgId = 11 , lepton_criterion = lambda l:abs(l['mcMatchAny'])!=5) ,
            binning=[50,0,50],
            )
        fill_only.append( extraEle_TT_nonMatched )

        #2D plots
        extraMu_TT_pt_vs_MET  = Plot2D(
            name = "extraMu_pt_vs_MET",
            texX = 'p_{T,#mu}', texY = 'p_{T,#nu}',
            stack = TTJets_stack, 
            variables = (
                extraLep_pt( pdgId = 13 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ,
                lambda event, sample: event.extraMu_nuPt ,
            ),
            binning=[200,0,200, 200,0,200],
            weight = weight,
            selectionString = selectionString
            )
        plots2D.append( extraMu_TT_pt_vs_MET )

        extraEle_TT_pt_vs_MET  = Plot2D(
            name = "extraEle_pt_vs_MET",
            texX = 'p_{T,e}', texY = 'p_{T,#nu}',
            stack = TTJets_stack, 
            variables = (
                extraLep_pt( pdgId = 11 , lepton_criterion = lambda l:abs(l['mcMatchAny'])==5) ,
                lambda event, sample: event.extraEle_nuPt ,
            ),
            binning=[200,0,200, 200,0,200],
            weight = weight,
            selectionString = selectionString
            )
        plots2D.append( extraEle_TT_pt_vs_MET )

        # MT2ll
        extraMu_mt2ll_data  = Plot(
            texX = 'extraMu_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraMu_mt2ll_data )

        extraEle_mt2ll_data  = Plot(
            texX = 'extraEle_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = data_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraEle_mt2ll_data )

        extraMu_mt2ll_noTT_matched  = Plot(
            texX = 'extraMu_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None and event.extraMu['mcMatchAny']==5 else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraMu_mt2ll_noTT_matched )

        extraEle_mt2ll_noTT_matched  = Plot(
            texX = 'extraEle_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None and event.extraEle['mcMatchAny']==5 else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraEle_mt2ll_noTT_matched )

        extraMu_mt2ll_noTT_unmatched  = Plot(
            texX = 'extraMu_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None and event.extraMu['mcMatchAny']!=5 else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraMu_mt2ll_noTT_unmatched )

        extraEle_mt2ll_noTT_unmatched  = Plot(
            texX = 'extraEle_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = noTT_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None and event.extraEle['mcMatchAny']!=5 else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraEle_mt2ll_noTT_unmatched )

        extraMu_mt2ll_TT  = Plot(
            texX = 'extraMu_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraMu_mt2ll_TT )

        extraEle_mt2ll_TT  = Plot(
            texX = 'extraEle_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None else float('nan') ,
            binning=[40,0,200],
            )
        plots.append( extraEle_mt2ll_TT )

        extraMu_mt2ll_TT_matched  = Plot(
            texX = 'extraMu_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None and event.extraMu['mcMatchAny']==5 else float('nan') ,
            binning=[40,0,200],
            )
        fill_only.append( extraMu_mt2ll_TT_matched )

        extraEle_mt2ll_TT_matched  = Plot(
            texX = 'extraEle_mt2ll', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None and event.extraEle['mcMatchAny']==5 else float('nan') ,
            binning=[40,0,200],
            )
        fill_only.append( extraEle_mt2ll_TT_matched )

        extraMu_mt2ll_TT_nonMatched  = Plot(
            texX = 'extraMu', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraMu is not None and event.extraMu['mcMatchAny']!=5 else float('nan') ,
            binning=[40,0,200],
            )
        fill_only.append( extraMu_mt2ll_TT_nonMatched )

        extraEle_mt2ll_TT_nonMatched  = Plot(
            texX = 'extraEle', texY = 'Number of Events / 1 GeV',
            stack = TTJets_stack, 
            attribute = lambda event, sample: event.mt2ll if event.extraEle is not None and event.extraEle['mcMatchAny']==5 else float('nan') ,
            binning=[40,0,200],
            )
        fill_only.append( extraEle_mt2ll_TT_nonMatched )

        #Fill all plots
        plotting.fill(plots + fill_only + plots2D, read_variables = read_variables, sequence = sequence)

        if not os.path.exists( plot_path ): os.makedirs( plot_path )

        e_TT_nm = extraEle_TT_nonMatched.histos_added[0][0]
        e_TT_nm.legendText = "TTJets (not matched)"
        e_TT_nm.style = styles.fillStyle(ROOT.kCyan + 3)
        e_TT_m  = extraEle_TT_matched.histos_added[0][0]
        e_TT_m.legendText = "TTJets (matched)"
        e_TT_m.style = styles.fillStyle(color.TTJets)
        e_nTT_nm   = extraEle_noTT_unmatched.histos_added[0][0]
        e_nTT_nm.legendText = "ST (not matched)"
        e_nTT_nm.style = styles.fillStyle(color.singleTop+1)
        e_nTT_m   = extraEle_noTT_matched.histos_added[0][0]
        e_nTT_m.legendText = "ST (matched)"
        e_nTT_m.style = styles.fillStyle(color.singleTop)
        e_data  = extraEle_event.histos_added[0][0]
        e_event.style = styles.errorStyle( ROOT.kBlack )
        e_event.legendText = "data (Ele)"

        m_TT_nm = extraMu_TT_nonMatched.histos_added[0][0]
        m_TT_nm.legendText = "TTJets (not matched)"
        m_TT_nm.style = styles.fillStyle(ROOT.kCyan + 3)
        m_TT_m  = extraMu_TT_matched.histos_added[0][0]
        m_TT_m.legendText = "TTJets (matched)"
        m_TT_m.style = styles.fillStyle(color.TTJets)
        m_nTT_nm   = extraMu_noTT_unmatched.histos_added[0][0]
        m_nTT_nm.legendText = "ST (not matched)"
        m_nTT_nm.style = styles.fillStyle(color.singleTop+1)
        m_nTT_m   = extraMu_noTT_matched.histos_added[0][0]
        m_nTT_m.legendText = "ST (matched)"
        m_nTT_m.style = styles.fillStyle(color.singleTop)
        m_data  = extraMu_event.histos_added[0][0]
        m_event.legendText = "data (Mu)"
        m_event.style = styles.errorStyle( ROOT.kBlack )

        ratio = {'yRange':(0.1,1.9)} if not args.noData else None
        plotting.draw(
            Plot.fromHisto("extraEle_pt",
                [ [e_TT_m, e_nTT_m, e_TT_nm, e_nTT_nm], [e_data]],
                texX = "extra electron p_{T}"
            ), 
            plot_directory = plot_path, ratio = ratio, 
            logX = False, logY = True, sorting = False, 
            yRange = (0.03, "auto"), 
            scaling = {0:1},
            drawObjects = drawObjects( dataMCScale )
        )
        plotting.draw(
            Plot.fromHisto("extraMu_pt",
                [ [m_TT_m, m_nTT_m, m_TT_nm, m_nTT_nm], [m_data]],
                texX = "extra muon p_{T}"
            ), 
            plot_directory = plot_path, ratio = ratio, 
            logX = False, logY = True, sorting = False, 
            yRange = (0.03, "auto"), 
            scaling = {0:1},
            drawObjects = drawObjects( dataMCScale )
        )

        for plot in plots2D:
            plotting.draw2D(
                plot = plot,
                plot_directory = plot_path,
                logX = False, logY = False, logZ = True,
            )

        e_mt2ll_TT_nm = extraEle_mt2ll_TT_nonMatched.histos_added[0][0]
        e_mt2ll_TT_nm.legendText = "TTJets (not matched)"
        e_mt2ll_TT_nm.style = styles.fillStyle(ROOT.kCyan + 3)
        e_mt2ll_TT_m  = extraEle_mt2ll_TT_matched.histos_added[0][0]
        e_mt2ll_TT_m.legendText = "TTJets (matched)"
        e_mt2ll_TT_m.style = styles.fillStyle(color.TTJets)
        e_mt2ll_nTT_nm   = extraEle_mt2ll_noTT_unmatched.histos_added[0][0]
        e_mt2ll_nTT_nm.legendText = "ST (not matched)"
        e_mt2ll_nTT_nm.style = styles.fillStyle(color.singleTop+1)
        e_mt2ll_nTT_m   = extraEle_mt2ll_noTT_matched.histos_added[0][0]
        e_mt2ll_nTT_m.legendText = "ST (matched)"
        e_mt2ll_nTT_m.style = styles.fillStyle(color.singleTop)
        e_mt2ll_data  = extraEle_mt2ll_event.histos_added[0][0]
        e_mt2ll_event.style = styles.errorStyle( ROOT.kBlack )
        e_mt2ll_event.legendText = "data (Ele)"

        m_mt2ll_TT_nm = extraMu_mt2ll_TT_nonMatched.histos_added[0][0]
        m_mt2ll_TT_nm.legendText = "TTJets (not matched)"
        m_mt2ll_TT_nm.style = styles.fillStyle(ROOT.kCyan + 3)
        m_mt2ll_TT_m  = extraMu_mt2ll_TT_matched.histos_added[0][0]
        m_mt2ll_TT_m.legendText = "TTJets (matched)"
        m_mt2ll_TT_m.style = styles.fillStyle(color.TTJets)
        m_mt2ll_nTT_nm   = extraMu_mt2ll_noTT_unmatched.histos_added[0][0]
        m_mt2ll_nTT_nm.legendText = "ST (not matched)"
        m_mt2ll_nTT_nm.style = styles.fillStyle(color.singleTop+1)
        m_mt2ll_nTT_m   = extraMu_mt2ll_noTT_matched.histos_added[0][0]
        m_mt2ll_nTT_m.legendText = "ST (matched)"
        m_mt2ll_nTT_m.style = styles.fillStyle(color.singleTop)
        m_mt2ll_data  = extraMu_mt2ll_event.histos_added[0][0]
        m_mt2ll_event.legendText = "data (Mu)"
        m_mt2ll_event.style = styles.errorStyle( ROOT.kBlack )

        ratio = {'yRange':(0.1,1.9)} if not args.noData else None
        plotting.draw(
            Plot.fromHisto("extraEle_mt2ll",
                [ [e_mt2ll_TT_m, e_mt2ll_nTT_m, e_mt2ll_TT_nm, e_mt2ll_nTT_nm], [e_mt2ll_data]],
                texX = "M_{T2}(ll) (GeV)" 
            ),
            plot_directory = plot_path, ratio = ratio, 
            logX = False, logY = True, sorting = False, 
            yRange = (0.03, "auto"), 
            scaling = {0:1},
            drawObjects = drawObjects( dataMCScale )
        )
        plotting.draw(
            Plot.fromHisto("extraMu_mt2ll",
                [ [m_mt2ll_TT_m, m_mt2ll_nTT_m, m_mt2ll_TT_nm, m_mt2ll_nTT_nm], [m_mt2ll_data]],
                texX = "M_{T2}(ll) (GeV)" 
            ), 
            plot_directory = plot_path, ratio = ratio, 
            logX = False, logY = True, sorting = False, 
            yRange = (0.03, "auto"), 
            scaling = {0:1},
            drawObjects = drawObjects( dataMCScale )
        )

        logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
