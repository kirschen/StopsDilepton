'''
/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v3//COMBINED/controlAll//cardFiles/T2tt/observed/
Get a signal region plot from the cardfiles
'''

#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--signal",               dest='signal',  action='store', default='T2tt',    choices=["T2tt"], help="which signal?")
parser.add_option("--massPoints",           dest='massPoints',  action='store', default='800_100', help="which masspoints??")
parser.add_option("--channel",              dest='channel',  action='store', default='all', choices=['all','OF','SF'], help="which channel??")
parser.add_option("--small",                action='store_true', help="small?")
parser.add_option('--logLevel',             dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option('--blinded',              action="store_true")
parser.add_option('--overwrite',            dest="overwrite", default = False, action = "store_true", help="Overwrite existing output files, bool flag set to True  if used")
parser.add_option('--postFit',              dest="postFit", default = False, action = "store_true", help="Apply pulls?")
parser.add_option('--expected',             action = "store_true", help="Run expected?")
parser.add_option('--preliminary',             action = "store_true", help="Run expected?")
parser.add_option('--combined',             action = "store_true", help="combined fit for all years?")
parser.add_option("--year",                 action='store',      default=2017, type="int", help='Which year?')
parser.add_option("--region",               action='store',      default="controlAll", choices=['controlAll', 'signalOnly', 'controlDYVV', 'controlTT', 'controlTTZ'], help='Which year?')
(options, args) = parser.parse_args()

# Standard imports
import ROOT
import os
import sys
import pickle
import math

# Analysis
from StopsDilepton.tools.u_float           import u_float
from StopsDilepton.tools.user              import plot_directory, analysis_results
from StopsDilepton.samples.color           import color
from StopsDilepton.tools.getPostFit        import *
from StopsDilepton.analysis.regions        import *

if options.region == 'controlAll':
    pass
elif options.region == 'signalOnly':
    regions = regionsLegacy[1:] + regionsLegacy[1:]

from RootTools.core.standard import *
# logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   options.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None)

# get a setup
from StopsDilepton.analysis.Setup import Setup
if options.combined:
    setup=Setup(2016)
    lumiStr = 138.4
else:
    setup = Setup(options.year)
    lumiStr = setup.dataLumi/1000
analysis_results = '/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v5/'
isData = True if not options.expected else False
#lumiStr = setup.dataLumi/1000
years=[2016,2017,2018]
controlRegions = options.region
massPoints = options.massPoints
cardName = "T2tt_%s_shapeCard"%massPoints

if options.combined:
    cardDir = analysis_results+"/COMBINED/%s/cardFiles/%s/%s/"%(controlRegions,options.signal,'expected' if options.expected else 'observed')
else:
    cardDir = analysis_results+"/%s/%s/cardFiles/%s/%s/"%(options.year,controlRegions,options.signal,'expected' if options.expected else 'observed')

cardFile = "%s/%s.txt"%(cardDir, cardName)

logger.info("Plotting from cardfile %s"%cardFile)

# get the results
postFitResults = getPrePostFitFromMLF(cardFile.replace('.txt','_FD.root'))
preFitHist={}
postFitHist={}
bhistos=[]
hists={}
histos={}
bkgHist=[]
processes = [   ( 'TTJets', 't#bar{t}/t'),
                ('DY', 'Drell-Yan'),
                ('multiBoson', 'VV/VVV'),
                ('TTZ', 't#bar{t}Z'),
                ('other', 't#bar{t}X, rare') ]
if options.combined:
    for year in years:
        preFitHist[year]        = postFitResults['hists']['shapes_prefit']['dc_%s'%year]
        postFitHist[year]       = postFitResults['hists']['shapes_fit_s']['dc_%s'%year]
        hists[year] = preFitHist[year] if not options.postFit else postFitHist[year]

        # signal is always prefit for the plots
        hists[year]['signal1'] = postFitResults['hists']['shapes_prefit']['dc_%s'%year]['signal']
        #print hists[year]
#    preFitHists.update(preFitHist[2016], preFitHists[2017] ,preFitHists[2018])
    #hists = preFitHist if not options.postFit else postFitHist
    for i,(p,tex) in enumerate(processes):
        print i, hists[2016][p]
        bhistos.append( hists[2016][p])
        #bhistos.Reset()
        #bhistos.SetName('%s')%p
        print bhistos[i]
    dataHist = hists[2016]['DY'].Clone()
    dataHist.Reset()
    dataHist.SetName('data')
    dataHist.legendText = 'Data'
    for n,(p,tex) in enumerate(processes):
        print n
        for i in range(bhistos[n].GetNbinsX()):
            #print i, bhistos[n].GetNbinsX()
            v=0
            v=hists[2016][p].GetBinContent(i+1) + hists[2017][p].GetBinContent(i+1) + hists[2018][p].GetBinContent(i+1)
            print v
            bhistos[n].SetBinContent(i+1, v)
        if tex:
            bhistos[n].legendText = tex
        histos[p]=bhistos[n]
        print bhistos[n], histos[p]
        bhistos[n].style = styles.fillStyle( getattr(color, p), lineColor=getattr(color,p), errors=False )
        bkgHist.append( bhistos[n])
    print bkgHist
    dataHist.SetBinErrorOption(ROOT.TH1F.kPoisson)
    for i in range(dataHist.GetNbinsX()):
        dataHist.SetBinContent(i+1, (hists[2016]['data'].Eval(i+0.5) + hists[2017]['data'].Eval(i+0.5) + hists[2018]['data'].Eval(i+0.5)))
        #dataHist.SetBinError(i+1, (hists[2016]['data'].Eval(i+0.5) + hists[2017]['data'].Eval(i+0.5) + hists[2018]['data'].Eval(i+0.5)))
    histos['data'] = dataHist

    histos['data'].style = styles.errorStyle( ROOT.kBlack, markerSize = 1. )
    histos['data'].legendOption = 'p'
    print histos

    signalHist = hists[2016]['DY'].Clone()
    signalHist.Reset()
    signalHist.SetName('signal')
    signalHist.legendText = 'T2tt (800,100)'
    for i in range(signalHist.GetNbinsX()):
        signalHist.SetBinContent(i+1, (hists[2016]['signal1'].GetBinContent(i+1) + hists[2017]['signal1'].GetBinContent(i+1) + hists[2018]['signal1'].GetBinContent(i+1)))
    histos['signal1'] = signalHist
    histos['signal1'].style = styles.lineStyle( ROOT.kBlack, width=2 )

else:
    preFitHists     = postFitResults['hists']['shapes_prefit']['Bin0']
    postFitHists    = postFitResults['hists']['shapes_fit_b']['Bin0']
    print preFitHists
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
        print 'Data observation', hists['data'].Eval(i+0.5)
        dataHist.SetBinContent(i+1, hists['data'].Eval(i+0.5))
        dataHist.SetBinError(i+1, math.sqrt(hists['data'].Eval(i+0.5)))

    hists['data'] = dataHist
    #hists['data'].style = styles.errorStyle( ROOT.kBlack, markerSize = 1. )
    hists['data'].style = styles.lineStyle( ROOT.kBlack, width = 1 )
    hists['data'].legendOption = 'p'
#hists['BSM'].legendOption = 'l'

boxes = []
ratio_boxes = []
if options.combined:
    for ib in range(1, 1 + hists[2016]['total_background'].GetNbinsX() ):
        val = hists[2016]['total_background'].GetBinContent(ib) + hists[2017]['total_background'].GetBinContent(ib) + hists[2018]['total_background'].GetBinContent(ib)
        if val<0: continue
        #sys = hists[2016]['total_background'].GetBinError(ib) + hists[2017]['total_background'].GetBinError(ib) + hists[2018]['total_background'].GetBinError(ib)
        sys = math.sqrt((hists[2016]['total_background'].GetBinError(ib) * hists[2016]['total_background'].GetBinError(ib))+ (hists[2017]['total_background'].GetBinError(ib) * hists[2017]['total_background'].GetBinError(ib)) +( hists[2018]['total_background'].GetBinError(ib) * hists[2018]['total_background'].GetBinError(ib)))
        if val > 0:
            sys_rel = sys/val
        else:
            sys_rel = 1.
        
        # uncertainty box in main histogram
        box = ROOT.TBox( hists[2016]['total_background'].GetXaxis().GetBinLowEdge(ib),  max([0.006, val-sys]), hists[2016]['total_background'].GetXaxis().GetBinUpEdge(ib), max([0.006, val+sys]) )
        box.SetLineColor(ROOT.kGray+1)
        box.SetFillStyle(3244)
        box.SetFillColor(ROOT.kGray+1)
        
        # uncertainty box in ratio histogram
        r_box = ROOT.TBox( hists[2016]['total_background'].GetXaxis().GetBinLowEdge(ib),  max(0.11, 1-sys_rel), hists[2016]['total_background'].GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys_rel) )
        r_box.SetLineColor(ROOT.kGray+1)
        r_box.SetFillStyle(3244)
        r_box.SetFillColor(ROOT.kGray+1)

        boxes.append( box )
        hists[2016]['total_background'].SetBinError(ib, 0)
        ratio_boxes.append( r_box )
else:

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

def setBinLabels( hist ):
    for i in range(1, hist.GetNbinsX()+1):
        hist.GetXaxis().SetBinLabel(i, "   %s"%((i+1)/2 if i%2==1 else ''))


drawObjects = drawObjects( isData=isData, lumi=round(lumiStr,1)) + boxes
if options.combined:
    plots = [ bkgHist, [histos['data']]]
        
    plotName = "%s_COMBINED"%options.region
else:
    plots = [ bkgHists, [hists['data']]]
    plotName = "%s_%s"%(options.region, options.year)
if options.postFit:
    plotName += '_postFit'

for i in range(dataHist.GetNbinsX()):
    print hists['data'].GetBinContent(i+1)

plotting.draw(
    Plot.fromHisto(plotName,
                plots,
                texX = "",
                texY = 'Number of events',
            ),
    plot_directory = os.path.join(plot_directory, "controlRegions", 'v5'),
    logX = False, logY = True, sorting = False, 
    #legend = (0.75,0.80-0.010*32, 0.95, 0.80),
    legend = (0.70,0.55, 0.95, 0.85),
    widths = {'x_width':900, 'y_width':600, 'y_ratio_width':250},
    yRange = (0.2,300000.),
    #yRange = (0.03, [0.001,0.5]),
    ratio = {'yRange': (0.11, 1.89), 'texY':'Data/pred', 'histos':[(1,0)], 'drawObjects':ratio_boxes, #+ drawLabelsLower( regions ) +drawHeadlineLower( regions ) + drawDivisionsLower(regions),
            'histModifications': [lambda h: setBinLabels(h), lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(28), lambda h: h.GetYaxis().SetTitleOffset(1.2), lambda h: h.GetXaxis().SetTitleSize(32), lambda h: h.GetXaxis().SetLabelSize(27), lambda h: h.GetXaxis().SetLabelOffset(0.035)]} ,
    drawObjects = drawObjects,
    histModifications = [lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(28), lambda h: h.GetYaxis().SetTitleOffset(1.2)],
    #canvasModifications = [ lambda c : c.SetLeftMargin(0.08), lambda c : c.GetPad(2).SetLeftMargin(0.08), lambda c : c.GetPad(1).SetLeftMargin(0.08), lambda c: c.GetPad(2).SetBottomMargin(0.60), lambda c : c.GetPad(1).SetRightMargin(0.03), lambda c: c.GetPad(2).SetRightMargin(0.03) ],
    copyIndexPHP = True,
)

