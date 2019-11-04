'''
Extraction of PDF and scale uncertainties in the SRs
'''

#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",     dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--selectWeight",         dest="selectWeight",       default=None,                action="store",      help="select weight?")
parser.add_option("--selectRegion",         dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option("--sample",               dest='sample',  action='store', default='TTZ',    choices=["TTZ", "DY", "multiBoson", "TTJets", "other"], help="which sample?")
parser.add_option("--year",                 dest='year',  action='store', default='2016',    choices=["2016", "2017", "2018"], help="which year?")
parser.add_option("--small",                action='store_true', help="small?")
parser.add_option("--reducedPDF",           action='store_true', help="Don't use all PDF variations for tests?")
parser.add_option("--combine",              action='store_true', help="Combine results?")
parser.add_option("--noKeepNorm",           action='store_true', help="Keep the normalization = acceptance uncertainty only?")
parser.add_option('--logLevel',             dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option('--overwrite',            dest="overwrite", default = False, action = "store_true", help="Overwrite existing output files, bool flag set to True  if used")
parser.add_option('--skipCentral',          dest="skipCentral", default = False, action = "store_true", help="Skip central weights")
parser.add_option('--regionsXSec',          dest="regionsXSec", default = False, action = "store_true", help="Use nJet and nBTag binning")
parser.add_option('--dpm',                  dest='dpm',         default=False,      action='store_true', help='Use dpm?')
(options, args) = parser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

# Standard imports
import ROOT
import os
import sys
import pickle
import math

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.SetupHelpers import channels, allChannels, trilepChannels
from StopsDilepton.analysis.estimators   import *
from StopsDilepton.analysis.regions      import regionsLegacy, noRegions
from StopsDilepton.tools.resultsDB       import resultsDB
from Analysis.Tools.u_float              import u_float

if options.dpm:
    data_directory = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

# dummy values for now
PDFset = 'NNPDF30'#options.PDFset
PDFType = "hessian"
PSweights = False

from StopsDilepton.analysis.Setup import Setup

year        = int(options.year)

#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed            import Top_pow_16, DY_HT_LO_16, TTZ_16, multiBoson_16,TTXNoZ_16
#from StopsDilepton.samples.nanoTuples_Fall17_postProcessed              import Top_pow_17, DY_HT_LO_17, TTZ_17, multiBoson_17, TTXNoZ_17
#from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed            import Top_pow_18, DY_HT_LO_18, TTZ_18, multiBoson_18, TTXNoZ_18

setup       = Setup(year=year)
setupIncl   = setup.sysClone(parameters={'mllMin':0, 'nJets':(0,-1), 'nBTags':(0,-1), 'zWindow':'allZ', 'metSigMin':0})

sample = setup.samples[options.sample]

allRegions = regionsLegacy
#if options.aggregate: allRegions = regionsAgg

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation


'''
PDF4LHC variations are hessian eigenvectors
NNPDF30 variations are usually mc replicas (unless otherwise stated)

## Summer16 ##
LHE scale variation weights (w_var / w_nominal); [0] is muR=0.50000E+00 muF=0.50000E+00 ; [1] is muR=0.50000E+00 muF=0.10000E+01 ; [2] is muR=0.50000E+00 muF=0.20000E+01 ; [3] is muR=0.10000E+01 muF=0.50000E+00 ; [4] is muR=0.10000E+01 muF=0.10000E+01 ; [5] is muR=0.10000E+01 muF=0.20000E+01 ; [6] is muR=0.20000E+01 muF=0.50000E+00 ; [7] is muR=0.20000E+01 muF=0.10000E+01 ; [8] is muR=0.20000E+01 muF=0.20000E+01
Therefore, use 0, 1,3,4 (central?), 5, 7, 8
Used PDF sets
TTLep_pow: 260000 (NNPDF30_nlo_as_0118)
TTZToLLNuNu: 292200 (NNPDF30_nlo_nf_5_pdfas)
LowMass TTZ: 262000 (NNPDF30_lo_as_0118) -> sample could go to ttX anyway (nunu not included)
SUSY: no weights stored. damn

## Fall17 ##
LHE scale variation weights (w_var / w_nominal); [0] is renscfact=0.5d0 facscfact=0.5d0 ; [1] is renscfact=0.5d0 facscfact=1d0 ; [2] is renscfact=0.5d0 facscfact=2d0 ; [3] is renscfact=1d0 facscfact=0.5d0 ; [4] is renscfact=1d0 facscfact=1d0 ; [5] is renscfact=1d0 facscfact=2d0 ; [6] is renscfact=2d0 facscfact=0.5d0 ; [7] is renscfact=2d0 facscfact=1d0 ; [8] is renscfact=2d0 facscfact=2d0
Therefore, use 0, 1,3,4 (central?), 5, 7, 8
Used PDF sets
TTLep_pow: 91400 (PDF4LHC15_nnlo_30_pdfas)
TTZToLLNuNu: 91400 (PDF4LHC15_nnlo_30_pdfas)
LowMass TTZ: 91400
SUSY: no weights stored atm.

Autumn18:
LHE scale variation weights (w_var / w_nominal); [0] is renscfact=0.5d0 facscfact=0.5d0 ; [1] is renscfact=0.5d0 facscfact=1d0 ; [2] is renscfact=0.5d0 facscfact=2d0 ; [3] is renscfact=1d0 facscfact=0.5d0 ; [4] is renscfact=1d0 facscfact=1d0 ; [5] is renscfact=1d0 facscfact=2d0 ; [6] is renscfact=2d0 facscfact=0.5d0 ; [7] is renscfact=2d0 facscfact=1d0 ; [8] is renscfact=2d0 facscfact=2d0 
Therefore, use 0, 1,3,4 (central?), 5, 7, 8
Used PDF sets
TTLep_pow: 91400 (PDF4LHC15_nnlo_30_pdfas)
TTZToLLNuNu: 91400 (PDF4LHC15_nnlo_30_pdfas)
LowMass TTZ: 91400
SUSY: no weights stored atm.
'''

scale_indices = [0,1,3,4,5,7,8]
LHEweight_original = 'abs(LHEScaleWeight[4])'
centralWeight = LHEweight_original

if year == 2016:
    if options.sample == 'TTLep_pow': #only use ttbar sample, no single-t
        PDF_indices = range(100) # no central weight stored
        aS_indices = []
    elif options.sample == 'TTZToLLNuNu':
        PDF_indices = range(100)
        aS_indices = [100,101]
    #elif options.sample.contains('T2tt'):
    #    raise NotImplementedError

if not options.selectWeight:
    scale_variations= [ "abs(LHEScaleWeight[%i])"%(i) for i in scale_indices ]
    PDF_variations  = []
    aS_variations   = []
    variations      = scale_variations + []

regions = allRegions if not options.selectRegion else  [allRegions[options.selectRegion]]

results = {}

scale_systematics = {}

cacheDir = "/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/PDF_v2_%s/"%(PDFset)

estimate = MCBasedEstimate(name=sample.name, sample=sample )
estimate.initCache(cacheDir)

## Results DB for scale and PDF uncertainties

PDF_cache = resultsDB(cacheDir+sample.name+'_unc.sq', "PDF", ["region", "channel", "PDFset"])
scale_cache = resultsDB(cacheDir+sample.name+'_unc.sq', "scale", ["region", "channel", "PDFset"])
PS_cache = resultsDB(cacheDir+sample.name+'_unc.sq', "PSscale", ["region", "channel", "PDFset"])

def wrapper(args):
        r, c, setup = args
        res = estimate.cachedEstimate(r, c, setup)
        logger.info("Done with one of the jobs in region %s and channel %s", r, c)
        return (estimate.uniqueKey(r, c, setup), res )

jobs=[]

if not options.skipCentral:
    # First run over seperate channels
    jobs.append((noRegions[0], 'all', setupIncl))
    jobs.append((noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[LHEweight_original]})))
    for var in variations:
        for c in ['EE', 'MuMu', 'EMu']:
            jobs.append((noRegions[0], c, setupIncl.sysClone(sys={'reweight':[var]})))


if not options.combine:
    for region in regions:
        for c in ['EE', 'MuMu', 'EMu']:
        #for region in regions:
            jobs.append((region, c, setup))
            jobs.append((region, c, setup.sysClone(sys={'reweight':[LHEweight_original]})))
            for var in variations:
                print var
                jobs.append((region, c, setup.sysClone(sys={'reweight':[var]})))
                #sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
    
    logger.info("Created %s jobs",len(jobs))

    if options.noMultiThreading: 
        results = map(wrapper, jobs)
    else:
        from multiprocessing import Pool
        pool = Pool(processes=1)
        results = pool.map(wrapper, jobs)
        pool.close()
        pool.join()
    
    logger.info("All done.")



PDF_unc     = []
Scale_unc   = []
PS_unc      = []

if options.combine:
    for c in ['SF','EMu']:#allChannels:
    
        for region in regions:
            logger.info("Region: %s", region)
            
            scales = []
            showerScales = []
            deltas = []
            delta_squared = 0
            # central yield inclusive and in region
            logger.info("Getting inclusive (noRegions) yield")
            sigma_incl_central  = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[LHEweight_original]}))
            logger.info("Getting yield for region with LHEweight_original")
            sigma_central       = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[LHEweight_original]}))
            logger.info("Getting yield for region with centralWeight")
            sigma_centralWeight = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[centralWeight]}))

            for var in scale_variations:
                print var
                logger.info("Getting inclusive yield with varied weight")
                simga_incl_reweight = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
                norm = sigma_incl_central/simga_incl_reweight if not options.noKeepNorm else 1
                
                logger.info("Getting yield for region with varied weight")
                sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
                sigma_reweight_acc = sigma_reweight * norm
                
                #logger.info("Using norm of %s", norm)
                unc = abs( ( sigma_reweight_acc - sigma_central) / sigma_central ) if sigma_central > 0 else u_float(1)
                scales.append(unc.val)
            
            scale_rel = max(scales)

            for var in PDF_variations:
                # calculate x-sec noramlization
                simga_incl_reweight = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
                norm = sigma_incl_central/simga_incl_reweight if not options.noKeepNorm else 1

                sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
                sigma_reweight_acc = sigma_reweight * norm

                ## For replicas, just get a list of all sigmas, sort it and then get the 68% interval
                deltas.append(sigma_reweight_acc.val)
                ## recommendation for hessian is to have delta_sigma = sum_k=1_N( (sigma_k - sigma_0)**2 )
                ## so I keep the norm for both sigma_k and sigma_0 to obtain the acceptance uncertainty. Correct?
                delta_squared += ( sigma_reweight.val - sigma_centralWeight.val )**2
            
            deltas = sorted(deltas)

            # calculate uncertainty
            if PDFType == "replicas":
                # get the 68% interval
                upper = len(deltas)*84/100-1
                lower = len(deltas)*16/100 - 1
                delta_sigma = (deltas[upper]-deltas[lower])/2
            elif PDFType == "hessian":
                delta_sigma = math.sqrt(delta_squared)

            # recommendation is to multiply uncertainty by 1.5
            deltas_as = []
            for var in aS_variations:
                simga_incl_reweight = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[var]}))
                norm = sigma_incl_central/simga_incl_reweight if not options.noKeepNorm else 1
                
                sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
                sigma_reweight_acc = sigma_reweight * norm

                deltas_as.append(sigma_reweight_acc.val)

            if len(deltas_as)>0:
                scale = 1.5 if PDFset.count("NNPDF") else 1.0
                delta_sigma_alphaS = scale * ( deltas_as[0] - deltas_as[1] ) / 2.

                # add alpha_s and PDF in quadrature
                delta_sigma_total = math.sqrt( delta_sigma_alphaS**2 + delta_sigma**2 )

                # make it relative wrt central value in region
                delta_sigma_rel = delta_sigma_total/sigma_central.val

            # calculate the PS uncertainties
            if PSweights:
                sigma_incl_central  = estimate.cachedEstimate(noRegions[0], 'all', setupIncl.sysClone(sys={'reweight':[PSweight_original]}))
                sigma_central       = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[PSweight_original]}))
                print "Count:", sigma_central.val/0.5148500
                shower_scales  = []
                for var in PS_variations:
                    simga_incl_reweight = estimate.cachedEstimate(noRegions[0], channel(-1,-1), setupIncl.sysClone(sys={'reweight':[var]}))
                    norm = sigma_incl_central/simga_incl_reweight
                    
                    sigma_reweight  = estimate.cachedEstimate(region, c, setup.sysClone(sys={'reweight':[var]}))
                    sigma_reweight_acc = sigma_reweight #* norm

                    #unc = ( ( sigma_reweight_acc - sigma_central) / sigma_central ) # no abs atm
                    unc = sigma_reweight_acc / sigma_central
                    #print ( sigma_reweight_acc - sigma_central) / sigma_central
                    showerScales.append(unc.val)

                print "ISR up/down", round(showerScales[0], 3), round( showerScales[2], 3)
                print "FSR up/down", round(showerScales[1], 3), round( showerScales[3], 3)

                PS_scale_rel = max(showerScales)
            else:
                PS_scale_rel = 0.


            logger.info("Calculated PDF and alpha_s uncertainties for region %s in channel %s"%(region, c))
            logger.info("Central x-sec: %s", sigma_central)
            #logger.info("Delta x-sec using PDF variations: %s", delta_sigma)
            #logger.info("Delta x-sec using alpha_S variations: %s", delta_sigma_alphaS)
            #logger.info("Delta x-sec total: %s", delta_sigma_total)
            #logger.info("Relative uncertainty: %s", delta_sigma_rel)
            logger.info("Relative scale uncertainty: %s", scale_rel)
            #logger.info("Relative shower scale uncertainty: %s", PS_scale_rel)
            
            #PDF_unc.append(delta_sigma_rel)
            if scale_rel < 1: Scale_unc.append(scale_rel) # only append here if we have enough stats
            #PS_unc.append(PS_scale_rel)
            
            # Store results
            #if not options.reducedPDF:
            #    PDF_cache.add({"region":region, "channel":c, "PDFset":PDFset}, delta_sigma_rel, overwrite=True)
            scale_cache.add({"region":region, "channel":c, "PDFset":'scale'}, scale_rel, overwrite=True)
            #PS_cache.add({"region":region, "channel":c, "PDFset":'PSscale'}, PS_scale_rel, overwrite=True)

            #if not options.reducedPDF:
            #    PDF_cache.get({"region":region, "channel":c, "PDFset":PDFset})
            scale_cache.get({"region":region, "channel":c, "PDFset":'scale'})
            #PS_cache.get({"region":region, "channel":c, "PDFset":'PSscale'})

    #logger.info('Min. PDF uncertainty: %.3f', min(PDF_unc))
    #logger.info('Max. PDF uncertainty: %.3f', max(PDF_unc))
    
    logger.info('Min. scale uncertainty: %.3f', min(Scale_unc))
    logger.info('Max. scale uncertainty: %.3f', max(Scale_unc))
    
    #logger.info('Min. PS scale uncertainty: %.3f', min(PS_unc))
    #logger.info('Max. PS scale uncertainty: %.3f', max(PS_unc))




