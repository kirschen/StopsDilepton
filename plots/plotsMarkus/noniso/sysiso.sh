# calculate uncertainty histos
python sysiso.py --private --era Run2016 --plot_directory v0p19 --reweightPU Central --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 #--overwrite
python sysiso.py --private --era Run2017 --plot_directory v0p19 --reweightPU Central --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1-badEEJetVeto --add #--overwrite
python sysiso.py --private --era Run2018 --plot_directory v0p19 --reweightPU VUp --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --add #--overwrite

#python sysiso.py --dpm --era Run2016 --plot_directory v0p19 --reweightPU Central --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 #--overwrite
#python sysiso.py --dpm --era Run2017 --plot_directory v0p19 --reweightPU Central --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1-badEEJetVeto --add #--overwrite
#python sysiso.py --dpm --era Run2018 --plot_directory v0p19 --reweightPU VUp --normalize --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --add #--overwrite

# plot
#python sysiso.py --dpm --era Run2016 --plot_directory v0p19 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --normalize
#python sysiso.py --dpm --era Run2017 --plot_directory v0p19 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1-badEEJetVeto --normalize
#python sysiso.py --dpm --era Run2018 --plot_directory v0p19 --reweightPU VUp --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --normalize
