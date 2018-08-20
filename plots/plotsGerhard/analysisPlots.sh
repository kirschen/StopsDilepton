#!/bin/bash

# plotdir
# analysisPlot_Reader_T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow
# analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow

python analysisPlots.py --MVA 0 1       --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 
python analysisPlots.py --MVA 0 0.2     --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 
python analysisPlots.py --MVA 0.2 0.4   --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1
python analysisPlots.py --MVA 0.4 0.6   --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 
python analysisPlots.py --MVA 0.6 0.8   --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 
python analysisPlots.py --MVA 0.8 1     --noData --signal T8bbllnunu --plot_directory analysisPlot_Reader_SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 
