'''
EvaluateClassifier.py loads a Keras binary classifier (eventually created by TrainClassifier.py) and evaluate it on preloaded testsamples (eventually loaded by LoadEvents.py)
X_test, y_test and X_mt2ll (seperated Dataframe which contains Mt2ll value for test Sample).

Visualisations of Evaluation are put in plotpath
'''

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import  ListedColormap
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers
from keras.models import load_model
from sklearn.metrics import roc_curve, roc_auc_score, auc
from sklearn.preprocessing import StandardScaler
from helpers import *
import os, time

# Variables - use %load MVADefinition.py
#datapath = 'h5_files/T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all_small/'
#plotpath_part1 = '/afs/hephy.at/user/g/gungersback/www/plots_Classifier/' + 'T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all_small/' 
#Datestring = str(2018) + '-' + str(7).zfill(2) + '-' + str(2).zfill(2) + '-' + str(1409).zfill(4)
#plotpath = plotpath_part1 + Datestring + '/'
#nbins = 20

#import models from .h5 file
model = load_model( plotpath + 'model/keras.h5' )

# evaluation on test sample - from here i am only allowed to use test samples!
loss_and_metrics = model.evaluate(X_test.values, y_test.values, batch_size=512)

#roccurve und auc
# neuronal net
y_test_pred = pd.DataFrame( model.predict( X_test.values  ) , index = X_test.index)
fpr_test, tpr_test, thresholds_test = roc_curve( y_test.values, y_test_pred.values )
auc_val_test = auc(fpr_test, tpr_test)

# mt2ll - X_mt2ll must be set to range 0 - 1 to interpret it like an outcome of an classifiere
fpr_mt2ll, tpr_mt2ll, thresholds_mt2ll = roc_curve( y_test.values, X_mt2ll.values )
auc_val_mt2ll = auc( fpr_mt2ll, tpr_mt2ll)

plt.plot( tpr_test, 1-fpr_test, 'b', label= 'Neural net, Auc=' + str(round(auc_val_test,4) ))
plt.plot( tpr_mt2ll, 1-fpr_mt2ll, 'r', label= 'Mt2ll, Auc=' + str(round(auc_val_mt2ll,4) ))
#plt.plot( fpr[cut_idx], tpr[cut_idx],'o', markersize=10, fillstyle="none" )
plt.title('ROC')
plt.xlabel('$\epsilon_{Sig}$', fontsize = 20) # 'False positive rate'
plt.ylabel('$1-\epsilon_{Back}$', fontsize = 20) #  '1-True positive rate' 
plt.legend(loc ='lower left')
plt.savefig( plotpath + 'roc.png')
plt.clf()

#saveTGraph( fpr, tpr, pathstring=plotpath, filename="Roc.png" )

# Visualisation or Classifier output
n, bins, patches = plt.hist( [ y_test_pred[y_test==0].values, y_test_pred[y_test==1].values ], nbins, log=True, label=['Background','Signal'], histtype='stepfilled', alpha=0.5) 
plt.title('Classifier output')
plt.xlabel('y_pred')
plt.ylim([0.5,10**5])
plt.legend()
plt.savefig( plotpath + 'classifier_output.png')
plt.clf()

# Comparision with variable mt2ll
n, bins, patches = plt.hist( [ X_mt2ll[y_test==0] , X_mt2ll[y_test==1] ], nbins, log=True, range=(0,300), label=['Background','Signal'], histtype='stepfilled', alpha=0.5) 
plt.title('MT2ll')
plt.xlabel('mt2ll')
plt.ylim([0.5,10**5])
plt.legend()
plt.savefig( plotpath + 'mt2ll.png')
plt.clf()

# MVA Cut
signi = (tpr_test *(y_test==1).sum()) / np.sqrt( tpr_test *(y_test==1).sum() + fpr_test *(y_test==0).sum() ) 
cut_sig = np.nanmax(signi)
cut_idx = int(np.where(signi ==  cut_sig)[0] )
cut_y = thresholds_test[cut_idx]

plt.figure()
fig, ax1 = plt.subplots()

l1 = ax1.plot( thresholds_test , tpr_test  , 'b', label= 'Singaleff')
l2 = ax1.plot( thresholds_test , fpr_test  , 'g', label= 'Backgroundeff')
ax1.set_xlabel('Threshold')
ax1.set_ylabel('Efficiencies')

ax2 = ax1.twinx()
l3 = ax2.plot( thresholds_test , signi  , 'r', label= 'Significance')                                                                             
ax2.set_ylabel('Significance')

plt.title('MVA Cut Optimisation')
lall = l1+l2+l3
labels = [l.get_label() for l in lall]
ax2.legend(lall, labels, loc='center')
plt.tight_layout()
plt.xlim([0, 1])

plt.savefig( plotpath + 'MVA_Cut_opti.png')
plt.clf()

## mt2ll shapes for different D cuts:
for i in range(0,9,2):
    X_temp = X_mt2ll[ ( y_test_pred[0] > (i/10.)) & (y_test_pred[0] <= (i/10.+0.2)) ]
    n, bins, patches = plt.hist( X_temp[y==0], nbins, log=True, normed=True, label= str(i/10.) + ' < D <= ' + str(i/10. + 0.2)  ,  histtype='stepfilled', alpha=0.2)
plt.title('MT2ll for Background')
plt.xlabel('mt2ll')
plt.ylim([10**(-3)*2,0.2])
plt.legend()
plt.savefig( plotpath + 'mt2ll_backgound_D.png')
plt.clf()

for i in range(0,9,2):
    X_temp = X_mt2ll[ ( y_test_pred[0] > (i/10.)) & (y_test_pred[0] <= (i/10.+0.2)) ]
    n, bins, patches = plt.hist( X_temp[y==1], nbins, log=True, normed=True, label= str(i/10.) + ' < D <= ' + str(i/10. + 0.2)  ,  histtype='stepfilled', alpha=0.2)
plt.title('MT2ll for Signal')
plt.xlabel('mt2ll')
plt.ylim([10**(-3)*2,0.2])
plt.legend()
plt.savefig( plotpath + 'mt2ll_signal_D.png')
plt.clf()

# D shapes for different Mt2ll cuts:
for i in range(5):
    y_temp = y_test_pred[ ( X_mt2ll > ( 50+i*30) ) & ( X_mt2ll > ( 80+i*30) ) ]
    n, bins, patches = plt.hist( y_temp[y==0], nbins, log=True, normed=True, label= str( 50+i*30 ) + ' < MT2ll <= ' + str( 80+i*30 )  , range=(0,1), histtype='stepfilled', alpha=0.2)
plt.title('y_pred for Background')
plt.xlabel('y_pred')
plt.legend()
plt.savefig( plotpath + 'D_backgound_mt2ll.png')
plt.clf()

for i in range(5):
    y_temp = y_test_pred[ ( X_mt2ll > ( 50+i*30) ) & ( X_mt2ll > ( 80+i*30) ) ]
    n, bins, patches = plt.hist( y_temp[y==1], nbins, log=True, normed=True, label= str( 50+i*30 ) + ' < MT2ll <= ' + str( 80+i*30 )  , range=(0,1), histtype='stepfilled', alpha=0.2)
plt.title('y_pred for Signal')
plt.xlabel('y_pred')
plt.legend()
plt.savefig( plotpath + 'D_signal_mt2ll.png')
plt.clf()

# S over sqrt B - Si
SqB = (tpr_test*(y_test==1).sum()) / np.sqrt( fpr_test*(y_test==0).sum() )
SqB_mt2ll = (tpr_mt2ll*(y_test==1).sum()) / np.sqrt( fpr_mt2ll*(y_test==0).sum() )

plt.plot(thresholds_test, SqB , 'g', label= 'Neural net')
plt.plot(thresholds_mt2ll/thresholds_mt2ll.max(), SqB_mt2ll , 'ro', label= 'mt2ll')

plt.title('SqB')
plt.xlabel('thresholds')
plt.legend()
plt.savefig( plotpath + 'SqB.png')
plt.clf()

## S over sqrt B - Cuts
#plt.plot(thresholds_mt2ll, SqB_mt2ll, 'ro', label= 'mt2ll')
#for events in y_test_pred:
#    if y_test_pred 
#    if events
#for i in range(5):
#    for 
#
#
#    y_tmp_pred = model.predict( X_test[ y_test_pred > ].values )
#    fpr_tmp, tpr_tmp, thresholds_tmp = roc_curve( y_test.values, y_test_pred.values )
#    SqB_tmp = (tpr_tmp*(y_mt2ll_sp==1).sum() ) / np.sqrt( fpr_tmp*(y_mt2ll_sp==0).sum() )
#    plt.plot(thresholds_mt2ll/thresholds_mt2ll.max(), SqB_tmp, 'ro', label= str(i/10.) + ' < D <= ' + str(i/10. + 0.2) )
#plt.title('SqB')
#plt.xlabel('thresholds')
#plt.yscale('log')
#plt.legend()
#plt.savefig( plotpath + 'SqB_cuts.png')
#plt.clf()
#
