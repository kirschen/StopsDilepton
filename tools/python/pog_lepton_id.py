# Electrons
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2

ele_pog_ids = ['veto', 'loose', 'medium', 'tight']

#80X-tuned selection, barrel cuts ( |eta supercluster| <= 1.479)
#    Veto    Loose   Medium  Tight

#80X-tuned selection, endcap cuts ( |eta supercluster| <= 1.479) |

ele_pog_id_thresholds_barrel = {
    'sigmaIEtaIEta':        ( 0.0115,  0.011,  0.00998,  0.00998),
    'AbsDEtaScTrkIn':       ( 0.00749,  0.00477,  0.00311,  0.00308),
    'AbsDPhiScTrkIn':       ( 0.228,  0.222,  0.103,  0.0816),
    'hadronicOverEm':       ( 0.356,  0.298,  0.253,  0.0414),
    'AbsEInvMinusPInv':     ( 0.299,  0.241,  0.134,  0.0129),
    'lostHits':             ( 2,  1,  1,  1),
    'relIso03':             ( 0.175,  0.0994,  0.0695,  0.0588),
}

#80X-tuned selection, endcap cuts ( |eta supercluster| > 1.479) |
ele_pog_id_thresholds_endcap = {
    'sigmaIEtaIEta':        (0.037,  0.0314,  0.0298,  0.0292),
    'AbsDEtaScTrkIn':       (0.00895,  0.00868,  0.00609,  0.00605),
    'AbsDPhiScTrkIn':       (0.213,  0.213,  0.045,  0.0394),
    'hadronicOverEm':       (0.211,  0.101,  0.0878,  0.0641),
    'AbsEInvMinusPInv':     (0.15,  0.14,  0.13,  0.0129),
    'lostHits':             (3,  1,  1,  1),
    'relIso03':             (0.159,  0.107,  0.0821,  0.0571),
}

def ele_ID_functor( wp, isolation = True):

    idx = ele_pog_ids.index( wp )

    ele_pog_id_thresholds_barrel_sigmaIEtaIEta =       ele_pog_id_thresholds_barrel['sigmaIEtaIEta'][idx] 
    ele_pog_id_thresholds_barrel_AbsDEtaScTrkIn =      ele_pog_id_thresholds_barrel['AbsDEtaScTrkIn'][idx] 
    ele_pog_id_thresholds_barrel_AbsDPhiScTrkIn =      ele_pog_id_thresholds_barrel['AbsDPhiScTrkIn'][idx] 
    ele_pog_id_thresholds_barrel_hadronicOverEm =      ele_pog_id_thresholds_barrel['hadronicOverEm'][idx] 
    ele_pog_id_thresholds_barrel_AbsEInvMinusPInv =    ele_pog_id_thresholds_barrel['AbsEInvMinusPInv'][idx] 
    ele_pog_id_thresholds_barrel_lostHits =            ele_pog_id_thresholds_barrel['lostHits'][idx] 
    ele_pog_id_thresholds_barrel_relIso03 =            ele_pog_id_thresholds_barrel['relIso03'][idx]

    ele_pog_id_thresholds_endcap_sigmaIEtaIEta =       ele_pog_id_thresholds_endcap['sigmaIEtaIEta'][idx] 
    ele_pog_id_thresholds_endcap_AbsDEtaScTrkIn =      ele_pog_id_thresholds_endcap['AbsDEtaScTrkIn'][idx] 
    ele_pog_id_thresholds_endcap_AbsDPhiScTrkIn =      ele_pog_id_thresholds_endcap['AbsDPhiScTrkIn'][idx] 
    ele_pog_id_thresholds_endcap_hadronicOverEm =      ele_pog_id_thresholds_endcap['hadronicOverEm'][idx] 
    ele_pog_id_thresholds_endcap_AbsEInvMinusPInv =    ele_pog_id_thresholds_endcap['AbsEInvMinusPInv'][idx] 
    ele_pog_id_thresholds_endcap_lostHits =            ele_pog_id_thresholds_endcap['lostHits'][idx]
    ele_pog_id_thresholds_endcap_relIso03 =            ele_pog_id_thresholds_endcap['relIso03'][idx]

    def func( ele ):
        if abs(ele['pdgId'])!=11: return False
        if abs( ele['etaSc'] ) <= 1.479:
            return \
                ele["sigmaIEtaIEta"] <      ele_pog_id_thresholds_barrel_sigmaIEtaIEta and \
                abs(ele["dEtaScTrkIn"]) <   ele_pog_id_thresholds_barrel_AbsDEtaScTrkIn and \
                abs(ele["dPhiScTrkIn"]) <   ele_pog_id_thresholds_barrel_AbsDPhiScTrkIn and \
                ele["hadronicOverEm"] <     ele_pog_id_thresholds_barrel_hadronicOverEm and \
                abs(ele["eInvMinusPInv"]) < ele_pog_id_thresholds_barrel_AbsEInvMinusPInv and \
                ele["lostHits"] <=          ele_pog_id_thresholds_barrel_lostHits and \
                ( ele["relIso03"] <         ele_pog_id_thresholds_barrel_relIso03 or not isolation )
        else: 
                ele["sigmaIEtaIEta"] <      ele_pog_id_thresholds_endcap_sigmaIEtaIEta and \
                abs(ele["dEtaScTrkIn"]) <   ele_pog_id_thresholds_endcap_AbsDEtaScTrkIn and \
                abs(ele["dPhiScTrkIn"]) <   ele_pog_id_thresholds_endcap_AbsDPhiScTrkIn and \
                ele["hadronicOverEm"] <     ele_pog_id_thresholds_endcap_hadronicOverEm and \
                abs(ele["eInvMinusPInv"]) < ele_pog_id_thresholds_endcap_AbsEInvMinusPInv and \
                ele["lostHits"] <=          ele_pog_id_thresholds_endcap_lostHits and \
                ( ele["relIso03"] <         ele_pog_id_thresholds_endcap_relIso03 or not isolation )

    return func

# Muons
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2

#mu_pog_ids = [ 'soft', 'loose', 'medium', 'mediumICHEP', 'tight']

def mu_ID_functor( wp ):
    #idx = mu_pog_ids.index( wp )

    if wp == 'loose':
        def func( mu ):
            return mu['pfMuonId'] and abs(mu['pdgId'])==13 
        return func
    elif wp == 'soft':
        def func( mu ):
            return mu['softMuonId'] and abs(mu['pdgId'])==13 
        return func
    elif wp == 'medium':
        def func( mu ):
            return mu['mediumMuonId'] and abs(mu['pdgId'])==13
        return func
    elif wp == 'tight':
        def func( mu ):
            return mu['tightId'] and abs(mu['pdgId'])==13
        return func
    elif wp == 'mediumICHEP':
        def func( mu ):
            return mu['ICHEPmediumMuonId'] and abs(mu['pdgId'])==13
        return func

    else: raise ValueError( "Don't know muon Id %r" % wp )

