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
    choices=['doubleMu', 'doubleEle',  'muEle', 'dilepton', 'sameFlavour'])

argParser.add_argument('--charges',
    default='OS',
    action='store',
    choices=['OS', 'SS'])

argParser.add_argument('--zMode',
    default='onZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)

argParser.add_argument('--small',
    action='store_true',
    #default = True,
    help='Small?',
)

argParser.add_argument('--dPhi',
    action='store',
    default = 'def',
    choices=['def', 'inv','none', 'lead'],
    help='dPhi?',
)

argParser.add_argument('--dPhiLepMET',
    action='store_true',
    #default = True,
    help='Small?',
)

argParser.add_argument('--mt2ll',
    action='store',
    type = int,
    default = 120,
)

argParser.add_argument('--njet',
    default='2p',
    type=str,
    action='store',
    choices=['0', '0p', '1', '1p', '2', '2p', '01']
)

argParser.add_argument('--mIsoWP',
    default=5,
    type=int,
    action='store',
    choices=[0,1,2,3,4,5]
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


args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
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
dataFilterCut = mcFilterCut+"&&weight>0"

#Data 
if args.mode == 'doubleMu':
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
    from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import DoubleMuon_Run2016BCD_backup as PR

    data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
    postProcessing_directory = "postProcessed_80X_v15/dilepTiny"
    from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import DoubleMuon_Run2016BCD_backup as RR
else:
    raise NotImplementedError


if args.mode=="doubleMu":
    lepton_selection_string_data = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    lepton_selection_string_mc   = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    #qcd_sample = QCD_Mu5 #FIXME
elif args.mode=="doubleEle":
    lepton_selection_string_data = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    #qcd_sample = QCD_EMbcToE
elif args.mode=="muEle":
    lepton_selection_string_data = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    lepton_selection_string_mc = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])

else:
    raise ValueError( "Mode %s not known"%args.mode )

if args.small:
    for sample in [RR, PR]:
        sample.reduceFiles(to = 1)

if args.dPhi == 'inv':
    dPhi = [ ("dPhiJetMETInv", "(!(Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0))") ]
if args.dPhi == 'lead':
    dPhi = [ ("dPhiJetMETLead", "Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0") ]
elif args.dPhi=='def':
    dPhi = [ ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0") ]
else:
    dPhi = []

wpStr = { 5: "VT", 4: "T", 3: "M" , 2: "L" , 1: "VL", 0:"None"}
basic_cuts=[
    ("mll20", "dl_mass>20"),
    ("l1pt25", "l1_pt>25"),
    ("mIso%s"%wpStr[args.mIsoWP], "l1_mIsoWP>=%i&&l2_mIsoWP>=%i"%( args.mIsoWP, args.mIsoWP)),
    ] + dPhi + [
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
        ("metSig5", "(met_pt/sqrt(ht)>5||nJetGood==0)"),
        ])
    elif args.met=='low':
        res.extend([  ("metSm80", "met_pt<80")] )
    elif args.met=='none':
        pass
    res.append( ('mt2ll%i'%args.mt2ll, 'dl_mt2ll>=%i'%args.mt2ll ) )
    return res

cuts = selection()

if args.dPhiLepMET:
    cuts.extend( [ 
        ("dPhiLepMET", "cos(l1_phi-met_phi)>-0.9"),
        ] )

sequence = []
read_variables = ["evt/l", "run/I", "lumi/I"]
read_variables += [ "JetGood[pt/F,eta/F,phi/F,btagCSV/F,id/I]", "nJetGood/I", "isOS/I", 'nGoodMuons/I', 'nGoodElectrons/I', 'met_phi/F']

if args.charges=="OS":
    presel = [("isOS","isOS")]
elif args.charges=="SS":
    presel = [("isSS","l1_pdgId*l2_pdgId>0")]
else:
    raise ValueError

presel.extend( basic_cuts )
presel.extend( selection() )

prefix =  '-'.join([p[0] for p in presel ] )
selectionString = "&&".join( [p[1] for p in presel] )

logger.info( "Using prefix %s and selectionString %s", prefix, selectionString )

PR, RR = RR, PR

r_PR = PR.treeReader( variables = map( TreeVariable.fromString, read_variables )  )
r_PR.activateAllBranches()

RR.setSelectionString([dataFilterCut, lepton_selection_string_data, selectionString])
r_RR = RR.treeReader( variables = map( TreeVariable.fromString, read_variables )  )
r_RR.activateAllBranches()
event_list = RR.getEventList( RR.selectionString )
r_RR.setEventList( event_list )

r_RR.start()
p_RR = {}
while r_RR.run():
    p_RR[( r_RR.event.run, r_RR.event.lumi, r_RR.event.evt )] = r_RR.position - 1
    evt_str = "%i:%i:%i"%(r_RR.event.run, r_RR.event.lumi, r_RR.event.evt)
    event_list = PR.getEventList( "run==%i&&lumi==%i&&evt==%i"%(r_RR.event.run, r_RR.event.lumi, r_RR.event.evt) )
    if event_list.GetN()==0:
        logger.warning("PR not found: %s"%evt_str) 
    elif event_list.GetN()==1:
        logger.warning("PR     found: %s"%evt_str)
    else:
        raise RuntimeError( "Found %i events for %s"%(event_list.GetN(), evt_str) )

