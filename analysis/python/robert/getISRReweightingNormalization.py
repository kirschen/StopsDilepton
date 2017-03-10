import ROOT
import pickle
import os


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--small",           action='store_true')
argParser.add_argument("--signal",          action='store', default='T2tt',     nargs='?',  choices=["T2tt","T2bt","T2bW","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05","T8bbllnunu_XCha0p5_XSlep0p5","T8bbllnunu_XCha0p5_XSlep0p95", "T8bbllnunu_XCha0p5_XSlep0p09"], help="which signal?")
args = argParser.parse_args()

from StopsDilepton.analysis.daniel.isrWeight import ISRweight
from StopsDilepton.samples.heppy_dpm_samples import T2tt_heppy_mapper, T8bbllnunu_heppy_mapper, ttbarDM_heppy_mapper, T2bX_heppy_mapper

isrWeight = ISRweight().getWeightString()

if 'T2' in args.signal or args.small or 'T8bbllnunu' in args.signal:
    def getT2ttSignalWeight(sample):
        '''Get a dictionary for T2tt signal weights
        '''
        mMax = 1600
        bStr = str(mMax)+','+str(mMax)
        sample.chain.Draw("Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000022)):Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000006))>>hNEvents("+','.join([bStr, bStr])+")", "","goff")
        sample.chain.Draw("Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000022)):Max$(genPartAll_mass*(abs(genPartAll_pdgId)==1000006))>>hISR("+','.join([bStr, bStr])+")", isrWeight,"goff")

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
    if args.small:
        samples = sorted(T2tt_heppy_mapper.heppy_sample_names)[-1:]
        print "Doing subset of", samples
    else:
        if 'T8bb' in args.signal:
            samples = sorted(T8bbllnunu_heppy_mapper.heppy_sample_names)
            mapper = T8bbllnunu_heppy_mapper
        elif 'T2b' in args.signal:
            samples = sorted(T2bX_heppy_mapper.heppy_sample_names)
            mapper = T2bX_heppy_mapper

        if args.signal == 'T2tt':
            samples = sorted(T2tt_heppy_mapper.heppy_sample_names)
            mapper = T2tt_heppy_mapper

        elif args.signal == 'T2bt':
            tmpList = []
            for s in samples:
                if 'T2bt' in s: tmpList.append(s)
            samples = tmpList

        elif args.signal == 'T2bW':
            tmpList = []
            for s in samples:
                if 'T2bW' in s: tmpList.append(s)
            samples = tmpList

        elif args.signal == 'T8bbllnunu_XCha0p5_XSlep0p05':
            tmpList = []
            for s in samples:
                if 'XSlep0p05' in s: tmpList.append(s)
            samples = tmpList

        elif args.signal == 'T8bbllnunu_XCha0p5_XSlep0p09':
            tmpList = []
            for s in samples:
                if 'XSlep0p09' in s: tmpList.append(s)
            samples = tmpList

        elif args.signal == 'T8bbllnunu_XCha0p5_XSlep0p5':
            tmpList = []
            for s in samples:
                if 'XSlep0p5' in s: tmpList.append(s)
            samples = tmpList

        elif args.signal == 'T8bbllnunu_XCha0p5_XSlep0p95':
            tmpList = []
            for s in samples:
                if 'XSlep0p95' in s: tmpList.append(s)
            samples = tmpList

    for s in samples:
        print "Processing %s"%s
        sample = mapper.from_heppy_samplename(s)
        correction.update( getT2ttSignalWeight( sample ) )


elif args.signal == "TTbarDM":
    samples = sorted(ttbarDM_heppy_mapper.heppy_sample_names)
    correction = {}
    for s in samples:
        print "Processing %s"%s
        sample = ttbarDM_heppy_mapper.from_heppy_samplename(s)
        ssplit_ = s.split('_')
        masses = []
        for el in ssplit_:
            try:
                m = int(el)
                masses.append(m)
            except ValueError: pass
        assert len(masses) == 2, "Found more than two integers in name, don't know what that means"
        mchi = masses[0]
        mphi = masses[1]
        print "Mchi {:5} Mphi {:5}".format(mchi,mphi)
        n = sample.getYieldFromDraw()['val']
        b = sample.getYieldFromDraw(weightString = isrWeight)['val']
        if n>0:
            correction[(mchi, mphi)] = n / b
else:
    raise NotImplementedError( "Don't know what to do with signal: %s." % args.signal )

from StopsDilepton.tools.user import analysis_results
if not os.path.isdir(os.path.join(analysis_results, 'systematics')):
    os.mkdir(os.path.join(analysis_results, 'systematics'))
ofile = os.path.join(analysis_results, 'systematics', 'isrSignalSysNormalization_%s.pkl' % args.signal)
pickle.dump(correction, file(ofile, 'w') )
print "Written %s"%ofile
