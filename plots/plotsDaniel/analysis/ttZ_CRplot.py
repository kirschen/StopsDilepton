import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools

from math                                import sqrt, cos, sin, pi, atan2
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory, analysis_results
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

import pickle


processes   = ['TTZ', 'TTXNoZ', 'multiBoson', 'DY_HT_LO','Top_pow','ZZ4l']
bins        = ['2j2b','3j1b','3j2b','4j1b','4j2b']
yields      = [ pickle.load(file('ttZ_yields_2016.pkl','r')), pickle.load(file('ttZ_yields_2017.pkl','r')), pickle.load(file('ttZ_yields_2018.pkl','r')) ]
#yields      = [ pickle.load(file('ttZ_yields_2018.pkl','r')) ]

hists = { proc:ROOT.TH1F(proc,proc,len(bins),0,len(bins)) for proc in processes + ['data'] } 

for y in yields:
    for proc in processes + ['data']:
        for i,b in enumerate(bins):
            scaleFactor = 1
            if proc == 'TTZ':           scaleFactor = 1.2
            if proc == 'DY_HT_LO':      scaleFactor = 1.3
            if proc == 'multiBoson':    scaleFactor = 1.2
            if proc == 'ZZ4l':          scaleFactor = 2.0
            if proc == 'Top_pow':       scaleFactor = 1.0
            hists[proc].SetBinContent(i+1, hists[proc].GetBinContent(i+1) + y[proc][b]*scaleFactor )
            hists[proc].GetXaxis().SetBinLabel(i+1, b.replace('j','j ').replace('4j', '#geq4j').replace('2b', '#geq2b') )



def drawObjects( isData=False, lumi=36. ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Simulation') if not isData else (0.15, 0.95, 'CMS Preliminary'),
      (0.70, 0.95, '%sfb^{-1} (13 TeV)'%int(lumi) )
    ]
    return [tex.DrawLatex(*l) for l in lines]

from StopsDilepton.samples.color import color

for proc in processes:
    hists[proc].style = styles.fillStyle(getattr(color, proc))
    hists[proc].legendText = proc.replace('_HT_LO','').replace('_pow','').replace('4l','(4l)').replace('NoZ','(no Z)')

hists['data'].style = styles.errorStyle(color=ROOT.kBlack)
hists['data'].legendText = "Data"


dO = drawObjects( isData=True, lumi=round(35.9+41.5+60.,0))

plots_CR = [ [hists[proc] for proc in processes], [hists['data'] ] ]

plotting.draw(
    Plot.fromHisto("combined",
                plots_CR,
                texX = "Region",
                texY = "Events"
            ),
    plot_directory = os.path.join(plot_directory, "ttZ_norm"),
    logX = False, logY = True,
    sorting = True,
    legend = [ (0.19,0.9-0.03*sum(map(len, plots_CR)),0.9,0.9), 2],
#    widths = {'x_width':700, 'y_width':600},
    ratio = {'yRange': (0.1, 1.9), 'texY':"Data/Pred."},
    drawObjects = dO,
    copyIndexPHP = True,
)

