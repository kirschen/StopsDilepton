#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.defaultAnalysis import setup
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.analysis.DataDrivenDYEstimate import DataDrivenDYEstimate

setup.dataSamples = {"EE" : DoubleEG_Run2015D, "MuMu" : DoubleMuon_Run2015D, "EMu" : MuonEG_Run2015D}
setup.verbose = True

estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None)

regionDY = Region('dl_mt2ll', (0,-1))

for channel, sample in setup.dataSamples.iteritems():
    setup.lumi[channel] = sample.lumi
    res = estimateDY.cachedEstimate(regionDY,channel,setup)
    print "\n Result in ", channel," for estimate ", estimateDY.name, regionDY,":", res#, 'jer',jer, 'jec', jec
