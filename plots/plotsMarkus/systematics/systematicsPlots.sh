# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys None --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys jesTotalUp --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys jesTotalDown --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys PU36fbVVUp --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys PU36fbUp --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys unclustEnUp --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys unclustEnDown --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys BTag_SF_b_Down --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys BTag_SF_b_Up --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys BTag_SF_l_Down --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys BTag_SF_l_Up --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys DilepTriggerDown --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys DilepTriggerUp --small

# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys LeptonSFDown --small
# python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys LeptonSFUp --small

# run when all others are finished
python systematicsPlots.py --year 2018 --plot_directory v1 --runLocal --isChild --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --selectSys combine --small
