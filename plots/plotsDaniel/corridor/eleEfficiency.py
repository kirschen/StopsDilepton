import ROOT

from RootTools.core.standard import *

FullSim_T2tt_175_1 = Sample.fromDirectory("FullSim_T2tt_175_1", "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_175_mLSP_1/")
FastSim_T2tt_175_1 = Sample.fromDirectory("FastSim_T2tt_175_1", "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_175_0/")

FullSim_T2tt_250_50 = Sample.fromDirectory("FullSim_T2tt_250_50", "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_250_mLSP_50/")
FastSim_T2tt_250_50 = Sample.fromDirectory("FastSim_T2tt_250_50", "/afs/hephy.at/data/cms01/nanoTuples/stops_2018_nano_v0p19/inclusive/SMS_T2tt_mStop_150to250_250_50/")


## some functions

cuts_ele = ['Electron_pt>30','abs(Electron_eta)<2.4', 'Electron_cutBased>0', 'Electron_cutBased>1', 'Electron_cutBased>2', 'Electron_cutBased>3',\
             'Electron_miniPFRelIso_all<0.2','Electron_sip3d<4.','Electron_lostHits==0','Electron_convVeto>0','abs(Electron_dz)<0.1','abs(Electron_dxy)<0.05']

cuts_mu = ['Muon_pt>30', 'abs(Muon_eta)<2.4', 'Muon_mediumId>0', 'Muon_miniPFRelIso_all<0.2', 'Muon_sip3d<4.0', 'abs(Muon_dz)<0.1', 'abs(Muon_dxy)<0.05']

def getEfficiencies( sample, cuts ):
    print sample.name
    presel = '(1)'
    y = sample.getYieldFromDraw("Sum$(%s)>0"%presel, 'weight')
    yields = [y['val']]
    print '{:40}{:>10}{:>10}{:>10}'.format('cut', 'yield 1/fb', 'wrt prev', 'wrt entry')
    print '{:40}{:10.2f}{:10.3f}{:10.3f}'.format(presel, y['val'], y['val']/yields[-1], y['val']/yields[0])
    for c in cuts:
        presel += '&&%s'%c
        y = sample.getYieldFromDraw("Sum$(%s)>0"%presel, 'weight')
        print '{:40}{:10.2f}{:10.3f}{:10.3f}'.format(c, y['val'], y['val']/yields[-1], y['val']/yields[0])
        yields.append(y['val'])

cutFlowEle = [\
    'Sum$(Electron_pt>30&&abs(Electron_eta)<2.4&&Electron_cutBased>3&&Electron_miniPFRelIso_all<0.2&&Electron_sip3d<4&&Electron_lostHits==0&&Electron_convVeto>0&&abs(Electron_dz)<0.1&&abs(Electron_dxy)<0.05)>1',
    'Sum$(Electron_pt>30&&abs(Electron_eta)<2.4&&Electron_cutBased>3&&Electron_miniPFRelIso_all<0.2&&Electron_sip3d<4&&Electron_lostHits==0&&Electron_convVeto>0&&abs(Electron_dz)<0.1&&abs(Electron_dxy)<0.05)>1',
    'Sum$(Electron_pt>30&&abs(Electron_eta)<2.4&&Electron_cutBased>3&&Electron_miniPFRelIso_all<0.2&&Electron_sip3d<4&&Electron_lostHits==0&&Electron_convVeto>0&&abs(Electron_dz)<0.1&&abs(Electron_dxy)<0.05)>1',
]

cutFlowMu = [\
    ('2 mu',        'Sum$(Muon_pt>20&&abs(Muon_eta)<2.4&&Muon_mediumId>0&&Muon_miniPFRelIso_all<0.2&&Muon_sip3d<4.0&&abs(Muon_dz)<0.1&&abs(Muon_dxy)<0.05)>1'),
    ('pt_l1>30',    'Sum$(Muon_pt>30&&abs(Muon_eta)<2.4&&Muon_mediumId>0&&Muon_miniPFRelIso_all<0.2&&Muon_sip3d<4.0&&abs(Muon_dz)<0.1&&abs(Muon_dxy)<0.05)>0'),
    ('loose veto',  '(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_miniPFRelIso_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_miniPFRelIso_all<0.4) )==2'),
    ('S>12',        'MET_significance>12'),
]

cutFlowAnalysis = [\
    ('filters',     'Flag_goodVertices&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_ecalBadCalibFilter&&Flag_BadPFMuonFilter'),
    ('2l',          '(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0||isEE==1&&nGoodMuons==0&&nGoodElectrons==2||isEMu==1&&nGoodMuons==1&&nGoodElectrons==1)'),
    ('OS',          'isOS'),
    ('3l veto',     '(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2'),
    ('M(ll)>20',    'dl_mass>=20'),
    ('pT_(l2)>20',  'l2_pt>20'),
    ('pT_(l1)>30',  'l1_pt>30'),
    ('lepton iso',  'l1_miniRelIso<0.2&&l2_miniRelIso<0.2'),
    ('off-Z',       '(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1||(abs(dl_mass - 91.1876)>15&&(isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0||isEE==1&&nGoodMuons==0&&nGoodElectrons==2)))'),
    ('Nj>1',        'nJetGood>=2'),
    ('Nb>0',        'nBTag>=1'),
    ('S>12',        'MET_significance>=12'),
    ('dPhi(MET,j1)','cos(met_phi-JetGood_phi[0])<0.8'),
    ('dPhi(MET,j2)','cos(met_phi-JetGood_phi[1])<cos(0.25)'),
    ('MT2ll>100',   'dl_mt2ll>100'),
    #('MT2ll>140',   'dl_mt2ll>140'),
    #('MT2ll>240',   'dl_mt2ll>240'),
    #('fullSim filt','Flag_globalSuperTightHalo2016Filter&&Flag_ecalBadCalibFilterV2'),     
    #('fastSim filt','Flag_ecalBadCalibFilter'),
]

def getEfficienciesAlt( sample, cuts, entryPoint='(1)', weight='weight' ):
    print sample.name
    presel = entryPoint
    y = sample.getYieldFromDraw(presel, weight)
    yields = [y['val']]
    print '{:40}{:>22}{:>10}{:>10}'.format('cut', 'yield 1/fb', 'wrt prev', 'wrt entry')
    print '{:40}{:10.2f}{:5}{:<7.2f}{:10.3f}{:10.3f}'.format(presel, y['val'], ' +/- ', y['sigma'], y['val']/yields[-1], y['val']/yields[0])
    for c in cuts:
        presel += '&&%s'%c[1]
        y = sample.getYieldFromDraw(presel, weight)
        print '{:40}{:10.2f}{:5}{:<7.2f}{:10.3f}{:10.3f}'.format(c[0], y['val'], ' +/- ', y['sigma'], y['val']/yields[-1], y['val']/yields[0])
        yields.append(y['val'])




## use nanoAOD tool functionality

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor   import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel       import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop       import Module
from corridorTools import corridorTools

skim = "Sum$(abs(GenPart_pdgId)==11&&GenPart_pt>10&&GenPart_status==23&&abs(GenPart_eta)<2.4)==1"

sample = FastSim_T2tt_175_1
#sample = FullSim_T2tt_175_1

p = PostProcessor('.',sample.files,cut=skim, modules=[corridorTools()])


#sample.setSelectionString(oneGen)
#
### initialize reader
##reader = sample.treeReader(allBranchesActive=True, variables = variables )
#reader = sample.treeReader(allBranchesActive=True )
#reader.start()
#
#nEvents =  u_float(tmpSample.getYieldFromDraw())
#nPass = 0
#while reader.run():
#    ev = reader.event
#    if ev.Electron_pt

