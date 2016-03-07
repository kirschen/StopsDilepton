# Standard imports 
import os

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

def fromHeppySample(sample, data_path, sample_module = 'CMGTools.RootTools.samples.samples_13TeV_RunIIFall15MiniAODv2', maxN = None):
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
    sample = Sample.fromCMGOutput(heppy_sample.name, path, treeFilename = 'tree.root', treeName = 'tree', isData = heppy_sample.isData, maxN = maxN)
    sample.heppy = heppy_sample
    return sample
