#Standard import 
import copy, os, sys
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

#user specific
from StopsDilepton.tools.user import data_directory

#RootTools
from RootTools.core.standard import *

signals_TTbarDM = []

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
  postProcessing_directory = "postProcessed_80X_v35/dilepTiny"

logger.info("Loading Higgs samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
dirs['ZH_ZToMM_HToInvisible_M125']  = [ "ZH_ZToMM_HToInvisible_M125" ]
dirs['ZH_ZToEE_HToInvisible_M125']  = [ "ZH_ZToEE_HToInvisible_M125" ]


directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

ZH_ZToMM_HToInvisible_M125  = Sample.fromDirectory(name="ZH_ZToMM_HToInvisible_M125",   treeName="Events", isData=False, color=1,    texName="ZH(125), Z to \mu\mu", directory=directories['ZH_ZToMM_HToInvisible_M125'])
ZH_ZToEE_HToInvisible_M125  = Sample.fromDirectory(name="ZH_ZToEE_HToInvisible_M125",   treeName="Events", isData=False, color=1,    texName="ZH(125), Z to ee", directory=directories['ZH_ZToEE_HToInvisible_M125'])

