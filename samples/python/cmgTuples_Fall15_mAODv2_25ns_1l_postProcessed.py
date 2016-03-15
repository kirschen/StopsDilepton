import copy, os, sys
from StopsDilepton.tools.user import data_output_directory
from RootTools.core.Sample import Sample
import ROOT


dirs = {}
dirs['DY']               = ["DYJetsToLL_M10to50", "DYJetsToLL_M50"]
dirs['DY_LO']            = ["DYJetsToLL_M5to50_LO", "DYJetsToLL_M50_LO"]
dirs['DY_HT_LO']         = ["DYJetsToLL_M50_LO_lheHT100.0", "DYJetsToLL_M50_HT100to200", "DYJetsToLL_M50_HT200to400", "DYJetsToLL_M50_HT400to600", "DYJetsToLL_M50_HT600toInf", "DYJetsToLL_M5to50_LO_lheHT100.0", "DYJetsToLL_M5to50_HT100to200", "DYJetsToLL_M5to50_HT200to400", "DYJetsToLL_M5to50_HT400to600", "DYJetsToLL_M5to50_HT600toInf"]
dirs['TTJets']           = ["TTJets_comb"]
dirs['TTJets_LO']        = ["TTJets_LO"]
dirs['TTLep_pow']        = ["TTLep_pow"]
dirs['TTJets_Lep']       = ["TTJets_DiLepton_comb", "TTJets_SingleLeptonFromTbar_comb", "TTJets_SingleLeptonFromT_comb"]
dirs['TTJets_HT_LO']     = ["TTJets_LO_HT600to800_comb", "TTJets_LO_HT800to1200", "TTJets_LO_HT1200to2500_comb", "TTJets_LO_HT2500toInf"]
dirs['singleT']          = ["TBar_tWch", "TToLeptons_sch", "TToLeptons_tch_amcatnlo_comb", "T_tWch"] # ["TBar_tWch_DS", "T_tWch_DS"]
dirs['TTX']              = ["TTHbb_comb", "TTHnobb", "TTWToLNu", "TTWToQQ",  "TTZToLLNuNu", "TTZToQQ", "tZq_ll", "tZq_nunu"]
dirs['TTXNoZ']           = ["TTHbb_comb", "TTHnobb", "TTWToLNu", "TTWToQQ", "tZq_ll", "tZq_nunu"]
dirs['TTH']              = ["TTHbb_comb", "TTHnobb"]
dirs['TTW']              = ["TTWToLNu", "TTWToQQ"]
dirs['TTZ']              = ["TTZToLLNuNu", "TTZToQQ"]
dirs['TZQ']              = ["tZq_ll", "tZq_nunu"]
dirs['WJetsToLNu']       = ["WJetsToLNu"]
dirs['WJetsToLNu_LO']    = ["WJetsToLNu_LO"]
dirs['WJetsToLNu_HT']    = ["WJetsToLNu_HT100to200", "WJetsToLNu_HT200to400", "WJetsToLNu_HT400to600", "WJetsToLNu_HT600to800", "WJetsToLNu_HT800to1200", "WJetsToLNu_HT1200to2500", "WJetsToLNu_HT2500toInf"]
dirs['diBoson']          = ["VVTo2L2Nu", "WWTo2L2Nu", "WWToLNuQQ", "WZTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu", "ZZTo2L2Q", "ZZTo2Q2Nu"]
dirs['ZZ']               = ["ZZTo2L2Q", "ZZTo2Q2Nu"]
dirs['WZ']               = ["WZTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu"]
dirs['triBoson']         = ["WWZ","WZZ","ZZZ"]
dirs['QCD_HT']           = ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500", "QCD_HT1500to2000", "QCD_HT2000toInf"]
dirs['QCD_Mu5']          = ["QCD_Pt20to30_Mu5", "QCD_Pt50to80_Mu5", "QCD_Pt80to120_Mu5", "QCD_Pt120to170_Mu5", "QCD_Pt170to300_Mu5", "QCD_Pt300to470_Mu5", "QCD_Pt470to600_Mu5", "QCD_Pt600to800_Mu5", "QCD_Pt800to1000_Mu5", "QCD_Pt1000toInf_Mu5"]
dirs['QCD_EM+bcToE']     = ["QCD_Pt_15to20_bcToE", "QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt30to50_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched", "QCD_Pt300toInf_EMEnriched"]
dirs['QCD_Mu5+EM+bcToE'] = ["QCD_Pt20to30_Mu5", "QCD_Pt50to80_Mu5", "QCD_Pt80to120_Mu5", "QCD_Pt120to170_Mu5", "QCD_Pt170to300_Mu5", "QCD_Pt300to470_Mu5", "QCD_Pt470to600_Mu5", "QCD_Pt600to800_Mu5", "QCD_Pt800to1000_Mu5", "QCD_Pt1000toInf_Mu5", "QCD_Pt_15to20_bcToE", "QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt30to50_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched", "QCD_Pt300toInf_EMEnriched"]
dirs['QCD']              = ["QCD_Pt10to15", "QCD_Pt15to30", "QCD_Pt30to50", "QCD_Pt50to80", "QCD_Pt80to120", "QCD_Pt120to170", "QCD_Pt170to300", "QCD_Pt300to470", "QCD_Pt470to600", "QCD_Pt600to800", "QCD_Pt800to1000", "QCD_Pt1000to1400", "QCD_Pt1400to1800", "QCD_Pt1800to2400", "QCD_Pt2400to3200", "QCD_Pt3200"]

for key in dirs:
  dirs[key] = [data_output_directory + '/postProcessed_Fall15_mAODv2/dilepTiny/' + dir for dir in dirs[key]]

DY             = Sample.fromDirectory(name="DY",               treeName="Events", isData=False, color=8,              texName="DY + Jets",                 directory=dirs['DY'])
#DY_LO          = Sample.fromDirectory(name="DY_LO",            treeName="Events", isData=False, color=8,              texName="DY + Jets (LO)",            directory=dirs['DY_LO'])
#DY_HT_LO       = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=8,              texName="DY + Jets (LO,HT)",         directory=dirs['DY_HT_LO'])
TTJets         = Sample.fromDirectory(name="TTJets",           treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets",           directory=dirs['TTJets'])
TTJets_LO      = Sample.fromDirectory(name="TTJets_LO",        treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets (LO)",      directory=dirs['TTJets_LO'])
TTLep_pow      = Sample.fromDirectory(name="TTLep_pow",        treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets (lep,pow)", directory=dirs['TTLep_pow'])
TTJets_Lep     = Sample.fromDirectory(name="TTJets_Lep",       treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets (lep)",     directory=dirs['TTJets_Lep'])
TTJets_HT_LO   = Sample.fromDirectory(name="TTJets_HT_LO",     treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets (HT,LO)",   directory=dirs['TTJets_HT_LO'])
#singleTop      = Sample.fromDirectory(name="singleT",          treeName="Events", isData=False, color=40,             texName="single top",                directory=dirs['singleT'])
#TTX            = Sample.fromDirectory(name="TTX",              treeName="Events", isData=False, color=ROOT.kPink,     texName="t#bar{t}X",                 directory=dirs['TTX'])
#TTXNoZ         = Sample.fromDirectory(name="TTXNoZ",           treeName="Events", isData=False, color=ROOT.kPink,     texName="t#bar{t}H/W, tZq",          directory=dirs['TTXNoZ'])
#TTH            = Sample.fromDirectory(name="TTH",              treeName="Events", isData=False, color=ROOT.kPink-4,   texName="t#bar{t}H",                 directory=dirs['TTH'])
TTW            = Sample.fromDirectory(name="TTW",              treeName="Events", isData=False, color=ROOT.kPink-8,   texName="t#bar{t}W",                 directory=dirs['TTW'])
TTZ            = Sample.fromDirectory(name="TTZ",              treeName="Events", isData=False, color=ROOT.kPink+9,   texName="t#bar{t}Z",                 directory=dirs['TTZ'])
TZQ            = Sample.fromDirectory(name="TZQ",              treeName="Events", isData=False, color=ROOT.kPink-7,   texName="tZq",                       directory=dirs['TZQ'])
WJetsToLNu     = Sample.fromDirectory(name="WJetsToLNu",       treeName="Events", isData=False, color=ROOT.kRed-10,   texName="W(l,#nu) + Jets",           directory=dirs['WJetsToLNu'])
WJetsToLNu_LO  = Sample.fromDirectory(name="WJetsToLNu_LO",    treeName="Events", isData=False, color=ROOT.kRed-10,   texName="W(l,#nu) + Jets (LO)",      directory=dirs['WJetsToLNu_LO'])
#WJetsToLNu_HT  = Sample.fromDirectory(name="WJetsToLNu_HT",    treeName="Events", isData=False, color=ROOT.kRed-10,   texName="W(l,#nu) + Jets (HT)",      directory=dirs['WJetsToLNu_HT'])
#diBoson        = Sample.fromDirectory(name="diBoson",          treeName="Events", isData=False, color=ROOT.kOrange,   texName="WW/ZZ/WZ",                  directory=dirs['diBoson'])
ZZ             = Sample.fromDirectory(name="ZZ",               treeName="Events", isData=False, color=ROOT.kOrange+1, texName="ZZ",                        directory=dirs['ZZ'])
WZ             = Sample.fromDirectory(name="WZ",               treeName="Events", isData=False, color=ROOT.kOrange+2, texName="WZ",                        directory=dirs['WZ'])
#triBoson       = Sample.fromDirectory(name="triBoson",         treeName="Events", isData=False, color=ROOT.kYellow,   texName="WWZ,WZZ,ZZZ",               directory=dirs['triBoson'])
QCD_HT         = Sample.fromDirectory(name="QCD_HT",           treeName="Events", isData=False, color=46,             texName="QCD (HT)",                  directory=dirs['QCD_HT'])
#QCD_Mu5        = Sample.fromDirectory(name="QCD_Mu5",          treeName="Events", isData=False, color=46,             texName="QCD (Mu5)",                 directory=dirs['QCD_Mu5'])
#QCD_EMbcToE    = Sample.fromDirectory(name="QCD_EM+bcToE",     treeName="Events", isData=False, color=46,             texName="QCD (Em+bcToE)",            directory=dirs['QCD_EM+bcToE'])
#QCD_Mu5EMbcToE = Sample.fromDirectory(name="QCD_Mu5+EM+bcToE", treeName="Events", isData=False, color=46,             texName="QCD (Mu5+Em+bcToE)",        directory=dirs['QCD_Mu5+EM+bcToE'])
#QCD_Pt         = Sample.fromDirectory(name="QCD",              treeName="Events", isData=False, color=46,             texName="QCD",                       directory=dirs['QCD'])
