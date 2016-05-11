import os
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--metSigMin",  dest="metSigMin",  default=5,  type="int",    action="store", help="metSigMin?")
parser.add_option("--metMin",     dest="metMin",     default=80, type="int",    action="store", help="metMin?")
parser.add_option("--multiIsoWP", dest="multiIsoWP", default="", type="string", action="store", help="multiIsoWP?")
parser.add_option("--relIso04",   dest="relIso04",   default=-1, type=float,    action="store", help="relIso04 cut?")
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.defaultAnalysis import setup, regions, bkgEstimators
setup.verbose = False
setup.parameters['metMin']    = options.metMin
setup.parameters['metSigMin'] = options.metSigMin

if options.multiIsoWP!="":
    multiIsoWPs = ['VL', 'L', 'M', 'T', 'VT']
    wpMu, wpEle=options.multiIsoWP.split(',')
    from StopsDilepton.tools.objectSelection import multiIsoLepString
    setup.externalCuts.append(multiIsoLepString(wpMu, wpEle, ('l1_index','l2_index')))
    setup.prefixes.append('multiIso'+options.multiIsoWP.replace(',',''))

if options.relIso04>0:
    setup.externalCuts.append("&&".join(["LepGood_relIso04["+ist+"]<"+str(options.relIso04) for ist in ('l1_index','l2_index')]))
    setup.prefixes.append('relIso04sm'+str(int(100*options.relIso04)))

for e in bkgEstimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.u_float import u_float
from math import sqrt
##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.user import combineReleaseLocation
from StopsDilepton.tools.cardFileWriter import cardFileWriter

limitPrefix = 'flavSplit_almostAllReg'
overWrite = True
verbose   = True

def wrapper(s):
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    counter=0
    c.reset()
    c.addUncertainty('PU', 'lnN')
    c.addUncertainty('topPt', 'lnN')
    c.addUncertainty('JEC', 'lnN')
    c.addUncertainty('JER', 'lnN')
    c.addUncertainty('SFb', 'lnN')
    c.addUncertainty('SFl', 'lnN')
    c.addUncertainty('SFFS', 'lnN')
    c.addUncertainty('leptonSF', 'lnN')

    eSignal = MCBasedEstimate(name=s.name,    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() )
    cardFileName = os.path.join(setup.analysis_results,  setup.prefix(), 'cardFiles', limitPrefix, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
        for r in regions:
            for channel in ['MuMu', 'EE', 'EMu']:
#      for channel in ['all']:
                niceName = ' '.join([channel, r.__str__()])
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name for e in bkgEstimators], niceName)
                for e in bkgEstimators:
                    expected = e.cachedEstimate(r, channel, setup)
                    total_exp_bkg += expected.val
                    c.specifyExpectation(binname, e.name, expected.val )

                    if expected.val>0:

                        #PU bkg
                        c.specifyUncertainty('PU', binname, e.name, 1 + e.PUSystematic(r, channel, setup).val )

                        #JEC bkg
                        c.specifyUncertainty('JEC', binname, e.name, 1 + e.JECSystematic(r, channel, setup).val )

                        #JER bkg
                        c.specifyUncertainty('JER', binname, e.name, 1 + e.JERSystematic(r, channel, setup).val )

                        #topPt reweighting
                        c.specifyUncertainty('topPt', binname, e.name, 1 + e.topPtSystematic(r, channel, setup).val )

                        #b-tagging SF
                        c.specifyUncertainty('SFb', binname, e.name, 1 + e.btaggingSFbSystematic(r, channel, setup).val )
                        c.specifyUncertainty('SFl', binname, e.name, 1 + e.btaggingSFlSystematic(r, channel, setup).val )

                        #MC bkg stat (some condition to neglect the smaller ones?)
                        uname = 'Stat_'+binname+'_'+e.name
                        c.addUncertainty(uname, 'lnN')
                        c.specifyUncertainty('Stat_'+binname+'_'+e.name, binname, e.name, 1+expected.sigma/expected.val )

    #      assert total_exp_bkg>=0, "Total background is negative. Don't know what to do."

                c.specifyObservation(binname, int(total_exp_bkg) )

                #signal
                e = eSignal
                signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']}, parameters={'useTriggers':False})
                signal = e.cachedEstimate(r, channel, signalSetup)

                c.specifyExpectation(binname, 'signal', signal.val )

                if signal.val>0:

                    #PU signal
                    c.specifyUncertainty('PU', binname, 'signal', 1 + e.PUSystematic(r, channel, signalSetup).val )

                    #JEC signal
                    c.specifyUncertainty('JEC', binname, 'signal', 1 + e.JECSystematic(r, channel, signalSetup).val )

                    #JER signal
                    c.specifyUncertainty('JER', binname, 'signal', 1 + e.JERSystematic(r, channel, signalSetup).val )

                    #lepton FastSim SF uncertainty
                    c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonFSSystematic(r, channel, signalSetup).val )

                    #b-tagging SF (including FastSim SF)
                    c.specifyUncertainty('SFb', binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('SFl', binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('SFFS', binname, 'signal', 1 + e.btaggingSFFSSystematic(r, channel, signalSetup).val )

                    #signal MC stat added in quadrature with PDF uncertainty: 10% uncorrelated
                    uname = 'Stat_'+binname+'_signal'
                    c.addUncertainty(uname, 'lnN')
                    c.specifyUncertainty(uname, binname, 'signal', 1 + sqrt(0.1**2 + signal.sigma/signal.val) )

                if signal.val<=0.01 and total_exp_bkg<=0.01 or total_exp_bkg<=0:# or (total_exp_bkg>300 and signal.val<0.05):
                    if verbose: print "Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
                    c.muted[binname] = True
                else:
                    if verbose: print "NOT Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
        #
        c.addUncertainty('Lumi', 'lnN')
        c.specifyFlatUncertainty('Lumi', 1.046)
        cardFileName = c.writeToFile(cardFileName)
    else:
        print "File %s found. Reusing."%cardFileName
    res = c.calcLimit(cardFileName)
    mStop, mNeu = s.mStop, s.mNeu
    try:
        if res: print "Result: mStop %i mNeu %i obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(mStop, mNeu, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
    except:
        print "Something wrong with the limit: %r"%res
    return mStop, mNeu, res

jobs = [T2tt_450_0]
#jobs = [T2tt_400_0, T2tt_400_50, T2tt_650_250]
#jobs = signals_T2tt

#from multiprocessing import Pool
#pool = Pool(processes=2)
#results = pool.map(wrapper, jobs)
#pool.close()
#pool.join()

results = map(wrapper, jobs)

T2tt_exp      = ROOT.TH2F("T2tt_exp", "T2tt_exp", 1000/25, 0, 1000, 1000/25, 0, 1000)
T2tt_exp_down = T2tt_exp.Clone("T2tt_exp_down")
T2tt_exp_up   = T2tt_exp.Clone("T2tt_exp_up")
T2tt_obs      = T2tt_exp.Clone("T2tt_obs")

for r in results:
  mStop, mNeu, res = r
  for hist, qE in [(T2tt_exp, '0.500'), (T2tt_exp_up, '0.160'), (T2tt_exp_down, '0.840'), (T2tt_obs, '-1.000')]:
    try:
        hist.Fill(mStop, mNeu, res[qE])
    except:
        print "Something failed for mStop %i mNeu %i"%(mStop, mNeu)

limitResultsFilename = os.path.join(os.path.join(setup.analysis_results, setup.prefix(), 'limits', limitPrefix,'T2tt_limitResults.root'))
if not os.path.exists(os.path.dirname(limitResultsFilename)):
    os.makedirs(os.path.dirname(limitResultsFilename))

outfile = ROOT.TFile(limitResultsFilename, "recreate")
T2tt_exp      .Write()
T2tt_exp_down .Write()
T2tt_exp_up   .Write()
T2tt_obs      .Write()
outfile.Close()
print "Written %s"%limitResultsFilename
