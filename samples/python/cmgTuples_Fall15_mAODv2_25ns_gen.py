import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

from StopsDilepton.tools.user import data_directory
from StopsDilepton.samples.color import color

# Take post processing directory if defined in main module
try:
  import sys
  postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
  postProcessing_directory = "postProcessed_Fall15_mAODv2/gen"

dirs = {}
dirs['TTZtoLLNuNu']      = ["TTZToLLNuNu"]
dirs['TTGJets']	         = ["TTGJets"]

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

TTZtoLLNuNu    = Sample.fromDirectory(name="TTZtoNuNu",        treeName="Events", isData=False, color=color.TTZtoLLNuNu,     texName="t#bar{t}Z (l#bar{l}/#nu#bar{#nu})", directory=directories['TTZtoLLNuNu'])
TTG            = Sample.fromDirectory(name="TTGJets",          treeName="Events", isData=False, color=color.TTG,             texName="t#bar{t}#gamma + Jets",             directory=directories['TTGJets'])
