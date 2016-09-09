import ROOT
import pickle
import os

from StopsDilepton.analysis.robert.helpers import isrWeight

def getT2ttSignalWeight(sample):
    '''Get a dictionary for T2tt signal weights
    '''
    mMax = 1500
    bStr = str(mMax)+','+str(mMax)
    sample.chain.Draw("GenSusyMNeutralino:GenSusyMStop>>hNEvents("+','.join([bStr, bStr])+")", "","goff")
    sample.chain.Draw("GenSusyMNeutralino:GenSusyMStop>>hISR("+','.join([bStr, bStr])+")", isrWeight,"goff")

    hNEvents = ROOT.gDirectory.Get("hNEvents")
    hISR = ROOT.gDirectory.Get("hISR")

    correction={}
    for i in range (mMax):
        for j in range (mMax):
            b = hNEvents.FindBin(i,j)
            n = hNEvents.GetBinContent( b )
            if n>0:
                correction[(i,j)] = n/hISR.GetBinContent( b ) 

    return correction                 
    #            logger.info( "Found mStop %5i mNeu %5i Number of events: %6i, xSec: %10.6f, weight: %6.6f (+1 sigma rel: %6.6f, -1 sigma rel: %6.6f)", i,j,n, xSecSusy_.getXSec(channel=channel,mass=i,sigma=0),  signalWeight[(i,j)]['weight'], signalWeight[(i,j)]['xSecFacUp'], signalWeight[(i,j)]['xSecFacDown'] )

from StopsDilepton.samples.helpers import fromHeppySample

samples = ["SMS_T2tt_mStop_150to250", "SMS_T2tt_mStop_250to350", "SMS_T2tt_mStop_350to400", "SMS_T2tt_mStop_400to1200", "SMS_T2tt_mStop_425_mLSP_325", "SMS_T2tt_mStop_500_mLSP_325", "SMS_T2tt_mStop_850_mLSP_100"]
#samples = ["SMS_T2tt_mStop_425_mLSP_325"]#, "SMS_T2tt_mStop_250to350"]
dataDir = "/scratch/rschoefbeck/cmgTuples/80X_0l_13"

maxN = -1

correction = {}
for s in samples:
    print "Processing %s"%s
    sample = fromHeppySample(s, data_path = dataDir, maxN = maxN)
    correction.update( getT2ttSignalWeight( sample ) )

from StopsDilepton.tools.user import analysis_results
ofile = os.path.join(analysis_results, 'systematics', 'isrSignalSysNormalization.pkl')
pickle.dump(correction, file(ofile, 'w') )
print "Written %s"%ofile
