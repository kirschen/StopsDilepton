
''' All samples for MVA training'''

# Standard imports
from RootTools.core.standard import *

#
# Stopsdilepton samples 
#
postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *

SMS_T8bbllnunu_XCha0p5_XSlep0p09 = Sample.fromDirectory( "SMS_T8bbllnunu_XCha0p5_XSlep0p09", directory = ["/afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v37/dilepTiny/SMS_T8bbllnunu_XCha0p5_XSlep0p09"] )
