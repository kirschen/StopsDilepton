import numpy as np
from defclassifier import training_vars

# KERAS - environment is not made to predict single events - so one has to handicraft to predict single events: 
#model.predict( X_test.values[0:1] )[0][0]
#model.predict( np.array([ X_test.iloc[0].values ] ))[0][0]
#model.predict( np.array([ [testdict[k] for k in training_vars] ] ) ) [0][0]

def mva( keras, **kwargs ):
    '''
    Takes Keras Sequential model and Variables defining an event - look at how to use it.  
    '''
    tmp =  np.array([[kwargs[k] for k in training_vars]])
    return keras.predict( tmp )[0][0]
# how to use it:
#print mva(Jet1_eta = -0.201244380235, Jet1_pt = -0.518631026539, Jet2_eta = 1.36229103387, Jet2_pt = -0.743024457025, dl_eta = -1.32902276368, dl_mass = -0.743049409701, ht = -0.690160664083, l1_eta = -0.911253136088, l2_eta = -2.24572811641, metSig = 0.0601274708186, met_phi = -0.460269264713, met_pt = -0.461781724461, Jet_dphi = 1.22214449763, lep_dphi = -1.360960266)

# for testing: get data string for arbitrary events:
#mystring = ''
#i = 0
#for x in X_test.iloc[0]:
#    mystring += training_vars[i] + ' = ' + str( x ) + ', '
#    i += 1
#mystring = mystring[:-2]

def mva_dict( keras, mydict ):
    '''
    Takes Keras Sequential model and dictionary with all Variables defining an event - look at how to use it.
    '''
    return keras.predict( np.array( [ [mydict[k] for k in training_vars] ] ) )[0][0]
# how to use it:
# mva_dict( X_test.iloc[0].to_dict()  )
