#!/usr/bin/env python
import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.interpolate import interpolate, rebin
from StopsDilepton.tools.niceColorPalette import niceColorPalette
from StopsDilepton.tools.user import plot_directory, analysis_results
from StopsDilepton.analysis.run.limitHelpers import getContours, cleanContour

ROOT.gROOT.SetBatch(True)

#signalString = 'T8bbllnunu_XCha0p5_XSlep0p5'
signalString = 'T8bbllnunu_XCha0p5_XSlep0p09'

defFile= os.path.join(analysis_results, "fitAll/limits/%s/%s/limitResults.root"%(signalString,signalString))

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--file", dest="filename", default=defFile, type="string", action="store", help="Which file?")
(options, args) = parser.parse_args()

ifs = options.filename.split('/')
plotDir = os.path.join(plot_directory, ifs[-3], ifs[-2]+'_new5')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

hists = {}

for i in ["exp","exp_up","exp_down","obs"]:
  hists[i] = getObjFromFile(options.filename, i)

for i in ["obs_UL","obs_up","obs_down"]:
  hists[i] = hists["obs"].Clone(i)

for i in ["obs_up","obs_down"]:
  hists[i].Reset()

if signalString == 'T8bbllnunu_XCha0p5_XSlep0p05':
    blanklist = []
    #blanklist = [(510,110),(560,155),(560,180),(560,205),(580,230),(610,155),(610,130),(610,260),(630,205),(655,205),(655,230),(680,230),(680,255),(705,230),(705,255)]
else:
    blanklist = []

from StopsDilepton.tools.xSecSusy import xSecSusy
xSecSusy_ = xSecSusy()
xSecKey = "obs" # exp or obs
for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        #mStop = 200
        mStop = hists[xSecKey].GetXaxis().GetBinLowEdge(ix)
        mNeu  = hists[xSecKey].GetYaxis().GetBinLowEdge(iy)
        v = hists[xSecKey].GetBinContent(hists[xSecKey].FindBin(mStop, mNeu))
        if mStop>99 and v>0:
            #print mStop
            scaleup   = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=1) /xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            scaledown = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=-1)/xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0))
            hists["obs_up"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaleup)
            hists["obs_down"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaledown)
            if signalString == 'T8bbllnunu_XCha0p5_XSlep0p05':#0.5, 160
                if mNeu > (0.35*mStop-100): hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), 0)
            if signalString == 'T8bbllnunu_XCha0p5_XSlep0p5':    
                if mNeu > (mStop-150): hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), 0)
for bl in blanklist:
    hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(bl[0],bl[1]), 0)

for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        if iy>(ix-1):
            #if hists["obs"].GetBinContent(ix,iy) == 0: hists["obs"].SetBinContent(ix,iy,1e6)
            for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
                if hists[i].GetBinContent(ix,iy) == 0:
                    hists[i].SetBinContent(ix,iy,1e6)

for i in ["exp", "exp_up", "exp_down", "obs", "obs_UL", "obs_up", "obs_down"]:
  hists[i + "_int"]    = interpolate(hists[i])

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  hists[i + "_smooth"] = hists[i + "_int"].Clone(i + "_smooth")
  #hists[i + "_smooth"] = rebin(hists[i + "_smooth"])
  hists[i + "_smooth"].Smooth(1,"k5b")

ROOT.gStyle.SetPadRightMargin(0.15)
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
  for g in contours: cleanContour(g, model=modelname)
  contours = max(contours , key=lambda x:x.GetN()).Clone("contour_" + i)
  if False and signalString == 'T8bbllnunu_XCha0p5_XSlep0p05':
    if i == "obs":
        for j in range(contours.GetN()):
            x = ROOT.Double()
            y = ROOT.Double()
            contours.GetPoint(j,x,y)
        contours.RemovePoint(j)
        contours.SetPoint(j,500,15)
  #for cont in contours:
  #  cont.Draw('same')
  #  cont.Write()
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
fileIN = inputFile('T8bbllnunu_limit.cfg')

# classic temperature histogra
xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "asdf")
xsecPlot.Draw()
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

