'''
/afs/hephy.at/work/p/phussain/StopsDileptonLegacy/results/v3//COMBINED/controlAll//cardFiles/T2tt/observed/
Get a signal region plot from the cardfiles
'''

#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--signal",               dest='signal',  action='store', default='T2tt',    choices=["T2tt", "T2bW", "ttHinv"], help="which signal?")
parser.add_option("--only",                 dest='only',  action='store', default='T2tt_800_100', help="which masspoints??")
parser.add_option("--small",                action='store_true', help="small?")
parser.add_option('--logLevel',             dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option('--blinded',              action="store_true")
parser.add_option('--overwrite',            dest="overwrite", default = False, action = "store_true", help="Overwrite existing output files, bool flag set to True  if used")
parser.add_option('--expected',             action = "store_true", help="Run expected?")
parser.add_option('--preliminary',          action = "store_true", help="Run expected?")
parser.add_option('--testGrayscale',        action = "store_true", help="Do the most important test for this collaboration?")
parser.add_option('--signalOnly',           action = "store_true", help="Show only signals?")
parser.add_option("--year",                 action='store',      default=0, type="int", help='Which year?')
parser.add_option("--postFix",              action='store',      default="", help='Add sth?')
(options, args) = parser.parse_args()

# Standard imports
import ROOT
import os
import sys
import pickle
import math

# Analysis
from StopsDilepton.tools.u_float           import u_float
from StopsDilepton.tools.user              import plot_directory, analysis_results
from StopsDilepton.samples.color           import color
from StopsDilepton.tools.getPostFit        import *
from StopsDilepton.analysis.regions        import *
from StopsDilepton.tools.cardFileWriter import cardFileWriter

from RootTools.core.standard import *
# logger
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   options.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None)

#lumiStr = setup.dataLumi/1000
years=[2016,2017,2018]

## ttH example: /afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v7/2018/fitAll/cardFiles/ttHinv/observed/ttH_HToInvisible_M125_shapeCard.txt
cardName = "%s"%(options.only) if not options.signal == 'ttHinv' else "ttH_HToInvisible_M125"

cardDir = analysis_results+"/COMBINED/fitAll/cardFiles/%s/%s/"%(options.signal,'expected' if options.expected else 'observed')

cardFile = "%s/%s.txt"%(cardDir, cardName)


logger.info("Plotting from cardfile %s"%cardFile)


preFitHist={}
postFitHist={}
bhistos=[]
hists={}
histos={}
bkgHist=[]
processes = [   ('TTJets', 't#bar{t}/t'),
            ('DY', 'Drell-Yan'),
            ('multiBoson', 'VV/VVV'),
            ('TTZ', 't#bar{t}Z'),
            ('TTXNoZ', 't#bar{t}X, rare')]

# tex, name, list of nuisances, combine nuisances?

systematics = [ 
    ("Jet energy scale",                        "JEC",      ["JEC_2016", "JEC_2017", "JEC_2018"],               False), 
    ("Integrated luminosity",                   "Lumi",     ["Lumi_2016", "Lumi_2017", "Lumi_2018"],            True),
    ("Pileup modeling",                         "PU",       ["PU_2016", "PU_2017", "PU_2018"],                  False),
    ("Jet energy resolution",                   "JER",      ["JER_2018", "JER_2017",  "JER_2016"],              True),
    ("Modeling of unclust. en.",                "unclEn",   ["unclEn_2016", "unclEn_2017", "unclEn_2018"],      True), 
    ("Trigger efficiency",                      "trigger",  ["trigger_2018", "trigger_2016", "trigger_2017"],   True),
    ("b tagging light flavor",                  "SFl",      ["SFl_2018", "SFl_2017", "SFl_2016"],               False),
    ("b tagging heavy flavor",                  "SFb",      ["SFb_2017", "SFb_2016", "SFb_2018"],               False),
    ("Lepton scale factors",                    "leptonSF", ["leptonSF"],                                       False),
    ("L1 prefire correction",                   "L1prefire", ["L1prefire"],                                     False),
    ("0 missing hit scale factor",              "leptonHit0SF", ["leptonHit0SF"],                               False),
    ("Impact parameter scale factor",           "leptonSIP3DSF", ["leptonSIP3DSF"],                             False),
    ("PDF choice",                              "PDF",      ["PDF"],                                            False),
    ("$p_{T}(\\textrm{top})$",                  "topPt",    ["topPt"],                                          False),
    ("t#bar{t} cross section",                  "topXSec",  ["topXSec"],                                        False),
    ("t#bar{t}Z background",                    "ttZ_SR",   ["ttZ_SR"],                                         False),
    ("fake/non-prompt leptons",                 "topFakes", ["topFakes"],                                       False),
    ("Drell-Yan background",                    "DY_SR",    ["DY_SR"],                                          False),
    ("non-gaussian jet mismeasurements",        "topNonGauss", ["topNonGauss"],                                 False),
    ("multiboson background",                   "MB_SR",    ["MB_SR"],                                          False),
    ("$\mu_{R}$ and $\mu_{F}$ choice $(t\bar{t})$", "scaleTT", ["scaleTT"],                                     False),
    ("rare background",                         "rare",     ["rare"],                                           False),
    ("$\mu_{R}$ and $\mu_{F}$ choice $(t\bar{t}Z)$", "scaleTTZ", ["scaleTTZ"],                                  False),
    ("Drell-Yan tail",                          "DY_hMT2ll", ["DY_hMT2ll"],                                     False), 
]

#from infoFromCards import *
#getPUFC = getPreFitUncFromCard

from makeDataFrameFromCard import getDict

result = getDict(cardFile)

if options.year >0 : years = [options.year]

bins    = range(46)
years   = [2016,2017,2018]

c = cardFileWriter.cardFileWriter()
c.releaseLocation = os.path.abspath('.')
cardFileName = cardFile.replace('.txt', '_combination.txt') # name of the new card file
c.reset()
c.setPrecision(3)

# nuisances
for sys_tex, sys_name, sys_corr, merge in systematics:
    if merge or len(sys_corr)==1:
        c.addUncertainty(sys_name,    'lnN')
    else:
        for sys_c in sys_corr:
            c.addUncertainty(sys_c,    'lnN')

if options.signal == "ttHinv":
    c.addUncertainty('xsec_QCD',    'lnN')
    c.addUncertainty('xsec_PDF',    'lnN')
else:
    c.addUncertainty('leptonFS',    'lnN')
    c.addUncertainty('btagFS',      'lnN')
    c.addUncertainty('isr',         'lnN')
    c.addUncertainty('FSmet',       'lnN')

# rate parameters
c.addRateParameter('DY',            1, '[0,10]')
c.addRateParameter('TTZ',           1, '[0,10]')
c.addRateParameter('TTJets',        1, '[0,10]')
c.addRateParameter('multiBoson',    1, '[0.6,1.4]')

print cardFile

for b in bins:
    binname = "Bin%s"%b
    print
    print binname
    #obs     = sum( [ getObservationFromCard(cardFile, "dc_%s_Bin%s"%(year, b)) for year in years ])
    obs     = sum( [ result["dc_%s_Bin%s"%(year, b)]["obs"]["yield"] for year in years ])
    #signal   = sum( [ getEstimateFromCard(cardFile, "signal", "dc_%s_Bin%s"%(year,b)) for year in years ])
    signal   = sum( [ result["dc_%s_Bin%s"%(year,b)]["signal"]["yield"] for year in years ])
    c.addBin(binname, [ p for p,t in processes ], binname)
    for proc, tex in processes + [('signal','')]:
        est = sum( [ result["dc_%s_Bin%s"%(year,b)][proc]["yield"] for year in years ])
        ests = { year: result["dc_%s_Bin%s"%(year,b)][proc]["yield"] for year in years }
        c.specifyExpectation(binname, proc, est )
        for sys_tex, sys_name, sys_corr, merge in systematics:
            if len(sys_corr) == 1:
                sigma = sum( [ result["dc_%s_%s"%(year, binname)][proc][sys_corr[0]]*ests[year] for year in years ])
                if est > 0 and sigma > 0:
                    c.specifyUncertainty(sys_name,    binname, proc, 1 + sigma/est)
            else:
                if merge:
                    listOfSigmas = [ (result["dc_%s_%s"%(year, binname)][proc][sorted(sys_corr)[i]]*ests[year])**2 for i,year in enumerate(years) ]
                    sigma = math.sqrt(sum( listOfSigmas ))
                    if est > 0 and sigma > 0:
                        c.specifyUncertainty(sys_name,    binname, proc, 1 + sigma/est)
                else:
                    for i, year in enumerate(years):
                        sigma = result["dc_%s_%s"%(year, binname)][proc][sorted(sys_corr)[i]]*ests[year]
                        if est > 0 and sigma > 0:
                            c.specifyUncertainty(sorted(sys_corr)[i],    binname, proc, 1 + sigma/est)
                    

        # stat uncertainty
        listOfSigmas = [ (result["dc_%s_%s"%(year,binname)][proc]["stat"]*ests[year])**2 for i,year in enumerate(years) ]
        sigma = math.sqrt(sum( listOfSigmas ))
        uname = 'Stat_'+binname+'_'+proc
        c.addUncertainty(uname, 'lnN')
        if est>0:
            c.specifyUncertainty(uname,    binname, proc, 1+sigma/est)

    ## OBSERVATION
    c.specifyObservation(binname, int(obs))

    ### SIGNAL
    if options.signal == "ttHinv":
        # x-sec uncertainties for ttH: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBSMAt13TeV#ttH_Process
        c.specifyUncertainty('xsec_QCD',      binname, 'signal', 1.092)
        c.specifyUncertainty('xsec_PDF',      binname, 'signal', 1.036)
    elif options.signal == "T2tt":
        if est>0:
            c.specifyUncertainty('leptonFS', binname, 'signal', 1 +  sum( [ (result["dc_%s_%s"%(year,binname)][proc]["leptonFS"]*ests[year]) for year in years ])/est )
            c.specifyUncertainty('btagFS',   binname, 'signal', 1 +  sum( [ (result["dc_%s_%s"%(year,binname)][proc]["btagFS"]*ests[year]) for year in years ])/est )
            c.specifyUncertainty('isr',      binname, 'signal', 1 +  sum( [ (result["dc_%s_%s"%(year,binname)][proc]["isr"]*ests[year]) for year in years ])/est )
            c.specifyUncertainty('FSmet',    binname, 'signal', 1 +  sum( [ (result["dc_%s_%s"%(year,binname)][proc]["FSmet"]*ests[year]) for year in years ])/est )

c.writeToFile(cardFileName)

print cardFileName

