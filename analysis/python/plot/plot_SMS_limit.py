'''
/afs/hephy.at/data/dspitzbart02/StopsDileptonLegacy/results/v1/2017/signalOnly/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v1//comb/signalOnly/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v2/2017/fitAll/limits/T2tt/T2tt/limitResults.root

/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v3//comb/fitAll/limits/T2tt/T2tt/limitResults.root
'''

#!/usr/bin/env python
import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers                import getObjFromFile
from StopsDilepton.tools.interpolate            import interpolate, rebin
from StopsDilepton.tools.niceColorPalette       import niceColorPalette
from StopsDilepton.tools.user                   import plot_directory, analysis_results
from StopsDilepton.analysis.plot.limitHelpers   import getContours, cleanContour

ROOT.gROOT.SetBatch(True)

#signalString = 'T8bbllnunu_XCha0p5_XSlep0p95'
#signalString = 'T8bbllnunu_XCha0p5_XSlep0p5'
#signalString = 'T8bbllnunu_XCha0p5_XSlep0p09'
#signalString = 'T8bbllnunu_XCha0p5_XSlep0p05'

#signalString = 'T2tt'
#year = 2017
#signalString = "T2bW"


from optparse import OptionParser
parser = OptionParser()
#parser.add_option("--file",             dest="filename",    default=None,   type="string", action="store",  help="Which file?")
parser.add_option("--signal",           action='store',     default='T2tt',          nargs='?', choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95", "T2bt","T2bW", "T8bbllnunu_XCha0p5_XSlep0p09", "ttHinv"], help="which signal?")
parser.add_option("--year",             dest="year",   type="int",    action="store",  help="Which year?")

(options, args) = parser.parse_args()
#year = int(options.year)
signalString = options.signal
#defFile = os.path.join(analysis_results, "%s/signalOnly/limits/%s/%s/limitResults.root"%(options.year,signalString,signalString))
defFile = os.path.join(analysis_results, "comb/signalOnly/limits/%s/%s/limitResults.root"%(signalString,signalString))
#defFile = os.path.join(analysis_results, "comb/fitAll/limits/%s/%s/limitResults.root"%(signalString,signalString))
#defFile = os.path.join(analysis_results, "%s/fitAll/limits/%s/%s/limitResults.root"%(options.year,signalString,signalString))

print defFile
if options.year == 2016:
    lumi    = 36.9
    #eraText =  "(2016)"
elif options.year == 2017:
    lumi    = 41.5
    #eraText =  "(2017)"
elif options.year == 2018:
    lumi    = 60 
    #eraText =  "(2018)"
else:
     lumi = 138.4
def toGraph2D(name,title,length,x,y,z):
    result = ROOT.TGraph2D(length)
    result.SetName(name)
    result.SetTitle(title)
    for i in range(length):
        result.SetPoint(i,x[i],y[i],z[i])
    h = result.GetHistogram()
    h.SetMinimum(min(z))
    h.SetMaximum(max(z))
    c = ROOT.TCanvas()
    result.Draw()
    del c
    #res = ROOT.TGraphDelaunay(result)
    return result


ifs = defFile.split('/')
plotDir = os.path.join(plot_directory,ifs[-3],'v3', ifs[-2]+'FR_signalOnly_combined')

#plotDir = os.path.join(plot_directory,ifs[-3],'v3', ifs[-2]+'FR_limitAll_combined')

#plotDir = os.path.join(plot_directory, ifs[-3], 'v3', ifs[-2]+'FR_%i'%options.year)

#plotDir = os.path.join(plot_directory, ifs[-3],'v3', ifs[-2]+'limitAll_FR_%i'%options.year)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

histsCol = {}

for i in ["exp","exp_up","exp_down","obs"]:
  histsCol[i] = getObjFromFile(defFile, i)

for i in ["obs_UL","obs_up","obs_down"]:
  histsCol[i] = histsCol["obs"].Clone(i)

for i in ["obs_up","obs_down"]:
  histsCol[i].Reset()


hists = {}

for i in ["exp","exp_up","exp_down","obs"]:
    tmp = getObjFromFile(defFile, i) #options.filename
    x = []
    y = []
    z = []
    binSizeX = 25
    binSizeY = 25
    #print binSizeX, binSizeY
    for ix in range(1,1625/25):
        for iy in range(0,1525/25):
            r = tmp.GetBinContent(ix,iy)
            if iy == 0 and tmp.GetBinContent(ix,iy+1)>0:
                r2 = tmp.GetBinContent(ix,iy+1)
                x.append((ix-1)*binSizeX)
                y.append((iy-1)*binSizeY)
                z.append(r2)
            if r>0:
                #print ix*binSizeX, iy*binSizeY, r
#                x.append((2*ix-3)/2.*binSizeX)
#                y.append((2*iy-3)/2.*binSizeY)
                x.append((ix-1)*binSizeX)
                y.append((iy-1)*binSizeY)
                z.append(r)
    
    a = toGraph2D(i,i,len(x),x,y,z)
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    bin_size = 25
    nxbins = max(1, min(500, int((xmax-xmin+bin_size/100.)/bin_size)))
    nybins = max(1, min(500, int((ymax-ymin+bin_size/100.)/bin_size)))
    a.SetNpx(nxbins)
    a.SetNpy(nybins)
    hists[i] = a.GetHistogram().Clone()
    hists[i].Draw()

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
        v2 = histsCol[xSecKey].GetBinContent(histsCol[xSecKey].FindBin(mStop, mNeu))
        if mStop>99 and v>0:
            #print mStop
            scaleup   = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=1) /xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            scaledown = xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=-1)/xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0)
            histsCol["obs_UL"].SetBinContent(histsCol[xSecKey].FindBin(mStop, mNeu), v2*xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0))
            hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*xSecSusy_.getXSec(channel='stop13TeV',mass=mStop,sigma=0))
            hists["obs_up"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaleup)
            hists["obs_down"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), v*scaledown)
            if signalString == 'T8bbllnunu_XCha0p5_XSlep0p05':#0.5, 160
                if mNeu > (0.5*mStop-100):
                    histsCol["obs_UL"].SetBinContent(histsCol[xSecKey].FindBin(mStop, mNeu), 0)
                    hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), 0)
            if signalString == 'T8bbllnunu_XCha0p5_XSlep0p5':    
                if mNeu > (mStop-150):
                    histsCol["obs_UL"].SetBinContent(histsCol[xSecKey].FindBin(mStop, mNeu), 0)
                    hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(mStop, mNeu), 0)

for bl in blanklist:
    hists["obs_UL"].SetBinContent(hists[xSecKey].FindBin(bl[0],bl[1]), 0)

for ix in range(hists[xSecKey].GetNbinsX()):
    for iy in range(hists[xSecKey].GetNbinsY()):
        if iy>(ix-4):
            #if hists["obs"].GetBinContent(ix,iy) == 0: hists["obs"].SetBinContent(ix,iy,1e6)
            for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
                if hists[i].GetBinContent(ix,iy) == 0:
                    hists[i].SetBinContent(ix,iy,1e6)
                if histsCol[i].GetBinContent(ix,iy) == 0:
                    histsCol[i].SetBinContent(ix,iy,1e6)

for i in ["exp", "exp_up", "exp_down", "obs", "obs_UL", "obs_up", "obs_down"]:
  hists[i + "_int"]    = hists[i]
  histsCol[i + "_int"]    = interpolate(histsCol[i])

for i in ["exp", "exp_up", "exp_down", "obs", "obs_up", "obs_down"]:
  #print i
  hists[i + "_smooth"] = hists[i + "_int"].Clone(i + "_smooth")
  #hists[i + "_smooth"] = rebin(hists[i + "_smooth"])
  hists[i + "_smooth"].Smooth(1,"k5a")

  histsCol[i + "_smooth"] = histsCol[i + "_int"].Clone(i + "_smooth")
  histsCol[i + "_smooth"].Smooth(1,"k5b")

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
fileIN = inputFile('SMS_limit.cfg')

# classic temperature histogra
xsecPlot = smsPlotXSEC(modelname, fileIN.HISTOGRAM, fileIN.OBSERVED, fileIN.EXPECTED, fileIN.ENERGY, fileIN.LUMI, fileIN.PRELIMINARY, "asdf")
xsecPlot.Draw( lumi = lumi, zAxis_range = (10**-3,10) )
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

