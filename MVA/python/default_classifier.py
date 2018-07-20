
training_variables = [
# Read from root files
        'Jet1_eta', 'Jet1_pt',
        'Jet2_eta', 'Jet2_pt',
        'dl_eta', 'dl_mass',
        'ht',
        'l1_eta', 'l2_eta',
        'metSig', 'met_phi', 'met_pt',
# Calculated from read root files, defined in preprocessing.py
        'Jet_dphi',
        'lep_dphi',
]

spectator_variables = ['dl_mt2ll']
