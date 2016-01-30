import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/niceColorPalette.C")

def niceColorPalette(n=255):
    ROOT.niceColorPalette(n)
