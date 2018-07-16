'''
LoadEvents.py loads Events from .h5 files saved by EventsToH5.py and prepares them for machine learning purpose.

Reads .h5 files, keeps all variables (=columns) specified by training_vars, normalizes the variables to mean=0 and std=1, and randomly splitts data set into
Training set (X_train, y_train)
Test set (X_test, y_test)
addidionally it saves the Mt2ll value of the Test set in a DataFrame X_mt2ll.

'''

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import os, time

# Variables - use %load MVADefinition.py
# datapath = 'h5_files/T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all/'
# training_vars = ...

# read .h5 files to create feature Matrix X and target vector y
X = pd.read_hdf( datapath + 'data_X.h5', 'df')
y = pd.read_hdf( datapath + 'data_y.h5', 'df')

# create new Variables from Data
X['Jet_dphi'] = abs(X['Jet1_phi'] - X['Jet2_phi'])
X['lep_dphi'] = abs(X['l1_phi'] - X['l2_phi'])

# all variables we have from events
allvar = list(X.columns)
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

#keep information of training_vars and mt2ll
intrvar= training_vars+['dl_mt2ll']
X = X[intrvar]

print 'Number of variables for training ' + str( len(training_vars) )
print 'Number of signal / backround events: ' + str( (y==1).sum()) + ' / ' + str( (y==0).sum()) 
print 'Number of events and percentage of signal events in sample: ' + str( y.shape[0] ) + ' // ' + str( round( 100.* (y==1).sum() / y.shape[0] ,2 )) + ' %'

# Normalize Data ( Using Standardscaler we would loose columns naming)
X_mean, X_std = X.mean(), X.std()

X -= X_mean
X /= X_std  

# Inverse transform
# X *= X_std
# X += X_mean

# Splitting in training and test samples
train_per=0.75
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size= int( train_per*y.shape[0] ), random_state=42)

X_mt2ll = X_test['dl_mt2ll']
X_test = X_test.drop(['dl_mt2ll'], axis=1)
X_train = X_train.drop(['dl_mt2ll'], axis=1)

# Inverse Transf of mt2ll
X_mt2ll *= X_std.dl_mt2ll
X_mt2ll += X_mean.dl_mt2ll
X_mean = X_mean.drop(['dl_mt2ll'])
X_std = X_std.drop(['dl_mt2ll'])
