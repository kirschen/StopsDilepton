#!/usr/bin/env python
'''
Combination on card file level
'''

import ROOT
import os
import argparse
from RootTools.core.Sample import Sample
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',        default='INFO',         nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store',        default='T2tt',         nargs='?', choices=["T2tt","T8bbllnunu_XCha0p5_XSlep0p5","T8bbllnunu_XCha0p5_XSlep0p05","T8bbllnunu_XCha0p5_XSlep0p95","T2bW"],                                                                         help="which signal scan?")
argParser.add_argument("--overwrite",      action = "store_true", default = False,                                                                                                             help="Overwrite existing output files")
argParser.add_argument("--controlRegions", action='store',        default='signalOnly',   nargs='?', choices=["controlAll","signalOnly","controlDYVV","controlTTZ","controlTT","fitAll"],                help="which signal scan?")

argParser.add_argument("--model",          action='store',        default='dim6top_LO',   nargs='?', choices=["dim6top_LO", "ewkDM"],                                                          help="which signal model?")
argParser.add_argument("--only",           action='store',        default=None,           nargs='?',                                                                                           help="pick only one signal point?")
argParser.add_argument("--includeCR",      action='store_true',                                                                                                                                help="Do simultaneous SR and CR fit")
argParser.add_argument("--expected",       action='store_true',                                                                                                                                help="Do simultaneous SR and CR fit")
argParser.add_argument("--calcNuisances",  action='store_true',                                                                         help="Extract the nuisances and store them in text files?")


args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

from math                               import sqrt
from copy                               import deepcopy


from StopsDilepton.analysis.Setup               import Setup

#from StopsDilepton.tools.resultsDB             import resultsDB
from StopsDilepton.tools.u_float                import u_float
from StopsDilepton.tools.user                   import analysis_results,  plot_directory
from StopsDilepton.tools.cardFileWriter         import cardFileWriter
from StopsDilepton.analysis.Cache               import Cache

# some fake setup
setup = Setup(2016)

years = [2016,2017,2018]
#analysis_results = '/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v3/'

overWrite = args.overwrite
def wrapper(s):

    logger.info("Now working on %s", s.name)

    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = os.path.abspath('.')
    cards = {}
    
    # get the seperated cards
    for year in years:
        
        baseDir  = analysis_results+"/%s/%s/"%(year,args.controlRegions)
        limitDir = baseDir+"/cardFiles/%s/%s/"%(args.signal,'expected' if args.expected else 'observed')
        cardFileName = os.path.join(limitDir, s.name+'_shapeCard.txt')

        if not os.path.isfile(cardFileName):
            raise IOError("File %s doesn't exist!"%cardFileName)

        cards[year] = cardFileName
    
    baseDir  = baseDir.replace('2018','comb')
    limitDir = limitDir.replace('2018','comb')
    
    cacheFileName = os.path.join(limitDir, 'calculatedLimits')
    limitCache    = Cache(cacheFileName, verbosity=2)


    # run combine and store results in sqlite database
    if not os.path.isdir(limitDir):
        os.makedirs(limitDir)
    #resDB = resultsDB(limitDir+'/results.sq', "results", setup.resultsColumns)

    if   args.signal == "TTbarDM":                      sConfig = s.mChi, s.mPhi, s.type
    elif args.signal == "T2tt":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T2bt":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T2bW":                         sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  sConfig = s.mStop, s.mNeu
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": sConfig = s.mStop, s.mNeu
    elif args.signal == "ttHinv":                       sConfig = ("ttHinv", "2l")

    #overWrite = False

    if not overWrite and limitCache.contains(sConfig):
        
        res = limitCache.get(sConfig)
        logger.info("Found result for %s, reusing", s.name)

    else:
        print "*" *100
        combinedCard = c.combineCards( cards )
        res = c.calcLimit(combinedCard)
        print res 
        print "+"*10
        if args.calcNuisances:
            c.calcNuisances(combinedCard)

            ###################
            # extract the SFs #
            ###################
            #if not args.useTxt 
            if True:
                # Would be a bit more complicated with the classical txt files, so only automatically extract the SF when using shape based datacards
                from StopsDilepton.tools.getPostFit import getPrePostFitFromMLF
                print combinedCard
                print cardFileName
                combineWorkspace = combinedCard.replace('shapeCard.txt','shapeCard_FD.root')
                print "Extracting fit results from %s"%combineWorkspace

                postFitResults = getPrePostFitFromMLF(combineWorkspace)

                top_prefit  = 0
                top_postfit = 0
                ttZ_prefit  = 0
                ttZ_postfit = 0
                DY_prefit   = 0
                DY_postfit  = 0
                MB_prefit   = 0
                MB_postfit   = 0
                other_prefit  = 0
                other_postfit  = 0

                for year in years:
                    binName = "dc_%s"%year

                    top_prefit  += postFitResults['results']['shapes_prefit'][binName]['TTJetsF'] + postFitResults['results']['shapes_prefit'][binName]['TTJetsG'] + postFitResults['results']['shapes_prefit'][binName]['TTJetsNG']
                    top_postfit += postFitResults['results']['shapes_fit_b'][binName]['TTJetsF'] + postFitResults['results']['shapes_fit_b'][binName]['TTJetsG'] + postFitResults['results']['shapes_fit_b'][binName]['TTJetsNG']

                    ttZ_prefit  += postFitResults['results']['shapes_prefit'][binName]['TTZ']
                    ttZ_postfit += postFitResults['results']['shapes_fit_b'][binName]['TTZ']

                    DY_prefit  += postFitResults['results']['shapes_prefit'][binName]['DY']
                    DY_postfit += postFitResults['results']['shapes_fit_b'][binName]['DY']

                    MB_prefit  += postFitResults['results']['shapes_prefit'][binName]['multiBoson']
                    MB_postfit += postFitResults['results']['shapes_fit_b'][binName]['multiBoson']

                    other_prefit  += postFitResults['results']['shapes_prefit'][binName]['other']
                    other_postfit += postFitResults['results']['shapes_fit_b'][binName]['other']

                print
                print "## Scale Factors for backgrounds: ##"
                print "{:20}{:4.2f}{:3}{:4.2f}".format('top:',          (top_postfit/top_prefit).val, '+/-',  top_postfit.sigma/top_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('ttZ:',          (ttZ_postfit/ttZ_prefit).val, '+/-',  ttZ_postfit.sigma/ttZ_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('Drell-Yan:',    (DY_postfit/DY_prefit).val,   '+/-',  DY_postfit.sigma/DY_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('multiBoson:',   (MB_postfit/MB_prefit).val,   '+/-',  MB_postfit.sigma/MB_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('other:',        (other_postfit/other_prefit).val,   '+/-',  other_postfit.sigma/other_postfit.val)




        #print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
        limitCache.add(sConfig, res)
        logger.info("Adding results to database")
        logger.info("Results stored in %s", limitDir )


    if res:
        if   args.signal == "TTbarDM":                        sString = "mChi %i mPhi %i type %s" % sConfig
        elif args.signal == "T2tt":                           sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T2bt":                           sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T2bW":                           sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":   sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09":   sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":    sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":   sString = "mStop %i mNeu %i" % sConfig
        elif args.signal == "ttHinv":                         sString = "ttH->inv"
    #print sString, res
    try:
        print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
        return sConfig, res
    except:
        print "Problem with limit: %r"%str(res)
        return None

if args.signal == "T2tt":
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2017_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt as jobs
elif args.signal == "T2bW":
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 as jobs
elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 as jobs

# FIXME: removing 1052_0 from list
for i, j in enumerate(jobs):
    if j.name == "T8bbllnunu_XCha0p5_XSlep0p05_1052_0":
        print "~removing ", j.name
        del jobs[i]

allJobs = [j for j in jobs if j.name != 'T2tt_150_63']
if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        jobNames = [ x.name for x in jobs ]
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)
#i= [j for j in jobs if j.name != 'T2tt_150_63']

results = map(wrapper, allJobs)
results = [r for r in results if r]

#########################################################################################
# Process the results. Make 2D hists for SUSY scans, or table for the DM interpretation #
#########################################################################################

# Make histograms for T2tt
baseDir  = analysis_results+"/comb/%s/"%(args.controlRegions)
if "T2" in args.signal or  "T8bb" in args.signal:
    binSize = 25
    shift = binSize/2.*(-1)
    exp      = ROOT.TH2F("exp", "exp", 1600/25, shift, 1600+shift, 1500/25, shift, 1500+shift)
    exp_down = exp.Clone("exp_down")
    exp_up   = exp.Clone("exp_up")
    obs      = exp.Clone("obs")
    limitPrefix = args.signal
    for r in results:
        s, res = r
        mStop, mNeu = s
        resultList = [(exp, '0.500'), (exp_up, '0.160'), (exp_down, '0.840'), (obs, '-1.000')]

        for hist, qE in resultList:
            #print hist, qE, res[qE]
            if qE=='0.500':
              print "Masspoint m_gl %5.3f m_neu %5.3f, expected limit %5.3f"%(mStop,mNeu,res[qE])
            if qE=='-1.000':
              print "Observed limit %5.3f"%(res[qE])
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

