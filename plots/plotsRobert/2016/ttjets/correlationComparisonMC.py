#Standard imports
import ROOT
import os

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
args = argParser.parse_args()

# RootTools
from RootTools.core.standard import *

# StopsDilepton
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

plot_directory += "/ttjets_correlation"

data_directory = "/afs/hephy.at/data/dspitzbart02/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v31/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *

#TTJets = Sample.fromDirectory( "TTJets", "/afs/hephy.at/data/dspitzbart02/cmgTuples/postProcessed_80X_v23/dilepTiny/TTJets", texName)

samples = [TTJets_Dilep, TTLep_pow]#, TTJets]

maxN = 1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)
if maxN != -1:
    plot_directory+="_small"

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string = 'weight*reweightDilepTriggerBackup*reweightLeptonSF'
lumiFac = 2.4

cuts=[
  ("opposite sign","isOS==1"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
    ]

iso_cuts   =  [("==2 relIso03<0.12 leptons", "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12"),
                  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
                ]
#iso_cuts =  [("==2 VT leptons (25/20)",    "nGoodMuons+nGoodElectrons==2&&l1_mIsoWP>=5&&l2_mIsoWP>=5&&l1_pt>25"),
#                  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
#                ]

#h_relIso   = Top_relIso.get1DHistoFromDraw( "dl_mt2ll", binning = [300/20,0,300], selectionString = "&&".join([c[1] for c in cuts + relIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
#h_relIso.style = styles.lineStyle( errors = True,  color = ROOT.kRed )
#h_relIso.legendText = "relIso03<0.12"

binning = [0,25,50,75,100,140,240,340]
mt2blbl_binning = [0,25,50,75,100,150,250]

for met_bin in [ (80, -1), (80,200), (200,-1)]:
    met_low, met_high = met_bin
    met_cuts = [("", "met_pt>"+str(met_low))]
    if met_high>0: met_cuts += [("", "met_pt<"+str(met_high))]

    # njet reweighting
    h_TTJets_Dilep_njets = TTJets_Dilep.get1DHistoFromDraw( "nJetGood", binning = [10,0,10], selectionString = "&&".join([c[1] for c in cuts + met_cuts + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
    h_TTLep_pow_njets = TTLep_pow.get1DHistoFromDraw( "nJetGood", binning = [10,0,10], selectionString = "&&".join([c[1] for c in cuts + met_cuts + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string)

    h_TTJets_Dilep_njets.Scale(1./h_TTJets_Dilep_njets.Integral())
    h_TTLep_pow_njets.Scale(1./h_TTLep_pow_njets.Integral())

    njet_rw = h_TTLep_pow_njets.Clone()
    njet_rw.Divide( h_TTJets_Dilep_njets )

    njet_mg_to_pow_reweight = "("+"+".join( [ "%3.3f*(nJetGood==%i)"%(njet_rw.GetBinContent(i+1), i) for i in range(2,10) ] + ["(nJetGood>=10)"] )+")"

    print "Using njet reweighting %s" % njet_mg_to_pow_reweight

    njet_rw.legendText = "n-jet reweight"
    plotting.draw(
        Plot.fromHisto("njet_reweighting_met_%i_%i"%(met_low, met_high),
            [ [ njet_rw ] ],
            texX = "jet multiplicity"
        ), 
        plot_directory = plot_directory, ratio = None, 
        logX = False, logY = False, sorting = False, 
        yRange = (0.003, "auto"), # xRange = (2,10), 
        # scaling = {1:0, 2:0},
        legend = "auto",
        #drawObjects = drawObjects( dataMCScale )
    )

    for prefix, reweight in [ ( "nominal", "(1)"), ("mg_to_pow", njet_mg_to_pow_reweight) ]:

        h_TTJets_Dilep = TTJets_Dilep.get1DHistoFromDraw( "dl_mt2ll", binning = binning, selectionString = "&&".join([c[1] for c in cuts + met_cuts + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string+"*"+reweight, binningIsExplicit = True)
        h_TTJets_Dilep.style = styles.lineStyle( errors = True,  color = ROOT.kRed )
        h_TTJets_Dilep.legendText = "madgraph"

        h_TTLep_pow = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", binning = binning, selectionString = "&&".join([c[1] for c in cuts + met_cuts + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string,
        binningIsExplicit = True)
        h_TTLep_pow.style = styles.lineStyle( errors = True,  color = ROOT.kBlue )
        h_TTLep_pow.legendText = "powheg"

#        h_TTJets = TTJets.get1DHistoFromDraw( "dl_mt2ll", binning = binning, selectionString = "&&".join([c[1] for c in cuts + met_cuts + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string,
#        binningIsExplicit = True)
#        h_TTJets.style = styles.lineStyle( errors = True,  color = ROOT.kGreen )
#        h_TTJets.legendText = "amc@nlo"

        h_TTJets_Dilep.Scale(2.4)
        h_TTLep_pow.Scale(2.4)
#        h_TTJets.Scale(2.4)

        ratio = {'yRange':(0.1,1.9), 'num':2, 'den':1, 'texY':'pow/MG'}
        plotting.draw(
            Plot.fromHisto("mt2ll_top_comparison_met_%i_%i_rw_%s"%(met_low, met_high, prefix),
                #[ [h_TTJets], [ h_TTJets_Dilep ], [ h_TTLep_pow ] ],
                [ [ h_TTJets_Dilep ], [ h_TTLep_pow ] ],
                texX = "MT_{2}^{ll} (GeV)"
            ), 
            plot_directory = plot_directory, ratio = ratio, 
            logX = False, logY = True, sorting = False, 
            yRange = (0.003, "auto"), 
            scaling = {1:0, 2:0},
            legend = "auto",
            #drawObjects = drawObjects( dataMCScale )
        )


        for mt2ll_low, mt2ll_high in [ [ 0, 25], [25, 50], [50, 75], [75, 100], [100, 140], [140,240]]:
            cuts_mt2blbl = cuts + met_cuts + [("mt2ll_low", "dl_mt2ll>%f"%mt2ll_low), ("mt2ll_high", "dl_mt2ll<%f"%mt2ll_high)]

            h_TTJets_Dilep = TTJets_Dilep.get1DHistoFromDraw( "dl_mt2blbl", binning = mt2blbl_binning, selectionString = "&&".join([c[1] for c in cuts_mt2blbl + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string+"*"+reweight, binningIsExplicit = True )
            h_TTJets_Dilep.style = styles.lineStyle( errors = True,  color = ROOT.kRed )
            h_TTJets_Dilep.legendText = "madgraph"

            h_TTLep_pow = TTLep_pow.get1DHistoFromDraw( "dl_mt2blbl", binning = mt2blbl_binning, selectionString = "&&".join([c[1] for c in cuts_mt2blbl + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string, binningIsExplicit = True )
            h_TTLep_pow.style = styles.lineStyle( errors = True,  color = ROOT.kBlue )
            h_TTLep_pow.legendText = "powheg"

            h_TTJets = TTJets.get1DHistoFromDraw( "dl_mt2blbl", binning = mt2blbl_binning, selectionString = "&&".join([c[1] for c in cuts_mt2blbl + iso_cuts]), addOverFlowBin = 'upper', weightString = weight_string, binningIsExplicit = True)
            h_TTJets.style = styles.lineStyle( errors = True,  color = ROOT.kGreen )
            h_TTJets.legendText = "amc@nlo"

            h_TTJets_Dilep.Scale(2.4)
            h_TTLep_pow.Scale(2.4)
            h_TTJets.Scale(2.4)

            ratio = {'yRange':(0.1,1.9), 'num':1, 'den':0, 'texY':'pow/MG'}
            plotting.draw(
                Plot.fromHisto("mt2blbl_mt2ll_%i_%i_met_%i_%i_top_comparison_rw_%s"%(mt2ll_low, mt2ll_high, met_low, met_high, prefix),
                    [ [ h_TTJets_Dilep ], [ h_TTLep_pow ], [h_TTJets] ],
                    texX = "MT_{2}^{blbl} (GeV)"
                ), 
                plot_directory = plot_directory, ratio = ratio, 
                logX = False, logY = True, sorting = False, 
                yRange = "auto", 
                scaling = {0:2, 1:2},
                legend = "auto",
                #drawObjects = drawObjects( dataMCScale )
            )
