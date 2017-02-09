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
  postProcessing_directory = "postProcessed_80X_v30/dilepTiny"

dirs = {}
dirs['TTGJets'] = ["TTGJets"]
dirs['ZG']      = ["ZGTo2LG"]
dirs['WG']      = ["WGToLNuG"]
dirs['WWG']     = ["WWG"]

directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

TTG            = Sample.fromDirectory(name="TTGJets",          treeName="Events", isData=False, color=color.TTG,             texName="t#bar{t}#gamma + Jets",             directory=directories['TTGJets'])
ZG             = Sample.fromDirectory(name="ZG",               treeName="Events", isData=False, color=color.WZ,              texName="ZG",                                directory=directories['ZG'])
WG             = Sample.fromDirectory(name="WG",               treeName="Events", isData=False, color=color.WG,              texName="WG",                                directory=directories['WG'])
#WWG            = Sample.fromDirectory(name="WWG",              treeName="Events", isData=False, color=color.WWG,             texName="WWG",                               directory=directories['WWG'])
