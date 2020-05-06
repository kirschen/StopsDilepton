# check METSignificance
python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22 --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1
python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22 --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1
python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22 --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1
# ------------

#python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ
#python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll140
#python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll240
#python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0
#python analysisPlots.py --era Run2016 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0-dPhiJet1
#
#python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ
#python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll140
#python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll240
#python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0
#python analysisPlots.py --era Run2017 --reweightPU Central --plot_directory v0p22_dPhiJet --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0-dPhiJet1
#
#python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ
#python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll140
#python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-mt2ll240
#python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0
#python analysisPlots.py --era Run2018 --reweightPU VUp --plot_directory v0p22_dPhiJet --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ-dPhiJet0-dPhiJet1


#python analysisPlots.py --year 2018 --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ
#python analysisPlots.py --year 2018 --era ABC --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ
#python analysisPlots.py --year 2018 --era D --selection lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-onZ

# without Met/MetSig cut
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1

#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --preHEM

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --postHEM


#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --preHEM

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --noReweightPU --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --postHEM


#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25
#
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --preHEM
#
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --postHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig25 --postHEM


######################
# Analysis Note 2017 #
######################

# Control plots with 2016 data
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2016 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1


# Control plots with 2017 data
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1

#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2017 --signal T2tt --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12


# Control plots with 2018 data
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv-dPhiJet0-dPhiJet1

#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet1-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig0To12
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --preHEM
#python analysisPlots.py --plot_directory v0 --year 2018 --signal T2tt --splitBosons --selection lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12 --postHEM


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

