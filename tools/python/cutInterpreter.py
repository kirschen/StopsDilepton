''' Class to interpret string based cuts
'''

import logging
logger = logging.getLogger(__name__)

jetSelection    = "nJetGood"
bJetSelectionM  = "nBTag"

mIsoWP = { "VT":5, "T":4, "M":3 , "L":2 , "VL":1, 0:"None" }

special_cuts = {
    # ("multiIsoVT":        "(1)", 
    "oldLooseLeptonVeto":     "(Sum$(Electron_pt>15&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&Muon_pfRelIso03_all<0.4) )==2",
    "looseLeptonVeto":        "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2",
    "looseLeptonMiniIsoVeto": "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_miniPFRelIso_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_miniPFRelIso_all<0.4) )==2",
    "tightLooseLeptonVeto":   "(Sum$(Electron_pt>5&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>5&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2",
    "supertightLooseLeptonVeto":   "(nElectron+nMuon)==2",
    "eleFakeFix":        "(Sum$(Electron_pt>20&&abs(Electron_eta)<2.4&&Electron_miniPFRelIso_all<0.1&&Electron_sip3d<4&&Electron_lostHits==0) + Sum$(Muon_pt>20&&abs(Muon_eta)<2.4&&Muon_miniPFRelIso_all<0.1) )==2",

    # for debugging: Apply 2016 cuts on sip3d 
    "tightDebugLeptonId":   "(Sum$(Electron_pt>20&&abs(Electron_eta)<2.4&&Electron_miniPFRelIso_all<0.1&&Electron_sip3d<4&&Electron_lostHits==0&&abs(Electron_dz)<0.1&&abs(Electron_dxy)<0.05&&Electron_convVeto&&Electron_cutBased>3) + Sum$(Muon_pt>20&&abs(Muon_eta)<2.4&&Muon_miniPFRelIso_all<0.1&&Muon_mediumId&&Muon_sip3d<4&&abs(Muon_dz)<0.1&&abs(Muon_dxy)<0.05) )==2",

    "OS":                "(l1_pdgId*l2_pdgId)<0",
    "lepSel":            "l1_pt>30&&l2_pt>20",
    "lep1Sel":           "l1_pt>30",
    "lepSel1Tight":      "l1_pt>20&&(!(l2_pt>=0))",
    "lepSelTight":       "l1_pt>40&&l2_pt>20",
    "lepSelEXO":         "l1_pt>25&&l2_pt>10",
    "quadlep":           "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12)>3",
    "trilep":            "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12)>2",
    "trilepTight":       "Sum$(lep_pt>20&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12)>2",

    "allZ":              "(1)",
    "onZ":               "abs(dl_mass-91.1876)<15",
    "offZ":              "abs(dl_mass-91.1876)>15",
    "onZZ" :             "abs(Z1_mass-91.1876)<20&&abs(Z2_mass-91.1876)<20",
    "onZ1" :             "abs(Z1_mass-91.1876)<20",
    "offZ1" :            "abs(Z1_mass-91.1876)>20",
    "offZ2":             "(1)",# taken care off in plot script. Think of something better! "abs(Z2_mass_4l-91.1876)>20",
    "minZ2mass12":       "(1)",# taken care off in plot script.
    "llgNoZ":            "(abs(dlg_mass-91.1876)>15||isEMu)",

    "gLepdR":            "(1)",
    "gJetdR":            "(1)",
   
    "photondR":          "photonJetdR>0.3&&photonLepdR>0.3",
    "photonEta":         "abs(photon_eta)<2.5",

    "dPhiJet0":          "Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0",
    "antiHEM":           "Sum$( ( cos(met_phi-JetGood_phi)<-0.8 )*(Iteration$==1) )==0",
    "antiHEMv2":         "Sum$( ( cos(met_phi-JetGood_phi)<-0.8 )*(Iteration$<2) )==0",
    "dPhiJet1":          "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )==0",
    "dPhiInv":           '(!(cos(met_phi-JetGood_phi[0])<0.8&&cos(met_phi-JetGood_phi[1])<cos(0.25)))', # here we want an njet requirement
    "metInv":            "met_pt<80",
    "metSigInv":         "metSig<5",
    "badJetSrEVeto":     "Sum$(Jet_neEmEF*Jet_pt*cosh(Jet_eta)*(2.6<abs(Jet_eta)&&abs(Jet_eta)<3&&Jet_pt<50))<200",
    "badEEJetVeto":      "Sum$((2.6<abs(Jet_eta)&&abs(Jet_eta)<3&&Jet_pt>30))==0",

    "HEMJetVeto":        "Sum$(Jet_pt>20&&Jet_eta<-1.3&&Jet_eta>-3.0&&Jet_phi<-0.87&&Jet_phi>-1.57)==0", # exact ranges: eta [-3.0, -1.3], phi [-1.57, -0.87]
    "HEMJetVetoWide":    "Sum$(Jet_pt>20&&Jet_eta<-1.0&&Jet_eta>-3.2&&Jet_phi<-0.5&&Jet_phi>-2.0)==0",
    "extraLepVeto":      "Sum$(abs(LepGood_pdgId)==13&&LepGood_pt>20&&( abs(LepGood_dz)>0.2 || abs(LepGood_dxy)>0.2 ) ) + Sum$(abs(LepOther_pdgId)==13&&LepOther_pt>20&&( abs(LepOther_dz)>0.2 || abs(LepOther_dxy)>0.2 ) )==0",

    #"ZEtaMinus":            "dl_eta>-3&&dl_eta<-1",
    #"ZEtaBarrel":           "dl_eta>-1&&dl_eta<1",
    #"ZEtaPlus":             "dl_eta>1&&dl_eta<3",
    "ZPhiHEM":          "dl_phi>-2+pi&&dl_phi<-0.5+pi",
    "ZPhiNoHEM":        "(!(dl_phi>-2+pi&&dl_phi<-0.5+pi))",
    "fwdJetVeto":       "Sum$(abs(Jet_eta)>4.53&&Jet_pt>30)==0",
    "metPhiPeak":       "met_phi>-1.2&&met_phi<-0.6",
    "metVetoPhiPeak":   "(!(met_phi>-1.2&&met_phi<-0.6))",
    "leadingMu":        "abs(l1_pdgId)==13",
    "leadingE":         "abs(l1_pdgId)==11",
    "Jet12Central":     "abs(JetGood_eta[0])<1.5&&abs(JetGood_eta[1])<1.5",
    "CSVV2":            "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_btagCSVV2>0.8484)==0"
  }

continous_variables = [ ("POGMetSig", "MET_significance"), ("metSig", "metSig"), ("mll", "dl_mass"), ("metPhi", "met_phi"), ("met", "met_pt"), ("mt2ll", "dl_mt2ll"), ("mt2blbl", "dl_mt2blbl"),("mt2bb", "dl_mt2bb"),("htCMG", "htJet40j"), ("photon","photon_pt"), ("nPV", "PV_npvsGood"), ("Z2mass", "Z2_mass"), ("Z1mass", "Z1_mass") ]
discrete_variables  = [ ("njet", "nJetGood"), ("btag", "nBTag") , ("nCMGjet", "nJet30")]

class cutInterpreter:
    ''' Translate var100to200-var2p etc.
    '''

    @staticmethod
    def translate_cut_to_string( string ):

        if string.startswith("multiIso"):
            str_ = mIsoWP[ string.replace('multiIso','') ]
            return "l1_mIsoWP>%i&&l2_mIsoWP>%i" % (str_, str_)
        elif string.startswith("relIso"):
           iso = float( string.replace('relIso','') )
           #raise ValueError("We do not want to use relIso for our analysis anymore!")
           return "l1_relIso03<%3.2f&&l2_relIso03<%3.2f"%( iso, iso )
        elif string.startswith("miniIso"):
           iso = float( string.replace('miniIso','') )
           return "l1_miniRelIso<%3.2f&&l2_miniRelIso<%3.2f"%( iso, iso )
        # special cuts
        if string in special_cuts.keys(): return special_cuts[string]

        # continous Variables
        for var, tree_var in continous_variables:
            if string.startswith( var ):
                num_str = string[len( var ):].replace("to","To").split("To")
                upper = None
                lower = None
                if len(num_str)==2:
                    lower, upper = num_str
                elif len(num_str)==1:
                    lower = num_str[0]
                else:
                    raise ValueError( "Can't interpret string %s" % string )
                res_string = []
                if lower: res_string.append( tree_var+">="+lower )
                if upper: res_string.append( tree_var+"<"+upper )
                return "&&".join( res_string )

        # discrete Variables
        for var, tree_var in discrete_variables:
            logger.debug("Reading discrete cut %s as %s"%(var, tree_var))
            if string.startswith( var ):
                # So far no njet2To5
                if string[len( var ):].replace("to","To").count("To"):
                    raise NotImplementedError( "Can't interpret string with 'to' for discrete variable: %s. You just volunteered." % string )

                num_str = string[len( var ):]
                # logger.debug("Num string is %s"%(num_str))
                # var1p -> tree_var >= 1
                if num_str[-1] == 'p' and len(num_str)==2:
                    # logger.debug("Using cut string %s"%(tree_var+">="+num_str[0]))
                    return tree_var+">="+num_str[0]
                # var123->tree_var==1||tree_var==2||tree_var==3
                else:
                    vls = [ tree_var+"=="+c for c in num_str ]
                    if len(vls)==1:
                      # logger.debug("Using cut string %s"%vls[0])
                      return vls[0]
                    else:
                      # logger.debug("Using cut string %s"%'('+'||'.join(vls)+')')
                      return '('+'||'.join(vls)+')'
        raise ValueError( "Can't interpret string %s. All cuts %s" % (string,  ", ".join( [ c[0] for c in continous_variables + discrete_variables] +  special_cuts.keys() ) ) )

    @staticmethod
    def cutString( cut, select = [""], ignore = [], photonEstimated=False):
        ''' Cutstring syntax: cut1-cut2-cut3
        '''
        cuts = cut.split('-')
        # require selected
        cuts = filter( lambda c: any( sel in c for sel in select ), cuts )
        # ignore
        cuts = filter( lambda c: not any( ign in c for ign in ignore ), cuts )

        cutString = "&&".join( map( cutInterpreter.translate_cut_to_string, cuts ) )

        if photonEstimated:
          for var in ['met_pt','met_phi','metSig','dl_mt2ll','dl_mt2bb']:
            cutString = cutString.replace(var, var + '_photonEstimated')

        return cutString
    
    @staticmethod
    def cutList ( cut, select = [""], ignore = []):
        ''' Cutstring syntax: cut1-cut2-cut3
        '''
        cuts = cut.split('-')
        # require selected
        cuts = filter( lambda c: any( sel in c for sel in select ), cuts )
        # ignore
        cuts = filter( lambda c: not any( ign in c for ign in ignore ), cuts )
        return [ cutInterpreter.translate_cut_to_string(cut) for cut in cuts ] 
        #return  "&&".join( map( cutInterpreter.translate_cut_to_string, cuts ) )

if __name__ == "__main__":
    print cutInterpreter.cutString("njet2-btag0p-multiIsoVT-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100")
    print
    print cutInterpreter.cutList("njet2-btag0p-multiIsoVT-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100")
