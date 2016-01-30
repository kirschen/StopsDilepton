#data_path = "/data/rschoefbeck/cmgTuples/T2tt_0l_151231/"
data_path = "/data/rschoefbeck/cmgTuples/T2tt_0l_150109/"
from CMGTools.RootTools.samples.samples_13TeV_signals import *

TTJetsDMSamples=[]
#from CMGTools.RootTools.samples.TTbarDMJets_signals_RunIISpring15MiniAODv2 import samples as TTJetsDMSamples
#from CMGTools.RootTools.samples.TTbarDMJets_signals_RunIISpring15MiniAODv2 import *

from StopsDilepton.samples.helpers import getSubDir
import os

signals = []
for s in SignalSUSYFullScan:
    s.isData = False
    s.treeName = "tree"
##for production with heppy_batch
#  s.rootFileLocation = "treeProducerSusySingleLepton/tree.root"
#  s.skimAnalyzerDir = "skimAnalyzerCount"
##for production with crab
    s.skimAnalyzerDir = ""
    s.rootFileLocation = "tree.root"
    subDir = getSubDir(s.dataset)
    if not subDir:
        print "Warning: Not a good dataset name: %s"%s.dataset
        continue
    path = '/'.join([ data_path, getSubDir(s.dataset) ] )
    if os.path.exists(path):
        s.path = path
        s.chunkString = subDir
        signals.append(s)
    else:
        print "Did not find %s in %s"%(s.name, path)

print
print "Found %i signals in %s\n%s"% (len(signals), data_path, (", ".join([s.name for s in signals])))
print
