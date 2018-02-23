#!/usr/bin/env python
import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.interpolate import interpolate, rebin
from StopsDilepton.tools.niceColorPalette import niceColorPalette
from StopsDilepton.tools.user import plot_directory, analysis_results
from StopsDilepton.analysis.run.limitHelpers import getContours, cleanContour

ROOT.gROOT.SetBatch(True)

signalString = 'T2tt'

#defFile= os.path.join(analysis_results, "fitAll/limits/T2tt/T2tt/limitResults.root")
#defFile= os.path.join(analysis_results, "fitAll/limits/"+signalString+"/"+signalString+"/limitResults.root")
defFile= os.path.join(analysis_results, "fitAll/limits/"+signalString+"/"+signalString+"/limitResults.root")
#defFile= os.path.join(analysis_results, "fitAll/limits/T2tt_approval/T2tt_approval/limitResults.root")
#defFile= os.path.join(analysis_results, "isOS-nJets2p-nbtag1p-met80-metSig5-dPhiJet0-dPhiJet-mll20-looseLeptonVeto-relIso0.12/DY/TTZ/TTJets/multiBoson/limits/T2tt/regionsO/limitResults.root")

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--file", dest="filename", default=defFile, type="string", action="store", help="Which file?")
(options, args) = parser.parse_args()

ifs = options.filename.split('/')
plotDir = os.path.join(plot_directory, ifs[-3], ifs[-2]+'_lateTest')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

hists = {}

for i in ["exp","exp_up","exp_down","obs"]:
  hists[i] = getObjFromFile(options.filename, i)

for i in ["obs_UL","obs_up","obs_down"]:
  hists[i] = hists["obs"].Clone(i)

for i in ["obs_up","obs_down"]:
  hists[i].Reset()

from StopsDilepton.tools.xSecSusy import xSecSusy
xSecSusy_ = xSecSusy()
xSecKey = "obs" # exp or obs
for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        mStop = hists[xSecKey].GetXaxis().GetBinLowEdge(ix)
        mNeu  = hists[xSecKey].GetYaxis().GetBinLowEdge(iy)
        v = hists[xSecKey].GetBinContent(hists[xSecKey].FindBin(mStop, mNeu))
        if v>0:
            scaleup   = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=1) /xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            scaledown = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=-1)/xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            hists["obs_UL"].SetBinContent(hists["obs"].FindBin(mStop, mNeu), v*xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0))
            hists["obs_up"].SetBinContent(hists["obs"].FindBin(mStop, mNeu), v*scaleup)
            hists["obs_down"].SetBinContent(hists["obs"].FindBin(mStop, mNeu), v*scaledown)

newHists = {}

for k in ["obs","obs_UL","obs_up","obs_down","exp","exp_up","exp_down"]:
    xmax = hists[k].GetXaxis().GetXmax()
    xmin = hists[k].GetXaxis().GetXmin()
    Nx = hists[k].GetXaxis().GetNbins()
    ymax = hists[k].GetYaxis().GetXmax()
    ymin = hists[k].GetYaxis().GetXmin()
    Ny = hists[k].GetYaxis().GetNbins()
    yWidth = (ymax-ymin)/Ny
    newMin = ymin#-yWidth
    newHists[k] = ROOT.TH2F(hists[k].GetName(),hists[k].GetTitle(),Nx,xmin,xmax,Ny+1,newMin,ymax)
    for ix in range(1, hists[k].GetNbinsX()+1):
        newHists[k].SetBinContent(ix,1,hists[k].GetBinContent(ix,1))
        for iy in range(1, hists[k].GetNbinsY()+1):
            newHists[k].SetBinContent(ix,iy+1,hists[k].GetBinContent(ix,iy))

hists = newHists

#for k in ["obs","obs_UL","obs_up","obs_down","exp","exp_up","exp_down"]:
#    for ix in range(hists[k].GetNbinsX()):
#        hists[k].SetBinContent(ix,0, hists[k].GetBinContent(ix,1))

for i in ["exp", "exp_up", "exp_down", "obs", "obs_UL", "obs_up", "obs_down"]:
  hists[i + "_int"]    = interpolate(hists[i])

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  hists[i + "_smooth"] = hists[i + "_int"].Clone(i + "_smooth")
 #hists[i + "_smooth"] = rebin(hists[i + "_smooth")
  hists[i + "_smooth"].Smooth()

ROOT.gStyle.SetPadRightMargin(0.15)
c1 = ROOT.TCanvas()
niceColorPalette(255)

hists["obs"].GetZaxis().SetRangeUser(0.02, 99)
hists["obs"].Draw('COLZ')
c1.SetLogz()

temp = ROOT.TFile("tmp.root","recreate")
hists["obs_UL_int"].Clone("temperature").Write()

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  contours = getContours(hists[i + "_smooth"], plotDir)
  for g in contours: cleanContour(g)
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
modelname = signalString
analysisLabel = "SUS-16-027"
outputname = os.path.join(plotDir, 'limit')

# read the config file
fileIN = inputFile('T2tt_limit.cfg')

# classic temperature histogra
xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "")
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

