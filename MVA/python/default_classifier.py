from StopsDilepton.tools.helpers import deltaPhi

# Read from root files
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I",
                  "dl_pt/F","l1_pt/F","l2_pt/F"]

training_variables = {
        'JetGood_pt[0]':  lambda event: event.JetGood_pt[0]     , 
        'JetGood_eta[0]': lambda event: event.JetGood_eta[0]    ,
        'JetGood_pt[1]':  lambda event: event.JetGood_pt[1]     , 
        'JetGood_eta[1]': lambda event: event.JetGood_eta[1]    ,
        'dl_eta':       lambda event: event.dl_eta            ,
        'dl_mass':      lambda event: event.dl_mass           ,
        'ht':           lambda event: event.ht                ,
        'l1_eta':       lambda event: event.l1_eta            , 
        'l2_eta':       lambda event: event.l2_eta            ,
        'metSig':       lambda event: event.metSig            , 
        'met_pt':       lambda event: event.met_pt            ,
        'Jet_dphi':     lambda event: deltaPhi( event.JetGood_phi[0],   event.JetGood_phi[1] ),
        'lep_dphi':     lambda event: deltaPhi( event.l1_phi, event.l2_phi ), 
#        'dl_pt':        lambda event: event.dl_pt             , 
#        'l1_pt':        lambda event: event.l1_pt             , 
#        'l2_pt':        lambda event: event.l2_pt             , 
}

spectator_variables = {
        'dl_mt2ll':       lambda event: event.dl_mt2ll ,
        'JetGood_pt[2]':  lambda event: event.JetGood_pt[2]  , 
        'JetGood_eta[2]': lambda event: event.JetGood_eta[2] ,
        'JetGood_pt[3]':  lambda event: event.JetGood_pt[3]  , 
        'JetGood_eta[3]': lambda event: event.JetGood_eta[3] ,
}

training_variables_list = training_variables.keys()
training_variables_list.sort()
spectator_variables_list = spectator_variables.keys()
spectator_variables_list.sort()

# Training selection 
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.objectSelection import getFilterCut
selection = 'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1'
mode = 'all'
offZ = "&&abs(dl_mass-91.1876)>15" if not (selection.count("onZ") or selection.count("allZ") or selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="all":  return "nGoodMuons+nGoodElectrons==2&&isOS&&( " + "(isEE||isMuMu)" + offZ + "|| isEMu)"

selection_cutstring = "&&".join( [cutInterpreter.cutString(selection), getFilterCut(isData=False, badMuonFilters = "Summer16"), getLeptonSelection(mode)] )

#training_variables_low = [
#        'JetGood_pt[0]', 'JetGood_eta[0]',
#        'JetGood_pt[1]', 'JetGood_eta[1]',
#        'dl_eta', 'dl_mass',
#        'ht',
#        'l1_eta', 'l2_eta',
#        'metSig', 'met_pt',
#]
#
## Class to define new variables based on variables from root file 
#class newvariable(object):
#    def __init__(self, name, function, argumentlist, lambda_function):
#        self.name = name
#        self.function = function
#        self.argumentlist = argumentlist
#        self.lambda_function = lambda_function
#
#training_variables_high = [
#       newvariable('Jet_dphi', deltaPhi, ["JetGood_phi[0]", "JetGood_phi[1]"], lambda event: deltaPhi( event.JetGood_phi[0],   event.JetGood_phi[1] ),
#       newvariable('lep_dphi', deltaPhi, ["l1_phi", "l2_phi"], lambda event: deltaPhi( event.l1_phi, l2_phi ) )
#]

#training_variables = training_variables_low + [ variable.name for variable in training_variables_high ]

#spectator_variables = ['dl_mt2ll']

def get_dict( event ):
    return {k: l(event) for k, l in training_variables.iteritems()}
