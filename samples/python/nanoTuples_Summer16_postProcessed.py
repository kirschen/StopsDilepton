import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.samples.color import color

# Data directory
try:
    data_directory = sys.modules['__main__'].data_directory
except:
    from StopsDilepton.tools.user import data_directory as user_data_directory
    data_directory = user_data_directory 

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "stops_2016_nano_v2/dilep/"

logger.info("Loading MC samples from directory %s", os.path.join(data_directory, postProcessing_directory))

DY_M5to50_HT = [
                "DYJetsToLL_M10to50_LO_lheHT70", 
                "DYJetsToLL_M5to50_HT70to100",
                "DYJetsToLL_M5to50_HT100to200_comb",
                "DYJetsToLL_M5to50_HT200to400_comb",
                "DYJetsToLL_M5to50_HT400to600_comb",
                "DYJetsToLL_M5to50_HT600toInf_comb"
                ] 

DY_M50_HT =[
            "DYJetsToLL_M50_LO_ext1_comb_lheHT70", 
            "DYJetsToLL_M50_HT70to100",
            "DYJetsToLL_M50_HT100to200_comb",
            "DYJetsToLL_M50_HT200to400_comb",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ] 


dirs = {}
dirs['DY']               = ["DYJetsToLL_M50_ext2"]#, "DYJetsToLL_M10to50_LO" ]
dirs['DY_LO']            = ["DYJetsToLL_M50_LO_ext1_comb"]
dirs['DY_HT_LO']         =  DY_M50_HT + DY_M5to50_HT

dirs['TTLep_pow']        = ["TTLep_pow"]

dirs['singleTop']        = ["TBar_tWch_ext", "T_tWch_ext"]#, "TToLeptons_tch_powheg", "TBarToLeptons_tch_powheg"]
dirs['singleTop_tch']    = ["T_tch_powheg", "TBar_tch_powheg"]
dirs['singleTop_sch']    = ["TToLeptons_sch_amcatnlo"]

dirs['Top_pow']          = dirs['TTLep_pow'] + dirs['singleTop']

dirs['TZQ']              = ["tZq_ll_ext"]#, "tZq_nunu_reHLT"]
dirs['TWZ']              = ["tWll", "tWnunu"]
dirs['TTW']              = ["TTWToLNu_ext_comb"]#, "TTWToQQ"]

dirs['TTH']              = ["TTHbb"]#, "TTHnobb_mWCutfix_ext"] FIXME got deleted, need to be re-added later
dirs['TTZtoLLNuNu']      = ["TTZToLLNuNu_ext1_comb"]
dirs['TTZtoQQ']          = ["TTZToQQ"]
dirs['TTZ']              = ["TTZToLLNuNu_ext1_comb", "TTZToQQ"]

dirs['TTXNoZ']           = dirs['TTH'] + dirs['TTW'] + dirs['TWZ'] + dirs['TZQ']
dirs['TTX']              = dirs['TTXNoZ'] + dirs['TTZ']

#dirs['WJetsToLNu']       = ["WJetsToLNu"]
##dirs['WJetsToLNu_LO']    = ["WJetsToLNu_LO"]
##dirs['WJetsToLNu_HT']    = ["WJetsToLNu_HT100to200_comb", "WJetsToLNu_HT200to400_comb", "WJetsToLNu_HT400to600", "WJetsToLNu_HT600to800", "WJetsToLNu_HT800to1200", "WJetsToLNu_HT1200to2500", "WJetsToLNu_HT2500toInf"]
dirs['diBosonInclusive'] = ["WW", "WZ", "ZZ"]
dirs['WW']               = ["WWToLNuQQ_comb"]
#dirs['WW_']              = ["WWToLNuQQ_comb","WWTo2L2Nu"]
#dirs['WWTo2L2Nu']        = ["WWTo2L2Nu"]
dirs['VVTo2L2Nu']        = ["VVTo2L2Nu_comb"]
dirs['WZ']               = ["WZTo1L1Nu2Q",  "WZTo3LNu_comb"] # "WZTo1L3Nu" "WZTo2L2Q",missing
dirs['ZZ']               = ["ZZTo2L2Q", "ZZTo2Q2Nu"]
#dirs['ZZTo2L2Nu']        = ["ZZTo2L2Nu"]
#dirs['ZZ_']              = ["ZZTo2L2Q", "ZZTo2Q2Nu","ZZTo2L2Nu"]
dirs['diBoson']          = dirs['WW'] + dirs['WZ'] + dirs['ZZ'] #+ dirs['VVTo2L2Nu'] #FIXME Got deleted
#dirs['diBoson_']         = dirs['WW_'] + dirs['WZ'] + dirs['ZZ_']
dirs['triBoson']         = ["WZZ","ZZZ"] 
#dirs['triBoson']         = ["WWZ","WZZ","ZZZ"] #FIXME... WWZ was deleted 
dirs['multiBoson']       = dirs['diBoson'] + dirs['triBoson']
#dirs['EWK']              = dirs['diBoson'] + dirs['triBoson'] + dirs['TTX']
#dirs['QCD_HT']           = ["QCD_HT300to500_comb", "QCD_HT500to700_ext", "QCD_HT700to1000_comb", "QCD_HT1000to1500_comb", "QCD_HT1500to2000_comb", "QCD_HT2000toInf_comb"]
##dirs['QCD_Mu5']          = ["QCD_Pt20to30_Mu5", "QCD_Pt50to80_Mu5", "QCD_Pt80to120_Mu5", "QCD_Pt120to170_Mu5", "QCD_Pt170to300_Mu5", "QCD_Pt300to470_Mu5", "QCD_Pt470to600_Mu5", "QCD_Pt600to800_Mu5", "QCD_Pt800to1000_Mu5", "QCD_Pt1000toInf_Mu5"]
##dirs['QCD_EM+bcToE']     = ["QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched"]
##dirs['QCD_EM+bcToE']    = ["QCD_Pt_15to20_bcToE", "QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt30to50_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched", "QCD_Pt300toInf_EMEnriched"]
##dirs['QCD_Mu5+EM+bcToE'] = ["QCD_Pt20to30_Mu5", "QCD_Pt50to80_Mu5", "QCD_Pt80to120_Mu5", "QCD_Pt120to170_Mu5", "QCD_Pt170to300_Mu5", "QCD_Pt300to470_Mu5", "QCD_Pt470to600_Mu5", "QCD_Pt600to800_Mu5", "QCD_Pt800to1000_Mu5", "QCD_Pt1000toInf_Mu5", "QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched"]
##dirs['QCD_Mu5+EM+bcToE']= ["QCD_Pt20to30_Mu5", "QCD_Pt50to80_Mu5", "QCD_Pt80to120_Mu5", "QCD_Pt120to170_Mu5", "QCD_Pt170to300_Mu5", "QCD_Pt300to470_Mu5", "QCD_Pt470to600_Mu5", "QCD_Pt600to800_Mu5", "QCD_Pt800to1000_Mu5", "QCD_Pt1000toInf_Mu5", "QCD_Pt_15to20_bcToE", "QCD_Pt_20to30_bcToE", "QCD_Pt_30to80_bcToE", "QCD_Pt_80to170_bcToE", "QCD_Pt_170to250_bcToE", "QCD_Pt_250toInf_bcToE", "QCD_Pt15to20_EMEnriched", "QCD_Pt20to30_EMEnriched", "QCD_Pt30to50_EMEnriched", "QCD_Pt50to80_EMEnriched", "QCD_Pt80to120_EMEnriched", "QCD_Pt120to170_EMEnriched", "QCD_Pt170to300_EMEnriched", "QCD_Pt300toInf_EMEnriched"]
##dirs['QCD']              = ["QCD_Pt30to50", "QCD_Pt50to80", "QCD_Pt80to120", "QCD_Pt120to170", "QCD_Pt170to300", "QCD_Pt300to470", "QCD_Pt470to600", "QCD_Pt600to800", "QCD_Pt800to1000", "QCD_Pt1000to1400", "QCD_Pt1400to1800", "QCD_Pt1800to2400", "QCD_Pt2400to3200"]
##dirs['QCD']             = ["QCD_Pt10to15", "QCD_Pt15to30", "QCD_Pt30to50", "QCD_Pt50to80", "QCD_Pt80to120", "QCD_Pt120to170", "QCD_Pt170to300", "QCD_Pt300to470", "QCD_Pt470to600", "QCD_Pt600to800", "QCD_Pt800to1000", "QCD_Pt1000to1400", "QCD_Pt1400to1800", "QCD_Pt1800to2400", "QCD_Pt2400to3200", "QCD_Pt3200"]
#
#dirs['nonTop']           = dirs['multiBoson'] + dirs['DY_HT_LO'] + dirs['TTZ_LO'] + dirs['TTXNoZ']
#
##dirs['WGToLNuG']     = ["WGToLNuG"]
#dirs['ZGTo2LG']      = ["ZGTo2LG_ext"]
##dirs['WGJets']       = ["WGJets"]
#dirs['ZGJets']       = ["ZGJets"]
#dirs['ZG']           = dirs['ZGTo2LG'] + dirs['ZGJets']
#

dirs['T2tt_mStop_850_mLSP_100'] = ['T2tt_mStop_850_mLSP_100']
dirs['T2tt_mStop_500_mLSP_325'] = ['T2tt_mStop_500_mLSP_325']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

#
DY_16              = Sample.fromDirectory(name="DY",               treeName="Events", isData=False, color=color.DY,              texName="DY",                                directory=directories['DY'])
DY_LO_16           = Sample.fromDirectory(name="DY_LO",            treeName="Events", isData=False, color=color.DY,              texName="DY (LO)",                           directory=directories['DY_LO'])
DY_HT_LO_16        = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_HT_LO'])
Top_pow_16         = Sample.fromDirectory(name="Top_pow",          treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t}/single-t",                 directory=directories['Top_pow'])
singleTop_16      = Sample.fromDirectory(name="singleTop",        treeName="Events", isData=False, color=color.singleTop,       texName="single top",                        directory=directories['singleTop'])
singleTop_tch_16  = Sample.fromDirectory(name="singleTop_tch",    treeName="Events", isData=False, color=color.singleTop,       texName="single top tch",                    directory=directories['singleTop_tch'])
singleTop_sch_16  = Sample.fromDirectory(name="singleTop_sch",    treeName="Events", isData=False, color=color.singleTop,       texName="single top sch",                    directory=directories['singleTop_sch'])
TTX_16            = Sample.fromDirectory(name="TTX",              treeName="Events", isData=False, color=color.TTX,             texName="t#bar{t}H/W/Z, tZq",                directory=directories['TTX'])
TTXNoZ_16         = Sample.fromDirectory(name="TTXNoZ",           treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}H/W, tZq, tWZ",             directory=directories['TTXNoZ'])
TTH_16            = Sample.fromDirectory(name="TTH",              treeName="Events", isData=False, color=color.TTH,             texName="t#bar{t}H",                         directory=directories['TTH'])
TTW_16            = Sample.fromDirectory(name="TTW",              treeName="Events", isData=False, color=color.TTW,             texName="t#bar{t}W",                         directory=directories['TTW'])
TTZ_16            = Sample.fromDirectory(name="TTZ",              treeName="Events", isData=False, color=color.TTZ,             texName="t#bar{t}Z",                         directory=directories['TTZ'])
TTZtoLLNuNu_16    = Sample.fromDirectory(name="TTZtoNuNu",        treeName="Events", isData=False, color=color.TTZtoLLNuNu,     texName="t#bar{t}Z (l#bar{l}/#nu#bar{#nu})", directory=directories['TTZtoLLNuNu'])
TTZtoQQ_16        = Sample.fromDirectory(name="TTZtoQQ",          treeName="Events", isData=False, color=color.TTZtoQQ,         texName="t#bar{t}Z (q#bar{q})",              directory=directories['TTZtoQQ'])
TZQ_16            = Sample.fromDirectory(name="TZQ",              treeName="Events", isData=False, color=color.TZQ,             texName="tZq",                               directory=directories['TZQ'])
TWZ_16            = Sample.fromDirectory(name="TWZ",              treeName="Events", isData=False, color=color.TWZ,             texName="tWZ",                               directory=directories['TWZ'])
#WJetsToLNu     = Sample.fromDirectory(name="WJetsToLNu",       treeName="Events", isData=False, color=color.WJetsToLNu,      texName="W(l,#nu) + Jets",                   directory=directories['WJetsToLNu'])
##WJetsToLNu_LO  = Sample.fromDirectory(name="WJetsToLNu_LO",    treeName="Events", isData=False, color=color.WJetsToLNu,      texName="W(l,#nu) + Jets (LO)",              directory=directories['WJetsToLNu_LO'])
##WJetsToLNu_HT  = Sample.fromDirectory(name="WJetsToLNu_HT",    treeName="Events", isData=False, color=color.WJetsToLNu,      texName="W(l,#nu) + Jets (HT)",              directory=directories['WJetsToLNu_HT'])
diBoson_16        = Sample.fromDirectory(name="diBoson",          treeName="Events", isData=False, color=color.diBoson,         texName="VV (excl.)",                        directory=directories['diBoson'])
#VVTo2L2Nu_16      = Sample.fromDirectory(name="VVTo2L2Nu",               treeName="Events", isData=False, color=color.VV,              texName="VV to ll#nu#nu",             directory=directories['VVTo2L2Nu'])
triBoson_16       = Sample.fromDirectory(name="triBoson",         treeName="Events", isData=False, color=color.triBoson,        texName="WWZ,WZZ,ZZZ",                       directory=directories['triBoson'])
multiBoson_16     = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])
#QCD_HT         = Sample.fromDirectory(name="QCD_HT",           treeName="Events", isData=False, color=color.QCD,             texName="QCD (HT)",                          directory=directories['QCD_HT'])
##QCD_Mu5        = Sample.fromDirectory(name="QCD_Mu5",          treeName="Events", isData=False, color=color.QCD,             texName="QCD (Mu5)",                         directory=directories['QCD_Mu5'])
##QCD_EMbcToE    = Sample.fromDirectory(name="QCD_EM+bcToE",     treeName="Events", isData=False, color=color.QCD,             texName="QCD (Em+bcToE)",                    directory=directories['QCD_EM+bcToE'])
##QCD_Mu5EMbcToE = Sample.fromDirectory(name="QCD_Mu5+EM+bcToE", treeName="Events", isData=False, color=color.QCD,             texName="QCD (Mu5+Em+bcToE)",                directory=directories['QCD_Mu5+EM+bcToE'])
##QCD_Pt         = Sample.fromDirectory(name="QCD",              treeName="Events", isData=False, color=color.QCD,             texName="QCD",                               directory=directories['QCD'])
#
##WGToLNuG = Sample.fromDirectory(name="WGToLNuG",       treeName="Events", isData=False, color=color.diBoson,       texName="WGToLNuG",                       directory=directories['WGToLNuG'])
##ZGTo2LG  = Sample.fromDirectory(name="ZGTo2LG",       treeName="Events", isData=False, color=color.diBoson,        texName="ZGTo2LG",                       directory=directories['ZGTo2LG'] )
##WGJets   = Sample.fromDirectory(name="WGJets",       treeName="Events", isData=False, color=color.diBoson,         texName="WGJets",                       directory=directories['WGJets']  )
##ZGJets   = Sample.fromDirectory(name="ZGJets",       treeName="Events", isData=False, color=color.diBoson,         texName="ZGJets",                       directory=directories['ZGJets']  )
#ZG        = Sample.fromDirectory(name="ZG",            treeName="Events", isData=False, color=color.QCD,             texName="ZG",                           directory=directories['ZG']  )
#EWK        = Sample.fromDirectory(name="EWK",            treeName="Events", isData=False, color=color.QCD,             texName="EWK",                           directory=directories['EWK']  )

## FullSim signals
T2tt_mStop_850_mLSP_100 = Sample.fromDirectory(name="T2tt_mStop_850_mLSP_100",  treeName="Events", isData=False, color=color.DY,    texName="T2tt(850,100)",                    directory=directories['T2tt_mStop_850_mLSP_100'])
T2tt_mStop_500_mLSP_325 = Sample.fromDirectory(name="T2tt_mStop_500_mLSP_325",  treeName="Events", isData=False, color=color.DY,    texName="T2tt(500,325)",                    directory=directories['T2tt_mStop_500_mLSP_325'])


Top_gaussian         = copy.deepcopy(Top_pow_16)
Top_gaussian.name    = Top_pow_16.name + ' (gaussian)'
Top_gaussian.texName = Top_pow_16.texName + ' (gaussian)'
Top_gaussian.color   = ROOT.kCyan
Top_gaussian.setSelectionString('abs(met_pt-met_genPt)&&abs(met_pt-met_genPt)<=50&&l1_mcMatchId!=0&&l2_mcMatchId!=0')


Top_nongaussian         = copy.deepcopy(Top_pow_16)
Top_nongaussian.name    = Top_pow_16.name + ' (non-gaussian)'
Top_nongaussian.texName = Top_pow_16.texName + ' (non-gaussian)'
Top_nongaussian.color   = ROOT.kCyan + 2
Top_nongaussian.setSelectionString('abs(met_pt-met_genPt)>50&&l1_mcMatchId!=0&&l2_mcMatchId!=0')


Top_fakes         = copy.deepcopy(Top_pow_16)
Top_fakes.name    = Top_pow_16.name + ' (fakes)'
Top_fakes.texName = Top_pow_16.texName + ' (fakes)'
Top_fakes.color   = ROOT.kCyan + 4
Top_fakes.setSelectionString('!(l1_mcMatchId!=0&&l2_mcMatchId!=0)')


