'''
Masterfile for 
LoadEvents.py ,TrainClassifier.py, EvaluateClassifier.py

eg. %load MVADefinition.py

'''
import time
from defclassifier import training_vars

# Define Path
small = True
datapath = 'h5_files/T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all'
plotpath_part1 = '/afs/hephy.at/user/g/gungersback/www/plots_Classifier/' + 'T8bbllnunu_XCha0p5_XSlep0p5_800_1-TTLep_pow/njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1_all'

if small:
    datapath += '_small/'
    plotpath_part1 += '_small/'
else:
    datapath += '/'
    plotpath_part1 += '/'
 
Datestring = time.strftime("%Y-%m-%d-%H%M") # so we don't overwrite previous model
#Datestring = str(2018) + '-' + str(7).zfill(2) + '-' + str(2).zfill(2) + '-' + str(1409).zfill(4)
plotpath = plotpath_part1 + '/' + Datestring + '/'

# Define Neural Net
NHLayer = 2
NUnits = 100
NEpochs = 100

# Plot adjustment
nbins = 20

execfile('LoadEvents.py') #loads .h5 files from datapath - gives X_train, y_train, X_test, y_test, X_mt2ll
execfile('TrainClassifier.py') # trains on X_train, y_train - stores weights and loss/acc plots in plotpath
execfile('EvaluateClassifier.py') # loads model from plotpath - stores Evaluation plots in plotpath
