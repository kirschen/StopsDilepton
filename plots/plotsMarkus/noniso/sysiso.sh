# calculate uncertainty histos
#python sysiso.py --dpm --era Run2016 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --overwrite
#python sysiso.py --dpm --era Run2017 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1-badEEJetVeto --overwrite
#python sysiso.py --dpm --era Run2018 --reweightPU VUp --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --overwrite

# plot
python sysiso.py --dpm --era Run2016 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --normalize
python sysiso.py --dpm --era Run2017 --reweightPU Central --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1-badEEJetVeto --normalize
python sysiso.py --dpm --era Run2018 --reweightPU VUp --selection lepSel1Tight-njet4p-btag1p-dPhiJet0-dPhiJet1 --normalize
