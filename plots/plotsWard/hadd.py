import os, sys

dir = './trees_metcut_' + sys.argv[1] + '_metsig_' + sys.argv[2]

os.chdir(dir)

os.system('hadd -f DY_LO_SF.root DY_LO+Jets_ee.root DY_LO+Jets_mumu.root')
os.system('hadd -f DY_HT_LO_SF.root DY_LO_HT+Jets_ee.root DY_LO_HT+Jets_mumu.root')
os.system('hadd -f data.root DoubleEG_Run2015D_ee.root DoubleEG_Run2015D_emu.root DoubleEG_Run2015D_mumu.root DoubleMuon_Run2015D_ee.root DoubleMuon_Run2015D_emu.root DoubleMuon_Run2015D_mumu.root MuonEG_Run2015D_ee.root MuonEG_Run2015D_emu.root MuonEG_Run2015D_mumu.root')
os.system('hadd -f TTJets_SF.root TTJets_ee.root TTJets_mumu.root')
os.system('hadd -f TTX_SF.root TTX_ee.root TTJets_mumu.root')

"""
os.system('hadd -f DY_SF.root DY_ee.root DY_mumu.root')
os.system('hadd -f DY_HT_SF.root DY_HT_ee.root DY_HT_mumu.root')
os.system('hadd -f QCD_Mu_SF.root QCD_Mu_ee.root QCD_Mu_mumu.root')
os.system('hadd -f W+Jets_SF.root W+Jets_ee.root W+Jets_mumu.root')
os.system('hadd -f WW+WZ+ZZ_SF.root WW+WZ+ZZ_ee.root WW+WZ+ZZ_mumu.root')
os.system('hadd -f singletop_SF.root singletop_ee.root singletop_mumu.root')
os.system('hadd -f tt+Jets2L2Nu_SF.root tt+Jets2L2Nu_ee.root tt+Jets2L2Nu_mumu.root')
#os.system('hadd -f Rare_SF.root Rare_ee.root Rare_mumu.root')
os.system('hadd -f TTX_SF.root TTX_ee.root TTX_mumu.root')
os.system('hadd -f data.root DoubleEG_ee.root DoubleEG_emu.root DoubleEG_mumu.root DoubleMuon_ee.root DoubleMuon_emu.root DoubleMuon_mumu.root MuonEG_ee.root MuonEG_emu.root MuonEG_mumu.root')
os.system('hadd -f SMS_T2tt_2J_mStop425_mLSP325.root SMS_T2tt_2J_mStop425_mLSP325_ee.root SMS_T2tt_2J_mStop425_mLSP325_emu.root SMS_T2tt_2J_mStop425_mLSP325_mumu.root')
os.system('hadd -f SMS_T2tt_2J_mStop500_mLSP325.root SMS_T2tt_2J_mStop500_mLSP325_ee.root SMS_T2tt_2J_mStop500_mLSP325_emu.root SMS_T2tt_2J_mStop500_mLSP325_mumu.root')
os.system('hadd -f SMS_T2tt_2J_mStop650_mLSP325.root SMS_T2tt_2J_mStop650_mLSP325_ee.root SMS_T2tt_2J_mStop650_mLSP325_emu.root SMS_T2tt_2J_mStop650_mLSP325_mumu.root')
os.system('hadd -f SMS_T2tt_2J_mStop850_mLSP100.root SMS_T2tt_2J_mStop850_mLSP100_ee.root SMS_T2tt_2J_mStop850_mLSP100_emu.root SMS_T2tt_2J_mStop850_mLSP100_mumu.root')
"""

deletefiles = []
deletefiles += [i for i in os.listdir('./') if ("ee" in i or "mumu" in i)]
deletefiles += [i for i in os.listdir('./') if ("SMS" in i and 'emu' in i)]
deletefiles += [i for i in os.listdir('./') if ("Double" in i or "Muon" in i)]

deletefiles = list(set(deletefiles))

for f in deletefiles:
        os.remove(f)
