'''
Measure trigger efficiencies directly from nanoAOD
'''

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
from StopsDilepton.tools.triggerSelector import *

tag_trigger = {'MET':{}, 'JetHT':{}}

tag_trigger['MET'][2016]    = ['HLT_MET200','HLT_MET250', 'HLT_MET300', 'HLT_MET600', 'HLT_MET700','HLT_PFMET300','HLT_PFMET400','HLT_PFMET500','HLT_PFMET600','HLT_PFMET90_PFMHT90_IDTight','HLT_PFMET100_PFMHT100_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight']
tag_trigger['JetHT'][2016]  = tag_trigger['MET'][2016] + ['HLT_HT200','HLT_HT275','HLT_HT325','HLT_HT425','HLT_HT575','HLT_HT410to430','HLT_HT430to450','HLT_HT450to470','HLT_HT470to500','HLT_HT500to550','HLT_HT550to650','HLT_HT650','HLT_PFHT300_PFMET100','HLT_PFHT300_PFMET110','HLT_DiPFJetAve15_HFJEC','HLT_DiPFJetAve25_HFJEC','HLT_DiPFJetAve35_HFJEC','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500']

tag_trigger['MET'][2017]    = ['HLT_PFHT500_PFMET100_PFMHT100_IDTight','HLT_PFHT500_PFMET110_PFMHT110_IDTight','HLT_PFHT700_PFMET85_PFMHT85_IDTight','HLT_PFHT700_PFMET95_PFMHT95_IDTight','HLT_PFHT800_PFMET75_PFMHT75_IDTight','HLT_PFHT800_PFMET85_PFMHT85_IDTight','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight']
tag_trigger['JetHT'][2017]  = tag_trigger['MET'][2017] + ['HLT_PFHT430', 'HLT_PFHT510', 'HLT_PFHT590', 'HLT_PFHT680', 'HLT_PFHT780', 'HLT_PFHT890', 'HLT_PFHT1050', 'HLT_PFJet40', 'HLT_PFJet60', 'HLT_PFJet80', 'HLT_PFJet140', 'HLT_PFJet200','HLT_PFJet260', 'HLT_PFJet320', 'HLT_PFJet400', 'HLT_PFJet450', 'HLT_PFJet500', 'HLT_PFJet550', 'HLT_DiPFJetAve15_HFJEC', 'HLT_DiPFJetAve25_HFJEC', 'HLT_DiPFJetAve35_HFJEC']
#tag_trigger_both_2017 = ['HLT_PFHT500_PFMET100_PFMHT100_IDTight', 'HLT_PFHT500_PFMET110_PFMHT110_IDTight', 'HLT_PFHT700_PFMET85_PFMHT85_IDTight', 'HLT_PFHT700_PFMET95_PFMHT95_IDTight', 'HLT_PFHT800_PFMET75_PFMHT75_IDTight', 'HLT_PFHT800_PFMET85_PFMHT85_IDTight', 'HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight']

tag_trigger['MET'][2018]     = ['HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFMET200_NotCleaned','HLT_PFMET200_HBHECleaned','HLT_PFMET250_HBHECleaned','HLT_PFMET300_HBHECleaned','HLT_PFMET200_HBHE_BeamHaloCleaned','HLT_CaloMET250_HBHECleaned','HLT_CaloMET300_HBHECleaned','HLT_CaloMET350_HBHECleaned']
tag_trigger['JetHT'][2018]   = tag_trigger['MET'][2018] + ['HLT_PFJet15','HLT_PFJet25','HLT_PFJet40','HLT_PFJet60','HLT_PFJet80','HLT_PFJet140','HLT_PFJet200','HLT_PFJet260','HLT_PFJet320','HLT_PFJet400','HLT_PFJet450','HLT_PFJet500','HLT_PFJet550','HLT_PFMET110_PFMHT110_IDTight','HLT_PFMET120_PFMHT120_IDTight','HLT_PFMET130_PFMHT130_IDTight','HLT_PFMET140_PFMHT140_IDTight','HLT_PFHT180','HLT_PFHT250','HLT_PFHT370','HLT_PFHT430','HLT_PFHT510','HLT_PFHT590','HLT_PFHT680','HLT_PFHT780','HLT_PFHT890','HLT_PFHT1050']

#HLT_MET = "(%s)"%"||".join( [ "Alt$(%s,0)"%trigger for trigger in tag_trigger_MET ] )
#HLT_HT  = "(%s)"%"||".join( [ "Alt$(%s,0)"%trigger for trigger in tag_trigger_HT ] )

#HLT_MET_hadronic = "(HLT_HT350_MET100||HLT_HT350||HLT_HT475||HLT_HT600||HLT_dijet||HLT_jet||HLT_dijet70met120||HLT_dijet55met110||HLT_HT900||HLT_HT800||HLT_MET170_NotCleaned||HLT_MET170_HBHECleaned||HLT_MET170_BeamHaloCleaned||HLT_AllMET170||HLT_AllMET300||HLT_HT350_MET100)"
#
#HLT_MET_hadronic = "(HLT_MET250||HLT_MET300||HLT_MET600||HLT_MET700)"

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',            action='store',             nargs='?',      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],      default='INFO',      help="Log level for logging")
argParser.add_argument('--small',               action='store_true',        help='Small?')   
argParser.add_argument('--selection',           default='',                 type=str,    action='store')
#argParser.add_argument('--baseTrigger',         default=HLT_MET,   type=str,    action='store')
#argParser.add_argument('--dileptonTrigger',     default='HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL',          type=str,    action='store')
argParser.add_argument('--sample',              default='MET',              type=str,    action='store')
argParser.add_argument('--plot_directory',      default='pngEff',           type=str,    action='store')
argParser.add_argument('--minLeadingLeptonPt',  default=0,                  type=int,    action='store')
argParser.add_argument('--mode',                default='muEle',            action='store',    choices=['doubleMu', 'doubleEle',  'muEle'])
argParser.add_argument('--year',                default=2016,               action='store')
args = argParser.parse_args()

year = int(args.year)

baseTrigger = "(%s)"%"||".join(tag_trigger[args.sample][year])


#if args.baseTrigger == 'HLT_MET':
#    baseTrigger = HLT_MET[year]
#elif args.baseTrigger == 'HLT_HT':
#    baseTrigger = HLT_HT[year]


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )


if year == 2016:
    from Samples.nanoAOD.Run2016_14Dec2018 import *
    if args.sample == "JetHT": data_samples = JetHT_Run2016
    elif args.sample == "MET": data_samples = MET_Run2016
    else: raise(NotImplementedError, "Don't know what to do with sample %s"%args.sample)
elif year == 2017:
    from Samples.nanoAOD.Run2017_14Dec2018 import *
    if args.sample == "JetHT": data_samples = JetHT_Run2017
    elif args.sample == "MET": data_samples = MET_Run2017 #[MET_Run2017B_14Dec2018]
    else: raise(NotImplementedError, "Don't know what to do with sample %s"%args.sample)
elif year == 2018:
    from Samples.nanoAOD.Run2018_17Sep2018_private import * #use private
    if args.sample == "JetHT": data_samples = JetHT
    elif args.sample == "MET": data_samples = MET
    else: raise(NotImplementedError, "Don't know what to do with sample %s"%args.sample)


for s in data_samples:
    print s.name

data=Sample.combine( "Run%s"%year, data_samples )
preprefix = "Run%s"%year

if args.small:
    if year == 2018:
        data.reduceFiles(to=100)
    else:
        data.reduceFiles(to=10)

tr = triggerSelector(int(args.year))

if args.mode == "muEle":
    dileptonTrigger = "(%s)"%"||".join([tr.SingleElectron, tr.SingleMuon, tr.MuonEG])
    triggerName = "HLT_muEle"
elif args.mode == "doubleEle":
    dileptonTrigger = "(%s)"%"||".join([tr.DoubleEG, tr.SingleElectron])
    triggerName = "HLT_ee"
elif args.mode == "doubleMu":
    dileptonTrigger = "(%s)"%"||".join([tr.DoubleMuon, tr.SingleMuon])
    triggerName = "HLT_mm"

print "Measuring the following triggers:"
print dileptonTrigger

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

if args.mode == 'doubleMu':
    selString           = muonSelectorString
    leadingStringPt     = "MaxIf$(Muon_pt,%s)"%selString(index=None,ptCut=0)
    subLeadingStringPt  = "MinIf$(Muon_pt,%s)"%selString(index=None,ptCut=0)
    leadingStringEta    = "Muon_eta"
    subLeadingStringEta = "Muon_eta"
elif args.mode == 'doubleEle':
    selString           = eleSelectorString
    leadingStringPt     = "MaxIf$(Electron_pt,%s)"%selString(index=None,ptCut=0)
    subLeadingStringPt  = "MinIf$(Electron_pt,%s)"%selString(index=None,ptCut=0)
    leadingStringEta    = "Electron_eta"
    subLeadingStringEta = "Electron_eta"
elif args.mode == 'muEle':
    selString           = leptonSelectorString
    leadingStringPt     = "MaxIf$(Muon_pt,{0})*(MaxIf$(Muon_pt,{0})>MaxIf$(Electron_pt,{0}))+MaxIf$(Electron_pt,{0})*(MaxIf$(Electron_pt,{0})>MaxIf$(Muon_pt,{0}))".format(selString(index=None,ptCut=0))
    subLeadingStringPt  = "MinIf$(Muon_pt,{0})*(MinIf$(Muon_pt,{0})<MinIf$(Electron_pt,{0}))+MaxIf$(Electron_pt,{0})*(MinIf$(Electron_pt,{0})<MinIf$(Muon_pt,{0}))".format(selString(index=None,ptCut=0)) 
    leadingStringEta     = "Muon_eta*(MaxIf$(Muon_pt,{0})>MaxIf$(Electron_pt,{0}))+Electron_eta*(MaxIf$(Electron_pt,{0})>MaxIf$(Muon_pt,{0}))".format(selString(index=None,ptCut=0))
    subLeadingStringEta  = "Muon_eta*(MinIf$(Muon_pt,{0})<MinIf$(Electron_pt,{0}))+Electron_eta*(MinIf$(Electron_pt,{0})<MinIf$(Muon_pt,{0}))".format(selString(index=None,ptCut=0)) 

else:   
    raise ValueError( "Mode %s not known" % args.mode )

selection_string    = "&&".join( str_ for str_ in [\
        'Sum$('+selString(ptCut=0,index=None)+')==2' if args.mode in ['doubleMu', 'doubleEle'] 
                else 'Sum$('+muonSelectorString(ptCut=0,index=None)+')==1&&Sum$('+eleSelectorString(ptCut=0,index=None)+')==1',   
        baseTrigger,
        args.selection
    ] if str_ )

plot_string_pt1      = dileptonTrigger+":%s>>eff_pt1"%leadingStringPt
plot_string_pt2      = dileptonTrigger+":%s>>eff_pt2"%subLeadingStringPt

print
print plot_string_pt1
print
print plot_string_pt2

logger.info( "Plot string: %s" % plot_string_pt1 )
logger.info( "Selection:   %s" % selection_string )
 
data.chain.Draw(plot_string_pt1, selection_string, 'goff')
data.chain.Draw(plot_string_pt2, selection_string, 'goff')

data.chain.Draw("Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_jetId>0))>>ht", selection_string, 'goff')

plot_string_eta1     = dileptonTrigger+":%s>>eff_eta1"%leadingStringEta
selection_string_eta1 = selection_string+"&&(Muon_pt==%s||Electron_pt==%s)"%(leadingStringPt,leadingStringPt)
print
print selection_string_eta1
data.chain.Draw(plot_string_eta1, selection_string_eta1, 'goff') 

plot_string_eta2     = dileptonTrigger+":%s>>eff_eta2"%subLeadingStringEta
if args.mode == 'doubleEle':
    selection_string_eta2 = selection_string+"&&(Electron_pt==%s)"%(subLeadingStringPt)
elif args.mode == 'doubleMu':
    selection_string_eta2 = selection_string+"&&(Muon_pt==%s)"%(subLeadingStringPt)
else:
    selection_string_eta2 = selection_string+"&&(Muon_pt==%s||Electron_pt==%s)"%(subLeadingStringPt,subLeadingStringPt)
print
print selection_string_eta2
data.chain.Draw(plot_string_eta2, selection_string_eta2, 'goff') 

#raise NotImplementedError

plot_string_pt1_pt2    = dileptonTrigger+":%s:%s>>eff_pt1_pt2"%(subLeadingStringPt,leadingStringPt)
data.chain.Draw(plot_string_pt1_pt2, selection_string, 'goff')
plot_string_pt1_pt2_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_veryCoarse"%(subLeadingStringPt,leadingStringPt)
data.chain.Draw(plot_string_pt1_pt2_veryCoarse, selection_string, 'goff')

if args.mode=='muEle':
    # split high/low ETA wrt muon
    # nanoAOD get sub-leading lepton:
    # MinIf$(Muon_pt,%s)*(MinIf$(Muon_pt,%s)<MinIf$(Electron_pt,%s))+MinIf$(Electron_pt,%s)*(MinIf$(Electron_pt,%s)<MinIf$(Muon_pt,%s))
    plot_string_pt1_pt2_highEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_highEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
    data.chain.Draw(plot_string_pt1_pt2_highEta1_veryCoarse, selection_string+"&&Sum$(abs(Muon_eta)>1.5&&"+selString(index=None,ptCut=0)+')==1', 'goff')

    plot_string_pt1_pt2_lowEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_lowEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
    data.chain.Draw(plot_string_pt1_pt2_lowEta1_veryCoarse, selection_string+"&&Sum$(abs(Muon_eta)<=1.5&&"+selString(index=None,ptCut=0)+')==1', 'goff')
else:
    # split high/low ETA wrt leading lepton
    if args.mode == 'doubleMu':
        plot_string_pt1_pt2_highEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_highEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
        data.chain.Draw(plot_string_pt1_pt2_highEta1_veryCoarse, selection_string+"&&Sum$(abs(Muon_eta)>1.5&&Muon_pt==%s)==1"%(leadingStringPt), 'goff')
    
        plot_string_pt1_pt2_lowEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_lowEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
        data.chain.Draw(plot_string_pt1_pt2_lowEta1_veryCoarse, selection_string+"&&Sum$(abs(Muon_eta)<=1.5&&Muon_pt==%s)==1"%(leadingStringPt), 'goff')
    elif args.mode == 'doubleEle':
        plot_string_pt1_pt2_highEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_highEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
        data.chain.Draw(plot_string_pt1_pt2_highEta1_veryCoarse, selection_string+"&&Sum$(abs(Electron_eta)>1.5&&Electron_pt==%s)==1"%(leadingStringPt), 'goff')
    
        plot_string_pt1_pt2_lowEta1_veryCoarse    = dileptonTrigger+":%s:%s>>eff_pt1_pt2_lowEta1_veryCoarse"%(subLeadingStringPt,leadingStringPt)
        data.chain.Draw(plot_string_pt1_pt2_lowEta1_veryCoarse, selection_string+"&&Sum$(abs(Electron_eta)<=1.5&&Electron_pt==%s)==1"%(leadingStringPt), 'goff')

plot_string_pt1_eta1   = dileptonTrigger+":%s:%s>>eff_pt1_eta1"%(leadingStringEta, leadingStringPt)
data.chain.Draw(plot_string_pt1_eta1, selection_string+"&&(Muon_pt==%s||Electron_pt==%s)"%(leadingStringPt,leadingStringPt), 'goff')

plot_string_pt2_eta2   = dileptonTrigger+":%s:%s>>eff_pt2_eta2"%(subLeadingStringEta, subLeadingStringPt)
data.chain.Draw(plot_string_pt2_eta2, selection_string+"&&(Muon_pt==%s||Electron_pt==%s)"%(subLeadingStringPt,subLeadingStringPt), 'goff')


prefix = preprefix+"_%s_%s_measuredIn%s_minLeadLepPt%i" % ( triggerName, 'baseTrigger_METhadronic', args.sample, args.minLeadingLeptonPt)
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
        #plot.Draw("COLZTextE")
        plot.Draw("COLZText")
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
