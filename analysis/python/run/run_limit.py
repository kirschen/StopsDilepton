#!/usr/bin/env python
import ROOT
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store', default='T2tt',          nargs='?', choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95"], help="which signal?")
argParser.add_argument("--only",           action='store', default=None,            nargs='?',                                                                                           help="pick only one masspoint?")
argParser.add_argument("--scale",          action='store', default=1.0, type=float, nargs='?',                                                                                           help="scaling all yields")
argParser.add_argument("--overwrite",      default = False, action = "store_true", help="Overwrite existing output files")
argParser.add_argument("--controlDYVV",    default = False, action = "store_true", help="Fits for DY/VV CR")
argParser.add_argument("--controlTTZ",     default = False, action = "store_true", help="Fits for TTZ CR")
argParser.add_argument("--fitAll",         default = False, action = "store_true", help="Fits SR and CR together")
args = argParser.parse_args()


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

from StopsDilepton.analysis.SetupHelpers    import channels, trilepChannels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList, MCBasedEstimate, DataDrivenTTJetsEstimate
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions         import regionsO, noRegions, regionsS
from StopsDilepton.analysis.Cache           import Cache


# Define CR
setupDYVV = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False,  'zWindow': 'onZ'})
setupTTZ1 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(2,2),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ2 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ3 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})
setupTTZ4 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False})
setupTTZ5 = setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})

# Define channels for CR
setup.channels     = ['SF','EMu']
setupDYVV.channels = ['SF']
setupTTZ1.channels = ['all']
setupTTZ2.channels = ['all']
setupTTZ3.channels = ['all']
setupTTZ4.channels = ['all']
setupTTZ5.channels = ['all']

# Define regions for CR
setup.regions     = regionsO[1:]
setupDYVV.regions = regionsO[1:]
setupTTZ1.regions = noRegions
setupTTZ2.regions = noRegions
setupTTZ3.regions = noRegions
setupTTZ4.regions = noRegions
setupTTZ5.regions = noRegions

# Define estimators for CR
setup.estimators     = constructEstimatorList(["TTJets-DD","TTZ","DY", 'multiBoson', 'other'])
setupDYVV.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ1.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ2.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ3.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ4.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
setupTTZ5.estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])

if args.fitAll:        setups = [setup, setupDYVV] #, setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
elif args.controlDYVV: setups = [setupDYVV]
elif args.controlTTZ:  setups = [setupTTZ1, setupTTZ2, setupTTZ3, setupTTZ4, setupTTZ5]
else:                  setups = [setup]

from StopsDilepton.analysis.u_float                                              import u_float
from math                                                                        import sqrt

#signals_T8bbllnunu_XCha0p5_XSlep0p5 = [s for s in signals_T8bbllnunu_XCha0p5_XSlep0p5 if not s.mStop==851]

##https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSYSignalSystematicsRun2
from StopsDilepton.tools.user           import combineReleaseLocation
from StopsDilepton.tools.cardFileWriter import cardFileWriter

if args.fitAll:        subDir = 'fitAll' 
elif args.controlDYVV: subDir = 'controlDYVV'
elif args.controlTTZ:  subDir = 'controlTTZ'
else:                  subDir = 'signalOnly'
baseDir = os.path.join(setup.analysis_results, subDir)

limitDir    = os.path.join(baseDir, 'cardFiles', args.signal)
overWrite   = (args.only is not None) or args.overwrite
useCache    = True
verbose     = True

if not os.path.exists(limitDir): os.makedirs(limitDir)
cacheFileName = os.path.join(limitDir, 'calculatedLimits.pkl')
limitCache    = Cache(cacheFileName, verbosity=2)


if   args.signal == "T2tt":                         fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  fastSim = True
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": fastSim = True
elif args.signal == "TTbarDM":                      fastSim = False

scaleUncCache = Cache('scale_%s.pkl' % args.signal, verbosity=2)
isrUncCache   = Cache('isr_%s.pkl'   % args.signal, verbosity=2)

def getScaleUnc(name, r, channel):
  if scaleUncCache.contains((name, r, channel)): return max(0.01, scaleUncCache.get((name, r, channel)))
  else:                                          return 0.01

def getIsrUnc(name, r, channel):
  return 0 #FIXME
  unc = isrUncCache.get((name, r, channel))
  return abs(unc)


def wrapper(s):
    xSecScale = 1
    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = combineReleaseLocation

    cardFileName = os.path.join(limitDir, s.name+'.txt')
    if not os.path.exists(cardFileName) or overWrite:
        counter=0
        c.reset()
        c.addUncertainty('PU',         'lnN')
        c.addUncertainty('topPt',      'lnN')
        c.addUncertainty('JEC',        'lnN')
        c.addUncertainty('unclEn',     'lnN')
        c.addUncertainty('JER',        'lnN')
        c.addUncertainty('SFb',        'lnN')
        c.addUncertainty('SFl',        'lnN')
        c.addUncertainty('trigger',    'lnN')
        c.addUncertainty('leptonSF',   'lnN')
        c.addUncertainty('scale',      'lnN')
        c.addUncertainty('isr',        'lnN')
        c.addUncertainty('top',        'lnN')
        c.addUncertainty('multiBoson', 'lnN')
        c.addUncertainty('DY',         'lnN')
        c.addUncertainty('ttZ',        'lnN')
        c.addUncertainty('other',      'lnN')
        if fastSim:
            c.addUncertainty('SFFS',     'lnN')
            c.addUncertainty('leptonFS', 'lnN')
            c.addUncertainty('FSmet',    'lnN')

        for setup in setups:
          eSignal     = MCBasedEstimate(name=s.name, sample={channel:s for channel in channels+trilepChannels}, cacheDir=setup.defaultCacheDir())
          observation = DataObservation(name='Data', sample=setup.sample['Data'], cacheDir=setup.defaultCacheDir())
          for e in setup.estimators: e.initCache(setup.defaultCacheDir())

          for r in setup.regions:
            for channel in setup.channels:
                niceName = ' '.join([channel, r.__str__()])
                if setup == setupDYVV: niceName += "_controlDYVV"
                if setup == setupTTZ1: niceName += "_controlTTZ1"
                if setup == setupTTZ2: niceName += "_controlTTZ2"
                if setup == setupTTZ3: niceName += "_controlTTZ3"
                if setup == setupTTZ4: niceName += "_controlTTZ4"
                if setup == setupTTZ5: niceName += "_controlTTZ5"
                binname = 'Bin'+str(counter)
                counter += 1
                total_exp_bkg = 0
                c.addBin(binname, [e.name.split('-')[0] for e in setup.estimators], niceName)
                for e in setup.estimators:
                  name = e.name.split('-')[0]
                  expected = e.cachedEstimate(r, channel, setup)
                  total_exp_bkg += expected.val
                  xSecScale = 1
                  #if s.mStop<810:
                  #    xSecScale = 0.01
                  #    print "SCALING XSEC DOWN BY %f"%xSecScale
                  c.specifyExpectation(binname, name, expected.val*args.scale*xSecScale)
                  if expected.val>0:
                      c.specifyUncertainty('PU',       binname, name, 1 + e.PUSystematic(         r, channel, setup).val )
                      c.specifyUncertainty('JEC',      binname, name, 1 + e.JECSystematic(        r, channel, setup).val )
                      c.specifyUncertainty('unclEn',   binname, name, 1 + e.unclusteredSystematic(r, channel, setup).val )
                      c.specifyUncertainty('JER',      binname, name, 1 + e.JERSystematic(        r, channel, setup).val )
                      c.specifyUncertainty('topPt',    binname, name, 1 + e.topPtSystematic(      r, channel, setup).val )
                      c.specifyUncertainty('SFb',      binname, name, 1 + e.btaggingSFbSystematic(r, channel, setup).val )
                      c.specifyUncertainty('SFl',      binname, name, 1 + e.btaggingSFlSystematic(r, channel, setup).val )
                      c.specifyUncertainty('trigger',  binname, name, 1 + e.triggerSystematic(    r, channel, setup).val )
                      c.specifyUncertainty('leptonSF', binname, name, 1 + e.leptonSFSystematic(   r, channel, setup).val )

                      if e.name.count('TTJets'):     c.specifyUncertainty('top',        binname, name, 2 if (setup.regions != noRegions and r == setup.regions[-1]) else 1.5)
                      if e.name.count('multiBoson'): c.specifyUncertainty('multiBoson', binname, name, 1.5)
                      if e.name.count('DY'):         c.specifyUncertainty('DY',         binname, name, 1.5)
                      if e.name.count('TTZ'):        c.specifyUncertainty('ttZ',        binname, name, 1.2)
                      if e.name.count('other'):      c.specifyUncertainty('other',      binname, name, 1.25)

                      #MC bkg stat (some condition to neglect the smaller ones?)
                      uname = 'Stat_'+binname+'_'+name
                      c.addUncertainty(uname, 'lnN')
                      c.specifyUncertainty(uname, binname, name, 1+expected.sigma/expected.val )

                c.specifyObservation(binname, int(args.scale*observation.cachedObservation(r, channel, setup).val))

                #signal
                e = eSignal
                eSignal.isSignal = True
                if fastSim: signalSetup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})
                else:       signalSetup = setup.sysClone()
                if fastSim: signal = 0.5 * (e.cachedEstimate(r, channel, signalSetup) + e.cachedEstimate(r, channel, signalSetup.sysClone({'selectionModifier':'genMet'})))
                else: signal = e.cachedEstimate(r, channel, signalSetup)
                xSecScale = 1
                #if s.mStop<810: xSecScale = 0.01
                c.specifyExpectation(binname, 'signal', args.scale*signal.val*xSecScale )

                if signal.val>0:
                  #c.specifyUncertainty('PU',       binname, 'signal', 1 + e.PUSystematic(         r, channel, signalSetup).val )
                  c.specifyUncertainty('JEC',      binname, 'signal', 1 + e.JECSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('unclEn',   binname, 'signal', 1 + e.unclusteredSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('JER',      binname, 'signal', 1 + e.JERSystematic(        r, channel, signalSetup).val )
                  c.specifyUncertainty('SFb',      binname, 'signal', 1 + e.btaggingSFbSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('SFl',      binname, 'signal', 1 + e.btaggingSFlSystematic(r, channel, signalSetup).val )
                  c.specifyUncertainty('trigger',  binname, 'signal', 1 + e.triggerSystematic(    r, channel, signalSetup).val )
                  c.specifyUncertainty('leptonSF', binname, 'signal', 1 + e.leptonSFSystematic(   r, channel, signalSetup).val )
                  c.specifyUncertainty('scale',    binname, 'signal', 1 + getScaleUnc(eSignal.name, r, channel))
                  c.specifyUncertainty('isr',      binname, 'signal', 1 + getIsrUnc(  eSignal.name, r, channel))
                  if fastSim: 
                    c.specifyUncertainty('leptonFS', binname, 'signal', 1 + e.leptonFSSystematic(    r, channel, signalSetup).val )
                    c.specifyUncertainty('SFFS',     binname, 'signal', 1 + e.btaggingSFFSSystematic(r, channel, signalSetup).val )
                    c.specifyUncertainty('FSmet',    binname, 'signal', 1 + e.fastSimMETSystematic(  r, channel, signalSetup).val )

                  #signal MC stat added in quadrature with PDF uncertainty: 10% uncorrelated
                  uname = 'Stat_'+binname+'_signal'
                  c.addUncertainty(uname, 'lnN')
                  c.specifyUncertainty(uname, binname, 'signal', 1 + sqrt(0.1**2 + signal.sigma/signal.val) )

                if not args.controlDYVV and (signal.val<=0.01 and total_exp_bkg<=0.01 or total_exp_bkg<=0):# or (total_exp_bkg>300 and signal.val<0.05):
                  if verbose: print "Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)
                  c.muted[binname] = True
                else:
                  if verbose: print "NOT Muting bin %s. Total sig: %f, total bkg: %f"%(binname, signal.val, total_exp_bkg)

        c.addUncertainty('Lumi', 'lnN')
        c.specifyFlatUncertainty('Lumi', 1.026)
        cardFileName = c.writeToFile(cardFileName)
    else:
        print "File %s found. Reusing."%cardFileName
    
    if   args.signal == "TTbarDM":                      sConfig = s.mChi, s.mPhi, s.type
    elif args.signal == "T2tt":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": sConfig = s.mStop, s.mNeu

    if useCache and not overWrite and limitCache.contains(sConfig):
      res = limitCache.get(sConfig)
    else:
      res = c.calcLimit(cardFileName)#, options="--run blind")
      c.calcNuisances(cardFileName)
      limitCache.add(sConfig, res, save=True)
    
    xSecScale = 1
    #if s.mStop<810:
    #    xSecScale = 0.1
    #if xSecScale != 1:
    #    for k in res:
    #        res[k] *= xSecScale
    
    if res: 
      if   args.signal == "TTbarDM":                      sString = "mChi %i mPhi %i type %s" % sConfig
      elif args.signal == "T2tt":                         sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  sString = "mStop %i mNeu %i" % sConfig
      elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": sString = "mStop %i mNeu %i" % sConfig
      try:
        print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
        return sConfig, res
      except:
        print "Problem with limit: %r" + str(res)
        return None


if   args.signal == "T2tt":                         from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs
elif args.signal == "TTbarDM":                      from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM as jobs

if args.only is not None:
  wrapper(jobs[int(args.only)])
  exit(0)

results = map(wrapper, jobs)
results = [r for r in results if r]

# Make histograms for T2tt
if args.signal == "T2tt" or args.signal == "T8bbllnunu_XCha0p5_XSlep0p05" or args.signal == "T8bbllnunu_XCha0p5_XSlep0p5" or args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
  exp      = ROOT.TH2F("exp", "exp", 1600/25, 0, 1600, 1500/25, 0, 1500)
  exp_down = exp.Clone("exp_down")
  exp_up   = exp.Clone("exp_up")
  obs      = exp.Clone("obs")
  limitPrefix = args.signal
  for r in results:
    s, res = r
    mStop, mNeu = s
    for hist, qE in [(exp, '0.500'), (exp_up, '0.160'), (exp_down, '0.840'), (obs, '-1.000')]:
      #print hist, qE, res[qE]
      if qE=='0.500':
        print "Masspoint m_gl %5.3f m_neu %5.3f, expected limit %5.3f"%(mStop,mNeu,res[qE])
      hist.GetXaxis().FindBin(mStop)
      hist.GetYaxis().FindBin(mNeu)
      #print hist.GetName(), mStop, mNeu, res[qE]
      hist.Fill(mStop, mNeu, res[qE])

  limitResultsFilename = os.path.join(baseDir, 'limits', args.signal, limitPrefix,'limitResults.root')
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
if args.signal == "TTbarDM":
  # Create table
  texdir = os.path.join(baseDir, 'limits', args.signal, limitPrefix)
  if not os.path.exists(texdir): os.makedirs(texdir)

  for type in sorted(set([type_ for ((mChi, mPhi, type_), res) in results])):
    for lim, key in [['exp','0.500'], ['obs', '-1.000']]:
        chiList = sorted(set([mChi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
        phiList = sorted(set([mPhi  for ((mChi, mPhi, type_), res) in results if type_ == type]))
        ofilename = texdir + "/%s_%s.tex"%(type, lim)
        print "Writing to ", ofilename 
        with open(ofilename, "w") as f:
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
                      result = "%.2f" % r[key]
              except:
                pass
              resultList.append(result)
            if chi == chiList[0]: f.write("\\multirow{" + str(len(chiList)) + "}{*}{$m_\\chi$ (GeV)}")
            f.write(" & " + str(chi) + " & " + " & ".join(resultList) + "\\\\ \n")
          f.write(" \\end{tabular}")
