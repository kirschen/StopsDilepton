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



dirs = {}
dirs['T2tt_mStop_175_mLSP_1']   = ['SMS_T2tt_mStop_175_mLSP_1']
dirs['T2tt_mStop_250_mLSP_50']  = ['SMS_T2tt_mStop_250_mLSP_50']
dirs['T2tt_mStop_250_mLSP_75']  = ['SMS_T2tt_mStop_250_mLSP_75']
dirs['T2tt_mStop_250_mLSP_100'] = ['SMS_T2tt_mStop_250_mLSP_100']
dirs['T2tt_mStop_650_mLSP_350'] = ['SMS_T2tt_mStop_650_mLSP_350']
dirs['T2tt_mStop_850_mLSP_100'] = ['SMS_T2tt_mStop_850_mLSP_100']

directories = { key : [ os.path.join( data_directory_, postProcessing_directory_, dir) for dir in dirs[key]] for key in dirs.keys()}

#

# FullSim signals
T2tt_mStop_175_mLSP_1    = Sample.fromDirectory(name="T2tt_mStop_175_mLSP_1",     treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_175_mLSP_1'])
T2tt_mStop_250_mLSP_50   = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_50",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_50'])
T2tt_mStop_250_mLSP_75   = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_75",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_75'])
T2tt_mStop_250_mLSP_100  = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_100",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_100'])
#T2tt_mStop_650_mLSP_350  = Sample.fromDirectory(name="T2tt_mStop_650_mLSP_350",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_650_mLSP_350'])
#T2tt_mStop_850_mLSP_100  = Sample.fromDirectory(name="T2tt_mStop_850_mLSP_100",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_850_mLSP_100'])

signals_T2tt = [
    T2tt_mStop_175_mLSP_1,
    T2tt_mStop_250_mLSP_50,
    T2tt_mStop_250_mLSP_75,
    T2tt_mStop_250_mLSP_100,
#    T2tt_mStop_650_mLSP_350,
#    T2tt_mStop_850_mLSP_100,
]

for s in signals_T2tt:
    t1, mStop, t2, mNeu = s.name.replace('T2tt_','').split('_')
    s.mStop = int(mStop)
    s.mNeu = int(mNeu)
    s.isFastSim = False

