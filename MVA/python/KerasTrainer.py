''' Class to train a sequential model with Keras
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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, auc
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

class SampleAttr:
    def __init__(self, name, tag, color):
        self.name = name
        self.tag = tag
        self.color = color

# Logging
import logging
logger = logging.getLogger(__name__)

class KerasTrainer:

    def __init__( self, input_data_directory, training_variables, spectator_variables = None):
        # location of training data
        self.input_data_directory = input_data_directory
        # training variables
        self.training_variables = training_variables
        # spectator variables
        self.spectator_variables = spectator_variables
        # fraction of events used for training
        self.train_fraction = 0.75

    def init_training_data( self ):
        ''' Initialize training data
        '''
        # read .h5 files to create feature Matrix X and target vector y
        X_tmp = pd.read_hdf( os.path.join( MVA_preprocessing_directory, self.input_data_directory,  'data_X.h5'), 'df')
        y_tmp = pd.read_hdf( os.path.join( MVA_preprocessing_directory, self.input_data_directory,  'data_y.h5'), 'df')

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

        logger.info( 'Number of training / spectator variables %i / %i', len(self.training_variables), len(self.spectator_variables) )
        logger.info( 'Number of signal / backround events: %i / %i', (y_tmp==1).sum(), (y_tmp==0).sum())
        logger.info( 'Number of events and percentage of signal events in sample: %s // %5.2f',  y_tmp.shape[0], round( 100.* (y_tmp==1).sum() / y_tmp.shape[0] ,2 ))

        # Normalize Data - mean to 0, and std to 1 
        self.X_mean, self.X_std = X_tmp.mean(), X_tmp.std()

        X_tmp -= self.X_mean
        X_tmp /= self.X_std

        # Splitting in training and test samples
        X_tmp_train, X_tmp_test, self.y_train, self.y_test = train_test_split(X_tmp, y_tmp, train_size= int( self.train_fraction*y_tmp.shape[0] ), random_state=42 )

        # Separating Training and Spectator variables
        self.X_train = X_tmp_train[ self.training_variables ] 
        self.X_test  = X_tmp_test[ self.training_variables ]
        self.X_spect = X_tmp_test[ self.spectator_variables ]

        # Inverse Transf of spectator variables
        self.X_spect *= self.X_std
        self.X_spect += self.X_mean
        self.X_mean   = self.X_mean.drop( self.spectator_variables )
        self.X_std    = self.X_std.drop( self.spectator_variables )
    
    def train( self, NHLayer = 2, units = 100, epochs = 100, batch_size = 5120, validation_split = 0.2):
        '''
        initializes a Keras binary classifier and trains it on X_train and y_train
        The trained classifier and the training visualisation (Lossfunction and Accuracy over time) are saved in a subfolder specified by the date of plotpath. 
        The classifier is saved as .h5 file.
        NHLayer ... 
        units   ...
        ...
        '''
        self.validation_split = validation_split
        self.batch_size = batch_size
        self.timestamp = time.strftime("%Y-%m-%d-%H%M")

        #Initialize and build classifier
        self.model = Sequential()
        self.model.add( Dense(units= units, activation='relu', input_dim=self.X_train.shape[1]) ) 
        for i in range(NHLayer):
            self.model.add( Dense(units= units, activation='relu' ) )
        self.model.add( Dense(units=1, activation='sigmoid') ) 

        # configuration
        self.model.compile( loss='binary_crossentropy', optimizer='rmsprop', metrics=['acc'])
        #self.model.compile( loss='binary_crossentropy',  optimizer=optimizers.RMSprop(lr=0.001) ,  metrics=['accuracy'])

        # training
        self.history = self.model.fit(self.X_train.values, self.y_train.values, epochs=epochs, batch_size=batch_size, validation_split=validation_split)

        # output directory (simplify?)
        output_directory = os.path.join( MVA_model_directory, self.input_data_directory, self.timestamp) 
        if not os.path.exists( output_directory ):
            os.makedirs( output_directory )
        self.model.save( os.path.join( output_directory, 'keras.h5'))

        # also save means and std of samples
        self.X_mean.to_hdf( os.path.join( output_directory, 'X_mean.h5') , key='df', mode='w')
        self.X_std.to_hdf( os.path.join( output_directory, 'X_std.h5') , key='df', mode='w')

    def validation( self ):
        self.plot_directory = os.path.join( plot_directory, 'KerasTrainer', self.input_data_directory, self.timestamp) 

        if not os.path.exists( self.plot_directory ):
            os.makedirs( self.plot_directory )
        
        # UNITS? - Implementation s.t. it works for arbitrary variables

        #
        # loss and accuracy 
        #

        self.history_dict = self.history.history

        self.loss_values  = self.history_dict['loss']
        self.acc_values = self.history_dict['acc']
        epochslist = range(1,  len(self.loss_values)+1)
        
        plt.plot(epochslist, self.loss_values, 'bo', label='Training loss')
        if self.history_dict.has_key('val_loss'):
            self.val_loss_values = self.history_dict['val_loss']
            plt.plot(epochslist, self.val_loss_values, 'b', label='Validation loss')
        plt.title('Training and validation loss (Valid. split = ' + str( self.validation_split ) + ')')
        plt.xlabel('Epochs  ( batch_size = ' + str( self.batch_size ) + ')')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig( os.path.join( self.plot_directory , 'loss.png'))
        plt.clf()

        plt.plot(epochslist, self.acc_values, 'bo', label='Training acc')
        if self.history_dict.has_key('val_acc'):
            self.val_acc_values = self.history_dict['val_acc']
            plt.plot(epochslist, self.val_acc_values, 'b', label='Validation acc')
        plt.title('Training and validation acc (Valid. split = ' + str( self.validation_split ) + ')')
        plt.xlabel('Epochs ( batch_size = ' + str( self.batch_size ) + ')')
        plt.ylabel('Acc')
        plt.legend()
        plt.savefig( os.path.join( self.plot_directory , 'acc.png'))
        plt.clf()

        #
        # ROC    
        #

        self.y_test_pred = pd.DataFrame( self.model.predict( self.X_test.values  ) , index = self.X_test.index)
        fpr_test, tpr_test, thresholds_test = roc_curve( self.y_test.values, self.y_test_pred.values )
        auc_val_test = auc(fpr_test, tpr_test)

        plt.plot( tpr_test, 1-fpr_test, 'b', label= 'Neural net, Auc=' + str(round(auc_val_test,4) ))
        plt.title('ROC')
        plt.xlabel('$\epsilon_{Sig}$', fontsize = 20) # 'False positive rate'
        plt.ylabel('$1-\epsilon_{Back}$', fontsize = 20) #  '1-True positive rate' 
        plt.legend(loc ='lower left')
        plt.savefig( os.path.join( self.plot_directory , 'roc.png') )
        plt.clf()

        signalAttr = SampleAttr('signal', 1,'kRed')
        backgroundAttr = SampleAttr('background', 0,'kBlue')

        #
        # histogramms input variables
        #
        
        # Transformation of Variables
        X_tmp = self.X_test * self.X_std
        X_tmp += self.X_mean

        X_tmp = pd.concat([ X_tmp, self.X_spect ], axis=1)
        ivar_can = []
        for variable in (self.training_variables + self.spectator_variables):
           xbin = 20
           xmin = getattr( X_tmp, variable).min() 
           xmax = getattr( X_tmp, variable).max() 
           ivar_can.append( ROOT.TCanvas())
           #leg1 = ROOT.TLegend(.73,.32,.97,.53)
           histos = []
           for attr in [ signalAttr , backgroundAttr ]: 
               histos.append( ROOT.TH1F( attr.name , attr.name ,xbin,xmin,xmax) ) 
               histos[-1].SetLineColor( getattr(ROOT, attr.color) )
               histos[-1].SetLineStyle(3)
               histos[-1].SetLineWidth(2)
               histos[-1].SetTitle('Distribution Input Variables')
               histos[-1].GetXaxis().SetTitle(variable)
               histos[-1].GetYaxis().SetTitle('events')
               for i in range( len( getattr( X_tmp, variable)[ self.y_test == attr.tag ].values )):
                   histos[-1].Fill( getattr( X_tmp, variable)[ self.y_test == attr.tag ].values[i] )
               #leg1.AddEntry(histos[-1], attr.name,"L")
               histos[-1].Draw('same')
           #leg.SetBorderSize(0) # no border
           #leg.SetFillColor(0)
           #leg.SetFillStyle(0)
           #leg.SetTextFont(42)
           #leg.SetTextSize(0.035)
           #leg1.Draw()
           ivar_can[-1].SetLogy()
           ivar_can[-1].Print( os.path.join( self.plot_directory, variable + '.png') )
           #histo.Scale(1000.) # norm must be set to total number of elements to get integral hist = 1
        
        #
        # output classifier
        #        

        xbin = 20
        xmin = 0 
        xmax = 1
        c1 = ROOT.TCanvas()
        leg1 = ROOT.TLegend(.73,.32,.97,.53)
        histos = []
        for attr in [ signalAttr , backgroundAttr ]: 
            histos.append( ROOT.TH1F( attr.name , attr.name ,xbin,xmin,xmax) ) 
            histos[-1].SetLineColor( getattr(ROOT, attr.color) )
            histos[-1].SetLineStyle(3)
            histos[-1].SetLineWidth(2)
            for i in range( len( self.y_test_pred[ self.y_test == attr.tag ].values )):
                histos[-1].Fill( self.y_test_pred[ self.y_test == attr.tag ].values[i] )
            leg1.AddEntry(histos[-1], attr.name,"L")
            histos[-1].Draw('same')
        #leg.SetBorderSize(0) # no border
        #leg.SetFillColor(0)
        #leg.SetFillStyle(0)
        #leg.SetTextFont(42)
        #leg.SetTextSize(0.035)
        leg1.Draw()
        c1.SetLogy()
        c1.Print( os.path.join( self.plot_directory, 'classifier_output.png') )
        #histo.Scale(1000.) # norm must be set to total number of elements to get integral hist = 1

        #
        # spectator shapes for classifier binning        
        #

        ybin = 2 
        ymin = 0.8
        ymax = 1
 
        deltay = (ymax-ymin)/ybin
        sh_can = []
        histos = []
        for variable in self.spectator_variables:
            for attr in [ signalAttr , backgroundAttr ]:
                sh_can.append( ROOT.TCanvas()) 
                for i in range(ybin):
                    y1 = ymin + i*deltay 
                    y2 = y1 + deltay
                    X_tmp = getattr( self.X_spect, variable)[ (self.y_test_pred[0] >  y1) & (self.y_test_pred[0] <= y2) ]
                    xbin = 20
                    xmin = 0
                    xmax= 400
                    histos.append( ROOT.TH1F( attr.name + str(i) , attr.name + str(i) , xbin, xmin, xmax) )
                    histos[-1].SetLineColor( getattr(ROOT, attr.color) )
                    histos[-1].SetLineStyle( i+1 )
                    histos[-1].SetLineWidth(2)
                    for i in range( len( X_tmp[ self.y_test == attr.tag ].values )):
                        histos[-1].Fill( X_tmp[ self.y_test == attr.tag ].values[i] )
                    #histos[-1].Sumw2()
                    histos[-1].Scale( 1./ histos[-1].Integral() ) 
                    histos[-1].Draw('same hist') # without argument hist it draws only markers 
                sh_can[-1].SetLogy()
                sh_can[-1].Print( os.path.join( self.plot_directory, variable + '_' + attr.name + '_binning.png') )
       
if __name__ == '__main__':
    import StopsDilepton.tools.logger as logger
    logger  = logger.get_logger('INFO', logFile = None)

    import RootTools.core.logger as logger_rt
    logger_rt = logger_rt.get_logger('INFO', logFile = None )


    input_data_directory = 'SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow/v1_small/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1/all/'
    from StopsDilepton.MVA.default_classifier import training_variables, spectator_variables

    kerasTrainer = KerasTrainer( input_data_directory, training_variables, spectator_variables)
    kerasTrainer.init_training_data()
    kerasTrainer.train( batch_size = 512 )
