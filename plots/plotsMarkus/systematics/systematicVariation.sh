# Signal region

#python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --signal T2tt #--dpm --overwrite
#python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --signal T2tt --add #--dpm --overwrite
#python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag1p-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --signal T2tt --add #--dpm --overwrite


# Sidebands

python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --beta overflowBin #--dpm --overwrite 
python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite
python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize
python systematicVariation.py --era Run2016 --plot_directory v0p19 --reweightPU Central --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize



python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --add --beta overflowBin #--dpm --overwrite
python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite
python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize
python systematicVariation.py --era Run2017 --plot_directory v0p19 --reweightPU Central --selection lepSel-badEEJetVeto-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize



python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --add --beta overflowBin #--dpm --overwrite
python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-onZ --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite
python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1 --add --beta overflowBin #--dpm --overwrite

python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-onZ-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize
python systematicVariation.py --era Run2018 --plot_directory v0p19 --reweightPU VUp --selection lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonMiniIsoVeto-mll20-dPhiJet0-dPhiJet1-mt2ll100 --add --beta overflowBin #--dpm --overwrite --normalize




#####################################################################################################################################################################################




# Other control regions

#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet2p-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet2p-btag1p-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2016 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite

#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig0To12-njet2p-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig0To12-njet2p-btag1p-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig0To12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2017 --plot_directory v5 --reweightPU Central --scaling mc --variation_scaling --selection lepSel-badEEJetVeto-POGMetSig0To12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite

#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet2p-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet2p-btag1p-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet01-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite
#python systematicVariation.py --dpm --era Run2018 --plot_directory v3 --reweightPU VUp --scaling mc --variation_scaling --selection lepSel-POGMetSig0To12-njet01-btag1-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1 --overwrite

