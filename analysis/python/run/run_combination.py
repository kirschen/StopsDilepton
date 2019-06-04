#!/usr/bin/env python
'''
Combination on card file level
'''

import ROOT
import os
import argparse
from RootTools.core.Sample import Sample
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',         nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],             help="Log level for logging")
argParser.add_argument("--signal",         action='store',      default='T2tt',         nargs='?', choices=["T2tt"], help="which signal scan?")
argParser.add_argument("--model",          action='store',      default='dim6top_LO',   nargs='?', choices=["dim6top_LO", "ewkDM"], help="which signal model?")
argParser.add_argument("--only",           action='store',      default=None,           nargs='?',                                                                                           help="pick only one signal point?")
argParser.add_argument("--includeCR",      action='store_true', help="Do simultaneous SR and CR fit")
argParser.add_argument("--expected",      action='store_true', help="Do simultaneous SR and CR fit")
argParser.add_argument("--calcNuisances",  action='store_true', help="Extract the nuisances and store them in text files?")


args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

from math                               import sqrt
from copy                               import deepcopy


from StopsDilepton.analysis.Setup              import Setup

#from StopsDilepton.tools.resultsDB             import resultsDB
from StopsDilepton.tools.u_float               import u_float
from StopsDilepton.tools.user                  import analysis_results,  plot_directory
from StopsDilepton.tools.cardFileWriter        import cardFileWriter

# some fake setup
setup = Setup(2016)

years = [2017,2018]

def wrapper(s):

    logger.info("Now working on %s", s.name)

    c = cardFileWriter.cardFileWriter()
    c.releaseLocation = os.path.abspath('.')
    cards = {}
    
    # get the seperated cards
    for year in years:
        
        controlRegions = 'controlAll'
        limitDir = analysis_results+"/%s/%s/cardFiles/%s/%s/"%(year,controlRegions,args.signal,'expected' if args.expected else 'observed')
        cardFileName = os.path.join(limitDir, s.name+'_shapeCard.txt')

        if not os.path.isfile(cardFileName):
            raise IOError("File %s doesn't exist!"%cardFileName)

        cards[year] = cardFileName
    
    limitDir = limitDir.replace('2018','comb')
    
    # run combine and store results in sqlite database
    if not os.path.isdir(limitDir):
        os.makedirs(limitDir)
    #resDB = resultsDB(limitDir+'/results.sq', "results", setup.resultsColumns)
    res = {"signal":s.name}

    overWrite = True

    if not overWrite and res.DB.contains(key):
        res = resDB.getDicts(key)[0]
        logger.info("Found result for %s, reusing", s.name)

    else:
        
        combinedCard = c.combineCards( cards )
        res = c.calcLimit(combinedCard)

        if args.calcNuisances:
            c.calcNuisances(combinedCard)

            ###################
            # extract the SFs #
            ###################
            #if not args.useTxt 
            if True:
                # Would be a bit more complicated with the classical txt files, so only automatically extract the SF when using shape based datacards
                from StopsDilepton.tools.getPostFit import getPrePostFitFromMLF

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
                MB_postfit  = 0

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

                print
                print "## Scale Factors for backgrounds: ##"
                print "{:20}{:4.2f}{:3}{:4.2f}".format('top:',          (top_postfit/top_prefit).val, '+/-',  top_postfit.sigma/top_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('ttZ:',          (ttZ_postfit/ttZ_prefit).val, '+/-',  ttZ_postfit.sigma/ttZ_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('Drell-Yan:',    (DY_postfit/DY_prefit).val,   '+/-',  DY_postfit.sigma/DY_postfit.val)
                print "{:20}{:4.2f}{:3}{:4.2f}".format('multiBoson:',   (MB_postfit/MB_prefit).val,   '+/-',  MB_postfit.sigma/MB_postfit.val)

        if   args.signal == "TTbarDM":                      sConfig = s.mChi, s.mPhi, s.type
        elif args.signal == "T2tt":                         sConfig = s.mStop, s.mNeu
        elif args.signal == "T2bt":                         sConfig = s.mStop, s.mNeu
        elif args.signal == "T2bW":                         sConfig = s.mStop, s.mNeu
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05": sConfig = s.mStop, s.mNeu
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p09": sConfig = s.mStop, s.mNeu
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":  sConfig = s.mStop, s.mNeu
        elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95": sConfig = s.mStop, s.mNeu
        elif args.signal == "ttHinv":                       sConfig = ("ttHinv", "2l")



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

            print "Result: %r obs %5.3f exp %5.3f -1sigma %5.3f +1sigma %5.3f"%(sString, res['-1.000'], res['0.500'], res['0.160'], res['0.840'])
        #    return sConfig, res

        logger.info("Adding results to database")

    logger.info("Results stored in %s", limitDir)


if args.signal == "T2tt":
    data_directory              = '/afs/hephy.at/data/dspitzbart03/nanoTuples/'
    postProcessing_directory    = 'stops_2017_nano_v0p7/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt as jobs

allJobs = [j.name for j in jobs]

if args.only is not None:
    if args.only.isdigit():
        wrapper(jobs[int(args.only)])
    else:
        jobNames = [ x.name for x in jobs ]
        wrapper(jobs[jobNames.index(args.only)])
    exit(0)



