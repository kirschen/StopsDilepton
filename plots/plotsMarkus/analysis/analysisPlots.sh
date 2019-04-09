######################
# Analysis Note 2017 #
######################

# Analysis Note figure 16a-g with 2016 data
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1

# Analysis Note figure 16a-g with 2017 data
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1

python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12 --small

# Analysis Note figure 16a-g with 2018 data
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1


# 2018: preHEM and postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1 --postHEM

# 2018: HEMJetVeto
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-HEMJetVeto


# 2016-2018: Tails
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-mt2ll100
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-mt2ll100
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-mt2ll100


# 2016-2018: POGMetSig plots
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-POGMetSig12-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-POGMetSig12-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-POGMetSig12-dPhiJet0-dPhiJet1

# 2016-2018: Pileup < 25
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-nPV0to25
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-nPV0to25
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-nPV0to25
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-nPV0to25 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-nPV0to25 --postHEM

