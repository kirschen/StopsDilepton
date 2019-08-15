import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.samples.color import color

data_directory_ = '/afs/hephy.at/data/cms01/nanoTuples/'
postProcessing_directory_ = 'stops_2016_nano_v0p16/dilep/'

logger.info("Loading MC samples from directory %s", os.path.join(data_directory_, postProcessing_directory_))



dirs = {}
dirs['T2tt_mStop_150_mLSP_50']  = ['SMS_T2tt_mStop_150_mLSP_50']
dirs['T2tt_mStop_175_mLSP_1']   = ['SMS_T2tt_mStop_175_mLSP_1']
dirs['T2tt_mStop_200_mLSP_50']  = ['SMS_T2tt_mStop_200_mLSP_50']
dirs['T2tt_mStop_225_mLSP_50']  = ['SMS_T2tt_mStop_225_mLSP_50']
dirs['T2tt_mStop_250_mLSP_50']  = ['SMS_T2tt_mStop_250_mLSP_50']
dirs['T2tt_mStop_250_mLSP_75']  = ['SMS_T2tt_mStop_250_mLSP_75']
dirs['T2tt_mStop_250_mLSP_150'] = ['SMS_T2tt_mStop_250_mLSP_150']
dirs['T2tt_mStop_300_mLSP_150'] = ['SMS_T2tt_mStop_300_mLSP_150']
dirs['T2tt_mStop_325_mLSP_150'] = ['SMS_T2tt_mStop_325_mLSP_150']
dirs['T2tt_mStop_350_mLSP_150'] = ['SMS_T2tt_mStop_350_mLSP_150']

directories = { key : [ os.path.join( data_directory_, postProcessing_directory_, dir) for dir in dirs[key]] for key in dirs.keys()}

#

# FullSim signals
T2tt_mStop_150_mLSP_50   = Sample.fromDirectory(name="T2tt_mStop_150_mLSP_50",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_150_mLSP_50'])
T2tt_mStop_175_mLSP_1    = Sample.fromDirectory(name="T2tt_mStop_175_mLSP_1",     treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_175_mLSP_1'])
T2tt_mStop_200_mLSP_50   = Sample.fromDirectory(name="T2tt_mStop_200_mLSP_50",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_200_mLSP_50'])
T2tt_mStop_225_mLSP_50   = Sample.fromDirectory(name="T2tt_mStop_225_mLSP_50",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_225_mLSP_50'])
T2tt_mStop_250_mLSP_50   = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_50",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_50'])
T2tt_mStop_250_mLSP_75   = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_75",    treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_75'])
T2tt_mStop_250_mLSP_150  = Sample.fromDirectory(name="T2tt_mStop_250_mLSP_150",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_250_mLSP_150'])
T2tt_mStop_300_mLSP_150  = Sample.fromDirectory(name="T2tt_mStop_300_mLSP_150",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_300_mLSP_150'])
T2tt_mStop_325_mLSP_150  = Sample.fromDirectory(name="T2tt_mStop_325_mLSP_150",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_325_mLSP_150'])
T2tt_mStop_350_mLSP_150  = Sample.fromDirectory(name="T2tt_mStop_350_mLSP_150",   treeName="Events", isData=False, color=color.DY,     texName="T2tt(150,50)",     directory=directories['T2tt_mStop_350_mLSP_150'])

signals_T2tt = [
    T2tt_mStop_150_mLSP_50,
    T2tt_mStop_175_mLSP_1,
    T2tt_mStop_200_mLSP_50,
    T2tt_mStop_225_mLSP_50,
    T2tt_mStop_250_mLSP_50,
    T2tt_mStop_250_mLSP_75,
    T2tt_mStop_250_mLSP_150,
    T2tt_mStop_300_mLSP_150,
    T2tt_mStop_325_mLSP_150,
    T2tt_mStop_350_mLSP_150,
]

for s in signals_T2tt:
    t1, mStop, t2, mNeu = name.replace('T2tt_','').split('_')
    s.mStop = int(mStop)
    s.mNeu = int(mNeu)
    s.isFastSim = False

