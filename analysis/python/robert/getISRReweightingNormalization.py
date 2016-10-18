import ROOT
import pickle
import os


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","TTbarDM"],                                                                                 help="which signal?")
args = argParser.parse_args()

from StopsDilepton.analysis.robert.helpers import isrWeight

maxN = -1

from StopsDilepton.samples.helpers import fromHeppySample

if args.signal == 'T2tt':
    # CMG SMS files
    samples = ["SMS_T2tt_mStop_150to250", "SMS_T2tt_mStop_250to350", "SMS_T2tt_mStop_350to400", "SMS_T2tt_mStop_400to1200", "SMS_T2tt_mStop_425_mLSP_325", "SMS_T2tt_mStop_500_mLSP_325", "SMS_T2tt_mStop_850_mLSP_100"]
    #samples = ["SMS_T2tt_mStop_425_mLSP_325"]#, "SMS_T2tt_mStop_250to350"]
    dataDir = "/scratch/rschoefbeck/cmgTuples/80X_0l_13"

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

    correction = {}
    for s in samples:
        print "Processing %s"%s
        sample = fromHeppySample(s, data_path = dataDir, maxN = maxN)
        correction.update( getT2ttSignalWeight( sample ) )
elif args.signal == "TTbarDM":
    samples = ["TTbarDMJets_pseudoscalar_Mchi_10_Mphi_100", "TTbarDMJets_pseudoscalar_Mchi_10_Mphi_10", "TTbarDMJets_pseudoscalar_Mchi_10_Mphi_15", "TTbarDMJets_pseudoscalar_Mchi_10_Mphi_50", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10000", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_100", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_200", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_300", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_500", "TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50", "TTbarDMJets_pseudoscalar_Mchi_50_Mphi_10", "TTbarDMJets_pseudoscalar_Mchi_50_Mphi_200", "TTbarDMJets_pseudoscalar_Mchi_50_Mphi_300", "TTbarDMJets_pseudoscalar_Mchi_50_Mphi_50", "TTbarDMJets_pseudoscalar_Mchi_50_Mphi_95", "TTbarDMJets_scalar_Mchi_10_Mphi_100", "TTbarDMJets_scalar_Mchi_10_Mphi_10", "TTbarDMJets_scalar_Mchi_10_Mphi_15", "TTbarDMJets_scalar_Mchi_10_Mphi_50", "TTbarDMJets_scalar_Mchi_1_Mphi_10000", "TTbarDMJets_scalar_Mchi_1_Mphi_100", "TTbarDMJets_scalar_Mchi_1_Mphi_10", "TTbarDMJets_scalar_Mchi_1_Mphi_200", "TTbarDMJets_scalar_Mchi_1_Mphi_20", "TTbarDMJets_scalar_Mchi_1_Mphi_300", "TTbarDMJets_scalar_Mchi_1_Mphi_500", "TTbarDMJets_scalar_Mchi_1_Mphi_50", "TTbarDMJets_scalar_Mchi_50_Mphi_10", "TTbarDMJets_scalar_Mchi_50_Mphi_200", "TTbarDMJets_scalar_Mchi_50_Mphi_300", "TTbarDMJets_scalar_Mchi_50_Mphi_50", "TTbarDMJets_scalar_Mchi_50_Mphi_95", ]
    dataDir = "/scratch/rschoefbeck/cmgTuples/80X_0l_TTDM"

    correction = {}
    for s in samples:
        print "Processing %s"%s
        sample = fromHeppySample(s, data_path = dataDir, maxN = maxN, 
                    module = "CMGTools.StopsDilepton.TTbarDMJets_signals_RunIISpring16MiniAODv2", 
                 ) 
        ssplit_ = s.split('_')
        mchi = int(ssplit_[3])
        mphi = int(ssplit_[5])
        n = sample.getYieldFromDraw()['val']
        b = sample.getYieldFromDraw(weightString = isrWeight)['val']
        if n>0:
            correction[(mchi, mphi)] = n / b
else:
    raise NotImplementedError( "Don't know what to do with signal: %s." % args.signal )

from StopsDilepton.tools.user import analysis_results
ofile = os.path.join(analysis_results, 'systematics', 'isrSignalSysNormalization_%s.pkl' % args.signal)
pickle.dump(correction, file(ofile, 'w') )
print "Written %s"%ofile
