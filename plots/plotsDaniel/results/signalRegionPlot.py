'''
Get a signal region plot from the cardfiles
'''

#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--signal",               dest='signal',  action='store', default='T2tt',    choices=["T2tt"], help="which signal?")
parser.add_option("--small",                action='store_true', help="small?")
parser.add_option('--logLevel',             dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option('--blinded',              action="store_true")
parser.add_option('--overwrite',            dest="overwrite", default = False, action = "store_true", help="Overwrite existing output files, bool flag set to True  if used")
parser.add_option('--postFit',              dest="postFit", default = False, action = "store_true", help="Apply pulls?")
parser.add_option('--expected',             action = "store_true", help="Run expected?")
parser.add_option('--preliminary',             action = "store_true", help="Run expected?")
parser.add_option("--year",                 action='store',      default=2017, type="int", help='Which year?')
(options, args) = parser.parse_args()

# Standard imports
import ROOT
import os
import sys
import pickle
import math

# Analysis
from StopsDilepton.tools.u_float           import u_float
from StopsDilepton.tools.user              import plot_directory
from StopsDilepton.samples.color           import color
from StopsDilepton.tools.getPostFit        import *

from RootTools.core.standard import *
# logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   options.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None)

# get a setup
from StopsDilepton.analysis.Setup import Setup

setup = Setup(options.year)

isData = True if not options.expected else False
lumiStr = setup.dataLumi/1000

controlRegions = 'controlAll'
cardName = "T2tt_700_0_shapeCard"
cardDir = "/afs/hephy.at/data/dspitzbart02/StopsDileptonLegacy/results/v1/%s/%s/cardFiles/%s/%s/"%(options.year,controlRegions,options.signal,'expected' if options.expected else 'observed')
#cardDir = "/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v1/%s/%s/cardFiles/%s/%s/"%(options.year,controlRegions,options.signal,'expected' if options.expected else 'observed')

cardFile = "%s/%s.txt"%(cardDir, cardName)


logger.info("Plotting from cardfile %s"%cardFile)

# get the results
postFitResults = getPrePostFitFromMLF(cardFile.replace('.txt','_FD.root'))


processes = [   ('TTJetsG',''), 
                ('TTJetsNG',''),
                ( 'TTJetsF', 't#bar{t}/t'),
                ('DY', 'Drell-Yan'),
                ('multiBoson', 'VV/VVV'),
                ('TTZ', 't#bar{t}Z'),
                ('other', 't#bar{t}X, rare') ]

preFitHists     = postFitResults['hists']['shapes_prefit']['Bin0']
postFitHists    = postFitResults['hists']['shapes_fit_b']['Bin0']

hists = preFitHists if not options.postFit else postFitHists

bkgHists = []

dataHist = hists['DY'].Clone()
dataHist.Reset()
dataHist.SetName('data')
dataHist.legendText = 'Data'

for p,tex in processes:
    hists[p].style = styles.fillStyle( getattr(color, p), lineColor=getattr(color,p), errors=False )
    bkgHists.append(hists[p])
    if tex:
        hists[p].legendText = tex
    

for i in range(dataHist.GetNbinsX()):
    dataHist.SetBinContent(i+1, hists['data'].Eval(i+0.5))
    dataHist.SetBinError(i+1, math.sqrt(hists['data'].Eval(i+0.5)))

hists['data'] = dataHist
hists['data'].style = styles.errorStyle( ROOT.kBlack, markerSize = 1. )
hists['data'].legendOption = 'p'
#hists['BSM'].legendOption = 'l'

### manually calculate the chi2 (no correlations).
#chi2SM  = 0
#chi2BSM = 0
#totalExp = 0
#totalObs = 0
#nDOF = 0
#Exp = []
#Obs = []
#printChi2 = False
#for i, r in enumerate(regions):
#    Exp.append(hists['total'].GetBinContent(i+1))
#    Obs.append(hists['observed'].GetBinContent(i+1))
#    if printChi2:
#        print "Region %s"%(i+1)
#        print "SM"
#        print hists['total'].GetBinContent(i+1)
#        print (hists['observed'].GetBinContent(i+1) - hists['total'].GetBinContent(i+1))
#        print hists['total'].GetBinError(i+1)
#        print hists['observed'].GetBinContent(i+1)/hists['total'].GetBinContent(i+1)
#        print "Chi2", ( ((hists['observed'].GetBinContent(i+1) - hists['total'].GetBinContent(i+1))**2) / (hists['total'].GetBinError(i+1)**2) )
#        print "BSM"
#        print hists['BSM'].GetBinContent(i+1)
#        print hists['observed'].GetBinContent(i+1) - hists['BSM'].GetBinContent(i+1)
#        print hists['BSM'].GetBinError(i+1)
#        print hists['observed'].GetBinContent(i+1)/hists['BSM'].GetBinContent(i+1)
#        print "Chi2", (hists['observed'].GetBinContent(i+1) - hists['BSM'].GetBinContent(i+1))**2/hists['BSM'].GetBinError(i+1)**2
#        print
#    totalExp += hists['total'].GetBinContent(i+1)
#    totalObs += hists['observed'].GetBinContent(i+1)
#    if hists['total'].GetBinContent(i+1) > 10:# or True:
#        chi2SM += ( ((hists['observed'].GetBinContent(i+1) - hists['total'].GetBinContent(i+1))**2) / (hists['total'].GetBinError(i+1)**2) )
#        nDOF +=1
#    if options.signal and hists['BSM'].GetBinContent(i+1) > 10:# or True:
#        chi2BSM += (hists['observed'].GetBinContent(i+1) - hists['BSM'].GetBinContent(i+1))**2/hists['BSM'].GetBinError(i+1)**2
#
#    if i == 14 and printChi2:
#        print "Intermediate Chi2 values:"
#        print chi2SM
#        print chi2BSM
#
#if printChi2:
#    print "Chi-squared for SM:", chi2SM
#    print "Chi-squared for BSM:", chi2BSM
#    print "nDOF:", len(regions)
#    print "nDOF (red):", nDOF
#    print "Total Obs/Exp:", totalObs/totalExp
#
## get the covariance matrix
# combineCards.py mycard.txt -S > myshapecard.txt
# text2workspace.py myshapecard.txt
# combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 5000 --saveOverall myshapecard.root
#
### calculate the chi2 with R^T*Cov^(-1)*R where R is the residual vector
#import numpy as np
#import pickle
#E = np.array(Exp)
#O = np.array(Obs)
#R = E - O
#RT = R.transpose()


boxes = []
ratio_boxes = []
for ib in range(1, 1 + hists['total_background'].GetNbinsX() ):
    val = hists['total_background'].GetBinContent(ib)
    if val<0: continue
    sys = hists['total_background'].GetBinError(ib)
    if val > 0:
        sys_rel = sys/val
    else:
        sys_rel = 1.
    
    # uncertainty box in main histogram
    box = ROOT.TBox( hists['total_background'].GetXaxis().GetBinLowEdge(ib),  max([0.006, val-sys]), hists['total_background'].GetXaxis().GetBinUpEdge(ib), max([0.006, val+sys]) )
    box.SetLineColor(ROOT.kGray+1)
    box.SetFillStyle(3244)
    box.SetFillColor(ROOT.kGray+1)
    
    # uncertainty box in ratio histogram
    r_box = ROOT.TBox( hists['total_background'].GetXaxis().GetBinLowEdge(ib),  max(0.11, 1-sys_rel), hists['total_background'].GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys_rel) )
    r_box.SetLineColor(ROOT.kGray+1)
    r_box.SetFillStyle(3244)
    r_box.SetFillColor(ROOT.kGray+1)

    boxes.append( box )
    hists['total_background'].SetBinError(ib, 0)
    ratio_boxes.append( r_box )

def drawObjects( isData=False, lumi=36. ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.05)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.945, 'CMS Simulation') if not isData else ( (0.15, 0.945, 'CMS') if not options.preliminary else (0.15, 0.945, 'CMS #bf{#it{Preliminary}}')),
      (0.70, 0.945, '#bf{%s fb^{-1} (13 TeV)}'%lumi )
    ]
    return [tex.DrawLatex(*l) for l in lines]

#def setBinLabels( hist ):
#    for i in range(1, hist.GetNbinsX()+1):
#        if i < 16:
#            hist.GetXaxis().SetBinLabel(i, "%s"%i)
#        else:
#            hist.GetXaxis().SetBinLabel(i, "%s"%(i-15))

drawObjects = drawObjects( isData=isData, lumi=round(lumiStr,1)) + boxes #+ drawDivisions( regions )

plots = [ bkgHists, [hists['data']]]

plotName = "controlRegions_%s"%options.year
if options.postFit:
    plotName += '_postFit'


plotting.draw(
    Plot.fromHisto(plotName,
                plots,
                texX = "",
                texY = 'Number of events',
            ),
    plot_directory = os.path.join(plot_directory, "controlRegions"),
    logX = False, logY = True, sorting = False, 
    #legend = (0.75,0.80-0.010*32, 0.95, 0.80),
    legend = (0.70,0.60, 0.95, 0.90),
    widths = {'x_width':900, 'y_width':600, 'y_ratio_width':250},
    yRange = (0.03,60000.),
    #yRange = (0.03, [0.001,0.5]),
    ratio = {'yRange': (0.11, 1.89), 'texY':'Data/pred', 'histos':[(1,0)], 'drawObjects':ratio_boxes, #+ drawLabelsLower( regions ) +drawHeadlineLower( regions ) + drawDivisionsLower(regions),
            'histModifications': [lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(28), lambda h: h.GetYaxis().SetTitleOffset(1.2), lambda h: h.GetXaxis().SetTitleSize(32), lambda h: h.GetXaxis().SetLabelSize(27), lambda h: h.GetXaxis().SetLabelOffset(0.035)]} ,
    drawObjects = drawObjects,
    histModifications = [lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(28), lambda h: h.GetYaxis().SetTitleOffset(1.2)],
    #canvasModifications = [ lambda c : c.SetLeftMargin(0.08), lambda c : c.GetPad(2).SetLeftMargin(0.08), lambda c : c.GetPad(1).SetLeftMargin(0.08), lambda c: c.GetPad(2).SetBottomMargin(0.60), lambda c : c.GetPad(1).SetRightMargin(0.03), lambda c: c.GetPad(2).SetRightMargin(0.03) ],
    copyIndexPHP = True,
)

