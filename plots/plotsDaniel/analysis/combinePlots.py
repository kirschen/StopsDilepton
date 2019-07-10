import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools

from math                                import sqrt, cos, sin, pi, atan2
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory, analysis_results
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.samples.color import color

import pickle
import copy

#processes = ['TTZ','TTXNoZ','DY','Top_pow','multiBoson']
processes = ['TTZ','TTXNoZ','ZZ','multiBoson']


hists = {}

#files = ['/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/2016/v0p7/mumumu_log/trilepTight-lepSelTight-njet3p-btag1p-onZ1/Z1_pt.root', '/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/2017/v0p7/mumumu_log/trilepTight-lepSelTight-njet3p-btag1p-onZ1/Z1_pt.root', '/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/2018/v0p7/mumumu_log/trilepTight-lepSelTight-njet3p-btag1p-onZ1/Z1_pt.root']
#tmpFile = '/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/2016/v0p7/all_log/trilepTight-lepSelTight-njet3p-btag1p-onZ1/met_pt.root'
tmpFile = '/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/v0p7/lepSel-quadlep-njet1p-btag1p-onZ1-offZ2/all_log/2016/mt2ll_Z_estimated.root'
#tmpFile = '/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/analysisPlots/v2_noScaling_recoil_VUp_splitMultiBoson_VUp/Run2018/SF_log/lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ/dl_mt2ll.root'
#tmpFile = 'dl_mt2llraw.root'

files = [tmpFile.replace('2016', year) for year in ['2016','2017','2018'] ]
#files = [tmpFile.replace('2018', year) for year in ['2018']]

for i,f in enumerate(files):
    print "Working on file:",f
    tmp_f = ROOT.TFile(f, 'READ')
    tmp_c = tmp_f.Get(tmp_f.GetListOfKeys()[0].GetName())
    tmp_hists = tmp_c.GetListOfPrimitives()[0].GetListOfPrimitives()
    
    hists[i] = {proc:{} for proc in processes + ['data']}
    
    hierarchy = []
    
    for k in range(len(tmp_hists)):
        for proc in processes + ['data']:
            if proc.lower() in tmp_hists[k].GetName().lower():
                if not proc in hierarchy:
                    hists[i][proc] = copy.deepcopy(tmp_hists[k])
                    if not proc == 'data':
                        hierarchy += [proc]
    tmp_f.Close()

    for j,proc in enumerate(hierarchy):
        if j < len(hierarchy)-1:
            hists[i][proc].Add(hists[i][hierarchy[j+1]], -1)

print hists

for i, f in enumerate(files):
    if i>0:
        for proc in processes + ['data']:
            hists[0][proc].Add(hists[i][proc])
    else:
        for proc in processes:
            hists[0][proc].style = styles.fillStyle(getattr(color, proc))
            hists[0][proc].legendText = proc.replace('_HT_LO','').replace('_pow','').replace('4l','(4l)').replace('TTZ','t#bar{t}Z').replace('TTXNoZ', 't#bar{t}W/H, tZq, tWZ').replace('multiBoson', 'Multiboson')
        
        hists[0]['data'].style = styles.errorStyle(color=ROOT.kBlack)
        hists[0]['data'].legendText = "Data"

def drawObjects( isData=False, lumi=36. ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      #(0.15, 0.95, 'CMS Simulation') if not isData else (0.15, 0.95, 'CMS Preliminary'),
      (0.15, 0.95, 'CMS Simulation') if not isData else (0.15, 0.95, 'Private Work'),
      (0.70, 0.95, '%sfb^{-1} (13 TeV)'%int(lumi) )
    ]
    return [tex.DrawLatex(*l) for l in lines]


dO = drawObjects( isData=True, lumi=round(35.9+41.5+60.,0))
#dO = drawObjects( isData=True, lumi=round(60.,0))

plots_CR = [ [hists[0][proc] for proc in processes], [hists[0]['data'] ] ]

plotting.draw(
    Plot.fromHisto("dl_mt2ll_Zestimated_thesis",
                plots_CR,
                texX = "M_{T2}(ll) Z estimated (GeV)",
                texY = "Events"
            ),

    #Plot.fromHisto("Z1_mass_4l_thesis",
    #            plots_CR,
    #            texX = "m(ll) best Z candidate (GeV)",
    #            texY = "Events"
    #        ),
    plot_directory = os.path.join(plot_directory, "propaganda"),
    logX = False, logY = True,
    sorting = True,
    yRange = (0.03, "auto"),
    scaling = {0:1},
    legend = (0.50,0.88-0.04*sum(map(len, plots_CR)),0.9,0.88), 
#if not args.noData else (0.50,0.9-0.047*sum(map(len, plots_CR)),0.85,0.9)
#    legend = [ (0.19,0.9-0.03*sum(map(len, plots_CR)),0.9,0.9), 2],
#    widths = {'x_width':700, 'y_width':600},
    ratio = {'yRange': (0.1, 1.9), 'texY':"Data/Pred."},
    drawObjects = dO,
    copyIndexPHP = True,
)




