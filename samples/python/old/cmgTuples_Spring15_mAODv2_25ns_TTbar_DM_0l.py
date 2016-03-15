data_path = "/data/rschoefbeck/cmgTuples/TTBar_DM"

from CMGTools.RootTools.samples.TTbarDMJets_signals_RunIISpring15MiniAODv2 import *
from CMGTools.RootTools.samples.TTbarDMJets_signals_RunIISpring15MiniAODv2 import samples as mcSamples

from StopsDilepton.samples.helpers import getSubDir
import os

samples=[]
for s in mcSamples:
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
        samples.append(s)
    else:
        print "Did not find %s in %s"%(s.name, path)

print
print "Found %i MC datasets in %s\n%s"% (len(samples), data_path, (", ".join([s.name for s in samples])))
print
