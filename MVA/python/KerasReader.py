''' Class to read a sequential model and classify events
'''

#Standard imports
import os
import time
import ROOT

# StopsDilepton
from StopsDilepton.tools.user    import MVA_preprocessing_directory, MVA_model_directory, plot_directory
from StopsDilepton.tools.helpers import deltaPhi

# Keras, Pandas, numpy etc.
import numpy as np
import pandas as pd
from keras.models import load_model

# Logging
import logging
logger = logging.getLogger(__name__)

class KerasReader:

    def __init__( self, keras_model_directory, keras_model_timestamp,training_variables):
        # location of keras model
        self.keras_model_directory = keras_model_directory
        self.keras_model_timestamp = keras_model_timestamp 
        # training variables
        self.training_variables = training_variables

        # load model
        self.model = load_model( os.path.join( MVA_model_directory, self.keras_model_directory, self.keras_model_timestamp, 'keras.h5'))
        # load transformation data 
        self.X_mean =  pd.read_hdf( os.path.join( MVA_model_directory, self.keras_model_directory, self.keras_model_timestamp, 'X_mean.h5'), 'df')
        self.X_std =  pd.read_hdf( os.path.join( MVA_model_directory, self.keras_model_directory, self.keras_model_timestamp, 'X_std.h5'), 'df')

    def eval( self, dict ):
        ''' Transforms Dataset for Keras use and lets model predict outcome 
        '''
        dict_cp = dict.copy()
        # Transformation  
        for variable in self.training_variables:
            dict_cp[variable] -= getattr( self.X_mean, variable )         
            dict_cp[variable] /= getattr( self.X_std, variable )         
        
        # Predict
        return self.model.predict( np.array( [ [dict_cp[k] for k in self.training_variables] ] ) )[0][0]
       
if __name__ == '__main__':
    import StopsDilepton.tools.logger as logger
    logger  = logger.get_logger('INFO', logFile = None)

    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger('INFO', logFile = None )


    keras_model_directory = 'SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow/v1_small/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/'
    from StopsDilepton.MVA.default_classifier import training_variables

    kerasReader = KerasReader( keras_model_directory, '2018-07-20-1538' ,training_variables)

    # testevent created via X_test.iloc[0].to_dict() 
    eventdict= {'Jet1_eta': 0.061895567923784256,
                'Jet1_pt': 235.32232666015625,
                'Jet2_eta': -1.4361321926116943,
                'Jet2_pt': 195.91734313964844,
                'Jet_dphi': 0.35395264625549316,
                'dl_eta': -1.7454613447189331,
                'dl_mass': 500.18313598632812,
                'ht': 597.5518798828125,
                'l1_eta': -1.8279483318328857,
                'l2_eta': 0.54515653848648071,
                'lep_dphi': 1.7098859548568726,
                'metSig': 14.18631649017334,
                'met_phi': 1.5897738933563232,
                'met_pt': 346.78271484375}

    print 'Keras prediction on example event'
    print eventdict
    print 'Keras Prediction: ' + str( kerasReader.eval(eventdict) )




