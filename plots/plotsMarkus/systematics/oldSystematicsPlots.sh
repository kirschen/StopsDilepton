# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys None --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys jesTotalUp --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys jesTotalDown --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys PUVVUp --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys PUUp --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys unclustEnUp --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys unclustEnDown --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys BTag_SF_b_Down --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys BTag_SF_b_Up --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys BTag_SF_l_Down --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys BTag_SF_l_Up --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys DilepTriggerDown --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys DilepTriggerUp --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys LeptonSFDown --small
# python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys LeptonSFUp --small

# run when all others are finished
python systematicsPlots.py --era Run2018 --plot_directory v2 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --reweightPU 'VUp' --selectSys combine --small
