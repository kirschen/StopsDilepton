# Standard imports 
import os
import ROOT

# RootTools
from RootTools.core.standard import *

def getSubDir(dataset, path):
    import re
    m=re.match("\/(.*)\/(.*)\/(.*)",dataset)
    if not m :
        print "NO GOOD DATASET"
        return
    if os.environ['USER'] in ['tomc']: 
      d=re.match("(.*)/cmgTuples/(.*)",path)
      return m.group(1)+"/"+m.group(2)+'_'+d.group(2)
    else :                             
      return m.group(1)+"_"+m.group(2)

def fromHeppySample(sample, data_path, module = None, maxN = None):
    ''' Load CMG tuple from local directory
    '''

    import importlib
    if module is not None:
        module_ = module
    elif "Run2015D" in sample:
        module_ = 'CMGTools.RootTools.samples.samples_13TeV_DATA2015'
    else:
        module_ = 'CMGTools.RootTools.samples.samples_13TeV_RunIIFall15MiniAODv2'

    try:
        heppy_sample = getattr(importlib.import_module( module_ ), sample)
    except:
        raise ValueError( "Could not load sample '%s' from %s "%( sample, module_ ) )

    # helpers
    subDir = getSubDir(heppy_sample.dataset, data_path)
    if not subDir:
        raise ValueError( "Not a good dataset name: '%s'"%heppy_sample.dataset )

    path = os.path.join( data_path, subDir )
    from StopsDilepton.tools.user import runOnGentT2
    if runOnGentT2: 
        sample = Sample.fromCMGCrabDirectory(
            heppy_sample.name, 
            path, 
            treeFilename = 'tree.root', 
            treeName = 'tree', isData = heppy_sample.isData, maxN = maxN)
    else:                              
        sample = Sample.fromCMGOutput(
            heppy_sample.name, 
            path, 
            treeFilename = 'tree.root', 
            treeName = 'tree', isData = heppy_sample.isData, maxN = maxN)

    sample.heppy = heppy_sample
    return sample

def getT2ttSignalWeight(sample, lumi):
    '''Get a dictionary for T2tt signal weights
    '''
    from StopsDilepton.tools.xSecSusy import xSecSusy
    xSecSusy_ = xSecSusy()
    channel='stop13TeV'
    signalWeight={}
    mMax = 1500
    bStr = str(mMax)+','+str(mMax)
    sample.chain.Draw("GenSusyMScan2:GenSusyMScan1>>hNEvents("+','.join([bStr, bStr])+")", "","goff")
    hNEvents = ROOT.gDirectory.Get("hNEvents")
    for i in range (mMax):
        for j in range (mMax):
            n = hNEvents.GetBinContent(hNEvents.FindBin(i,j))
            if n>0:
                signalWeight[(i,j)] = {'weight':lumi*xSecSusy_.getXSec(channel=channel,mass=i,sigma=0)/n, 'xSecFacUp':xSecSusy_.getXSec(channel=channel,mass=i,sigma=1)/xSecSusy_.getXSec(channel=channel,mass=i,sigma=0), 'xSecFacDown':xSecSusy_.getXSec(channel=channel,mass=i,sigma=-1)/xSecSusy_.getXSec(channel=channel,mass=i,sigma=0)}
    #            logger.info( "Found mStop %5i mNeu %5i Number of events: %6i, xSec: %10.6f, weight: %6.6f (+1 sigma rel: %6.6f, -1 sigma rel: %6.6f)", i,j,n, xSecSusy_.getXSec(channel=channel,mass=i,sigma=0),  signalWeight[(i,j)]['weight'], signalWeight[(i,j)]['xSecFacUp'], signalWeight[(i,j)]['xSecFacDown'] )
    del hNEvents
    return signalWeight

