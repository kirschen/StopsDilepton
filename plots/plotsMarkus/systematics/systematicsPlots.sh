python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys None --small
python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys jesTotalUp --small
python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys jesTotalDown --small

# run when all others are finished
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys combine --small
