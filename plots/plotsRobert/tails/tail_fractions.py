
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools
import copy
import array
import operator

from math                                import sqrt, cos, sin, pi, atan2, cosh
from RootTools.core.standard             import *

from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, deltaR, add_histos, getVarValue, getObjDict, getCollection
from StopsDilepton.tools.objectSelection import getJets 
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator

from Analysis.Tools.metFilters            import getFilterCut
from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                 action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--dpm',                                   action='store_true',     help='Use dpm?', )
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

## Load from DPM?
#if args.dpm:
#    data_directory = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"
#
#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
#from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
#from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
#

TTLep_pow_16 = Sample.fromFiles("TTLep_pow_16", "/afs/hephy.at/data/cms07/nanoTuples/skim/TTLep_pow_16_mt2ll100.root") 
TTLep_pow_17 = Sample.fromFiles("TTLep_pow_17", "/afs/hephy.at/data/cms07/nanoTuples/skim/TTLep_pow_17_mt2ll100.root")
TTLep_pow_18 = Sample.fromFiles("TTLep_pow_18", "/afs/hephy.at/data/cms07/nanoTuples/skim/TTLep_pow_18_mt2ll100.root")

mc = [ TTLep_pow_16, TTLep_pow_17, TTLep_pow_18 ]

weights = [ "weight", "reweightL1Prefire", "reweightDilepTrigger", "reweightLeptonSF", "reweightBTag_SF"]
TTLep_pow_16.setWeightString( "*".join( weights + ["reweightPU"] ))
TTLep_pow_17.setWeightString( "*".join( weights + ["reweightPU"] ))
TTLep_pow_18.setWeightString( "*".join( weights + ["reweightPUVUp"] ))

for sample in mc:
    sample.scale = 137 

if args.small:
    for sample in mc: 
        sample.reduceFiles( to=1 )

#TTLep_pow_comb = Sample.combine( "TTLep_pow_comb", [TTLep_pow_16, TTLep_pow_17, TTLep_pow_18] )
#TTLep_pow_comb.setWeightString("*".join( weights + ["reweightPU"]))

# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" #if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

selections = [
    "lepSel-POGMetSig12-njet2p-btag1p-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
    "lepSel-badEEJetVeto-POGMetSig12-njet2p-btag1p-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
    "lepSel-POGMetSig12-njet2p-btag1p-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1",
    ]

read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "RawMET_pt/F", "RawMET_phi/F"]
read_variables += ["l2_eleIndex/I"]
read_variables += ["l1_genPartFlav/B", "l2_genPartFlav/B"]
read_variables+= ["event/l", "luminosityBlock/I", "run/I"]

jetVars         = ['pt/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F', 'rawFactor/F', 'eta/F', 'phi/F', 'jetId/I', 'btagDeepB/F', 'btagCSVV2/F', 'area/F', 'pt_nom/F', 'corr_JER/F', 'genJetIdx/I'] 
jetVarNames     = map( lambda s:s.split('/')[0], jetVars)
read_variables += [\
    TreeVariable.fromString('nElectron/I'),
    VectorTreeVariable.fromString('Electron[pt/F,eta/F,phi/F,pdgId/I,cutBased/I,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,lostHits/b,convVeto/O,dxy/F,dz/F,charge/I,deltaEtaSC/F]'),
    TreeVariable.fromString('nMuon/I'),
    VectorTreeVariable.fromString('Muon[pt/F,eta/F,phi/F,pdgId/I,mediumId/O,miniPFRelIso_all/F,pfRelIso03_all/F,sip3d/F,dxy/F,dz/F,charge/I]'),
    TreeVariable.fromString('nJet/I'),
    VectorTreeVariable.fromString('Jet[%s]'% ( ','.join(jetVars) ) ),
    TreeVariable.fromString('nGenJet/I'),
    VectorTreeVariable.fromString('GenJet[pt/F,eta/F,phi/F]' ),
]


mt2llBins = [ 'mt2ll100' ]#, 'mt2ll240', 'mt2ll100To140' ]
for selection, sample in zip(selections, mc):
    print sample.name, selection
    for mt2llBin in mt2llBins:
        #for selection, sample in zip(selections, mc):


        sample.setSelectionString( cutInterpreter.cutString( selection + '-' + mt2llBin ) + "&&" + getLeptonSelection("all") )

        r = sample.treeReader( variables = map( lambda v: TreeVariable.fromString(v) if type(v)==type("") else v, read_variables ) )
        r.start()

        while r.run():
            # all nanoAOD objects
            genjets = getCollection( r.event, "GenJet", ["pt", "eta", "phi"], "nGenJet")
            jets = getJets(r.event, jetVars = jetVarNames)

            # analysis leptons
            l1 = {'pt':r.event.l1_pt, 'eta':r.event.l1_eta, 'phi':r.event.l1_phi}
            l2 = {'pt':r.event.l2_pt, 'eta':r.event.l2_eta, 'phi':r.event.l2_phi}

            # jets satisying Id and not in vicinity of analysis leptons
            all_good_jets = filter( lambda j: j['jetId'] and deltaR(j, l1)>0.2 and deltaR(j, l2)>0.2, jets) 

            # find non-gaussian mismeasurement
            delta_pts = [ abs(jet['pt'] - genjets[jet['genJetIdx']]['pt']) if jet['genJetIdx']>=0 and (jet['genJetIdx']<r.event.nGenJet) else 0 for jet in all_good_jets ]
            #delta_Rs  = [ deltaR(jet, genjets[jet['genJetIdx']]) if jet['genJetIdx']>=0 and (jet['genJetIdx']<r.event.nGenJet) else 0 for jet in all_good_jets ]
            #print zip(delta_Rs, delta_pts)

            nonGauss_30 = max( delta_pts+[0] )>30
            nonGauss_40 = max( delta_pts+[0] )>40

            # Gaussian mism 
            delta_x = [ (jet['pt'] - genjets[jet['genJetIdx']]['pt'])*cos(jet['phi']) if jet['genJetIdx']>=0 and (jet['genJetIdx']<r.event.nGenJet) else 0 for jet in all_good_jets ]
            delta_y = [ (jet['pt'] - genjets[jet['genJetIdx']]['pt'])*sin(jet['phi']) if jet['genJetIdx']>=0 and (jet['genJetIdx']<r.event.nGenJet) else 0 for jet in all_good_jets ]



            #print sum(delta_x), sum(delta_y)
            delta_mht = sqrt(sum( delta_x )**2 + sum( delta_y )**2)

            delta_mht_30 = delta_mht>30
            delta_mht_40 = delta_mht>40

            if nonGauss_30:
                print "nonGauss_30"
            elif delta_mht_30:
                print "delta_mht_30"
            elif ord(r.event.l1_genPartFlav)!=1 or ord(r.event.l2_genPartFlav)!=1:
                print "leptons"
            else:
                print "unclassified!"
             
#contributions = [
#    # 1 jet mism > 40 GeV (NonGauss) 
#    ('NonGauss', {'ee': 'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)>=1', 'mumu':'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)>=1'}),
#
#    # total jet mism > 40 GeV (Gauss)
#    ('Gauss', {'ee': 'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))>=40', 'mumu':'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))>=40'}),
#     
#    # no MET mismeasurement and matched leptons 
#    ('other', {'mumu':'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))<40&&((l1_muIndex>=0&&(Muon_genPartFlav[l1_muIndex])!=1)||(l2_muIndex>=0&&(Muon_genPartFlav[l2_muIndex])!=1))', 
#                 'ee':'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))<40&&((l1_muIndex>=0&&(Electron_genPartFlav[l1_muIndex])!=1)||(l2_muIndex>=0&&(Electron_genPartFlav[l2_muIndex])!=1))'}),
#       
#    # other (mism leptons) 
#    ('lepMism', {'mumu': 'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))<40&&(!((l1_muIndex>=0&&(Muon_genPartFlav[l1_muIndex])!=1)||(l2_muIndex>=0&&(Muon_genPartFlav[l2_muIndex])!=1)))',
#                  'ee': 'Sum$(abs(JetGood_pt-JetGood_genPt)>=40)==0&&Sum$(abs(JetGood_pt-JetGood_genPt))<40&&(!((l1_muIndex>=0&&(Electron_genPartFlav[l1_muIndex])!=1)||(l2_muIndex>=0&&(Electron_genPartFlav[l2_muIndex])!=1)))'})
#]

#mt2llBins = [ 'mt2ll100' ]#, 'mt2ll240', 'mt2ll100To140' ]
#
#
#for selection, sample in zip(selections, mc):
#    for mt2llBin in mt2llBins:
#        #for selection, sample in zip(selections, mc):
#        sample.setSelectionString( cutInterpreter.cutString( selection + '-' + mt2llBin ) )
#
#        for name, cont in contributions:
#            y_mumu = sample.getYieldFromDraw( cont['mumu'] + "&&" + getLeptonSelection( 'mumu' ) )['val']
#            y_ee = sample.getYieldFromDraw( cont['ee'] + "&&" + getLeptonSelection( 'ee' ) )['val']
#
#            print sample.name, mt2llBin, name, 'mumu', y_mumu, 'ee', y_ee, 'tot', y_mumu + y_ee 
#        
