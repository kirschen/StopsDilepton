import ROOT
import sys, ctypes, os
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.interpolate import interpolate, rebin
from StopsDilepton.tools.niceColorPalette import niceColorPalette
from StopsDilepton.tools.localInfo import plotDir
from StopsDilepton.analysis.run.limitHelpers import getContours, cleanContour

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--files", dest="filenames", default="", type="string", action="store", help="Which files?")
parser.add_option("--outfile", dest="outfile", default="", type="string", action="store", help="Output file")
(options, args) = parser.parse_args()

ofilename = os.path.join(plotDir, options.outfile)
if not os.path.exists(os.path.dirname(ofilename)):
    os.makedirs(os.path.dirname(ofilename))

files=options.filenames.split(',')
print files
assert len(files)==2, "Need two files"

T2tt_exp = {}
for i, f in enumerate(files):
    T2tt_exp[i]= getObjFromFile(f, "T2tt_exp")

ROOT.gStyle.SetPadRightMargin(0.15)
niceColorPalette(255)

T2tt_exp[0].Divide(T2tt_exp[1])

c1 = ROOT.TCanvas()
T2tt_exp[0].SetMarkerSize(0.4)
T2tt_exp[0].GetXaxis().SetTitle("m_{#tilde{t}_{1}} (GeV)")
T2tt_exp[0].GetYaxis().SetTitle("m_{#tilde{#chi}_{1}^{0}} (GeV)")

T2tt_exp[0].Draw('text45')
T2tt_exp[0].Draw('COLZ')
c1.Update()
c1.Print(ofilename)
