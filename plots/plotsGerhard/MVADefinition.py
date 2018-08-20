'''
Masterfile for 
LoadEvents.py ,TrainClassifier.py, EvaluateClassifier.py

eg. %load MVADefinition.py

'''
import time, os
from defclassifier import training_vars

# Define Path
name_sig_bkg='SMS_T8bbllnunu_XCha0p5_XSlep0p09-TTLep_pow'
#'T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow'
name_sel_mod='njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all'
small = True
Datestring = time.strftime("%Y-%m-%d-%H%M") # so we don't overwrite previous model
#Datestring = str(2018) + '-' + str(7).zfill(2) + '-' + str(3).zfill(2) + '-' + str(1146).zfill(4)

rootdatapath =''
rootplotpath = '/afs/hephy.at/user/g/gungersback/www/plots_Classifier/' 

if small:
    datapath = rootdatapath + 'h5_files/' + name_sig_bkg + '/' + name_sel_mod + '_small/'
    plotpath = rootplotpath +  name_sig_bkg + '/' +  name_sel_mod + '_small/' + Datestring + '/'
else:
    datapath = rootdatapath + 'h5_files/' + name_sig_bkg + '/' + name_sel_mod + '/'
    plotpath = rootplotpath +  name_sig_bkg + '/' +  name_sel_mod + '/' + Datestring + '/'

if not os.path.exists( datapath ): os.makedirs( datapath )
if not os.path.exists( plotpath ): os.makedirs( plotpath )

# Define Neural Net
NHLayer = 2
units = 100
epochs = 100
if small:
    batch_size = 512
else:
    batch_size = 5120
validation_split = 0.2

# Plot adjustment
nbins = 20

execfile('LoadEvents.py') #loads .h5 files from datapath - gives X_train, y_train, X_test, y_test, X_mt2ll
execfile('TrainClassifier.py') # trains on X_train, y_train - stores weights and loss/acc plots in plotpath
execfile('EvaluateClassifier.py') # loads model from plotpath - stores Evaluation plots in plotpath
