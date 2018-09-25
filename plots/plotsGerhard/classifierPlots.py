'''
Load Keras Models and create nice roc plots
'''
import ROOT
import pandas as pd
import os
from array import array
import ctypes

#from StopsDilepton.MVA.default_classifier import training_variables_list, get_dict
from StopsDilepton.MVA.default_classifier_lep_pt import training_variables_list as training_variables_list_lep_pt
from StopsDilepton.MVA.default_classifier import training_variables_list, get_dict

# define KerasReader
from StopsDilepton.MVA.KerasReader import KerasReader
from StopsDilepton.tools.user import  MVA_model_directory

# define models to print
paths = []
names = []
colorList=[]
lineWidthList=[]

# choose channel
#channel = 'TTZ'
#channel = 'T8bbllnunu005'
#channel = 'T8bbllnunu05'
channel = "T8bbllnunu095"


if channel=='TTZ':
    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-12-1437'))
    names.append('0x0')
    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1134'))
    names.append('1x100/DO:0.3')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1123'))
#    names.append('1x50, dropout 0.2')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-12-1524'))
#    names.append('1x100, dropout 0.2')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-12-1542'))
#    names.append('1x100, dropout 0.4')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-12-1642'))
#    names.append('1x200, dropout 0.5')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-12-1608'))
#    names.append('2x100, dropout 0.3')
#    paths.append( os.path.join( MVA_model_directory , 'T2tt_dM350-TTZtoLLNuNu/v1_lep_pt_10/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1206'))
#    names.append('1x100, dropout 0.3, Adagrad')
    
    
if channel=='T8bbllnunu005':
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p05_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1630'))
    names.append('0x0')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p05_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1639'))
    names.append('2x50       ')
    
if channel=='T8bbllnunu05':
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p5_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1516'))
    names.append('0x0')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p5_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1555'))
    names.append('2x50')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1031'))
    names.append('0x0, comp.')
#    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1626'))
#    names.append('2x50')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1511'))
    names.append('4x100/DO:0.2, comp.')
    
if channel=='T8bbllnunu095':
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p95_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1521'))
    names.append('0x0')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p95_dM350-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1626'))
    names.append('1x50')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1520'))
    names.append('0x0, comp.')
    paths.append( os.path.join( MVA_model_directory , 'T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller-TTLep_pow/v1_lep_pt/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/2018-09-13-1631'))
    names.append('2x50, comp.    ')

colorList.append(ROOT.kBlue-3 )
colorList.append(ROOT.kMagenta-3 )
#colorList.append(ROOT.kBlue+1 )
colorList.append(ROOT.kCyan+1 )
colorList.append(ROOT.kGreen+1 )

lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)
lineWidthList.append(1)

# information
#

logY = 0

#
# roc
#

pl_roc = ROOT.TCanvas()
if logY: pl_roc.SetLogy()
mg_roc = ROOT.TMultiGraph()
g_roc=[]

for i,path in enumerate(paths):
    tmpfilepath = os.path.join( path, 'validation.h5')
    fpr = pd.read_hdf( tmpfilepath ,key='roc')['fpr'].values
    tpr = pd.read_hdf( tmpfilepath ,key='roc')['tpr'].values
    thresholds = pd.read_hdf( tmpfilepath ,key='roc')['thresholds'].values
    
    g_roc.append( ROOT.TGraph( len(tpr) , array('d',tpr), array('d', 1-fpr) ))
    g_roc[-1].SetName( names[i] )
    g_roc[-1].SetTitle( names[i] )
    g_roc[-1].SetLineColor( colorList[i] )
    g_roc[-1].SetLineWidth( lineWidthList[i] )
    g_roc[-1].SetMarkerColor(colorList[i])
   #g_roc[-1].SetMarkerStyle( 5 )
    g_roc[-1].SetFillStyle(0)
    g_roc[-1].SetFillColor(0)
    g_roc[-1].SetMarkerSize(0)
    g_roc[-1].Draw("AL*")
    mg_roc.Add(g_roc[-1])

mg_roc.Draw("AL*")
mg_roc.SetTitle('Roc Auc')
mg_roc.GetXaxis().SetTitle('signal efficiency')
mg_roc.GetXaxis().SetLimits(0.0, 1.0 )
mg_roc.GetYaxis().SetTitle('backround rejection')
mg_roc.GetYaxis().SetRangeUser(0.0009, 1.01) if logY else mg_roc.GetYaxis().SetLimits(0.0, 1.0)
pl_roc.BuildLegend(0.12,0.90,0.5,0.7, ctypes.c_char(channel)) if logY else pl_roc.BuildLegend()
if channel=='TTZ':
    pl_roc.Print('/afs/hephy.at/user/g/gungersback/www/stopsDilepton/Classifier/TTZ_roc.png')
if channel=='T8bbllnunu005':
    pl_roc.Print('/afs/hephy.at/user/g/gungersback/www/stopsDilepton/Classifier/T8bbllnunu005_roc.png')
if channel=='T8bbllnunu05':
    pl_roc.Print('/afs/hephy.at/user/g/gungersback/www/stopsDilepton/Classifier/T8bbllnunu05_roc.png')
if channel=='T8bbllnunu095':
    pl_roc.Print('/afs/hephy.at/user/g/gungersback/www/stopsDilepton/Classifier/T8bbllnunu095_roc.png')

#
# acc plot
#

#pl_acc = ROOT.TCanvas()
#if logY: pl_acc.SetLogy()
#mg_acc = ROOT.TMultiGraph()
#g_acc=[]
#
#for i,path in enumerate(paths):
#    loss =pd.read_hdf( os.path.join( MVA_model_directory, path  ,'validation.h5'),key='loss').values
#    epochslist = range(1,len(loss)+1)
#    
#    g_acc.append( ROOT.TGraph( len(epochslist), array('d', epochslist), array('d', loss)) )
#    g_acc[-1].SetName( names[i] )
#    g_acc[-1].SetTitle( names[i] )
#    g_acc[-1].SetLineColor( colorList[i] )
#    g_acc[-1].SetLineWidth( lineWidthList[i] )
#    g_acc[-1].SetMarkerColor(colorList[i])
#   #g_acc[-1].SetMarkerStyle( 5 )
#    g_acc[-1].SetFillStyle(0)
#    g_acc[-1].SetFillColor(0)
#    g_acc[-1].SetMarkerSize(0)
#    g_acc[-1].Draw("C")
#    mg_acc.Add(g_acc[-1])
#
#mg_acc.Draw("AC")
#mg_acc.SetTitle('lossfunction')
#mg_acc.GetXaxis().SetTitle('epochs')
#mg_acc.GetXaxis().SetLimits(0, len(epochslist) )
#mg_acc.GetYaxis().SetTitle('loss')
#mg_acc.GetYaxis().SetRangeUser(0.0009, 1.01) if logY else mg_acc.GetYaxis().SetLimits(0.0, 1.0)
#pl_acc.BuildLegend(0.12,0.90,0.5,0.7) if logY else pl_acc.BuildLegend()
#pl_acc.Print('/afs/hephy.at/user/g/gungersback/www/test.png')

#
# acc plot
#

#pd.read_hdf('validation.h5',key='loss').values

#
# auc plot
#

#pd.read_hdf('validation.h5',key='auc')['aucs_train'].values
#pd.read_hdf('validation.h5',key='auc')['aucs_val'].values


