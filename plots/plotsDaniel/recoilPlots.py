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
      default='INFO',
      help="Log level for logging"
)

argParser.add_argument('--mode',
    default='doubleMu',
    action='store',
    choices=['doubleMu', 'doubleEle', 'sameFlavour'])

argParser.add_argument('--zMode',
    default='onZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)

argParser.add_argument('--dy',
    default='LO',
    action='store',
    choices=['LO', 'NLO'])

argParser.add_argument('--pu',
    default="reweightPU27fb",
    action='store',
    choices=["None", "reweightPU27fb", "reweightPU27fbUp", "reweightPU27fbDown", 'reweightPU', 'custom'],
    help='PU weight',
)

argParser.add_argument('--small',
    action='store_true',
    #default=True,
    help='Small?',
)

argParser.add_argument('--dPhi',
    action='store',
    default = 'none',
    choices=['def', 'inv','none'],
    help='dPhi?',
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
    default='recoil_80X_Run2016BCD',
    action='store',
)

argParser.add_argument('--trigger',
    action='store_true',
    #default = True,
    help='Small?',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

mcFilterCut   = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadronSummer2016&&Flag_badMuonSummer2016"
dataFilterCut = mcFilterCut+"&&weight>0"

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<8"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *

sample_DoubleMuon  = DoubleMuon_Run2016_backup
sample_DoubleEG    = DoubleEG_Run2016_backup
sample_MuonEG      = MuonEG_Run2016_backup

if args.mode=="doubleMu":
    lepton_selection_string_data = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    lepton_selection_string_mc   = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    data_samples = [sample_DoubleMuon]
    sample_DoubleMuon.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_DoubleMuon.addSelectionString( "(HLT_mumuIso||HLT_mumuNoiso)" )
    data_sample_texName = "Data (2 #mu)"
    #qcd_sample = QCD_Mu5 #FIXME
elif args.mode=="doubleEle":
    lepton_selection_string_data = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    data_samples = [sample_DoubleEG]
    sample_DoubleEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_DoubleEG.addSelectionString( "HLT_ee_DZ" )
    data_sample_texName = "Data (2 e)"
    #qcd_sample = QCD_EMbcToE
elif args.mode=="muEle":
    lepton_selection_string_data = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    data_samples = [sample_MuonEG]
    sample_MuonEG.setSelectionString([dataFilterCut, lepton_selection_string_data])
    if args.trigger: sample_MuonEG.addSelectionString( "HLT_mue" )
    data_sample_texName = "Data (1 #mu, 1 e)"
elif args.mode=="sameFlavour":
    doubleMu_selectionString =  "&&".join([ "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    doubleEle_selectionString = "&&".join([ "isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join([ "(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2)", getZCut(args.zMode)])

    data_samples = [sample_DoubleMuon, sample_DoubleEG]
    sample_DoubleMuon.setSelectionString([dataFilterCut, doubleMu_selectionString])
    sample_DoubleEG.setSelectionString([dataFilterCut, doubleEle_selectionString])
    if args.trigger:
        sample_DoubleMuon.addSelectionString( "(HLT_mumuIso||HLT_mumuNoiso)" )
        sample_DoubleEG.addSelectionString( "HLT_ee_DZ" )

    data_sample_texName = "Data (SF)"
    #qcd_sample = QCD_Mu5EMbcToE

else:
    raise ValueError( "Mode %s not known"%args.mode )

if args.dy == "NLO":
    dy_sample = DY
elif args.dy == "LO":
    dy_sample = DY_HT_LO
else:
    raise ValueError

#mc = [ DY, TTJets, qcd_sample, singleTop, TTX, diBoson, triBoson, WJetsToLNu]
#mc = [ DY, TTJets, qcd_sample, TTZ]

dy_highFakeMet = copy.deepcopy( dy_sample )
dy_highFakeMet.name = "dy_highFakeMet"
dy_highFakeMet.texName = "DY #slash{E}_{T, fake} > 100"
dy_highFakeMet.addSelectionString( "abs(met_pt-met_genPt)>100" )
dy_highFakeMet.color = ROOT.kGreen + 4

dy_mediumFakeMet = copy.deepcopy( dy_sample )
dy_mediumFakeMet.name = "dy_mediumFakeMet"
dy_mediumFakeMet.texName = "DY  50<#slash{E}_{T,fake}<100"
dy_mediumFakeMet.addSelectionString( "abs(met_pt-met_genPt)>50&&abs(met_pt-met_genPt)<100" )
dy_mediumFakeMet.color = ROOT.kGreen + 2

dy_lowFakeMet = copy.deepcopy( dy_sample )
dy_lowFakeMet.name = "dy_lowFakeMet"
dy_lowFakeMet.texName = "DY  #slash{E}_{T,fake}<50"
dy_lowFakeMet.addSelectionString( "abs(met_pt-met_genPt)<=50" )
dy_lowFakeMet.color = ROOT.kGreen 

mc = [ dy_lowFakeMet, dy_mediumFakeMet, dy_highFakeMet, Top, diBoson, TTZ_LO, TTW, triBoson, TWZ]#TTXNoZ,
#mc = [ TTX]
if args.small:
    for sample in mc + data_samples:
        sample.reduceFiles(to = 1)
    #TTJets_Dilep.reduceFiles(to = 1)

for s in data_samples:
    s.style = styles.errorStyle( ROOT.kBlack )

lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000

for sample in mc:
    sample.style = styles.fillStyle( sample.color)
    sample.addSelectionString([ mcFilterCut, lepton_selection_string_mc])

from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda event, sample:event.weight

if args.dPhi == 'inv':
    dPhi = [ ("dPhiJetMETInv", "(!(Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0))") ]
elif args.dPhi=='def':
    dPhi = [ ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0") ]
else:
    dPhi = []

cuts=[
#    ("leadingLepIsTight", "l1_miniRelIso<0.4"),
#    ("multiIsoWP", "l1_index>=0&&l1_index<1000&&l2_index>=0&&l2_index<1000&&"+multiIsoWP),
#    ("njet12", "nJetGood>=1&&nJetGood<=2"),
    ("njet2p", "nJetGood>=1&&nJetGood>=2"),
#    ("nbtag1", "nBTag>=1"),
#    ("nLooseBTag0", "Sum$(JetGood_pt>30&&JetGood_id&&abs(JetGood_eta)<2.4&&JetGood_btagCSV>0.460)==0"),
#    ("ptZ100", "dl_pt>100"),
#    ("mll20", "dl_mass>20"),
#    ("met80", "met_pt>80"),
#    ("metSig5", "met_pt/sqrt(ht)>5"),
#    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
    ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    
] + dPhi

                
def drawObjects( dataMCScale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if dataMCScale is not None: 
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) )
    else:
        lines.append( (0.50, 0.95, '13 TeV' ) )
    return [tex.DrawLatex(*l) for l in lines] 

stack = Stack(mc, data_samples)

sequence = []

def makeQTZ( event, sample ):
     
    event.qx = event.dl_pt*cos(event.dl_phi)  
    event.qy = event.dl_pt*sin(event.dl_phi)

    event.qt = sqrt( event.qx**2 + event.qy**2 )

def makeUParaUPerp( event, sample ):
    mex = event.met_pt*cos(event.met_phi) 
    mey = event.met_pt*sin(event.met_phi)
    ux = -mex - event.qx 
    uy = -mey - event.qy
    event.upara = (ux*event.qx+uy*event.qy)/event.qt
    event.uperp = (ux*event.qy-uy*event.qx)/event.qt
    event.uPlusQPara = -(mex*event.qx + mey*event.qy)/event.qt

sequence.append( makeQTZ )
sequence.append( makeUParaUPerp )


#TTJets_Dilep.read_variables = [
#    TreeVariable.fromString('ngenPartAll/I'),
#    VectorTreeVariable.fromString('genPartAll[pt/F,eta/F,phi/F,pdgId/I,status/I,charge/F,motherId/I,grandmotherId/I,nMothers/I,motherIndex1/I,motherIndex2/I,nDaughters/I,daughterIndex1/I,daughterIndex2/I]', nMax=200 ),
#]
#def makeTTJetsQT( data ):
#    
#    gPart = getGenPartsAll( data )
#    genW  = filter( lambda p:abs(p['pdgId'])==24 and abs(p['motherId'])==6, gPart)
#    if not len(genW)==2:
#        print "Warning, found %i W from t"%len(genW)
#    qx = sum([p['pt']*cos(p['phi']) for p in genW ],0.) 
#    qy = sum([p['pt']*sin(p['phi']) for p in genW ],0.)
#    qt = sqrt( qx**2 + qy**2 )
#    event.ttjets_qt = qt 
#
#TTJets_Dilep.sequence = [ makeTTJetsQT ]
#
#if len(args.signals)>0:
#    from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_2l_postProcessed import *
#    from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *
#    for s in args.signals:
#        if "*" in s:
#            split = s.split("*")
#            sig, fac = split[0], int(split[1])
#        else:
#            sig, fac = s, 1
#        try:
#            stack.append( [eval(sig)] )
#            if hasattr(stack[-1][0], "scale"): 
#                stack[-1][0].scale*=fac
#            elif fac!=1:
#                stack[-1][0].scale = fac
#            else: pass
#
#            if fac!=1:
#                stack[-1][0].name+=" x"+str(fac)                
#            logger.info( "Adding sample %s with factor %3.2f", sig, fac)
#        except NameError:
#            logger.warning( "Could not add signal %s", s)


presel = [("isOS","isOS")]
presel.extend( cuts )

ppfixes = [args.mode, args.zMode]
if args.pu != "None": ppfixes.append( args.pu )
if args.dy == "NLO": ppfixes.append( "DYNLO" )
if args.dy == "LO": ppfixes.append( "DYLO" )
if args.small: ppfixes = ['small'] + ppfixes
prefix = '_'.join( ppfixes + [ '-'.join([p[0] for p in presel ] ) ] )

plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
assert not os.path.exists(plot_path) or args.overwrite, "Path %s not empty. Skipping."

selectionString = "&&".join( [p[1] for p in presel])

logger.info( "Now plotting with prefix %s and selectionString %s", prefix, selectionString )

logger.info( "Calculating normalization constants" )        
#yield_mc    = sum(s.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val'] for s in mc)
#yield_data  = data_sample.getYieldFromDraw( selectionString = selectionString, weightString = 'weight')['val']

from StopsDilepton.tools.puReweighting import getReweightingFunction
nTrueInt36fb_puRW         = getReweightingFunction(data="PU_2016_36000_XSecCentral", mc="Spring16")

for sample in mc:
    dataMCScale = 1. #yield_data/(yield_mc*lumi_scale)
    sample.scale = lumi_scale*dataMCScale
    if args.pu != "None":
        if args.pu == 'custom':
          sample.read_variables = ['reweightDilepTriggerBackup/F', 'reweightBTag_SF/F', 'reweightLeptonSF/F', 'reweightLeptonHIPSF/F','nTrueInt/F']
          sample.weight = lambda event, sample: nTrueInt36fb_puRW(event.nTrueInt)*event.reweightDilepTriggerBackup*event.reweightLeptonSF
        else:
          sample.read_variables = [args.pu+'/F', 'reweightDilepTriggerBackup/F', 'reweightBTag_SF/F', 'reweightLeptonSF/F', 'reweightLeptonHIPSF/F']
          sample.weight = lambda event, sample: getattr( event, args.pu )*event.reweightDilepTriggerBackup*event.reweightLeptonSF
    else:
        sample.read_variables = ['reweightDilepTriggerBackup/F', 'reweightLeptonSF/F']
        sample.weight = lambda event, sample: event.reweightDilepTriggerBackup*event.reweightLeptonSF

        sample.read_variables = [args.pu+'/F']

weight = lambda event, sample: event.weight

#logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc, yield_data, lumi_scale )

plots = []
plots2D = []


qt  = Plot(
    name = "qt",
    texX = 'q_{T} (GeV)', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.qt,
    binning=[400/5,0,200],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    ) 
plots.append( qt )

upara  = Plot(
    name = "upara",
    texX = 'u_{\parallel} (GeV)', texY = 'Number of Events / 5 GeV',
   stack = stack, 
    attribute = lambda event, sample:event.upara,
    binning=[400/5,-200,200],
    selectionString = selectionString,
    addOverFlowBin = 'both',
    weight = weight,
    ) 
plots.append( upara )

dl_uPlusQPara  = Plot(
    name = "uPlusQPara",
    texX = '(u+q)_{\parallel} (GeV)', texY = 'Number of Events / 30 GeV',
   stack = stack, 
    attribute = lambda event, sample:event.uPlusQPara,
    binning=[600/30,-300,300],
    selectionString = selectionString,
    addOverFlowBin = 'both',
    weight = weight,
    ) 
plots.append( dl_uPlusQPara )

dl_uperp  = Plot(
    name = "uperp",
    texX = 'u_{\perp} (GeV)', texY = 'Number of Events / 5 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.uperp,
    binning=[400/5,-200,200],
    selectionString = selectionString,
    addOverFlowBin = 'both',
    weight = weight,
    ) 
plots.append( dl_uperp )

metZoomed  = Plot(
    name = "met_pt_zoomed",
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 10 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[22,0,220],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( metZoomed )

met  = Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[1050/50,0,1050],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( met )

metSig  = Plot(
    name = "metSig",
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    attribute = lambda event, sample: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan') , 
    read_variables =  ["met_pt/F", "ht/F"],
    binning=[30,0,30],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( metSig )

ht  = Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 100 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[2600/100,0,2600],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
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
    binning = [40,-1,1], 
    selectionString = selectionString,
    weight = weight,
)
plots.append( cosMetJet0phi )

cosMetJet1phi = Plot(\
    name = "cosMetJet1phi",
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
    stack = stack, 
    attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ), 
    binning = [40,-1,1], 
    selectionString = selectionString,
    weight = weight,
)
plots.append( cosMetJet1phi )

def qt_cut_weight( qtb ):
    def w( event, sample ):
        if event.qt>qtb[0] and event.qt<qtb[1]:
            return event.weight
        else:
            return 0
    return w

for qtb in [(0,10), (10,20), (20,30), (30,40), (40, 50), (50,60), (60, 70), (80, 90), (90,100), (100,120), (120,150), (150,200), (200,250), (250,350), (350,450), (450,550)]:
    upara_qt  = Plot(
        name = "upara_qt_%i_%i"%qtb,
        texX = 'u_{\parallel} (GeV)', texY = 'Number of Events / 10 GeV',
        stack = stack, 
        attribute = lambda event, sample:event.upara,
        weight   = qt_cut_weight(qtb),
        binning=[300/10,-150-qtb[0],150-qtb[0]],
        selectionString = selectionString,
        ) 
    plots.append( upara_qt )

    uPlusQPara_qt  = Plot(
        name = "uPlusQPara_qt_%i_%i"%qtb,
        texX = '(u+q)_{\parallel} (GeV)', texY = 'Number of Events / 10 GeV',
        stack = stack, 
        attribute = lambda event, sample:event.uPlusQPara,
        weight   = qt_cut_weight(qtb),
        binning=[500/10,-250,250],
        selectionString = selectionString,
        addOverFlowBin = 'both',
        ) 
    plots.append( uPlusQPara_qt )

    dl_uperp_qt  = Plot(
        name = "uperp_qt_%i_%i"%qtb,
        texX = 'u_{\perp} (GeV)', texY = 'Number of Events / 5 GeV',
        stack = stack, 
        attribute = lambda event, sample:event.uperp,
        weight   = qt_cut_weight(qtb),
        binning=[300/10,-150,150],
        selectionString = selectionString,
        ) 
    plots.append( dl_uperp_qt )

dl_mass  = Plot(
    texX = 'm(ll) (GeV)', texY = 'Number of Events / 3 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[150/3,0,150],
    selectionString = selectionString,
    addOverFlowBin = 'both',
    weight = weight,
    )
plots.append( dl_mass )

dl_pt  = Plot(
    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_pt/F" ),
    binning=[40,0,800],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( dl_pt )

dl_qt  = Plot(
    name = "qt",
    texX = 'q_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    stack = stack, 
    attribute = lambda event, sample:event.qt,
    binning=[40,0,400],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( dl_qt )

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
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( dl_mt2ll )

dl_mt2ll_100  = Plot(
    name = "dl_mt2ll_100",
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 25 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[350/25,100,450],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( dl_mt2ll_100 )

dl_mt2bb  = Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( dl_mt2bb )

dl_mt2blbl  = Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    stack = stack, 
    attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
    binning=[300/15,0,300],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    ) 
plots.append( dl_mt2blbl )


nbtags  = Plot(
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString('nBTag/I'),
    binning=[8,0,8],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( nbtags )

njets  = Plot(
    texX = 'number of jets', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( njets )

nVert  = Plot(
    texX = 'vertex multiplicity', texY = 'Number of Events',
    stack = stack, 
    attribute = TreeVariable.fromString( "nVert/I" ),
    binning=[50,0,50],
    selectionString = selectionString,
    addOverFlowBin = 'upper',
    weight = weight,
    )
plots.append( nVert )

read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]", "met_pt/F", "met_phi/F", "dl_pt/F", "dl_phi/F", "dl_mt2ll/F"]
plotting.fill(plots, read_variables = read_variables, sequence = sequence)
if not os.path.exists( plot_path ): os.makedirs( plot_path )

ratio = {'yRange':(0,2.2)}


for plot in plots:
    if args.mode in ['dilepton', 'sameFlavour']:
        data_histo =  plot.histos_added[-1][0]
        data_histo.style = styles.errorStyle( ROOT.kBlack )
        plot.histos = plot.histos[:-1]+[[data_histo]]
        plot.stack = plot.stack[:-1] + [[plot.stack[-1][0] ]]
        plot.stack[-1][0].texName = data_sample_texName
    plotting.draw(plot,
        plot_directory = plot_path, ratio = ratio,
        logX = False, logY = True, #sorting = True, 
        #scaling = {0:1} if not args.noScaling else {},
        yRange = (0.03, "auto"),
        drawObjects = drawObjects( dataMCScale )
    )
#logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )

#for plot in plots:
#    plotting.draw(plot, 
#        plot_directory = plot_path, ratio = ratio, 
#        logX = False, logY = True, sorting = False, 
#        yRange = (0.03, "auto"), 
#        drawObjects = drawObjects( dataMCScale ),
#    )

#for plot in plots2D:
#    plotting.draw2D(
#        plot = plot,
#        plot_directory = plot_path,
#        logX = False, logY = False, logZ = True,
#    )

logger.info( "Done with prefix %s and selectionString %s", prefix, selectionString )
