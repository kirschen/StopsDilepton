#!/usr/bin/env python
import os
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--metSigMin",  dest="metSigMin",  default=5,  type="int",    action="store", help="metSigMin?")
parser.add_option("--metMin",     dest="metMin",     default=80, type="int",    action="store", help="metMin?")
parser.add_option("--multiIsoWP", dest="multiIsoWP", default="", type="string", action="store", help="multiIsoWP?")
parser.add_option("--relIso04",   dest="relIso04",   default=-1, type=float,    action="store", help="relIso04 cut?")
parser.add_option("--regions",    dest="regions",    default="defaultRegions",  action="store", help="which regions setup?", choices=["defaultRegions","reducedRegionsA","reducedRegionsB","reducedRegionsAB","reducedRegionsNew","reducedRegionsC"])
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.estimators import setup, mcAnalysisEstimators
from StopsDilepton.analysis.regions import defaultRegions, reducedRegionsA, reducedRegionsB, reducedRegionsAB, reducedRegionsNew, reducedRegionsC
from StopsDilepton.analysis.Cache import Cache
setup.verbose = False
setup.parameters['metMin']    = options.metMin
setup.parameters['metSigMin'] = options.metSigMin

if options.regions == "defaultRegions":      regions = defaultRegions
elif options.regions == "reducedRegionsA":   regions = reducedRegionsA
elif options.regions == "reducedRegionsB":   regions = reducedRegionsB
elif options.regions == "reducedRegionsAB":  regions = reducedRegionsAB
elif options.regions == "reducedRegionsNew": regions = reducedRegionsNew
elif options.regions == "reducedRegionsC":   regions = reducedRegionsC
else: raise Exception("Unknown regions setup")


if options.multiIsoWP!="":
    multiIsoWPs = ['VL', 'L', 'M', 'T', 'VT']
    wpMu, wpEle=options.multiIsoWP.split(',')
    from StopsDilepton.tools.objectSelection import multiIsoLepString
    setup.externalCuts.append(multiIsoLepString(wpMu, wpEle, ('l1_index','l2_index')))
    setup.prefixes.append('multiIso'+options.multiIsoWP.replace(',',''))

if options.relIso04>0:
    setup.externalCuts.append("&&".join(["LepGood_relIso04["+ist+"]<"+str(options.relIso04) for ist in ('l1_index','l2_index')]))
    setup.prefixes.append('relIso04sm'+str(int(100*options.relIso04)))

for e in mcAnalysisEstimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.u_float import u_float
from math import sqrt
##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.user import combineReleaseLocation
from StopsDilepton.tools.cardFileWriter import cardFileWriter

limitPrefix = options.regions
limitDir    = os.path.join(setup.analysis_results, setup.prefix(), 'cardFiles', limitPrefix)
overWrite   = False
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits.pkl')
limitCache    = Cache(cacheFileName, verbosity=2)


def wrapper(s):
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    cardFileName = os.path.join(limitDir, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
	counter=0
	c.reset()
	c.addUncertainty('PU',       'lnN')
	c.addUncertainty('topPt',    'lnN')
	c.addUncertainty('JEC',      'lnN')
	c.addUncertainty('JER',      'lnN')
	c.addUncertainty('SFb',      'lnN')
	c.addUncertainty('SFl',      'lnN')
#	c.addUncertainty('SFFS',     'lnN')
#	c.addUncertainty('leptonSF', 'lnN')

	eSignal = MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() )
        for r in regions[1:]:
            for channel in ['MuMu', 'EE', 'EMu']:
#      for channel in ['all']:
                niceName = ' '.join([channel, r.__str__()])
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name for e in mcAnalysisEstimators], niceName)
                for e in mcAnalysisEstimators:
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
     #           signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']}, parameters={'useTriggers':False})
                signalSetup = setup.sysClone(parameters={'useTriggers':False})
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
#                    c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonFSSystematic(r, channel, signalSetup).val )

                    #b-tagging SF (including FastSim SF)
                    c.specifyUncertainty('SFb', binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('SFl', binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
#                    c.specifyUncertainty('SFFS', binname, 'signal', 1 + e.btaggingSFFSSystematic(r, channel, signalSetup).val )

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
    mChi, mPhi, type = s.mChi, s.mPhi, s.type
    if useCache and not overWrite and limitCache.contains((mChi, mPhi, type)):
      res = limitCache.get((mChi, mPhi, type))
    else:
      res = c.calcLimit(cardFileName)
      limitCache.add((mChi, mPhi, type), res, save=True)
    try:
      if res: print "Result: %s mChi %i mPhi %i obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(type, mChi, mPhi, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
    except:
      print "Something wrong with the limit: %r"%res
    return mChi, mPhi, type, res

#jobs = [DM_450_0]
#jobs = [DM_400_0, DM_400_50, DM_650_250]
jobs = signals_TTDM

#from multiprocessing import Pool
#pool = Pool(processes=2)
#results = pool.map(wrapper, jobs)
#pool.close()
#pool.join()

results = map(wrapper, jobs)

DM_exp      = ROOT.TH2F("DM_exp", "DM_exp", 1000/25, 0, 1000, 1000/25, 0, 1000)
DM_exp_down = DM_exp.Clone("DM_exp_down")
DM_exp_up   = DM_exp.Clone("DM_exp_up")
DM_obs      = DM_exp.Clone("DM_obs")

for r in results:
  mChi, mPhi, type, res = r
  if type != "scalar": continue
  for hist, qE in [(DM_exp, '0.500'), (DM_exp_up, '0.160'), (DM_exp_down, '0.840'), (DM_obs, '-1.000')]:
    try:
        hist.Fill(mChi, mPhi, res[qE])
    except:
        print "Something failed for mChi %i mPhi %i res %s"%(mChi, mPhi, res)

limitResultsFilename = os.path.join(os.path.join(setup.analysis_results, setup.prefix(), 'limits', limitPrefix,'DM_limitResults.root'))
if not os.path.exists(os.path.dirname(limitResultsFilename)):
    os.makedirs(os.path.dirname(limitResultsFilename))

outfile = ROOT.TFile(limitResultsFilename, "recreate")
DM_exp      .Write()
DM_exp_down .Write()
DM_exp_up   .Write()
DM_obs      .Write()
outfile.Close()
print "Written %s"%limitResultsFilename

# Create table
texdir = os.path.join(os.path.join(setup.analysis_results, setup.prefix(), 'limits', limitPrefix))

for type in sorted(set([type_ for (mChi, mPhi, type_, res) in results])):
  chiList = sorted(set([mChi for (mChi, mPhi, type_, res) in results if type_ == type]))
  phiList = sorted(set([mPhi for (mChi, mPhi, type_, res) in results if type_ == type]))
  print "Writing to " + texdir + "/" + type + ".tex"
  with open(texdir + "/" + type + ".tex", "w") as f:
    f.write("\\begin{tabular}{cc|" + "c"*len(phiList) + "} \n")
    f.write(" & & \multicolumn{" + str(len(phiList)) + "}{c}{$m_\\phi$ (GeV)} \\\\ \n")
    f.write("&" + " & ".join(str(x) for x in phiList) + "\\\\ \n \\hline \\hline \n")
    for chi in chiList:
      resultList = []
      for phi in phiList:
        result = ''
        try:
	  for (c, p, t, r) in results:
	    if c == chi and p == phi and t == type:
		result = "%.3f" % r['0.500']
        except:
          pass
        resultList.append(result)
      if chi == chiList[0]: f.write("\\multirow{" + str(len(chiList)) + "}{*}{$m_\\chi$ (GeV)}")
      f.write(" & " + str(chi) + " & " + " & ".join(resultList) + "\\\\ \n")
    f.write(" \\end{tabular}")
