import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.interpolate import interpolate, rebin
from StopsDilepton.tools.niceColorPalette import niceColorPalette
from StopsDilepton.tools.user import plotDir
from StopsDilepton.analysis.run.limitHelpers import getContours, cleanContour

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--files", dest="filenames", default="", type="string", action="store", help="Which files?")
parser.add_option("--outfile", dest="outfile", default="", type="string", action="store", help="Output file")
(options, args) = parser.parse_args()

ROOT_colors = [ROOT.kBlack, ROOT.kRed-7, ROOT.kBlue-2, ROOT.kGreen+3, ROOT.kOrange+1,ROOT.kRed-3, ROOT.kAzure+6, ROOT.kCyan+3, ROOT.kOrange , ROOT.kRed-10]

if ',' in options.outfile:
    ofilenames = [os.path.join(plotDir, f) for f in options.outfile.split(',')]
else:
    ofilenames = [os.path.join(plotDir, options.outfile)]

for ofilename in ofilenames:
    if not os.path.exists(os.path.dirname(ofilename)):
        os.makedirs(os.path.dirname(ofilename))

files = []
legendNames={}
for f in options.filenames.split(','):
    if ":" in f:
        n,f=f.split(":")
        files.append(f)
        legendNames[f]=n

contours = {}
for i, f in enumerate(files):
    T2tt_exp        = getObjFromFile(f, "T2tt_exp")
    T2tt_exp_int = interpolate(T2tt_exp)
    T2tt_exp_smooth = T2tt_exp_int.Clone("T2tt_exp_smooth")
    T2tt_exp_smooth.Smooth()
    T2tt_exp_smooth.SetName("T2tt_exp_smooth")
    contours_exp      = getContours(T2tt_exp_smooth)
    contour_exp      = max(contours_exp     , key=lambda x:x.GetN()).Clone("contour_exp") if contours_exp else None
    if not contour_exp: continue
    cleanContour(contour_exp)
    contours[f]=contour_exp
    contours[f].SetLineColor(ROOT_colors[i])
    contours[f].SetFillColor(0)
    contours[f].SetMarkerStyle(0)
    contours[f].SetMarkerColor(ROOT_colors[i])


ROOT.gStyle.SetPadRightMargin(0.15)
c1 = ROOT.TCanvas()
niceColorPalette(255)

l=ROOT.TLegend(0.16,0.13,0.4,0.5)
l.SetFillColor(0)
l.SetShadowColor(ROOT.kWhite)
l.SetBorderSize(1)

#T2tt_exp.Reset()
opt=''
for i, f in enumerate(files):
    if contours.has_key(f):
        contours[f].GetXaxis().SetRangeUser(300,800)
        contours[f].GetYaxis().SetRangeUser(0,350)
        contours[f].GetXaxis().SetTitle("m_{#tilde{t}_{1}} (GeV)")
        contours[f].GetYaxis().SetTitle("m_{#tilde{#chi}_{1}^{0}} (GeV)")
        if legendNames.has_key(f):
            l.AddEntry(contours[f], legendNames[f])
        if i==0:
            contours[f].Draw(opt)
            opt=opt+'same'
        else:
            contours[f].Draw(opt)
#T2tt_exp.Draw('same')
l.Draw()
c1.Update()
for ofilename in ofilenames:
    c1.Print(ofilename)
