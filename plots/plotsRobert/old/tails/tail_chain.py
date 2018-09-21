cut = "nJetGood==0&&(1)&&Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2&&dl_mass>20&&met_pt>150&&(Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&Flag_badChargedHadronSummer2016&&Flag_badMuonSummer2016&&weight>0)&&(nGoodMuons==2&&nGoodElectrons==0&&l1_pt>25&&l1_relIso03<0.12&&l2_relIso03<0.12&&isOS&&isMuMu&&abs(dl_mass-91.1876)<15)"
#data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"

#postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
#from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *

#DoubleMuon_Run2016BCD_backup as DoubleMuon_Run2016BCD_rereco

#data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
#postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
#from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import DoubleMuon_Run2016BCD_backup as DoubleMuon_Run2016BCD_prompt
#
#DoubleMuon_Run2016BCD_prompt.chain.Scan("run:lumi:evt", cut.replace("relIso03", "miniIso").replace("Summer2016",""), "@colsize=14")
#DoubleMuon_Run2016BCD_rereco.chain.Scan("run:lumi:evt", cut, "@colsize=14")
