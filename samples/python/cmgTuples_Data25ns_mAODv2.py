#data_path = "/afs/cern.ch/work/s/schoef/Run2015D_1l_4"
data_path = '/data/rschoefbeck/cmgTuples/Run2015D_1l_151225'
from CMGTools.RootTools.samples.samples_13TeV_DATA2015 import *
from StopsDilepton.samples.helpers import getSubDir
import os

samples = [DoubleEG_Run2015D_Promptv4, MuonEG_Run2015D_Promptv4, DoubleMuon_Run2015D_Promptv4, DoubleEG_Run2015D_05Oct, MuonEG_Run2015D_05Oct, DoubleMuon_Run2015D_05Oct]

dataSamples=[]
for s in samples:
    s.isData = True
    s.treeName = "tree"
    subDir = getSubDir(s.dataset)
    path = '/'.join([ data_path, subDir ] )
    s.skimAnalyzerDir = ""
    s.rootFileLocation = "tree.root"
##for production with heppy_batch
#  s.rootFileLocation = "treeProducerSusySingleLepton/tree.root"
#  s.skimAnalyzerDir = "skimAnalyzerCount"
#  subDir = s.name
#  path = data_path
##for production with crab
    s.json = '$CMSSW_BASE/src/CMGTools/TTHAnalysis/data/json/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt'
    if not subDir:
        print "Warning: Not a good dataset name: %s"%s.dataset
        continue

    if os.path.exists(path):
        s.path = path
        s.chunkString = subDir
        dataSamples.append(s)
    else:
        print "Did not find %s in %s"%(s.name, path)

#  vetoBaseDir='/afs/hephy.at/data/rschoefbeck01/cmgTuples/vetoLists/Run2015D/old/'
#  vetoSuffix='_Nov14'
#  s.vetoList=os.path.join(vetoBaseDir, s.name.split('_')[0]+vetoSuffix+'.tar.gz')
    vetoBaseDir='/afs/hephy.at/data/rschoefbeck01/cmgTuples/vetoLists/Run2015D/'
    fileNames  = ['csc2015_Dec01.txt.gz', 'ecalscn1043093_Dec01.txt.gz']
    s.vetoList = [os.path.join(vetoBaseDir, f) for f in fileNames]

print
print "Found %i Run2015D datasets in %s\n%s"% (len(dataSamples), data_path, (", ".join([s.name for s in dataSamples])))
print

