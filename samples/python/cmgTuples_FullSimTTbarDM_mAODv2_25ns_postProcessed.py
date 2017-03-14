#Standard import 
import copy, os, sys
import ROOT

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

DMsamples = []

for f in sorted(os.listdir(os.path.join(data_directory, postProcessing_directory))):
    if f.startswith('TTbarDMJets_'):

        splitter = ''
        if '_Tune' in f: splitter = '_Tune'
        else: splitter = '_13TeV'
        if 'ext1' in f: ext = '_ext1'
        elif 'ext2' in f: ext = '_ext2'
        else: ext = ''
        tmp1 = f.split(splitter)
        sampleName = tmp1[0].replace('/','').replace('-','_')
        masses = sampleName.split('_')
        BR = 1
        tp_ = ''
        if masses == ['']: break
        for i, m in enumerate(masses):
          if 'dilep' in m.lower(): BR = (3*0.108)**2
          if m.lower() == 'mchi': mChi = int(masses[i+1])
          if m.lower() == 'mphi': mPhi = int(masses[i+1])
          if m.lower() == 'scalar': tp_ = 'S'
          if m.lower() == 'pseudoscalar': tp_ = 'PS'
          if m.lower() == 'smm': tp_ = 'SMM'

        tmp = Sample.fromDirectory(\
            name = f,
            directory = [os.path.join(os.path.join(data_directory,postProcessing_directory,f))],
            treeName = "Events",
            isData = False,
            color = 8 ,
            texName = "%s(m_{#chi}=%i, m_{#phi}=%i)"%(tp_, mChi, mPhi)
        )
        tmp.mChi = mChi
        tmp.mPhi = mPhi
        tmp.type = tp_
        
        # use dilep samples whenever available: the list is sorted in the beginning so that dilep samples are added first
        if (mChi, mPhi, tp_) in DMsamples:
            print "Omitting sample {}, same point was already added".format((mChi, mPhi, tp_))
        else:
            DMsamples.append((mChi, mPhi, tp_))
            exec("%s=tmp"%f)
            exec("signals_TTbarDM.append(%s)"%f)

print "Loaded %i TTDM signals: %s"%(len(signals_TTbarDM), ",".join([s.name for s in signals_TTbarDM]))
