''' PU reweighting function
'''

# helpers
from StopsDilepton.tools.helpers import getObjFromFile

# Logging
import logging
logger = logging.getLogger(__name__)

#Define a functor that returns a reweighting-function according to the era
def getReweightingFunction(data="PU_2100_XSecCentral", mc="Spring15"):

    # Data
    fileNameData = "$CMSSW_BASE/src/StopsDilepton/tools/data/puReweightingData/%s.root" % data

    histoData = getObjFromFile(fileNameData, 'pileup')
    histoData.Scale(1./histoData.Integral())
    logger.info("Loaded 'pileup' from data file %s", fileNameData )

    # MC
    if mc=='Spring15':
        from StopsDilepton.tools.spring15MCPUProfile import spring15 as mcProfile
        logger.info("Loaded Spring15 MC Profile" )
    else:
        raise ValueError( "Don't know about MC PU profile %s" %mc )

    mcProfile.Scale(1./mcProfile.Integral())

    # Create reweighting histo
    reweightingHisto = histoData.Clone( '_'.join(['reweightingHisto', data, mc]) )
    reweightingHisto.Divide(mcProfile)

    # Define reweightingFunc
    def reweightingFunc(nvtx):
        return reweightingHisto.GetBinContent(reweightingHisto.FindBin(nvtx))

    return reweightingFunc
