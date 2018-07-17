''' Class to train a sequential model with Keras
'''

#Standard imports
import os
import time
import ROOT

# StopsDilepton
from StopsDilepton.tools.user import     MVA_preprocessing_directory, MVA_model_directory, plot_directory

# Keras, Pandas, numpy etc.
import numpy as np
import pandas as pd
from   sklearn.model_selection import train_test_split
from   keras.models import Sequential
from   keras.layers import Dense
from   keras import optimizers

def makeTGraph( x, y ):
    if len(x)!=len(y):
        raise RuntimeError( "Need same length! Got %i and %i"%(len(x), len(y) ) )
    return ROOT.TGraph(len(x), array.array('d', x), array.array('d', y))

def saveTGraph( x, y, pathstring= '/afs/hephy.at/user/g/gungersback/www/etc', filename='test.png'):
    if len(x)!=len(y):
        raise RuntimeError( "Need same length! Got %i and %i"%(len(x), len(y) ) )
    g = makeTGraph( x, y )
    c1 = ROOT.TCanvas()
    g.Draw("AC*")
    c1.Print(pathstring + '/' +  filename)
    return g

# Logging
import logging
logger = logging.getLogger(__name__)

class KerasTrainer:

    def __init__( self, input_data_directory, training_variables):
        # location of training data
        self.input_data_directory = input_data_directory
        # training variables
        self.training_variables = training_variables
        # percentage ov events used for training
        self.train_fraction = 0.75

    def init_training_data( self ):
        ''' Initialize training data
        '''
        # read .h5 files to create feature Matrix X and target vector y
        self.X = pd.read_hdf( os.path.join( MVA_preprocessing_directory, self.input_data_directory,  'data_X.h5'), 'df')
        self.y = pd.read_hdf( os.path.join( MVA_preprocessing_directory, self.input_data_directory,  'data_y.h5'), 'df')

        # create new Variables from Data
        self.X['Jet_dphi'] = abs(self.X['Jet1_phi'] - self.X['Jet2_phi'])
        self.X['lep_dphi'] = abs(self.X['l1_phi'] - self.X['l2_phi'])

        #['Jet1_btagCSV', 'Jet1_eta', 'Jet1_phi', 'Jet1_pt',
        # 'Jet2_btagCSV', 'Jet2_eta', 'Jet2_phi', 'Jet2_pt',
        # 'Jet3_btagCSV', 'Jet3_eta', 'Jet3_phi', 'Jet3_pt',
        # 'Jet4_btagCSV', 'Jet4_eta', 'Jet4_phi', 'Jet4_pt',
        # 'dl_eta', 'dl_mass', 'dl_mt2bb', 'dl_mt2blbl', 'dl_mt2ll',
        # 'ht',
        # 'l1_eta', 'l1_phi', 'l2_eta', 'l2_phi',
        # 'metSig', 'met_phi', 'met_pt',
        # 'nBTag',
        # 'nJetGood',
        # 'weight',
        # 'Jet_dphi'
        # 'lep_dphi']

        #Add MT2ll??
        self.training_variables+=['dl_mt2ll']
        #????
        self.X = self.X[self.training_variables]

        logger.info( 'Number of variables for training %i', len(self.training_variables) )
        logger.info( 'Number of signal / backround events: %i / %i', (self.y==1).sum(), (self.y==0).sum())
        logger.info( 'Number of events and percentage of signal events in sample: %s // %5.2f\%',  self.y.shape[0], round( 100.* (self.y==1).sum() / self.y.shape[0] ,2 ))

        # Normalize Data ( Using Standardscaler we would loose columns naming)
        X_mean, X_std = self.X.mean(), self.X.std()

        self.X -= X_mean
        self.X /= X_std

        # Inverse transform
        # X *= X_std
        # X += X_mean

        # Splitting in training and test samples
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, train_size= int( self.train_fraction*self.y.shape[0] ), random_state=42)

        self.X_mt2ll = self.X_test['dl_mt2ll']
        self.X_test  = self.X_test.drop(['dl_mt2ll'], axis=1)
        self.X_train = self.X_train.drop(['dl_mt2ll'], axis=1)

        # Inverse Transf of mt2ll
        self.X_mt2ll *= X_std.dl_mt2ll
        self.X_mt2ll += X_mean.dl_mt2ll
        self.X_mean   = X_mean.drop(['dl_mt2ll'])
        self.X_std    = X_std.drop(['dl_mt2ll'])
    
    def train( self, NHLayer = 2, units = 100, epochs = 100, batch_size = 5120, validation_split = 0.2):
        '''
        initializes a Keras binary classifier and trains it on X_train and y_train
        The trained classifier and the training visualisation (Lossfunction and Accuracy over time) are saved in a subfolder specified by the date of plotpath. 
        The classifier is saved as .h5 file.
        NHLayer ... 
        units   ...
        ...
        '''

        self.timestamp = time.strftime("%Y-%m-%d-%H%M")

        self.plot_directory = os.path.join( plot_directory, 'KerasTrainer', input_data_directory, self.timestamp) 

        if not os.path.exists( self.plot_directory ):
            os.makedirs( self.plot_directory )

        #Initialize and build classifier
        self.model = Sequential()
        self.model.add( Dense(units= units, activation='relu',  input_dim=self.X_train.shape[1]) ) 
        for i in range(NHLayer):
            self.model.add( Dense(units= units, activation='relu' ) )
        self.model.add( Dense(units=1, activation='sigmoid') ) 

        # configuration
        #model.compile( loss='binary_crossentropy',  optimizer=optimizers.RMSprop(lr=0.001) ,  metrics=['accuracy'])
        self.model.compile( loss='binary_crossentropy', optimizer='rmsprop', metrics=['acc'])

        # training
        self.history = self.model.fit(self.X_train.values, self.y_train.values, epochs=epochs, batch_size=batch_size, validation_split=validation_split)

        output_directory = os.path.join( MVA_model_directory, input_data_directory, self.timestamp)
        if not os.path.exists( output_directory + 'model' ):
            os.makedirs( output_directory + 'model' )
        model.save(output_directory + 'model/' + 'keras.h5')

        # for overtraining check
        self.history_dict = self.history.history
        self.loss_values  = self.history_dict['loss']

if __name__ == '__main__':

    input_data_directory = 'v1_small/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/'
    from StopsDilepton.MVA.default_classifier import training_variables

    kerasTrainer = KerasTrainer( input_data_directory, training_variables )
    kerasTrainer.init_training_data()
    kerasTrainer.train( batch_size = 512 )
