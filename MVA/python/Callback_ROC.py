import keras
from sklearn.metrics import roc_auc_score
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import os

class Callback_ROC(keras.callbacks.Callback):
    """
    Custom callback class for Keras which calculates and plots ROC aucs after training epochs. Intervall is adjustable.
    Also offers possibility to use earlystopping if auc value does not improve.
    """
    def __init__(self, X_train, y_train, plot_directory, keras_directory, interval_evaluate_auc = 5,  patience_earlystopping_auc = False ):
        # best auc value
        self.best = 0
        self.best_filename = ''
        # intervall of saving auc values 
        self.interval_evaluate_auc = interval_evaluate_auc
        # stop training if roc_auc value did not improve in the last patience_earlystopping_auc measurements
        self.patience_earlystopping_auc = patience_earlystopping_auc
        # counter for patience_earlystopping_auc
        self.wait = 0
 
        self.X_train = X_train
        self.y_train = y_train
        self.plot_directory = plot_directory 
        self.keras_directory = keras_directory 

    def on_train_begin(self, logs={}):
        self.epochs = []
        self.aucs_val = []
        self.aucs_train = []
 
    def on_train_end(self, logs={}):
        plt.plot(self.epochs, self.aucs_train, 'bo', label='Training auc')
        plt.plot(self.epochs, self.aucs_val, 'b', label='Validation auc')
        plt.title('Training and validation auc')
        plt.xlabel('Epochs')
        plt.ylabel('Auc')
        plt.legend()
        plt.savefig( os.path.join( self.plot_directory , 'auc.png'))
        plt.grid(True)
        plt.clf()
 
    def on_epoch_begin(self, epoch, logs={}):
        return
 
    def on_epoch_end(self, epoch, logs={}):
        
        if ( (epoch+1) % self.interval_evaluate_auc == 0 ):
            self.epochs.append(epoch+1)
            
             # validation sample
            y_pred_val = self.model.predict(self.validation_data[0])
            roc_auc_val = roc_auc_score(self.validation_data[1], y_pred_val)
            self.aucs_val.append(roc_auc_val)
            
            # training sample
            y_pred_train = self.model.predict(self.X_train.values)
            roc_auc_train = roc_auc_score(self.y_train.values, y_pred_train)
            self.aucs_train.append(roc_auc_train)

            # Save model with best roc auc
            current = roc_auc_val
            if current > self.best:
                self.best = current
                # remove old one
                if self.best_filename:
                    os.remove( os.path.join( self.keras_directory, self.best_filename ) )
                # create new one
                self.best_filename = 'best_roc_auc_' + str( int(self.best*1000) ) + '.h5'
                self.model.save( os.path.join( self.keras_directory, self.best_filename ) )
                self.wait = 0

            else:
                if self.patience_earlystopping_auc:
                    if self.wait >= self.patience_earlystopping_auc:            
                        self.model.stop_training = True
                        print('Epoch %05d: early stopping' % (epoch))
                    self.wait += 1
        return

    def on_batch_begin(self, batch, logs={}):
        return
 
    def on_batch_end(self, batch, logs={}):
        return
