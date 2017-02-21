#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import array
import os

#RootTools
from RootTools.core.standard import *

#StopsDilepton
from StopsDilepton.tools.objectSelection import muonSelectorString, eleSelectorString

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

argParser.add_argument('--selection',
    #default='Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=1',
    default='',
    type=str,
    action='store',
)

argParser.add_argument('--baseTrigger',
    default='',
    type=str,
    action='store',
)

argParser.add_argument('--dileptonTrigger',
    default='HLT_mue',
    type=str,
    action='store',
)


argParser.add_argument('--sample',
    default='JetHT',
    type=str,
    action='store',
)

argParser.add_argument('--plot_directory',
    default='pngEff',
    type=str,
    action='store',
)

argParser.add_argument('--minLeadingLeptonPt',
    default=0,
    type=int,
    action='store',
)

argParser.add_argument('--mode',
    default='muEle',
    action='store',
    choices=['doubleMu', 'doubleEle',  'muEle'])

args = argParser.parse_args()


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

maxN = 10 if args.small else -1 

from CMGTools.RootTools.samples.samples_13TeV_DATA2016 import *

from StopsDilepton.samples.heppy_dpm_samples import data_03Feb2017_heppy_mapper as data_heppy_mapper
#                return data_heppy_mapper.from_heppy_samplename(heppy_sample.name, maxN = maxN)

data_samples = [data_heppy_mapper.from_heppy_samplename(s.name) for s in dataSamples_03Feb2017 if s.name.startswith(args.sample)]
for s in data_samples:
    if maxN>0:
        s.files = s.files[:maxN]
    logger.info("Adding data sample %s (heppy: %s)", s.name, s.heppy.name)

#from StopsDilepton.samples.helpers import fromHeppySample
#data_Run2016B = fromHeppySample("%s_Run2016B_PromptReco_v2" % args.sample, data_path = '/scratch/rschoefbeck/cmgTuples/80X_1l_12', maxN = maxN)
#data_Run2016C = fromHeppySample("%s_Run2016C_PromptReco_v2" % args.sample, data_path = '/scratch/rschoefbeck/cmgTuples/80X_1l_12', maxN = maxN)
#data_Run2016D = fromHeppySample("%s_Run2016D_PromptReco_v2" % args.sample, data_path = '/scratch/rschoefbeck/cmgTuples/80X_1l_12', maxN = maxN)
#

data=Sample.combine( "Run2016BCDEFGH", data_samples )
preprefix = "Run2016BCDEFGH"
triggerName = args.dileptonTrigger.replace('||','_OR_')

pt_thresholds = range(0,30,2)+range(30,50,5)+range(50,210,10)
eta_thresholds = [x/10. for x in range(-25,26,1) ]
pt_thresholds_coarse = range(5,25,10)+range(25,130,15)+range(130,330,50)
pt_thresholds_veryCoarse = [20,25,35] + range(50,200,50)+[250]
eta_thresholds_coarse = [x/10. for x in range(-25,26,5) ]

eff_pt1 = ROOT.TProfile("eff_pt1","eff_pt1", len(pt_thresholds)-1, array.array('d',pt_thresholds), 0,1)
eff_pt1.GetYaxis().SetTitle(triggerName)
eff_pt1.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1.style = styles.errorStyle( ROOT.kBlack )

eff_pt2 = ROOT.TProfile("eff_pt2","eff_pt2", len(pt_thresholds)-1, array.array('d',pt_thresholds), 0,1)
eff_pt2.GetYaxis().SetTitle(triggerName)
eff_pt2.GetXaxis().SetTitle("p_{T} of trailing lepton")
eff_pt2.style = styles.errorStyle( ROOT.kBlack )

eff_eta1 = ROOT.TProfile("eff_eta1","eff_eta1", len(eta_thresholds)-1, array.array('d',eta_thresholds), 0,1)
eff_eta1.GetYaxis().SetTitle(triggerName)
eff_eta1.GetXaxis().SetTitle("#eta of leading lepton")
eff_eta1.style = styles.errorStyle( ROOT.kBlack )

eff_eta2 = ROOT.TProfile("eff_eta2","eff_eta2", len(eta_thresholds)-1, array.array('d',eta_thresholds), 0,1)
eff_eta2.GetYaxis().SetTitle(triggerName)
eff_eta2.GetXaxis().SetTitle("#eta of trailing lepton")
eff_eta2.style = styles.errorStyle( ROOT.kBlack )

ht = ROOT.TH1D("ht","ht", 2000/50,0,2000)
ht.GetYaxis().SetTitle("Number of events")
ht.GetXaxis().SetTitle("H_{T} (GeV)")
ht.style = styles.errorStyle( ROOT.kBlack )

eff_pt1_pt2 = ROOT.TProfile2D("eff_pt1_pt2","eff_pt1_pt2", len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
eff_pt1_pt2.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1_pt2.GetYaxis().SetTitle("p_{T} of trailing lepton")
eff_pt1_pt2.style = styles.errorStyle( ROOT.kBlack )

eff_pt1_pt2_veryCoarse = ROOT.TProfile2D("eff_pt1_pt2_veryCoarse","eff_pt1_pt2_veryCoarse", len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
eff_pt1_pt2_veryCoarse.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1_pt2_veryCoarse.GetYaxis().SetTitle("p_{T} of trailing lepton")
eff_pt1_pt2_veryCoarse.style = styles.errorStyle( ROOT.kBlack )

eff_pt1_pt2_highEta1_veryCoarse = ROOT.TProfile2D("eff_pt1_pt2_highEta1_veryCoarse","eff_pt1_pt2_highEta1_veryCoarse", len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
eff_pt1_pt2_highEta1_veryCoarse.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1_pt2_highEta1_veryCoarse.GetYaxis().SetTitle("p_{T} of trailing lepton")
eff_pt1_pt2_highEta1_veryCoarse.style = styles.errorStyle( ROOT.kBlack )

eff_pt1_pt2_lowEta1_veryCoarse = ROOT.TProfile2D("eff_pt1_pt2_lowEta1_veryCoarse","eff_pt1_pt2_lowEta1_veryCoarse", len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse), len(pt_thresholds_veryCoarse)-1, array.array('d',pt_thresholds_veryCoarse))
eff_pt1_pt2_lowEta1_veryCoarse.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1_pt2_lowEta1_veryCoarse.GetYaxis().SetTitle("p_{T} of trailing lepton")
eff_pt1_pt2_lowEta1_veryCoarse.style = styles.errorStyle( ROOT.kBlack )

eff_pt1_eta1 = ROOT.TProfile2D("eff_pt1_eta1","eff_pt1_eta1", len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))
eff_pt1_eta1.GetXaxis().SetTitle("p_{T} of leading lepton")
eff_pt1_eta1.GetYaxis().SetTitle("#eta of leading lepton")
eff_pt1_eta1.style = styles.errorStyle( ROOT.kBlack )

eff_pt2_eta2 = ROOT.TProfile2D("eff_pt2_eta2","eff_pt2_eta2", len(pt_thresholds_coarse)-1, array.array('d',pt_thresholds_coarse), len(eta_thresholds_coarse)-1, array.array('d',eta_thresholds_coarse))
eff_pt2_eta2.GetXaxis().SetTitle("p_{T} of trailing lepton")
eff_pt2_eta2.GetYaxis().SetTitle("#eta of trailing lepton")
eff_pt2_eta2.style = styles.errorStyle( ROOT.kBlack )

logger.info( "Sample:      %s" % data.name )

def leptonSelectorString(index, ptCut):
    return '('+muonSelectorString(index=index, ptCut=ptCut)+'||'+eleSelectorString(index=index, ptCut=ptCut)+')'

if args.mode=='doubleMu':
    selString = muonSelectorString
elif args.mode=='doubleEle':
    selString = eleSelectorString
elif args.mode== 'muEle':
    selString = leptonSelectorString
else:   
    raise ValueError( "Mode %s not known" % args.mode )

selection_string    = "&&".join( str_ for str_ in [\
        'Sum$('+selString(ptCut=0,index=None)+')==2' if args.mode in ['doubleMu', 'doubleEle'] 
                else 'Sum$('+muonSelectorString(ptCut=0,index=None)+')==1&&Sum$('+eleSelectorString(ptCut=0,index=None)+')==1',   
        args.baseTrigger,
        args.selection
    ] if str_ )


plot_string_pt1      = args.dileptonTrigger+":MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1"
plot_string_pt2      = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt2"

logger.info( "Plot string: %s" % plot_string_pt1 )
logger.info( "Selection:   %s" % selection_string )
 
data.chain.Draw(plot_string_pt1, selection_string, 'goff')
data.chain.Draw(plot_string_pt2, selection_string, 'goff')

data.chain.Draw("Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>>ht", selection_string, 'goff')

plot_string_eta1     = args.dileptonTrigger+":LepGood_eta>>eff_eta1"
data.chain.Draw(plot_string_eta1, selection_string+"&&LepGood_pt==MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+')', 'goff') 

plot_string_eta2     = args.dileptonTrigger+":LepGood_eta>>eff_eta2"
data.chain.Draw(plot_string_eta2, selection_string+"&&LepGood_pt==MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+')', 'goff') 

plot_string_pt1_pt2    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2"
data.chain.Draw(plot_string_pt1_pt2, selection_string, 'goff')
plot_string_pt1_pt2_veryCoarse    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2_veryCoarse"
data.chain.Draw(plot_string_pt1_pt2_veryCoarse, selection_string, 'goff')

if args.mode=='muEle':
    # split high/low wrt muon
    plot_string_pt1_pt2_highEta1_veryCoarse    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2_highEta1_veryCoarse"
    data.chain.Draw(plot_string_pt1_pt2_highEta1_veryCoarse, selection_string+"&&Sum$(abs(LepGood_pdgId)==13&&abs(LepGood_eta)>1.5&&"+selString(index=None,ptCut=0)+')==1', 'goff')

    plot_string_pt1_pt2_lowEta1_veryCoarse    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2_lowEta1_veryCoarse"
    data.chain.Draw(plot_string_pt1_pt2_lowEta1_veryCoarse, selection_string+"&&Sum$(abs(LepGood_pdgId)==13&&abs(LepGood_eta)<=1.5&&"+selString(index=None,ptCut=0)+')==1', 'goff')
else:
    # split high/low wrt leading lepton
    plot_string_pt1_pt2_highEta1_veryCoarse    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2_highEta1_veryCoarse"
    data.chain.Draw(plot_string_pt1_pt2_highEta1_veryCoarse, selection_string+"&&Sum$(abs(LepGood_eta)>1.5&&LepGood_pt==MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+'))==1', 'goff')

    plot_string_pt1_pt2_lowEta1_veryCoarse    = args.dileptonTrigger+":MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+"):MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_pt2_lowEta1_veryCoarse"
    data.chain.Draw(plot_string_pt1_pt2_lowEta1_veryCoarse, selection_string+"&&Sum$(abs(LepGood_eta)<=1.5&&LepGood_pt==MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+'))==1', 'goff')

plot_string_pt1_eta1   = args.dileptonTrigger+":LepGood_eta:MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt1_eta1"
data.chain.Draw(plot_string_pt1_eta1, selection_string+"&&LepGood_pt==MaxIf$(LepGood_pt,"+selString(index=None,ptCut=0)+')', 'goff')

plot_string_pt2_eta2   = args.dileptonTrigger+":LepGood_eta:MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+")>>eff_pt2_eta2"
data.chain.Draw(plot_string_pt2_eta2, selection_string+"&&LepGood_pt==MinIf$(LepGood_pt,"+selString(index=None,ptCut=0)+')', 'goff')


prefix = preprefix+"_%s_%s_measuredIn%s_minLeadLepPt%i" % ( triggerName, args.baseTrigger if args.baseTrigger is not '' else 'None', args.sample, args.minLeadingLeptonPt)
if args.small: prefix = "small_" + prefix

from StopsDilepton.tools.user import plot_directory
plot_path = os.path.join(plot_directory, args.plot_directory, prefix)

plotting.draw(
    Plot.fromHisto(name = 'pt1_'+triggerName, histos = [[ eff_pt1 ]], texX = "p_{T} of leading lepton", texY = triggerName),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)
plotting.draw(
    Plot.fromHisto(name = 'pt2_'+triggerName, histos = [[ eff_pt2 ]], texX = "p_{T} of trailing lepton", texY = triggerName),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)
plotting.draw(
    Plot.fromHisto(name = 'eta1_'+triggerName, histos = [[ eff_eta1 ]], texX = "#eta of leading lepton", texY = triggerName),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)
plotting.draw(
    Plot.fromHisto(name = 'eta2_'+triggerName, histos = [[ eff_eta2 ]], texX = "#eta of trailing lepton", texY = triggerName),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = False, sorting = False,
     yRange = (0,1), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)
plotting.draw(
    Plot.fromHisto(name = "ht_"+triggerName, histos = [[ ht ]], texX = "H_{T} (GeV)", texY = "Number of events"),
    plot_directory = plot_path, #ratio = ratio, 
    logX = False, logY = True, sorting = False,
     yRange = (0.3,"auto"), legend = None ,
    # scaling = {0:1},
    # drawObjects = drawObjects( dataMCScale )
)

ROOT.gStyle.SetPadRightMargin(0.15)
ROOT.gStyle.SetPaintTextFormat("2.2f")
for name, plot in [
    ["pt1_pt2", eff_pt1_pt2],
    ["pt1_pt2_veryCoarse", eff_pt1_pt2_veryCoarse],
    ["pt1_pt2_lowEta1_veryCoarse", eff_pt1_pt2_lowEta1_veryCoarse],
    ["pt1_pt2_highEta1_veryCoarse", eff_pt1_pt2_highEta1_veryCoarse],
    ["pt1_eta1", eff_pt1_eta1],
    ["pt2_eta2", eff_pt2_eta2],
    ]:
    c1 = ROOT.TCanvas()
    if 'veryCoarse' in name:
        plot.SetMarkerSize(0.8)
        plot.Draw("COLZTextE")
    else:
        plot.Draw("COLZ" )

    plot.GetZaxis().SetRangeUser(0,1)
    c1.Print(os.path.join(plot_path, triggerName+'_'+name+'.png') )
    c1.Print(os.path.join(plot_path, triggerName+'_'+name+'.pdf') )
    c1.Print(os.path.join(plot_path, triggerName+'_'+name+'.root') )
    del c1

ofile = ROOT.TFile.Open(os.path.join(plot_path, prefix+'.root'), 'recreate')
eff_pt1.Write()
eff_pt2.Write()
eff_eta1.Write()
eff_eta2.Write()
eff_pt1_pt2.Write()
eff_pt1_pt2_highEta1_veryCoarse.Write()
eff_pt1_pt2_lowEta1_veryCoarse.Write()
eff_pt1_eta1.Write()
eff_pt2_eta2.Write()
ht.Write()
ofile.Close()
