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

#import models from .h5 file
model = load_model( plotpath + 'model/keras.h5' )

# evaluation on test sample - from here i am only allowed to use test samples!
loss_and_metrics = model.evaluate(X_test.values, y_test.values, batch_size= batch_size)

#roccurve und auc
# neuronal net
y_test_pred = pd.DataFrame( model.predict( X_test.values  ) , index = X_test.index)
fpr_test, tpr_test, thresholds_test = roc_curve( y_test.values, y_test_pred.values )
auc_val_test = auc(fpr_test, tpr_test)

# mt2ll 
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

# Visualisation of Classifier output
n, bins, patches = plt.hist( [ y_test_pred[y_test==0].values, y_test_pred[y_test==1].values ], nbins, log=True, label=['Background ('+ str((y_test==0).sum()) +')' ,'Signal ('+ str((y_test==1).sum()) +')'], histtype='stepfilled', alpha=0.5) 
plt.title('Classifier output (of Test sample)')
plt.xlabel('y_pred')
plt.ylim([0.5,10**5])
plt.legend()
plt.savefig( plotpath + 'classifier_output.png')
plt.clf()

# Comparision with variable mt2ll
n, bins, patches = plt.hist( [ X_mt2ll[y_test==0] , X_mt2ll[y_test==1] ], nbins, log=True, range=(0,300), label= ['Background ('+ str((y_test==0).sum()) +')' ,'Signal ('+ str((y_test==1).sum()) +')'] , histtype='stepfilled', alpha=0.5) 
plt.title('MT2ll (of Test sample)')
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
#for i in range(5):
#    y_temp = y_test_pred[ ( X_mt2ll > ( 50+i*30) ) & ( X_mt2ll > ( 80+i*30) ) ]
#    try:
#        n, bins, patches = plt.hist( y_temp[y==0], nbins, log=True, normed=True, label= str( 50+i*30 ) + ' < MT2ll <= ' + str( 80+i*30 )  , range=(0,1), histtype='stepfilled', alpha=0.2)
#    except ValueError:  #raised if `X_temp` is empty.                                                                                                                                          
#        pass  
#plt.title('y_pred for Background')
#plt.xlabel('y_pred')
#plt.legend()
#plt.savefig( plotpath + 'D_backgound_mt2ll.png')
#plt.clf()
#
#for i in range(5):
#    y_temp = y_test_pred[ ( X_mt2ll > ( 50+i*30) ) & ( X_mt2ll > ( 80+i*30) ) ]
#    n, bins, patches = plt.hist( y_temp[y==1], nbins, log=True, normed=True, label= str( 50+i*30 ) + ' < MT2ll <= ' + str( 80+i*30 )  , range=(0,1), histtype='stepfilled', alpha=0.2)
#plt.title('y_pred for Signal')
#plt.xlabel('y_pred')
#plt.legend()
#plt.savefig( plotpath + 'D_signal_mt2ll.png')
#plt.clf()

# S over sqrt B - Idea was to compare S/sqrtB for mt2ll and y_pred cuts - but not needed 
#SqB = (tpr_test*(y_test==1).sum()) / np.sqrt( fpr_test*(y_test==0).sum() )
#SqB_mt2ll = (tpr_mt2ll*(y_test==1).sum()) / np.sqrt( fpr_mt2ll*(y_test==0).sum() )
#
#plt.plot(thresholds_test, SqB , 'g', label= 'Neural net')
#plt.plot(thresholds_mt2ll/thresholds_mt2ll.max(), SqB_mt2ll , 'ro', label= 'mt2ll')
#
#plt.title('( Nr of True Signal ) / Sqrt( Nr of True Backround )')
#plt.xlabel('mt2ll cuts')
#plt.legend()
#plt.savefig( plotpath + 'SqB.png')
#plt.clf()

# S / sqrt B over mt2ll cuts - for binned Classifier output
tresholds_mt2ll_red = np.linspace(75,174,50) # computation with thresholdes_mt2ll takes too long
plt.figure()
fig, ax = plt.subplots()
sqb_tmp = []                    
# without classifier                                        
for j in thresholds_mt2ll_red:                                             
    X_tmptmp = X_mt2ll[X_mt2ll > j]                                                                   
    sqb_tmp.append( len( X_tmptmp[y==1]) / np.sqrt( len( X_tmptmp[y==0] )))            
plt.plot( thresholds_mt2ll_red, sqb_tmp, label= 'without Classifier (' + str(len(y_test)) + ')' )

# with classifier
# loop over Classifier binning
for i in range(0,9,2):
    # Consider Subsets of events with given Classifier output range
    X_tmp = X_mt2ll[ ( y_test_pred[0] > (i/10.)) & (y_test_pred[0] <= (i/10.+0.2)) ]
    sqb_tmp = []
    # Step through mt2ll cut values 
    for j in thresholds_mt2ll_red:
        # look at all events which have a bigger mt2ll value than threshold
        X_tmptmp = X_tmp[X_tmp > j]          
        # from all these events we calculate Number of True Signals / sqrt (Number of True Background)
        sqb_tmp.append( len( X_tmptmp[y==1]) / np.sqrt( len( X_tmptmp[y==0] )))
    plt.plot( thresholds_mt2ll_red, sqb_tmp, label= str(i/10.) + ' < D <= ' + str(i/10. + 0.2)  + '(' +  str(len(X_tmp)) + ')' )

plt.title('( Nr of Signal events ) / Sqrt( Nr of Backround events ) \n in signal region defined by mt2ll cuts - with classifier binning D')
plt.xlabel('mt2ll cut')
ax.set_yscale('log')
plt.legend(loc='lower left')
plt.savefig( plotpath + 'SqB_cuts.png')
plt.clf()

