from optparse import OptionParser
parser = OptionParser()
parser.add_option("--plot", dest="plot", default="miniRelIso", type="string", action="store", help="which plot")
parser.add_option("--channel", dest="channel", default="mu", type="string", action="store", help="ele or mu?")
parser.add_option("--small", dest="small", default = False, action="store_true", help="small?")

(opts, args) = parser.parse_args()

import ROOT
ROOT.TH1F().SetDefaultSumw2()
from array import array
from math import cos,sin,sqrt,cosh,pi
import os, copy, sys
import itertools

from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_0l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, mZ#, getChain
from StopsDilepton.tools.user import plotDir
from StopsDilepton.plots.simplePlotHelpers import plot, stack, loopAndFill, drawNMStacks

puReweighting = None

cutBranches = ["weight", "leptonPt", "met*", "nVert",'run',\
                              'Jet_pt', "Jet_id", "Jet_eta", "Jet_phi", "Jet_btagCSV",
                              "LepGood_*",
                              "Flag_HBHENoiseFilter", "Flag_HBHENoiseIsoFilter", "Flag_goodVertices", "Flag_CSCTightHaloFilter", "Flag_eeBadScFilter",
                              "HLT_mumuIso", "HLT_ee_DZ", "HLT_mue",
#               "is*","dl_*","l1_*","l2_*"#, "nGoodMuons", "nGoodElectrons"
                                ]

subdir = "png25ns_2l_mAODv2_mcTrig_draw"
preprefixes = [] if not opts.small else ['small']
maxN = 1 if opts.small else -1

filterCut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"

cuts=[
  ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
  ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"),
# ("mll20", "dl_mass>20"),
  ("met50", "met_pt>50"),
# ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
# ("dPhiJet0-dPhiJet1", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
    ]


def getEleCut(remove=[]):
    eleCuts=[
    ("pt", "LepGood_pt>=20"),
    ("eta", "abs(LepGood_eta)<2.4"),
    ("mvaIdSpring15", "(abs(LepGood_eta)<0.8 && LepGood_mvaIdSpring15<0.87 || abs(LepGood_eta)<1.479 && LepGood_mvaIdSpring15<0.6 || abs(LepGood_eta)>1.57 && LepGood_mvaIdSpring15<0.17)"),
    ("miniRelIso", "LepGood_miniRelIso<0.2"),
    ("convVeto", "LepGood_convVeto"),
    ("lostHits", "LepGood_lostHits==0"),
    ("sip3d", "LepGood_sip3d < 4.0"),
    ("dxy", "abs(LepGood_dxy) < 0.05"),
    ("dz", "abs(LepGood_dz) < 0.1"),
    ]
    for r in remove:
        assert r in [e[0] for e in eleCuts], "Don't know how to remove cut %s"%r
    return "&&".join(["abs(LepGood_pdgId)==11"]+[c[1] for c in eleCuts if c[0] not in remove])

def getMuCut(remove=[]):
    muCuts=[
    ("pt", "LepGood_pt>=20"),
    ("eta", "abs(LepGood_eta)<2.4"),
    ("miniRelIso", "LepGood_miniRelIso<0.2"),
    ("convVeto", "LepGood_convVeto"),
    ("mediumMuonId", "LepGood_mediumMuonId"),
    ("lostHits", "LepGood_lostHits==0"),
    ("sip3d", "LepGood_sip3d < 4.0"),
    ("dxy", "abs(LepGood_dxy) < 0.05"),
    ("dz", "abs(LepGood_dz) < 0.1"),
    ]
    for r in remove:
        assert r in [e[0] for e in muCuts], "Don't know how to remove cut %s"%r
    return "&&".join(["abs(LepGood_pdgId)==13"]+[c[1] for c in muCuts if c[0] not in remove])

prefix = '_'.join(preprefixes+['-'.join([p[0] for p in cuts])])
preselCuts = [p[1] for p in cuts]

cutStringEle = "&&".join( preselCuts )
cutStringMu =  "&&".join( preselCuts )
ratioOps = None

def getStack(labels, var, binning, cut, options={}, qcdSample=None):

#      style_Data         = {'legendText':dataSample['name'],      'style':"e", 'lineThickness':0, 'errorBars':True, 'color':ROOT.kBlack, 'markerStyle':20, 'markerSize':1}
#  tyle_WJets        = {'legendText':'W + Jets',         'style':"l", 'lineThickness':0, 'errorBars':False, 'color':42, 'markerStyle':None, 'markerSize':None}
    style_TTJets       = {'legendText':'t#bar{t} + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':7, 'markerStyle':None, 'markerSize':None}
    style_DY           = {'legendText':'DY + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False,       'color':8, 'markerStyle':None, 'markerSize':None}
#  style_TTX          = {'legendText':'t#bar{t} + W/Z/H',  'style':"l", 'linethickNess':0, 'errorBars':False, 'color':ROOT.kYellow+2, 'markerStyle':None, 'markerSize':None}
    style_diBoson         = {'legendText':'WW/WZ/ZZ',  'style':"l", 'linethickNess':2, 'errorBars':False, 'color':ROOT.kGreen-5, 'markerStyle':None, 'markerSize':None}
    style_QCD          = {'legendText':'QCD',  'style':"l", 'linethickNess':2, 'errorBars':False,             'color':46, 'markerStyle':None, 'markerSize':None}
    style_singleTop    = {'legendText':'single top',  'style':"l", 'linethickNess':2, 'errorBars':False,      'color':40, 'markerStyle':None, 'markerSize':None}

#      data               = plot(var, binning, cut, sample=dataSample,       style=style_Data, weightString="weight")
    MC_TTJets          = plot(var, binning, cut, sample=TTJets,       style=style_TTJets,    weightString="weight", weightFunc=puReweighting)
#  MC_WJetsToLNu      = plot(var, binning, cut, sample=WJetsToLNu,   style=style_WJets,     weightString="weight", weightFunc=puReweighting)
    MC_DY              = plot(var, binning, cut, sample=DY,           style=style_DY,        weightString="weight", weightFunc=puReweighting)
    MC_singleTop       = plot(var, binning, cut, sample=singleTop,    style=style_singleTop, weightString="weight", weightFunc=puReweighting)
    MC_QCD             = plot(var, binning, cut, sample=qcdSample,        style=style_QCD,       weightString="weight", weightFunc=puReweighting)
#  MC_TTX             = plot(var, binning, cut, sample=TTX,          style=style_TTX, weightString="weight", weightFunc=puReweighting)
#  MC_diBoson         = plot(var, binning, cut, sample=diBoson,     style=style_diBoson, weightString="weight", weightFunc=puReweighting)
    #FIXME triBoson
#      mcStack = [MC_TTJets, MC_DY,  MC_QCD, MC_singleTop, MC_WJetsToLNu, MC_diBoson, MC_TTX]
#  mcStack = [MC_TTJets, MC_DY,  MC_QCD, MC_singleTop, MC_WJetsToLNu]

    ewk = [MC_TTJets, MC_DY]
    qcd = [ MC_QCD]
    MC_QCD.normalizeTo=ewk[0]

    plotLists = [ ewk, qcd]  #, MC_singleTop]
#      for s in mcStack:
#        s.sample['scale'] = lumiScaleFac*scaleFac


    for pL in plotLists:
        for p in pL:
            p.sample['small']=opts.small

    opt = {'small':opts.small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':ratioOps, 'fileName':var['name']}
#  opt = {'small':small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':None, 'fileName':var['name']}

    if opt.has_key('ratio') and opt['ratio']:
        opt['texLines'] = [{'pos':(0.15, 0.95),'text':'CMS Preliminary', 'options':{'size':0.052}},
#                           {'pos':(0.47, 0.95), 'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV) Scale %3.2f'%scaleFac, 'options':{'size':0.052}}
        ]
        opt['legend'] = {'coordinates':[0.55,0.90 - (len(ewk)+len(qcd))*0.05,.98,.93],'boxed':True}
    else:
        opt['texLines'] = [{'pos':(0.16, 0.965), 'text':'CMS Preliminary',       'options':{'size':0.038}},
#                           {'pos':(0.47, 0.965),  'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV) Scale %3.2f'%scaleFac,'options':{'size':0.038}}
        ]
        opt['legend'] = {'coordinates':[0.55,0.90 - (len(ewk)+len(qcd))*0.05,.98,.95],'boxed':True}

    opt.update(options)
    res = stack(plotLists, options = opt)
    res.usedBranches = cutBranches
    return res

allStacks=[]
if opts.channel.lower()=='mu':
    if opts.plot=='miniReliso':
        mu_miniRelIso_stack  = getStack(
                labels={'x':'miniRelIso (mu)','y':'Number of Events'},
                var={'name':'LepGood_miniRelIso_mu','string':"LepGood_miniRelIso", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,0.4]},
                cut={'string':cutStringMu+"&&"+getMuCut(["miniRelIso"])},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_miniRelIso_stack)

    if opts.plot=='dxy':
        mu_dxy_stack  = getStack(
                labels={'x':'dxy (mu)','y':'Number of Events'},
                var={'name':'LepGood_dxy_mu','string':"abs(LepGood_dxy)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.042]},
                cut={'string':cutStringMu+"&&"+getMuCut(["dxy"])},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_dxy_stack)

    if opts.plot=='dz':
        mu_dz_stack  = getStack(
                labels={'x':'dz (mu)','y':'Number of Events'},
                var={'name':'LepGood_dz_mu','string':"abs(LepGood_dz)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.42/3]},
                cut={'string':cutStringMu+"&&"+getMuCut(["dz"])},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_dz_stack)

    if opts.plot=='ip3d':
        mu_ip3d_stack  = getStack(
                labels={'x':'ip3d (mu)','y':'Number of Events'},
                var={'name':'LepGood_ip3d_mu','string':"LepGood_ip3d", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.42]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_ip3d_stack)

    if opts.plot=='sip3d':
        mu_sip3d_stack  = getStack(
                labels={'x':'sip3d (mu)','y':'Number of Events'},
                var={'name':'LepGood_sip3d_mu','string':"LepGood_sip3d", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,4.2]},
                cut={'string':cutStringMu+"&&"+getMuCut(["sip3d"])},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_sip3d_stack)

    if opts.plot=='relIso03':
        mu_relIso03_stack  = getStack(
                labels={'x':'relIso03 (mu)','y':'Number of Events'},
                var={'name':'LepGood_relIso03_mu','string':"LepGood_relIso03", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,0.4]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_relIso03_stack)

    if opts.plot=='relIso04':
        mu_relIso04_stack  = getStack(
                labels={'x':'relIso04 (mu)','y':'Number of Events'},
                var={'name':'LepGood_relIso04_mu','string':"LepGood_relIso04", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,0.4]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_relIso04_stack)

    if opts.plot=='jetPtRatiov1':
        mu_jetPtRatiov1_stack  = getStack(
                labels={'x':'jetPtRatiov1 (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRatiov1_mu','string':"LepGood_jetPtRatiov1", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,1]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetPtRatiov1_stack)

    if opts.plot=='jetPtRelv1':
        mu_jetPtRelv1_stack  = getStack(
                labels={'x':'jetPtRelv1 (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRelv1_mu','string':"LepGood_jetPtRelv1", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,40]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetPtRelv1_stack)

    if opts.plot=='jetPtRelv2':
        mu_jetPtRelv2_stack  = getStack(
                labels={'x':'jetPtRelv2 (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRelv2_mu','string':"LepGood_jetPtRelv2", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,40]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetPtRelv2_stack)

    if opts.plot=='jetPtRatiov2':
        mu_jetPtRatiov2_stack  = getStack(
                labels={'x':'jetPtRatiov2 (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRatiov2_mu','string':"LepGood_jetPtRatiov2", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,1]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetPtRatiov2_stack)

    if opts.plot=='jetBTagCSV':
        mu_jetBTagCSV_stack  = getStack(
                labels={'x':'jetBTagCSV (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetBTagCSV_mu','string':"LepGood_jetBTagCSV", 'overFlow':'both', 'branches':[]},
                binning={'binning':[40,-1,1]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetBTagCSV_stack)

    if opts.plot=='jetDR':
        mu_jetDR_stack  = getStack(
                labels={'x':'jetDR (mu)','y':'Number of Events'},
                var={'name':'LepGood_jetDR_mu','string':"LepGood_jetDR", 'overFlow':'both', 'branches':[]},
                binning={'binning':[42,0,0.42]},
                cut={'string':cutStringMu+"&&"+getMuCut()},
                qcdSample=QCD_Mu5
                )
        allStacks.append(mu_jetDR_stack)

if opts.channel.lower()=='ele':
    if opts.plot=='miniReliso':
        ele_miniRelIso_stack  = getStack(
            labels={'x':'miniRelIso (ele)','y':'Number of Events'},
            var={'name':'LepGood_miniRelIso_ele','string':"LepGood_miniRelIso", 'overFlow':'upper', 'branches':[]},
            binning={'binning':[40,0,0.4]},
            cut={'string':cutStringEle+"&&"+getEleCut(["miniRelIso"])},
            qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_miniRelIso_stack)

    if opts.plot=='dxy':
        ele_dxy_stack  = getStack(
                labels={'x':'dxy (ele)','y':'Number of Events'},
                var={'name':'LepGood_dxy_ele','string':"abs(LepGood_dxy)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.042]},
                cut={'string':cutStringEle+"&&"+getEleCut(["dxy"])},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_dxy_stack)

    if opts.plot=='dz':
        ele_dz_stack  = getStack(
                labels={'x':'dz (ele)','y':'Number of Events'},
                var={'name':'LepGood_dz_ele','string':"abs(LepGood_dz)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.42/3]},
                cut={'string':cutStringEle+"&&"+getEleCut(["dz"])},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_dz_stack)

    if opts.plot=='ip3d':
        ele_ip3d_stack  = getStack(
                labels={'x':'ip3d (ele)','y':'Number of Events'},
                var={'name':'LepGood_ip3d_ele','string':"abs(LepGood_ip3d)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,0.42]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_ip3d_stack)

    if opts.plot=='sip3d':
        ele_sip3d_stack  = getStack(
                labels={'x':'sip3d (ele)','y':'Number of Events'},
                var={'name':'LepGood_sip3d_ele','string':"abs(LepGood_sip3d)", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[42,0,4.2]},
                cut={'string':cutStringEle+"&&"+getEleCut(["sip3d"])},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_sip3d_stack)

    if opts.plot=='convVeto':
        ele_convVeto_stack  = getStack(
                labels={'x':'convVeto (ele)','y':'Number of Events'},
                var={'name':'LepGood_convVeto_ele','string':"LepGood_convVeto", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[2,0,2]},
                cut={'string':cutStringEle+"&&"+getEleCut(["convVeto"])},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_convVeto_stack)

    if opts.plot=='relIso03':
        ele_relIso03_stack  = getStack(
                labels={'x':'relIso03 (ele)','y':'Number of Events'},
                var={'name':'LepGood_relIso03_ele','string':"LepGood_relIso03", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,0.4]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_relIso03_stack)

    if opts.plot=='relIso04':
        ele_relIso04_stack  = getStack(
                labels={'x':'relIso04 (ele)','y':'Number of Events'},
                var={'name':'LepGood_relIso04_ele','string':"LepGood_relIso04", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,0.4]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_relIso04_stack)

    if opts.plot=='mvaIdSpring15':
        ele_mvaIdSpring15_stack  = getStack(
                labels={'x':'mvaIdSpring15 (ele)','y':'Number of Events'},
                var={'name':'LepGood_mvaIdSpring15_ele','string':"LepGood_mvaIdSpring15", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,-1,1]},
                cut={'string':cutStringEle+"&&"+getEleCut(["mvaIdSpring15"])},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_mvaIdSpring15_stack)

    if opts.plot=='jetPtRatiov1':
        ele_jetPtRatiov1_stack  = getStack(
                labels={'x':'jetPtRatiov1 (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRatiov1_ele','string':"LepGood_jetPtRatiov1", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,1]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetPtRatiov1_stack)

    if opts.plot=='jetPtRelv1':
        ele_jetPtRelv1_stack  = getStack(
                labels={'x':'jetPtRelv1 (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRelv1_ele','string':"LepGood_jetPtRelv1", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,40]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetPtRelv1_stack)

    if opts.plot=='jetPtRelv2':
        ele_jetPtRelv2_stack  = getStack(
                labels={'x':'jetPtRelv2 (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRelv2_ele','string':"LepGood_jetPtRelv2", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,40]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetPtRelv2_stack)

    if opts.plot=='jetPtRatiov2':
        ele_jetPtRatiov2_stack  = getStack(
                labels={'x':'jetPtRatiov2 (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetPtRatiov2_ele','string':"LepGood_jetPtRatiov2", 'overFlow':'upper', 'branches':[]},
                binning={'binning':[40,0,1]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetPtRatiov2_stack)

    if opts.plot=='jetBTagCSV':
        ele_jetBTagCSV_stack  = getStack(
                labels={'x':'jetBTagCSV (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetBTagCSV_ele','string':"LepGood_jetBTagCSV", 'overFlow':'both', 'branches':[]},
                binning={'binning':[40,-1,1]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetBTagCSV_stack)

    if opts.plot=='jetDR':
        ele_jetDR_stack  = getStack(
                labels={'x':'jetDR (ele)','y':'Number of Events'},
                var={'name':'LepGood_jetDR_ele','string':"LepGood_jetDR", 'overFlow':'both', 'branches':[]},
                binning={'binning':[42,0,0.42]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_jetDR_stack)

    if opts.plot=='lostHits':
        ele_lostHits_stack  = getStack(
                labels={'x':'lostHits (ele)','y':'Number of Events'},
                var={'name':'LepGood_lostHits_ele','string':"LepGood_lostHits", 'overFlow':'both', 'branches':[]},
                binning={'binning':[5,0,5]},
                cut={'string':cutStringEle+"&&"+getEleCut()},
                qcdSample=QCD_EMbcToE
                )
        allStacks.append(ele_lostHits_stack)

if len(allStacks)==0:
    print "Don't know what to do with channel: %s and plot: %s"%(opts.channel, opts.plot)

loopAndFill(allStacks, mode='draw')

path = '/'.join([plotDir, subdir, prefix])
print "path",path
if not os.path.exists(path): os.makedirs(path)
stuff=[]
for stk in allStacks:
    stuff.append(drawNMStacks(1,1,[stk], path=path, filename=stk.options['fileName']))

