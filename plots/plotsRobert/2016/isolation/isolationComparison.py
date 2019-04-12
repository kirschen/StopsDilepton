''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos, cosh
import itertools
import os

#RootTools
from RootTools.core.standard import *

# Tools 
from StopsDilepton.tools.mt2Calculator import mt2Calculator
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

argParser.add_argument('--small',
    action='store_true',
    #default = True,
    help='Small?',
)

#argParser.add_argument('--njet',
#    default='2p',
#    type=str,
#    action='store',
#    choices=['0', '0p', '1', '1p', '2', '2p', '01']
#)
#
#argParser.add_argument('--nbtag',
#    default='1p',
#    action='store',
#    choices=['0', '0p', '1', '1p',]
#)

argParser.add_argument('--leptonSelection',
    default='multiIsoVT',
    type=str,
    action='store',
    #choices=['miniRelIso02', 'POG', 'multiIsoVT', 'multiIsoT', 'multiIsoM', 'multiIsoL', 'multiIsoVL']
)

argParser.add_argument('--plot_directory',
    default='isolation',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#Sample
maxN = 2 if args.small else -1
import StopsDilepton.tools.user as user
from StopsDilepton.samples.helpers import fromHeppySample
ttbar = fromHeppySample("TTLep_pow_ext", data_path = user.cmg_directory, maxN = maxN)

targetLumi = 1000 #pb-1 Which lumi to normalize to
lumi_scale = 12.9
xSection = ttbar.heppy.xSection
lumiScaleFactor = xSection*targetLumi/float(ttbar.normalization)

#Selection
selection = [
  ("2l", "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5) + Sum$(LepOther_pt>20&&abs(LepOther_eta)<2.5)>=2" ),
  ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
  ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.800)>=1"),
  ("met80", "met_pt>80"),
  ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
  ("dPhiJetMet", "cos(met_phi-Jet_phi[0])<0.8&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
]

selectionString = "&&".join(c[1] for c in selection)
prefix = "-".join(c[0] for c in selection)
#wpStr = { 5: "VT", 4: "T", 3: "M" , 2: "L" , 1: "VL", 0:"None"}

prefix = 'lep-%s-'%( args.leptonSelection ) + prefix

if args.small: prefix = 'small_'+prefix
#colors = [ROOT.kBlack, ROOT.kBlue - 9, ROOT.kBlue, ROOT.kRed, ROOT.kGreen]
colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kOrange,  ROOT.kGreen]

selectionWeights = [ "other", "fakeMET_50", "hasGenHadTau", "fake", "nonPrompt" ]
channels = [ 'all', 'SF', 'OF', 'MuMu', 'EE', 'EMu']

# yields
yields = {s:{c:{wgt:0 for wgt in selectionWeights} for c in channels} for s in ['inclusive', 'highMT2ll']}

# Global counters for efficiency
lepton_eff_counters = {pdgId:{x:0 for x in ['hasMatch', 'hasNoMatch']} for pdgId in [11,13]}
lepton_fr_counters = {pdgId:{x:0 for x in ['fake', 'prompt', 'nonPrompt']} for pdgId in [11,13]}

# Define sequence
sequence = []

#Make lumi weight
def makeLumiWeight ( event, sample ):
        event.lumi_weight = lumiScaleFactor*event.genWeight

sequence.append( makeLumiWeight )

# Make all leptons
from StopsDilepton.tools.objectSelection import getMuons, getElectrons, getGoodLeptons, getGoodAndOtherLeptons, multiIsoWPInt, leptonVars

if args.leptonSelection == 'miniRelIso02':

    from StopsDilepton.tools.objectSelection import eleSelector, muonSelector
    loose_mu_selector = muonSelector( iso = 999., dxy = 1., dz = 0.1 )
    loose_ele_selector = eleSelector( iso = 999., dxy = 1., dz = 0.1 )

    mu_selector = muonSelector( iso = 0.2 )
    ele_selector = eleSelector( iso = 0.2 )

    def isolation( l ):
        return True

elif 'multiIso' in args.leptonSelection:

    from StopsDilepton.tools.objectSelection import eleSelector, muonSelector
    loose_mu_selector = muonSelector( iso = 999., dxy = 1., dz = 0.1 )
    loose_ele_selector = eleSelector( iso = 999., dxy = 1., dz = 0.1 )

    mu_selector = muonSelector( iso = 0.2 )
    ele_selector = eleSelector( iso = 0.2 )

    wp = args.leptonSelection.replace('multiIso', '') 
    from StopsDilepton.tools.objectSelection import multiIsoSelector

    isolation = multiIsoSelector( wp )

elif 'POG' in args.leptonSelection:
    
    from StopsDilepton.tools.objectSelection import eleSelector, muonSelector
    from StopsDilepton.tools.pog_lepton_id import ele_ID_functor, mu_ID_functor

    loose_mu_selector = muonSelector( iso = 999., dxy = 0.05, dz = 0.1 )
    loose_ele_selector = eleSelector( iso = 999., dxy = 0.05, dz = 0.1 )

    wps = args.leptonSelection.split('-')[1:]

    mu_selector  = mu_ID_functor( wps[0] ) 
    ele_selector = ele_ID_functor( wps[1] ) 
    #mu_selector = muonSelector( iso = 0.2 )
    #ele_selector = eleSelector( iso = 0.2 )

    # POG Id Iso for electrons, relIsoEA03 for Muons
    isolation = lambda l: abs(l['pdgId'])==11 or ( abs(l['pdgId'])==13 and l['relIso03']<0.12 ) 
else:
    raise ValueError( "Don't know what to do with leptonSelection %s" % args.leptonSelection )

from StopsDilepton.tools.objectSelection import getGenPartsAll 

def makeObjects( event, sample ):

    # fake MET
    fake_MEx = event.met_pt*cos(event.met_phi) - event.met_genPt*cos(event.met_genPhi)
    fake_MEy = event.met_pt*sin(event.met_phi) - event.met_genPt*sin(event.met_genPhi)

    event.fakeMET = sqrt(fake_MEx**2 + fake_MEy**2)

    # Leptons
    event.all_leptons = getGoodAndOtherLeptons(event, ptCut=20, 
            collVars = leptonVars + ['mcMatchPdgId', 'mcMatchAny', 'relIso03', 'sigmaIEtaIEta', 'dEtaScTrkIn', 'dPhiScTrkIn', 'hadronicOverEm', 'eInvMinusPInv'], 
            mu_selector  = loose_mu_selector, 
            ele_selector = loose_ele_selector
        )
    event.selected_muons      = filter( lambda l: mu_selector(l)  and isolation(l), event.all_leptons  )
    event.selected_electrons  = filter( lambda l: ele_selector(l) and isolation(l), event.all_leptons  )

    #print "#mu %i #ele %i" %( len(event.selected_muons), len(event.selected_electrons) )

    #print event.selected_muons
    event.selected_leptons = event.selected_muons + event.selected_electrons
    event.selected_leptons.sort( key = lambda p: -p['pt'] )

    # Gen leptons
    event.genPartsAll = getGenPartsAll( event )
    event.genHadTau = filter( lambda p: abs(p['pdgId'])==15 and p['daughterIndex2']<200 and p['isPromptHard'] and ( abs(event.genPartsAll[p['daughterIndex1']]['pdgId'])>20 or abs(event.genPartsAll[p['daughterIndex2']]['pdgId'])>100), event.genPartsAll)

    event.promptHardGenLep =  filter( lambda p:abs(p['pdgId']) in [11, 13] and p['status']==1 and p['isPromptHard'] and p['pt']>20 and abs(p['eta'])<2.1, event.genPartsAll )

sequence.append( makeObjects )

def match( l1, l2 ):
    return l1['pdgId'] == l2['pdgId'] and deltaR(l1, l2)<0.3

def increment_lepton_counters( event, sample ):
       
    for gl in event.promptHardGenLep:
        if not any(match(gl, l) for l in event.selected_leptons):
            #print "unmatched", gl, event.selected_leptons
            lepton_eff_counters[abs(gl['pdgId'])]['hasNoMatch'] += 1
        else:
            lepton_eff_counters[abs(gl['pdgId'])]['hasMatch'] += 1

    for l in event.selected_leptons:
        if  abs(l['mcMatchPdgId']) not in [11,13]: 
            lepton_fr_counters[abs(l['pdgId'])]['fake'] += 1
        elif abs(l['mcMatchAny']) in [4,5]:
            lepton_fr_counters[abs(l['pdgId'])]['nonPrompt'] += 1
        else:
            lepton_fr_counters[abs(l['pdgId'])]['prompt'] += 1

sequence.append( increment_lepton_counters )

def makeWeights( event, sample ):
    # boolean weights
    event.other = 1
    #event.fakeMET_40_60 = event.fakeMET>40 and event.fakeMET<60
    event.fakeMET_50 = event.fakeMET>50
    #if event.fakeMET_40_60 or event.fakeMET_60: event.other = 0
    if event.fakeMET_50: event.other = 0

    event.hasGenHadTau = 0
    if event.other == 1: #Avoid overlap
        if len(event.genHadTau) > 0:
            event.hasGenHadTau = 1
            event.other = 0

    event.fake = 0
    event.nonPrompt = 0
    if event.other == 1: #Avoid overlap
        for l in event.selected_leptons:
            #if ( abs(l['mcMatchPdgId']) not in [11,13] ) or ( abs(l['mcMatchAny']) not in [1] ):
            #    print "pdgId %3i mcMatchPdgId %3i mcMatchAny %3i pt %3.2f" % ( l['pdgId'], l['mcMatchPdgId'], l['mcMatchAny'], l['pt'] )
            if  abs(l['mcMatchPdgId']) not in [11,13]: 
                event.fake    = 1
                event.other   = 0
                break
            elif abs(l['mcMatchAny']) in [4,5]:
                event.nonPrompt  = 1
                event.other      = 0
                break

    event.mt2ll = float('nan')
    event.mll = float('nan')
    event.OS = False
    event.SF = False 
    event.OF = False
    event.MuMu = False
    event.EE = False
    event.EMu = False

    event.highMT2ll = False
    event.selection = False    

    if len(event.selected_leptons)>=2:
        event.l1, event.l2 = event.selected_leptons[:2]
        pdgIds = [abs(event.l1['pdgId']), abs(event.l2['pdgId'])]
        pdgIds.sort() 
        mt2Calculator.reset()
        mt2Calculator.setLeptons(event.l1['pt'], event.l1['eta'], event.l1['phi'], event.l2['pt'], event.l2['eta'], event.l2['phi'] )
        mt2Calculator.setMet( event.met_pt, event.met_phi )

        event.mt2ll = mt2Calculator.mt2ll() 
        event.highMT2ll = event.mt2ll>140
        event.mll = sqrt(2.0*event.l1['pt']*event.l2['pt']*(cosh(event.l1['eta']-event.l2['eta']) - cos(event.l1['phi'] - event.l2['phi'])))
        event.OS = event.l1['pdgId']*event.l2['pdgId'] < 0
        event.SF = ( abs(event.l1['pdgId'] ) == abs( event.l2['pdgId'] ) )
        event.OF = not event.SF
        if pdgIds == [11,11]:
            event.EE = True
        elif pdgIds == [11,13]:
            event.EMu = True
        elif pdgIds == [13,13]:
            event.MuMu = True

        event.selection = ( event.selected_leptons[0]['pt']>25 and event.mll>20 and event.OS and (event.OF or (abs(event.mll - 91.2)>15) ) ) 

sequence.append( makeWeights )

def increment_yields( event, sample ):
    #yields = {s:{c:{wgt:0 for wgt in selectionWeights} for c in channels} for s in ['inclusive', 'highMT2ll']}
    for  wgt in selectionWeights:
        if getattr(event, wgt): 
            for channel in channels:
                if channel=='all' or getattr(event, channel):
                    weight = event.selection*lumi_scale*event.lumi_weight
                    yields['inclusive'][channel][wgt]     += weight
                    if event.highMT2ll:
                        yields['highMT2ll'][channel][wgt] += weight 
             
sequence.append( increment_yields )

def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if dataMCScale is not None: 
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*10)/10., dataMCScale ) ) )
    else:
        lines.append( (0.50, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV)'%(int(lumi_scale*10)/10.) ) )
    return [tex.DrawLatex(*l) for l in lines] 

plot_path = os.path.join(user.plot_directory, args.plot_directory, prefix)

stack = Stack( [ ttbar ] )

plots = []

def weigthFunc( wgt, channel = 'all'):
    if channel == 'all':
        def func( event, sample ):
            return lumi_scale*event.lumi_weight*getattr( event, wgt )*(len(event.selected_muons)+len(event.selected_electrons)==2)*event.selection
        return func
    else:
        def func( event, sample ):
            return lumi_scale*event.lumi_weight*getattr( event, wgt )*(len(event.selected_muons)+len(event.selected_electrons)==2)*event.selection*getattr(event, channel)
        return func

met  = {channel: { wgt:Plot(
    name = "met_%s_%s" % (wgt, channel),
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[1050/50,0,1050],
    selectionString = selectionString,
    weight = weigthFunc( wgt, channel ), #, lambda event, sample: 12.9*0.03#*getattr(event,  wgt),
    ) for wgt in selectionWeights } for channel in channels }

plots.append( met )

mt2ll  = {channel: { wgt:Plot(
    name = "mt2ll_%s_%s" % (wgt, channel),
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.mt2ll,
    binning=[320/20,0,320],
    selectionString = selectionString,
    weight = weigthFunc( wgt, channel ), #, lambda event, sample: 12.9*0.03#*getattr(event,  wgt),
    ) for wgt in selectionWeights } for channel in channels }

plots.append( mt2ll )

read_variables = ["genWeight/F", 'met_pt/F', 'met_phi/F', 'met_genPt/F', 'met_genPhi/F'] #["weight/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F,id/I]", "nJetGood/I", "l1_eta/F", "l2_eta/F", 'l1_phi/F', 'l2_phi/F', 'met_pt/F', 'l1_pt/F', 'l2_pt/F']
read_variables.extend( ['nLepGood/I',   'LepGood[pt/F,eta/F,etaSc/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I,mcMatchPdgId/I,mcMatchAny/I,relIso03/F,sigmaIEtaIEta/F,dEtaScTrkIn/F,dPhiScTrkIn/F,hadronicOverEm/F,eInvMinusPInv/F]'] )
read_variables.extend( ['nLepOther/I', 'LepOther[pt/F,eta/F,etaSc/F,phi/F,pdgId/I,tightId/I,miniRelIso/F,sip3d/F,mediumMuonId/I,mvaIdSpring15/F,lostHits/I,convVeto/I,dxy/F,dz/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I,mcMatchPdgId/I,mcMatchAny/I,relIso03/F,sigmaIEtaIEta/F,dEtaScTrkIn/F,dPhiScTrkIn/F,hadronicOverEm/F,eInvMinusPInv/F]'] )
read_variables.extend( ['ngenPartAll/I', VectorTreeVariable.fromString('genPartAll[pt/F,eta/F,phi/F,pdgId/I,status/I,charge/F,motherId/I,grandmotherId/I,nMothers/I,motherIndex1/I,motherIndex2/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I,isPromptHard/I]', nMax=200 ) ] )

to_fill = []
for p in plots:
    for p_ in p.values():
        to_fill.extend( p_.values() )

plotting.fill( to_fill, read_variables = read_variables, sequence = sequence)
if not os.path.exists( plot_path ): os.makedirs( plot_path )

ratio = None #{'yRange':(0.1,1.9)} 

def legendText( w ):
    if w=='fakeMET_50':
        return "fake-#slash{E}_{T}>50"
    elif w=='fakeMET_60':
        return "fake-#slash{E}_{T}>60"
    elif w=='hasGenHadTau':
        return "#tau#rightarrow had."
    elif w=='fakeMET_40_60':
        return "40<fake-#slash{E}_{T}<60"
    elif w=='fake':
        return '#geq 1 fake l '
    elif w=='nonPrompt':
        return '#geq 1 non-prompt l '
    else:
        return w

for plot in plots:
    for channel in channels:

        p0_ = plot[channel].values()[0] 
        texX = p0_.texX
        name = p0_.name.split("_")[0]+'_'+channel
        histos = [sum( [plot[channel][wgt].histos[0] for wgt in selectionWeights], [])]

        for iw, w in enumerate(selectionWeights):
            histos[0][iw].legendText = legendText(w)
            histos[0][iw].style = styles.lineStyle( colors[iw], width = 2)

        plot_ = Plot.fromHisto(
                name,
                histos, 
                texX = texX, 
            )

        plotting.draw( plot_, 
            plot_directory = plot_path, ratio = ratio, 
            logX = False, logY = True, #sorting = True, 
            # scaling = {0:1} if not args.noScaling else {},
            yRange = (0.03, "auto"), 
            drawObjects = drawObjects( None )
        )

with open(os.path.join(plot_path, 'results.txt'), 'w') as f:
    mu_eff = lepton_eff_counters[13]['hasMatch']/float(lepton_eff_counters[13]['hasMatch']+lepton_eff_counters[13]['hasNoMatch'])
    ele_eff= lepton_eff_counters[11]['hasMatch']/float(lepton_eff_counters[11]['hasMatch']+lepton_eff_counters[11]['hasNoMatch'])
    mu_fr  = ( lepton_fr_counters[13]['fake'] + lepton_fr_counters[13]['nonPrompt'])/float(lepton_fr_counters[13]['fake'] + lepton_fr_counters[13]['nonPrompt'] + lepton_fr_counters[13]['prompt'])
    ele_fr = ( lepton_fr_counters[11]['fake'] + lepton_fr_counters[11]['nonPrompt'])/float(lepton_fr_counters[11]['fake'] + lepton_fr_counters[11]['nonPrompt'] + lepton_fr_counters[11]['prompt'])
    f.write("Mu  Eff %3.2f Mu  FR %5.4f\n"%( mu_eff, mu_fr ) )
    f.write("Ele Eff %3.2f Ele FR %5.4f\n"%( ele_eff, ele_fr ) )
    for c in channels:
        tot       =  sum(yields['inclusive'][c].values())
        tot_tail  =  sum(yields['highMT2ll'][c].values())
        f.write("Channel %6s yield: %8.2f tail: %8.2f\n" %(c, tot, tot_tail ))
        for wgt in selectionWeights:
            f.write("      tail contribution %16s: %8.2f\n" %(wgt, yields['highMT2ll'][c][wgt] ))
        
