import ROOT

from StopsDilepton.samples.helpers import singleton as singleton

@singleton
class color():
  pass

color.data           = ROOT.kBlack
color.DY             = 8
color.DYToNuNu       = ROOT.kGreen+2
color.TTJets         = 7
color.singleTop      = 40
color.TTX            = ROOT.kMagenta
color.TTXNoZ         = ROOT.kPink-3
color.TTH            = ROOT.kPink-4
color.TTW            = ROOT.kPink-8
color.TTZ            = ROOT.kPink+9
color.TTZtoLLNuNu    = 6
color.TTZtoQQ        = ROOT.kBlue
color.TTG            = ROOT.kRed
color.TZQ            = ROOT.kPink-7
color.WJetsToLNu     = ROOT.kRed-10
color.diBoson        = ROOT.kOrange
color.ZZ             = ROOT.kOrange+1
color.WZ             = ROOT.kOrange+2
color.WG             = ROOT.kOrange-5
color.ZG             = ROOT.kOrange-10
color.triBoson       = ROOT.kYellow
color.WZZ            = ROOT.kYellow
color.WWG            = ROOT.kYellow-5
color.QCD            = 46
color.QCD_HT         = 46
color.QCD_Mu5        = 46
color.QCD_EMbcToE    = 46
color.QCD_Mu5EMbcToE = 46

color.other          = 46

color.T2tt_450_0     = ROOT.kBlue
