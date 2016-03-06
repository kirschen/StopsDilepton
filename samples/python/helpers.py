# Standard imports 
import os

# location of cmg tuples
data_path = "/scratch/rschoefbeck/cmgTuples/763/"

# RootTools
from RootTools.core.standard import *

def getSubDir(dataset):
    import re
    m=re.match("\/(.*)\/(.*)\/(.*)",dataset)
    if not m :
        print "NO GOOD DATASET"
        return
    sample=m.group(1)+"_"+m.group(2)
    return sample

#def combineSamples(sList):
#    import copy
#    if not sList: return
#    assert all([s.has_key("bins") for s in sList]), "Key 'bins' not found in one or more samples."
#    assert len(list(set(s['dir'] for s in sList)))==1, "Directories not unique!"
#    res = copy.deepcopy(sList[0])
#    for s in sList[1:]:
#        res['bins'].extend(s['bins'])
#    return res

def fromHeppySample(sample, data_path = data_path, sample_module = 'CMGTools.RootTools.samples.samples_13TeV_RunIIFall15MiniAODv2'):
    import importlib
    try:
        heppy_sample = getattr(importlib.import_module( sample_module), sample)
    except:
        raise ValueError( "Could not load sample '%s' from %s "%( sample, sample_module ) )

    # helpers
    from StopsDilepton.samples.helpers import getSubDir
    subDir = getSubDir(heppy_sample.dataset)
    if not subDir:
        raise ValueError( "Not a good dataset name: '%s'"%heppy_sample.dataset )

    path = '/'.join([ data_path, subDir ] )
    sample = Sample.fromCMGOutput(heppy_sample.name, path, treeFilename = 'tree.root', treeName = 'tree', isData = heppy_sample.isData)
    return sample
