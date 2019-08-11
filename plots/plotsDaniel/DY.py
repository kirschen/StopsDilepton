


from RootTools.core.standard import *
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.objectSelection import getFilterCut

from StopsDilepton.tools.user            import plot_directory, analysis_results

postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
postProcessing_directory = 'postProcessed_80X_v35/dilepTiny'
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *

#filters and selection

selection = "(isMuMu)&&l1_pt>25&&l2_pt>20&&isOS==1&&dl_mt2blbl>140&&abs(dl_mass-91.2)<15"
#selection = "(isEE)&&nJetGood>1&&dl_mt2ll>100&&nBTag==0&&met_pt>80&&metSig>5&&l1_pt>25&&l2_pt>20&&l1_relIso03<0.12&&l2_relIso03<0.12&&abs(dl_mass-91.2)<15"
mc_selection = "&&".join([selection, getFilterCut(isData=False,badMuonFilters='Moriond2017Official')])
#data_selection = "&&".join([selection, getFilterCut(isData=True)])

weight = "35.9*weight*reweightTopPt*reweightBTag_SF*reweightLeptonSF*reweightDilepTriggerBackup*reweightPU36fb*reweightLeptonTrackingSF"


histos = {}

mc = [DY_HT_LO]

#binning = [0,20,40,60,80,100,120,140,160,200,250,300,350]
binning = [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300]
for s in mc:
    print s.name
    histos[s.name] = s.get1DHistoFromDraw("dl_mt2ll", binning, binningIsExplicit=True, selectionString=mc_selection, weightString=weight, addOverFlowBin='upper')
    histos[s.name].style = styles.fillStyle( s.color)

#histos['data'] = DoubleMuon_Run2016_backup.get1DHistoFromDraw("dl_mt2blbl", binning, binningIsExplicit=True, selectionString=data_selection, weightString='(1)', addOverFlowBin='upper')
#histos['data'] = DoubleEG_Run2016_backup.get1DHistoFromDraw("dl_mt2blbl", binning, binningIsExplicit=True, selectionString=data_selection, weightString='(1)', addOverFlowBin='upper')
#histos['data'].style = styles.errorStyle( ROOT.kBlack )

def drawObjects( isData=False, lumi=36. ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Simulation') if not isData else (0.15, 0.95, 'Private Work'),
      (0.70, 0.95, '%sfb^{-1} (13 TeV)'%int(lumi) )
    ]
    return [tex.DrawLatex(*l) for l in lines]


#dO = drawObjects( isData=True, lumi=round(35.9,0))

plots_CR = [ [histos[s.name] for s in mc] ]

plotting.draw(
    Plot.fromHisto("dl_mt2ll",
                plots_CR,
                texX = "M_{T2}(ll) (GeV)",
                texY = "Events"
            ),

    plot_directory = os.path.join(plot_directory, "DY_HT_LO_mumu_log"),
    logX = False, logY = True,
    sorting = True,
    yRange = (0.03, "auto"),
    #scaling = {0:1},
    legend = (0.50,0.88-0.04*sum(map(len, plots_CR)),0.9,0.88),
    #ratio = {'yRange': (0.1, 1.9), 'texY':"Data/Pred."},
    #drawObjects = dO,
    copyIndexPHP = True,
)


