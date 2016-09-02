#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--estimateDY",     action='store', default='DY',                nargs='?', choices=["DY","DY-DD"],                                                                                help="which DY estimate?")
argParser.add_argument("--estimateTTZ",    action='store', default='TTZ',               nargs='?', choices=["TTZ","TTZ-DD","TTZ-DD-Top16009"],                                                            help="which TTZ estimate?")
argParser.add_argument("--estimateTTJets", action='store', default='TTJets',            nargs='?', choices=["TTZJets","TTJets-DD"],                                                                       help="which TTJets estimate?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.estimators   import setup, constructEstimatorList, MCBasedEstimate, DataDrivenTTZEstimate, DataDrivenDYEstimate, DataDrivenTTJetsEstimate
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions      import regions80X
from StopsDilepton.analysis.Cache        import Cache


regions = regions80X

estimators = constructEstimatorList([args.estimateTTJets, 'other', args.estimateDY, args.estimateTTZ])
observation = DataObservation(name='Data', sample=setup.sample['Data'])

for e in estimators + [observation]:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt

##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.user           import combineReleaseLocation
from StopsDilepton.tools.cardFileWriter import cardFileWriter

limitPrefix = "regions80X"
limitDir    = os.path.join(setup.analysis_results, setup.prefix(), args.estimateDY, args.estimateTTZ, args.estimateTTJets, 'cardFiles', args.signal, limitPrefix)
overWrite   = False
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits.pkl')
limitCache    = Cache(cacheFileName, verbosity=2)

if   args.signal == "T2tt": fastSim = True
elif args.signal == "DM":   fastSim = False

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
	c.addUncertainty('trigger',  'lnN')
	c.addUncertainty('leptonSF', 'lnN')
        if fastSim:
 	  c.addUncertainty('SFFS',     'lnN')
  	  c.addUncertainty('leptonFS', 'lnN')

	eSignal = MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() )
        for r in regions[1:]:
            for channel in ['MuMu', 'EE', 'EMu']:
                niceName = ' '.join([channel, r.__str__()])
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name for e in estimators], niceName)
                for e in estimators:
                    expected = e.cachedEstimate(r, channel, setup)
                    total_exp_bkg += expected.val
                    c.specifyExpectation(binname, e.name, expected.val )

                    if expected.val>0:
                        c.specifyUncertainty('PU',       binname, e.name, 1 + e.PUSystematic(          r, channel, setup).val )
                        c.specifyUncertainty('JEC',      binname, e.name, 1 + e.JECSystematic(        r, channel, setup).val )
                        c.specifyUncertainty('JER',      binname, e.name, 1 + e.JERSystematic(        r, channel, setup).val )
                        c.specifyUncertainty('topPt',    binname, e.name, 1 + e.topPtSystematic(      r, channel, setup).val )
                        c.specifyUncertainty('SFb',      binname, e.name, 1 + e.btaggingSFbSystematic(r, channel, setup).val )
                        c.specifyUncertainty('SFl',      binname, e.name, 1 + e.btaggingSFlSystematic(r, channel, setup).val )
                        c.specifyUncertainty('trigger',  binname, e.name, 1 + e.triggerSystematic(    r, channel, setup).val )
                        c.specifyUncertainty('leptonSF', binname, e.name, 1 + e.leptonSFSystematic(   r, channel, setup).val )

                        #MC bkg stat (some condition to neglect the smaller ones?)
                        uname = 'Stat_'+binname+'_'+e.name
                        c.addUncertainty(uname, 'lnN')
                        c.specifyUncertainty('Stat_'+binname+'_'+e.name, binname, e.name, 1+expected.sigma/expected.val )

                c.specifyObservation(binname, int(observation.cachedObservation(r, channel, setup).val))

                #signal
                e = eSignal
                eSignal.isSignal = True
                if fastSim: signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']})
                signal = e.cachedEstimate(r, channel, signalSetup)

                c.specifyExpectation(binname, 'signal', signal.val )

                if signal.val>0:
                    c.specifyUncertainty('PU',       binname, 'signal', 1 + e.PUSystematic(         r, channel, signalSetup).val )
                    c.specifyUncertainty('JEC',      binname, 'signal', 1 + e.JECSystematic(        r, channel, signalSetup).val )
                    c.specifyUncertainty('JER',      binname, 'signal', 1 + e.JERSystematic(        r, channel, signalSetup).val )
                    c.specifyUncertainty('SFb',      binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('SFl',      binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('trigger',  binname, 'signal', 1 + e.triggerSystematic(    r, channel, signalSetup).val )
                    c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonSFSystematic(   r, channel, signalSetup).val )
                    if fastSim: 
                      c.specifyUncertainty('leptonFS', binname, 'signal', 1 + e.leptonFSSystematic(    r, channel, signalSetup).val )
                      c.specifyUncertainty('SFFS',     binname, 'signal', 1 + e.btaggingSFFSSystematic(r, channel, signalSetup).val )

                    #signal MC stat added in quadrature with PDF uncertainty: 10% uncorrelated
                    uname = 'Stat_'+binname+'_signal'
                    c.addUncertainty(uname, 'lnN')
                    c.specifyUncertainty(uname, binname, 'signal', 1 + sqrt(0.1**2 + signal.sigma/signal.val) )

                if signal.val<=0.01 and total_exp_bkg<=0.01 or total_exp_bkg<=0:# or (total_exp_bkg>300 and signal.val<0.05):
                    if verbose: print "Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
                    c.muted[binname] = True
                else:
                    if verbose: print "NOT Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)

        c.addUncertainty('Lumi', 'lnN')
        c.specifyFlatUncertainty('Lumi', 1.062)
        cardFileName = c.writeToFile(cardFileName)
    else:
        print "File %s found. Reusing."%cardFileName

    if   args.signal == "DM":   sConfig = s.mChi, s.mPhi, s.type
    elif args.signal == "T2tt": sConfig = s.mStop, s.mNeu

    if useCache and not overWrite and limitCache.contains(s):
      res = limitCache.get(sConfig)
    else:
      res = c.calcLimit(cardFileName)
      limitCache.add(sConfig, res, save=True)

    if res: 
      if   args.signal == "DM":   sString = "mChi %i mPhi %i type %i" % sConfig
      elif args.signal == "T2tt": sString = "mStop %i mNeu %i" % sConfig
      try:
        print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
        return sConfig, res
      except:
        print "Problem with limit: %r" + str(res)
        return None

if   args.signal == "T2tt": jobs = signals_T2tt 
elif args.signal == "DM":   jobs = signals_TTDM

results = map(wrapper, jobs)
results = [r for r in results if r]

# Make histograms for T2tt
if args.signal == "T2tt":
  exp      = ROOT.TH2F("exp", "exp", 1000/25, 0, 1000, 1000/25, 0, 1000)
  exp_down = exp.Clone("exp_down")
  exp_up   = exp.Clone("exp_up")
  obs      = exp.Clone("obs")

  for r in results:
    s, res = r
    mStop, mNeu = s
    for hist, qE in [(exp, '0.500'), (exp_up, '0.160'), (exp_down, '0.840'), (obs, '-1.000')]:
      hist.Fill(mStop, mNeu, res[qE])

  limitResultsFilename = os.path.join(os.path.join(setup.analysis_results, setup.prefix(), args.estimateDY, args.estimateTTZ, args.estimateTTJets, 'limits', args.signal, limitPrefix,'limitResults.root'))
  if not os.path.exists(os.path.dirname(limitResultsFilename)):
      os.makedirs(os.path.dirname(limitResultsFilename))

  outfile = ROOT.TFile(limitResultsFilename, "recreate")
  exp      .Write()
  exp_down .Write()
  exp_up   .Write()
  obs      .Write()
  outfile.Close()
  print "Written %s"%limitResultsFilename


# Make table for DM
if args.signal == "DM":
  # Create table
  texdir = os.path.join(os.path.join(setup.analysis_results, setup.prefix(), args.estimateDY, args.estimateTTZ, args.estimateTTJets, 'limits', args.signal, limitPrefix))
  if not os.path.exists(texdir): os.makedirs(texdir)

  for type in sorted(set([type_ for ((mChi, mPhi, type_), res) in results])):
    chiList = sorted(set([mChi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
    phiList = sorted(set([mPhi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
    print "Writing to " + texdir + "/" + type + ".tex"
    with open(texdir + "/" + type + ".tex", "w") as f:
      f.write("\\begin{tabular}{cc|" + "c"*len(phiList) + "} \n")
      f.write(" & & \multicolumn{" + str(len(phiList)) + "}{c}{$m_\\phi$ (GeV)} \\\\ \n")
      f.write("& &" + " & ".join(str(x) for x in phiList) + "\\\\ \n \\hline \\hline \n")
      for chi in chiList:
	resultList = []
	for phi in phiList:
	  result = ''
	  try:
	    for ((c, p, t), r) in results:
	      if c == chi and p == phi and t == type:
		  result = "%.3f" % r['0.500']
	  except:
	    pass
	  resultList.append(result)
	if chi == chiList[0]: f.write("\\multirow{" + str(len(chiList)) + "}{*}{$m_\\chi$ (GeV)}")
	f.write(" & " + str(chi) + " & " + " & ".join(resultList) + "\\\\ \n")
      f.write(" \\end{tabular}")
