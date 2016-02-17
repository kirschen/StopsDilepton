''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos
import itertools

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
    default='doubleEle',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle'])

argParser.add_argument('--zMode',
    default='allZ',
    action='store',
    choices=['onZ', 'offZ', 'allZ']
)

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
    default='png25ns_2l_mAODv2_2100_officialPU_new',
    action='store',
)

args = argParser.parse_args()

# Logging
from RootTools.core.logger import get_logger
logger = get_logger(args.logLevel, logFile = None)

# RootTools
from RootTools.plot.Stack import Stack 
from RootTools.plot.Plot import Plot 
from RootTools.core.Sample import Sample 
from RootTools.core.Variable import Variable
import RootTools.core.helpers as helpers
import RootTools.plot.styles as styles
import RootTools.plot.plotting as plotting

#make samples
from StopsDilepton.samples.cmgTuples_postprocessed_1l import *

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

if args.mode=="doubleMu":
    leptonSelectionString = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(args.zMode)])
    data_sample = DoubleMuon_Run2015D
    qcd_sample = QCD_Mu5
    trigger     = "HLT_mumuIso"
elif args.mode=="doubleEle":
    leptonSelectionString = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(args.zMode)])
    data_sample = DoubleEG_Run2015D
    qcd_sample = QCD_EMbcToE
    trigger   = "HLT_ee_DZ"
elif args.mode=="muEle":
    leptonSelectionString = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(args.zMode)])
    data_sample = MuonEG_Run2015D
    qcd_sample = QCD_Mu5EMbcToE
    trigger    = "HLT_mue"
else:
    raise ValueError( "Mode %s not known"%args.mode )

# Extra requirements on data
filterCut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"

data_sample.setSelectionString([filterCut, trigger])
data_sample.style = styles.errorStyle( ROOT.kBlack )

mc = [ DY_HT_LO, TTJets_Lep, qcd_sample, singleTop, TTX, diBoson, triBoson, WJetsToLNu]
#mc = [ TTX]

for sample in mc:
    sample.style = styles.fillStyle(sample.color)
    sample.setSelectionString([ trigger ])

# user data
from StopsDilepton.tools.user import plot_directory

# official PU reweighting
weight = lambda data:data.weightPU 

cuts=[
    ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
    ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"),
#    ("nbtag0", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)==0"),
    ("mll20", "dl_mass>20"),
    ("met80", "met_pt>80"),
    ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
]

for i in [len(cuts)]:
    for comb in itertools.combinations(cuts,i):
        presel = [("isOS","isOS")] 
        presel.extend( comb )

        prefix = '_'.join([args.mode, args.zMode, '-'.join([p[0] for p in presel])])
        plot_path = os.path.join(plot_directory, args.plot_directory, prefix)
        if os.path.exists(plot_path) and not args.overwrite:
            print "Path %s not empty. Skipping."%path
            continue

        if "nbtag1" in prefix and "nbtag0" in prefix: continue

        selectionString = "&&".join( [p[1] for p in presel] + [leptonSelectionString] )

        stack = Stack(mc, [data_sample])

        cosMetPhi = Plot(\
            stack = stack, 
            variable = Variable.fromString('cosMetPhi/F').addFiller (
                helpers.uses(lambda data: cos( data.met_phi ) , "met_phi/F")
            ), 
            binning = [10,-1,1], 
            selectionString = selectionString,
            weight = weight,
            texX = "cos(#phi(#slash{E}_{T}))",
            texY = "Number of Events ",
        )

        read_variables = ["weightPU/F"]
        plotting.fill([cosMetPhi], read_variables = read_variables)
        if not os.path.exists( plot_path ): os.makedirs( plot_path )
        plotting.draw(cosMetPhi, plot_directory = plot_path, ratio = {}, logX = False, logY = True, sorting = True)
