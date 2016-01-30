import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
def tdrStyle(padRightMargin=0.15):
    ROOT.setTDRStyle()
    if type(ROOT.tdrStyle)!=type(ROOT.gStyle):
        del ROOT.tdrStyle
    ROOT.setTDRStyle()
    ROOT.tdrStyle.SetPadRightMargin(padRightMargin)
