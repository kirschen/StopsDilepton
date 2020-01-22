'''
/afs/hephy.at/data/dspitzbart02/StopsDileptonLegacy/results/v1/2017/signalOnly/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v1//comb/signalOnly/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v2/2017/fitAll/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v3//comb/fitAll/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/data/cms04/StopsDileptonLegacy/results/v4/2016/signalOnly/limits/T2bW/T2bW/limitResults.root
/afs/hephy.at/data/cms04/StopsDileptonLegacy/results/v4/2016/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p05/T8bbllnunu_XCha0p5_XSlep0p05/limitResults.root
/afs/hephy.at/data/cms04/StopsDileptonLegacy/results/v4/2017/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p05/T8bbllnunu_XCha0p5_XSlep0p05/limitResults.root
/afs/hephy.at/data/cms04/StopsDileptonLegacy/results/v4/2017/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p5/T8bbllnunu_XCha0p5_XSlep0p5/limitResults.root
/afs/hephy.at/data/cms04/StopsDileptonLegacy/results/v4/2018/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p5/T8bbllnunu_XCha0p5_XSlep0p5/limitResults.root

/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4/2017/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p05/T8bbllnunu_XCha0p5_XSlep0p05/limitResults.root
afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4/2017/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p5/T8bbllnunu_XCha0p5_XSlep0p5/limitResults.root
/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4/2016/fitAll/limits/T2bW/T2bW/limitResults.root
/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4/2017/fitAll/limits/T2bW/T2bW/limitResults.root
Written /afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4//comb/fitAll/limits/T2tt/T2tt/limitResults.root
/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v4//comb/fitAll/limits/T8bbllnunu_XCha0p5_XSlep0p95/T8bbllnunu_XCha0p5_XSlep0p95/limitResults.root
'''

#!/usr/bin/env python
import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers                import getObjFromFile
from StopsDilepton.tools.interpolate            import interpolate, rebin
from StopsDilepton.tools.niceColorPalette       import niceColorPalette
from StopsDilepton.tools.user                   import plot_directory, analysis_results
from StopsDilepton.analysis.plot.limitHelpers   import getContours, cleanContour, getPoints

ROOT.gROOT.SetBatch(True)

from optparse import OptionParser
parser = OptionParser()
#parser.add_option("--file",             dest="filename",    default=None,   type="string", action="store",  help="Which file?")
parser.add_option("--signal",           action='store',     default='T2tt',  choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95", "T2bt","T2bW", "T8bbllnunu_XCha0p5_XSlep0p09", "ttHinv"], help="which signal?")
parser.add_option("--year",             dest="year",   type="int",    action="store",  help="Which year?")
parser.add_option("--version",          dest="version",  default='v6',  action="store",  help="Which version?")
parser.add_option("--subDir",           dest="subDir",  default='unblindV1',  action="store",  help="Give some extra name")
parser.add_option("--combined",         action="store_true",  help="Combine the years?")
parser.add_option("--unblind",          action="store_true",  help="Use real data?")
(options, args) = parser.parse_args()

yearString = str(options.year) if not options.combined else 'comb'
signalString = options.signal

# input
analysis_results = '/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/'+options.version

defFile = os.path.join(analysis_results, "%s/fitAll/limits/%s/%s/limitResults.root"%(yearString,signalString,signalString))

print defFile
if options.year == 2016:
    lumi    = 35.9
    #eraText =  "(2016)"
elif options.year == 2017:
    lumi    = 41.5
    #eraText =  "(2017)"
elif options.year == 2018:
    lumi    = 59.7 
    #eraText =  "(2018)"
else:
    #lumi = 35.92+41.53+59.74
    lumi = 137

plotDir = os.path.join(plot_directory,'limits', signalString, options.version, yearString, options.subDir)

import RootTools.plot.helpers as plot_helpers
plot_helpers.copyIndexPHP( plotDir )

if not os.path.exists(plotDir):
    os.makedirs(plotDir)

graphs  = {}
hists   = {}

#nbins = 50
nbins = 100

for i in ["exp","exp_up","exp_down","obs"]:
    graphs[i] = getObjFromFile(defFile, i)
    graphs[i].SetNpx(nbins)
    graphs[i].SetNpy(nbins)
    hists[i] = graphs[i].GetHistogram().Clone()

for i in ["obs_UL","obs_up","obs_down"]:
  hists[i] = hists["obs"].Clone(i)

for i in ["obs_up","obs_down"]:
  hists[i].Reset()

scatter = getObjFromFile(defFile, 'scatter')
c1 = ROOT.TCanvas()
scatter.SetLineWidth(0)
scatter.SetMarkerSize(1)
scatter.SetMarkerColor(ROOT.kGreen+3)
scatter.Draw()
c1.Print(os.path.join(plotDir, 'scatter.png'))

for i in ["exp","exp_up","exp_down","obs"]:
    c1 = ROOT.TCanvas()
    graphs[i].Draw()
    c1.SetLogz()
    c1.Print(os.path.join(plotDir, 'scatter_%s.png'%i))
    del c1

blanklist = []
if signalString == 'T8bbllnunu_XCha0p5_XSlep0p05':
    blanklist = []

from StopsDilepton.tools.xSecSusy import xSecSusy
xSecSusy_ = xSecSusy()
xSecKey = "obs" # exp or obs
for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        #mStop   = (hists[xSecKey].GetXaxis().GetBinUpEdge(ix)+hists[xSecKey].GetXaxis().GetBinLowEdge(ix)) / 2.
        mStop   = hists[xSecKey].GetXaxis().GetBinUpEdge(ix)
        mNeu    = (hists[xSecKey].GetYaxis().GetBinUpEdge(iy)+hists[xSecKey].GetYaxis().GetBinLowEdge(iy)) / 2.
        v       = hists[xSecKey].GetBinContent(hists[xSecKey].FindBin(mStop, mNeu))
        if mStop>99 and v>0 or True:
            scaleup   = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=1) /xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            scaledown = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=-1)/xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            xSec = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v * xSec)
            hists["obs_up"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaleup)
            hists["obs_down"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaledown)

for ix in range(hists[xSecKey].GetNbinsX()):
    hists["obs_UL"].SetBinContent(ix, 0, hists["obs_UL"].GetBinContent(ix,1))
    hists["obs_up"].SetBinContent(ix, 0, hists["obs_up"].GetBinContent(ix,1))
    hists["obs_down"].SetBinContent(ix, 0, hists["obs_down"].GetBinContent(ix,1))

for bl in blanklist:
    hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(bl[0],bl[1]), 0)

for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        if iy>ix:
            #if hists["obs"].GetBinContent(ix,iy) == 0: hists["obs"].SetBinContent(ix,iy,1e6)
            for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
                if hists[i].GetBinContent(ix,iy) == 0:
                    hists[i].SetBinContent(ix,iy,1e6)

for i in ["exp", "exp_up", "exp_down", "obs", "obs_UL", "obs_up", "obs_down"]:
  print i
  hists[i + "_int"]    = hists[i]

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  hists[i + "_smooth"] = hists[i + "_int"].Clone(i + "_smooth")
  #for x in range(3):
  if not signalString == "T2bW":
      hists[i + "_smooth"].Smooth(1,"k5a")
  #hists[i + "_smooth"].Smooth(1,"k5b")
  #hists[i + "_smooth"].Smooth(1,"k3a")

ROOT.gStyle.SetPadRightMargin(0.05)
c1 = ROOT.TCanvas()
niceColorPalette(255)

hists["obs"].GetZaxis().SetRangeUser(0.02, 299)
hists["obs"].Draw('COLZ')
c1.SetLogz()

modelname = signalString
temp = ROOT.TFile("tmp.root","recreate")
hists["obs_UL_int"].Clone("temperature").Write()

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  contours = getContours(hists[i + "_smooth"], plotDir)
  for g in contours:
    cleanContour(g, model=modelname)
    g = getPoints(g)
  contours = max(contours , key=lambda x:x.GetN()).Clone("contour_" + i)
  contours.Draw('same')
  contours.Write()

temp.Close()

c1.Print(os.path.join(plotDir, 'limit.png'))

from StopsDilepton.PlotsSMS.inputFile import inputFile
from StopsDilepton.PlotsSMS.smsPlotXSEC import smsPlotXSEC
from StopsDilepton.PlotsSMS.smsPlotCONT import smsPlotCONT
from StopsDilepton.PlotsSMS.smsPlotBrazil import smsPlotBrazil


# read input arguments
analysisLabel = "SUS-17-001"
outputname = os.path.join(plotDir, 'limit')

# read the config file
fileIN = inputFile('SMS_limit.cfg')

# classic temperature histogra
xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "asdf")
#xsecPlot.Draw( lumi = lumi, zAxis_range = (10**-3,10**2) )
if options.signal.startswith("T8"):
    xsecPlot.Draw( lumi = lumi, zAxis_range = (10**-4,5*10**2) )
else:
    xsecPlot.Draw( lumi = lumi, zAxis_range = (10**-3,10**2) )
xsecPlot.Save("%sXSEC" %outputname)

temp = ROOT.TFile("tmp.root","update")
xsecPlot.c.Write("cCONT_XSEC")
temp.Close()

# only lines
contPlot = smsPlotCONT(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "")
contPlot.Draw()
contPlot.Save("%sCONT" %outputname)

# brazilian flag (show only 1 sigma)
brazilPlot = smsPlotBrazil(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "")
brazilPlot.Draw()
brazilPlot.Save("%sBAND" %outputname)

