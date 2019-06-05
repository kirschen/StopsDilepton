import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.samples.color import color

# Data directory
try:
    data_directory_ = sys.modules['__main__'].data_directory
except:
    from StopsDilepton.samples.default_locations import default_locations
    data_directory_ = default_locations.mc_2018_data_directory 

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory_ = sys.modules['__main__'].postProcessing_directory
except:
  from StopsDilepton.samples.default_locations import default_locations
  postProcessing_directory_ = default_locations.mc_2018_postProcessing_directory 


logger.info("Loading MC samples from directory %s", os.path.join(data_directory_, postProcessing_directory_))

DY_M5to50_HT = [
                "DYJetsToLL_M10to50_LO_lheHT70", 
                "DYJetsToLL_M4to50_HT70to100",
                "DYJetsToLL_M4to50_HT100to200",
                "DYJetsToLL_M4to50_HT200to400",
                "DYJetsToLL_M4to50_HT400to600",
                "DYJetsToLL_M4to50_HT600toInf"
                ] 

DY_M50_HT =[
            "DYJetsToLL_M50_LO_lheHT70", 
            "DYJetsToLL_M50_HT70to100",
            "DYJetsToLL_M50_HT100to200",
            "DYJetsToLL_M50_HT200to400",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ] 


dirs = {}
dirs['DY']              = ["DYJetsToLL_M50" ]
dirs['DY_LO']           = ["DYJetsToLL_M50_LO", "DYJetsToLL_M10to50_LO"]
dirs['DY_HT_LO']        =  DY_M50_HT + DY_M5to50_HT

dirs['TTLep_pow']       = ["TTLep_pow"]

dirs['singleTop_sch']   = ["TToLeptons_sch_amcatnlo_redBy5"]
dirs['singleTop_tch']   = ["TBar_tch_pow_redBy15", "T_tch_pow_redBy15"]
dirs['singleTop_tW']    = ['T_tWch', 'TBar_tWch']


dirs['Top_pow']         = dirs['TTLep_pow'] + dirs['singleTop_sch'] + dirs['singleTop_tW'] + dirs['singleTop_tch']

dirs['TTZ']             = ['TTZToLLNuNu', 'TTZToLLNuNu_m1to10'] # no nanoAOD of TTZToQQ yet

dirs['TTH']             = ['TTHbbLep', 'TTHnobb_pow']
dirs['TWZ']             = ['tWnunu', 'tWll']
dirs['TTW']             = ['TTWToLNu', 'TTWToQQ']
dirs['TZQ']             = ['tZq_ll'] # tZq_nunu not there yet as miniAOD?
dirs['TTVV']            = ['TTWW', 'TTWZ','TTZZ']
dirs['THX']             = ['THW', 'THQ']
dirs['TTTT']            = ['TTTT']

dirs['TTXNoZ']          = dirs['TTVV'] + dirs['TTW'] + dirs['TWZ'] + dirs['TZQ'] + dirs['TTH'] + dirs['TTTT'] + dirs['THX']
dirs['TTX']             = dirs['TTVV'] + dirs['TTW'] + dirs['TWZ'] + dirs['TZQ'] + dirs['TTH'] + dirs['TTTT'] + dirs['THX'] + dirs['TTZ']

dirs['TTG']            = ['TTGLep']

dirs['VVTo2L2Nu']       = ['VVTo2L2Nu']

dirs['WW']              = ["WWToLNuQQ"]
dirs['WZ']              = ["WZTo1L3Nu", "WZTo2L2Q", "WZTo3LNu_amcatnlo"] # no miniAOD of WZTo1L1Nu2Q yet
dirs['ZZ']              = ["ZZTo2L2Q_redBy5", "ZZTo2Q2Nu"]

dirs['ZZ4l']            = ['ZZTo4L']

dirs['diBoson']         = dirs['VVTo2L2Nu'] + dirs['WW'] + dirs['WZ'] + dirs['ZZ']
dirs['triBoson']        = ["WWZ","WZZ","ZZZ"] # WWW_4F to be added in the next round
dirs['multiBoson']      = dirs['diBoson'] + dirs['triBoson']

dirs['allMC']           = dirs['DY_LO'] + dirs['Top_pow'] + dirs['TTZ'] + dirs['TTXNoZ'] + dirs['multiBoson']

directories = { key : [ os.path.join( data_directory_, postProcessing_directory_, dir) for dir in dirs[key]] for key in dirs.keys()}

DY_HT_LO_18     = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="DY (HT, LO)",                       directory=directories['DY_HT_LO'])
DY_LO_18        = Sample.fromDirectory(name="DY_LO",            treeName="Events", isData=False, color=color.DY,              texName="DY (LO)",                           directory=directories['DY_LO'])
Top_pow_18      = Sample.fromDirectory(name="Top_pow",          treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t}/single-t",                 directory=directories['Top_pow'])
TTXNoZ_18       = Sample.fromDirectory(name="TTXNoZ",           treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}H/W, tZq",                  directory=directories['TTXNoZ'])
TTX_18          = Sample.fromDirectory(name="TTX",              treeName="Events", isData=False, color=color.TTX,             texName="t#bar{t}Z/H/W, tZq",                directory=directories['TTX'])
TTH_18          = Sample.fromDirectory(name="TTH",              treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TTH'])
TWZ_18          = Sample.fromDirectory(name="TWZ",              treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TWZ'])
TTW_18          = Sample.fromDirectory(name="TTW",              treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TTW'])
TZQ_18          = Sample.fromDirectory(name="TZQ",              treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TZQ'])
TTVV_18         = Sample.fromDirectory(name="TTVV",             treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TTVV'])
THX_18          = Sample.fromDirectory(name="THX",              treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['THX'])
TTTT_18         = Sample.fromDirectory(name="TTTT",             treeName="Events", isData=False, color=color.TTXNoZ,          texName="t#bar{t}X",                         directory=directories['TTTT'])
TTZ_18          = Sample.fromDirectory(name="TTZ",              treeName="Events", isData=False, color=color.TTZ,             texName="t#bar{t}Z",                         directory=directories['TTZ'])
TTG_18          = Sample.fromDirectory(name="TTG",              treeName="Events", isData=False, color=color.TTG,             texName="t#bar{t}#gamma",                    directory=directories['TTG'])
VVTo2L2Nu_18    = Sample.fromDirectory(name="VVTo2L2Nu",        treeName="Events", isData=False, color=color.VV,              texName="VV to ll#nu#nu",                    directory=directories['VVTo2L2Nu'])
ZZ4l_18         = Sample.fromDirectory(name="ZZ4l",             treeName="Events", isData=False, color=color.ZZ,              texName="ZZ(4l)",                            directory=directories['ZZ4l'])
# WW missing
WZ_18           = Sample.fromDirectory(name="WZ",               treeName="Events", isData=False, color=color.WZ,              texName="WZ w/o ll#nu#nu",                   directory=directories['WZTo3LNu'])
ZZ_18           = Sample.fromDirectory(name="ZZ",               treeName="Events", isData=False, color=color.ZZ,              texName="ZZ w/o ll#nu#nu",                   directory=directories['ZZTo2L2Q'])
triboson_18     = Sample.fromDirectory(name="triBoson",         treeName="Events", isData=False, color=color.triBoson,        texName="triboson",                          directory=directories['triBoson'])
multiBoson_18   = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])
allBkgs_18      = Sample.fromDirectory(name="allBkgs",          treeName="Events", isData=False, color=color.diBoson,         texName="everything",                        directory=directories['allMC'])

#Top_gaussian         = copy.deepcopy(Top_pow)
#Top_gaussian.name    = Top_pow.name + ' (gaussian)'
#Top_gaussian.texName = Top_pow.texName + ' (gaussian)'
#Top_gaussian.color   = ROOT.kCyan
#Top_gaussian.setSelectionString('abs(met_pt-met_genPt)&&abs(met_pt-met_genPt)<=50&&l1_mcMatchId!=0&&l2_mcMatchId!=0')
#
#
#Top_nongaussian         = copy.deepcopy(Top_pow)
#Top_nongaussian.name    = Top_pow.name + ' (non-gaussian)'
#Top_nongaussian.texName = Top_pow.texName + ' (non-gaussian)'
#Top_nongaussian.color   = ROOT.kCyan + 2
#Top_nongaussian.setSelectionString('abs(met_pt-met_genPt)>50&&l1_mcMatchId!=0&&l2_mcMatchId!=0')
#
#
#Top_fakes         = copy.deepcopy(Top_pow)
#Top_fakes.name    = Top_pow.name + ' (fakes)'
#Top_fakes.texName = Top_pow.texName + ' (fakes)'
#Top_fakes.color   = ROOT.kCyan + 4
#Top_fakes.setSelectionString('!(l1_mcMatchId!=0&&l2_mcMatchId!=0)')


