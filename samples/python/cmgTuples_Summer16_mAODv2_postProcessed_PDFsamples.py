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
  postProcessing_directory = "postProcessed_80X_v36/dilep/"

logger.info("Loading MC samples from directory %s", os.path.join(data_directory, postProcessing_directory))

DY_M5to50_HT = [
                "DYJetsToLL_M5to50_HT100to200_comb",
                "DYJetsToLL_M5to50_HT200to400_comb",
                "DYJetsToLL_M5to50_HT400to600",
                "DYJetsToLL_M5to50_HT600toInf_comb"
                ] 

DY_M50_HT =["DYJetsToLL_M50_LO_ext_lheHT100", 
            "DYJetsToLL_M50_HT100to200_comb",
            "DYJetsToLL_M50_HT200to400_comb",
            "DYJetsToLL_M50_HT400to600_comb",
            "DYJetsToLL_M50_HT600to800",
            "DYJetsToLL_M50_HT800to1200",
            "DYJetsToLL_M50_HT1200to2500",
            "DYJetsToLL_M50_HT2500toInf"
            ] 


dirs = {}
dirs['DY_HT_LO']         =  DY_M50_HT + DY_M5to50_HT + ["DYJetsToLL_M10to50_LO_lheHT100"]
dirs['TTLep_pow']        = ["TTLep_pow"]
dirs['TTZtoLLNuNu']      = ["TTZToLLNuNu_ext"]
dirs['TTZtoQQ']          = ["TTZToQQ"]
dirs['TTZ']              = ["TTZToLLNuNu_ext", "TTZToQQ"]
dirs['TTZ_LO']           = ["TTZ_LO"]
dirs['diBosonInclusive'] = ["WW", "WZ", "ZZ"]
dirs['WW']               = ["WWToLNuQQ_comb"]
dirs['WW_']              = ["WWToLNuQQ_comb","WWTo2L2Nu"]
dirs['WWTo2L2Nu']        = ["WWTo2L2Nu"]
dirs['VVTo2L2Nu']        = ["VVTo2L2Nu_comb"]
dirs['WZ']               = ["WZTo1L1Nu2Q", "WZTo1L3Nu", "WZTo2L2Q", "WZTo3LNu"]
dirs['ZZ']               = ["ZZTo2L2Q", "ZZTo2Q2Nu"]
dirs['ZZTo2L2Nu']        = ["ZZTo2L2Nu"]
dirs['ZZ_']              = ["ZZTo2L2Q", "ZZTo2Q2Nu","ZZTo2L2Nu"]
dirs['diBoson']          = dirs['WW'] + dirs['WZ'] + dirs['ZZ'] + dirs['VVTo2L2Nu']
dirs['diBoson_']         = dirs['WW_'] + dirs['WZ'] + dirs['ZZ_']
dirs['triBoson']         = ["WWZ","WZZ","ZZZ"] 
dirs['multiBoson']       = dirs['diBoson'] + dirs['triBoson']

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

DY_HT_LO        = Sample.fromDirectory(name="DY_HT_LO",         treeName="Events", isData=False, color=color.DY,              texName="Drell-Yan",                         directory=directories['DY_HT_LO'])
TTLep_pow       = Sample.fromDirectory(name="TTLep_pow",        treeName="Events", isData=False, color=color.TTJets,          texName="t#bar{t} + Jets (lep,pow)",         directory=directories['TTLep_pow'])
TTZ            = Sample.fromDirectory(name="TTZ",              treeName="Events", isData=False, color=color.TTZ,             texName="t#bar{t}Z",                         directory=directories['TTZ'])
TTZ_LO        = Sample.fromDirectory(name="TTZ_LO",              treeName="Events", isData=False, color=color.TTZ,             texName="t#bar{t}Z",                         directory=directories['TTZ_LO'])
TTZtoLLNuNu    = Sample.fromDirectory(name="TTZtoNuNu",        treeName="Events", isData=False, color=color.TTZtoLLNuNu,     texName="t#bar{t}Z (l#bar{l}/#nu#bar{#nu})", directory=directories['TTZtoLLNuNu'])
TTZtoQQ        = Sample.fromDirectory(name="TTZtoQQ",          treeName="Events", isData=False, color=color.TTZtoQQ,         texName="t#bar{t}Z (q#bar{q})",              directory=directories['TTZtoQQ'])
diBoson        = Sample.fromDirectory(name="diBoson",          treeName="Events", isData=False, color=color.diBoson,         texName="VV (excl.)",                        directory=directories['diBoson'])
diBoson_       = Sample.fromDirectory(name="diBoson",          treeName="Events", isData=False, color=color.diBoson,         texName="VV (excl.)",                        directory=directories['diBoson_'])
diBosonInclusive = Sample.fromDirectory(name="diBosonInclusive",treeName="Events", isData=False, color=color.diBoson,        texName="VV (incl.)",                        directory=directories['diBosonInclusive'])
ZZ             = Sample.fromDirectory(name="ZZ",               treeName="Events", isData=False, color=color.ZZ,              texName="ZZ",                                directory=directories['ZZ_'])
ZZNo2L2Nu      = Sample.fromDirectory(name="ZZNo2L2Nu",        treeName="Events", isData=False, color=color.ZZ,              texName="ZZ (no 2L2Nu)",                     directory=directories['ZZ'])
ZZTo2L2Nu      = Sample.fromDirectory(name="ZZTo2L2Nu",        treeName="Events", isData=False, color=color.ZZ,              texName="ZZTo2l2Nu",                         directory=directories['ZZTo2L2Nu'])
WZ             = Sample.fromDirectory(name="WZ",               treeName="Events", isData=False, color=color.WZ,              texName="WZ",                                directory=directories['WZ'])
WW             = Sample.fromDirectory(name="WW",               treeName="Events", isData=False, color=color.WW,              texName="WW",                                directory=directories['WW_'])
WWNo2L2Nu      = Sample.fromDirectory(name="WWNo2L2Nu",        treeName="Events", isData=False, color=color.WW,              texName="WW (no 2L2Nu)",                     directory=directories['WW'])
WWTo2L2Nu      = Sample.fromDirectory(name="WWTo2L2Nu",        treeName="Events", isData=False, color=color.WW,              texName="WWTo2L2Nu",                         directory=directories['WWTo2L2Nu'])
VVTo2L2Nu      = Sample.fromDirectory(name="VVTo2L2Nu",               treeName="Events", isData=False, color=color.VV,              texName="VV to ll#nu#nu",             directory=directories['VVTo2L2Nu'])
triBoson       = Sample.fromDirectory(name="triBoson",         treeName="Events", isData=False, color=color.triBoson,        texName="WWZ,WZZ,ZZZ",                       directory=directories['triBoson'])
multiBoson     = Sample.fromDirectory(name="multiBoson",       treeName="Events", isData=False, color=color.diBoson,         texName="multi boson",                       directory=directories['multiBoson'])

