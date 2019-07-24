'''
TrainClassifier.py initializes a Keras binary classifier and trains it on preloaded X_train and y_train - eventually loaded by LoadEvents.py

The trained classifier and the training visualisation (Lossfunction and Accuracy over time) are saved in a subfolder specified by the date of plotpath. 
The classifier is saved as .h5 file.
'''
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers
from helpers import *
import os, time

# Variables - use %load MVADefinition.py
#plotpath_part1 = '/afs/hephy.at/user/g/gungersback/www/plots_Classifier/' + 'T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all/'
#Datestring = time.strftime("%Y-%m-%d-%H%M")
#plotpath = plotpath_part1 + '/' + Datestring + '/'
#NHLayer = 2
#units = 100
#epochs = 100

if not os.path.exists( plotpath ):
    os.makedirs( plotpath )

#Initialize and build classifier
model = Sequential()
model.add( Dense(units= units, activation='relu',  input_dim=X_train.shape[1]) ) 
for i in range(NHLayer):
    model.add( Dense(units= units, activation='relu' ) )
model.add( Dense(units=1, activation='sigmoid') ) 

# configuration
#model.compile( loss='binary_crossentropy',  optimizer=optimizers.RMSprop(lr=0.001) ,  metrics=['accuracy'])
model.compile( loss='binary_crossentropy',  optimizer='rmsprop',                     metrics=['acc'])

# training
history = model.fit(X_train.values, y_train.values, epochs= epochs, batch_size= batch_size, validation_split= validation_split)

if not os.path.exists( plotpath + 'model' ):
    os.makedirs( plotpath + 'model' )
model.save(plotpath + 'model/' + 'keras.h5')

# overtraining check
history_dict = history.history

loss_values = history_dict['loss']
if validation_split != 0:
    val_loss_values = history_dict['val_loss']
acc_values = history_dict['acc']
if validation_split != 0:
    val_acc_values = history_dict['val_acc']
epochslist = range(1,  len(loss_values)+1)

plt.plot(epochslist, loss_values, 'bo', label='Training loss')
if validation_split != 0:
    plt.plot(epochslist, val_loss_values, 'b', label='Validation loss')
plt.title('Training and validation loss (Valid. split = ' + str( validation_split ) + ')')
plt.xlabel('Epochs  ( batch_size = ' + str( batch_size ) + ')')
plt.ylabel('Loss')
plt.legend()
plt.savefig( plotpath + 'loss.png')
plt.clf()

plt.plot(epochslist, acc_values, 'bo', label='Training acc')
if validation_split != 0:
    plt.plot(epochslist, val_acc_values, 'b', label='Validation acc')
plt.title('Training and validation acc (Valid. split = ' + str( validation_split ) + ')')
plt.xlabel('Epochs ( batch_size = ' + str( batch_size ) + ')')
plt.ylabel('Acc')
plt.legend()
plt.savefig( plotpath + 'acc.png')
plt.clf()

#saveTGraph( epochslist, loss_values, pathstring=plotpath, filename="training_loss.png"  )
#saveTGraph( epochslist, val_loss_values, pathstring=plotpath ,filename="validation_loss.png"  )
#saveTGraph( epochslist, acc_values, pathstring=plotpath, filename="training_acc.png"  )
#saveTGraph( epochslist, val_acc_values, pathstring=plotpath, filename="validation_acc.png"  )
