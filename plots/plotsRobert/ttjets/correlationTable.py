import ROOT
import pickle

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)
args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
data_directory = "/afs/hephy.at/data/dspitzbart01/cmgTuples/"
postProcessing_directory = "postProcessed_80X_v21/dilepTiny"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain
from StopsDilepton.analysis.u_float import u_float
from math import sqrt

from StopsDilepton.tools.objectSelection import multiIsoLepString

cuts=[
  #("==2 VT leptons (25/20)", "nGoodMuons+nGoodElectrons==2&&l1_mIsoWP>=5&&l2_mIsoWP>=5&&l1_pt>25"),
  ("==2 relIso03<0.12 leptons", "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12"),
  ("opposite sign","isOS==1"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  #(">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=2 jets", "nJetGood>=2"),
  #(">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  (">=1 b-tags (CSVv2)", "nBTag>=1"),
  ("MET>80", "met_pt>80"),
  ("metSig>5", "metSig>5"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("MT2(ll) < 100", "dl_mt2ll<100"),
#  ("multiIso M(Mu), T(Ele)", multiIsoWPMT),
#  ("multiIso VT(Mu), VT(Ele)", multiIsoWPVTVT),
#  ("filterCut", "Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter" ),
# ("relIso04<0.12", relIso04sm12Cut),
# ("MT2(ll) > 240", "dl_mt2ll>240"),
    ]

def getZCut(mode):
    mZ = 91.2
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<15"
    if mode.lower()=="offz": return zstr+">15"
    return "(1)"

# Extra requirements on data
from StopsDilepton.tools.objectSelection import getFilterCut

DoubleMuon  = DoubleMuon_Run2016BCDEFG_backup
DoubleEG    = DoubleEG_Run2016BCDEFG_backup
MuonEG      = MuonEG_Run2016BCDEFG_backup

doubleMu_selectionString    = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0&&abs(dl_mass-91.2)>15"
doubleEle_selectionString   = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2&&abs(dl_mass-91.2)>15"
muEle_selectionString       = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"
lepton_selection_string_mc = "(isEMu==1&&nGoodMuons==1&&nGoodElectrons==1|| ( isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0 || isEE==1&&nGoodMuons==0&&nGoodElectrons==2 ) && abs(dl_mass-91.2)>15)"
data_samples = [DoubleMuon, DoubleEG, MuonEG]
DoubleMuon.setSelectionString(doubleMu_selectionString)
DoubleEG.setSelectionString(doubleEle_selectionString)
MuonEG.setSelectionString(muEle_selectionString)
DoubleMuon.name = "Data 2mu" 
DoubleEG.name = "Data 2e"
MuonEG.name = "Data 1e1mu"

data_sample_texName = "Data"
    #qcd_sample = QCD_Mu5EMbcToE

#Define chains for signals and backgrounds
mc_samples = [
    DY_HT_LO, 
    Top_pow, 
    TTZ, TTXNoZ, multiBoson, #QCD_Mu5EMbcToE, 
]
data_samples = [ DoubleMuon, DoubleEG, MuonEG ]

samples = mc_samples + data_samples

lumiFac = sum( s.lumi for s in data_samples )/len(data_samples)/1000.

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

for sample in mc_samples:
    sample.addSelectionString( getFilterCut( isData = False ) )
    sample.addSelectionString( lepton_selection_string_mc )
    sample.setWeightString( 'weight' )
for sample in data_samples:
    sample.addSelectionString( getFilterCut( isData = True ) )
    sample.setWeightString( "(1)" )

jet_systematics    = ['JECUp','JECDown']# 'JERDown','JECVUp','JECVDown']
met_systematics    = ['UnclusteredEnUp', 'UnclusteredEnDown']
jme_systematics    = jet_systematics + met_systematics
weight_systematics = ['PU36fbUp', 'PU36fbDown', 'TopPt', 'BTag_SF_b_Down', 'BTag_SF_b_Up', 'BTag_SF_l_Down', 'BTag_SF_l_Up', 'DilepTriggerBackupDown', 'DilepTriggerBackupUp', 'LeptonSFDown', 'LeptonSFUp']


def addSys( selectionString , sys = None ):
    if   sys in jet_systematics: 
        for var in ['nJetGood', 'nBTag', 'met_pt', 'metSig', 'dl_mt2ll', 'dl_mt2bb', 'dl_mt2blbl']:
            selectionString = selectionString.replace(var, var+'_'+sys)
        return selectionString
    elif sys in met_systematics: 
        for var in ['met_pt', 'metSig', 'dl_mt2ll', 'dl_mt2bb', 'dl_mt2blbl']:
            selectionString = selectionString.replace(var, var+'_'+sys)
        return selectionString
    else:  return selectionString

def weightMC( sys = None ):
    if sys is None:                 return "reweightLeptonSF*reweightDilepTriggerBackup*reweightPU27fb*reweightBTag_SF"
    elif 'PU' in sys:               return "reweightLeptonSF*reweightDilepTriggerBackup*reweight"+sys+"*reweightBTag_SF"
    elif 'BTag' in sys:             return "reweightLeptonSF*reweightDilepTriggerBackup*reweightPU27fb*reweight"+sys
    elif sys in weight_systematics: return "reweightLeptonSF*reweightDilepTriggerBackup*reweightPU27fb*reweightBTag_SF*reweight"+sys
    elif sys in jme_systematics :   return weightMC( sys = None )
    else:                           raise ValueError( "Systematic %s not known"%sys )


sys_pairs = [\
    ('JEC',         'JECUp', 'JECDown'),
    ('Unclustered', 'UnclusteredEnUp', 'UnclusteredEnDown'),
#    ('PU27fb',      'PU27fbUp', 'PU27fbDown'),
#    ('TopPt',       'TopPt', None),
##   ('JER',         'JERUp', 'JERDown'),
    ('BTag_b',      'BTag_SF_b_Down', 'BTag_SF_b_Up' ),
    ('BTag_l',      'BTag_SF_l_Down', 'BTag_SF_l_Up'),
#    ('trigger',     'DilepTriggerBackupDown', 'DilepTriggerBackupUp'),
#    ('leptonSF',    'LeptonSFDown', 'LeptonSFUp'),
]


def getResults( met_bin, mt2ll_bin, mt2blbl_bin ):
    print "met",met_bin,"mt2ll",mt2ll_bin, "mt2blbl", mt2blbl_bin
    selection = "&&".join(c[1] for c in cuts)

    met_low, met_high = met_bin
    mt2ll_low, mt2ll_high = mt2ll_bin
    mt2blbl_low, mt2blbl_high = mt2blbl_bin

    selection += "&&met_pt>"+str(met_low)
    if met_high>0: selection += "&&met_pt<"+str(met_high)
    selection += "&&dl_mt2ll>"+str(mt2ll_low)
    if mt2ll_high>0: selection += "&&dl_mt2ll<"+str(mt2ll_high)
    selection += "&&dl_mt2blbl>"+str(mt2blbl_low)
    if mt2blbl_high>0: selection += "&&dl_mt2blbl<"+str(mt2blbl_high)

    print "Central values for ", "met",met_bin,"mt2ll",mt2ll_bin, "mt2blbl", mt2blbl_bin
    data = sum( [         u_float(s.getYieldFromDraw( selectionString = selection )) for s in data_samples ] )
    mc   = sum( [ lumiFac*u_float(s.getYieldFromDraw( selectionString = selection, weightString = weightMC( sys = None) )) for s in mc_samples ] )

    rel_sys = {}
    for sys_name, sys_low, sys_high in sys_pairs:
        print "Systematic %s values for "%sys_name, "met",met_bin,"mt2ll",mt2ll_bin, "mt2blbl", mt2blbl_bin
        print addSys( selection, sys = sys_low), weightMC( sys = sys_low)
        print addSys( selection, sys = sys_high), weightMC( sys = sys_high)
        mc_low   = sum( [ lumiFac*u_float(s.getYieldFromDraw( selectionString = addSys( selection, sys = sys_low), weightString = weightMC( sys = sys_low) )) for s in mc_samples ] )
        mc_high  = sum( [ lumiFac*u_float(s.getYieldFromDraw( selectionString = addSys( selection, sys = sys_high), weightString = weightMC( sys = sys_high) )) for s in mc_samples ] )
        rel_sys[sys_name] = (mc_high - mc_low) / mc if mc.val > 0 else u_float(0.,0.)
        
    return {'data':data, 'mc':mc, 'rel_sys':rel_sys}

def wrapper( job ):
    return getResults(*job)

met_bins        = [ (80,120) , (120, 160), (160,200), (80,200), (200,-1)]
mt2ll_bins      = [ (0,25) , (25, 50), (50, 75), (75, 100)]
mt2blbl_bins    = [ ( 0, 100), (100, 200), (200, -1 )]

filename = "/afs/hephy.at/work/r/rschoefbeck/StopsDilepton/ttjets/correlation_yields_%i.pkl"% maxN
if os.path.exists(filename):
    results = pickle.load(file(filename))
    print "Loaded %s" % filename 
else:
#if True:
    jobs = []
    for met_bin in met_bins:
        for mt2ll_bin in mt2ll_bins:
            for mt2blbl_bin in mt2blbl_bins:
                jobs.append( (met_bin, mt2ll_bin, mt2blbl_bin) )

    # Read normalization
#    if False:
    if True:
        from multiprocessing import Pool
        pool = Pool(processes=20)
        results = pool.map( wrapper, jobs)
        pool.close()
        pool.join()
    else:
        results = map(wrapper, jobs)

    results = {jobs[i_job]:results[i_job] for i_job in range(len(jobs))}
         
    pickle.dump(results, file( filename ,"w") )
    print "Written %s" % filename 
#var = 0
#dof = 0

def t_str( b, v ):
    if b[0]>0: 
        res = "%i \\leq %s"%( b[0], v ) 
    else:
        res = v
    if b[1]>0:
        res+="< %i"%b[1]
    return res

corrTexFile = "corrTab.tex" 
with open(corrTexFile, "w") as corrTable:
    corrTable.write("\\begin{tabular}{r|r|"+"|lclcl"*len(mt2blbl_bins)+"} \n")
    corrTable.write("  \\ETmiss & $M_{T2}(ll)$ & "+ "&".join( "\\multicolumn{5}{c}{$%s$}" % t_str(mt2blbl_bin, "M_{T2}(blbl)") for mt2blbl_bin in mt2blbl_bins )+" \\\\ \n")
    corrTable.write("  &  & "+ "&".join( " ratio && stat. && sys." for mt2blbl_bin in mt2blbl_bins )+" \\\\ \n")
    corrTable.write("  \\hline \n")

    for met_bin in met_bins:
        chi2 = 0
        ndof = 0
        for mt2ll_bin in mt2ll_bins:
            y_mc_tot    = sum( results[(met_bin, mt2ll_bin, mt2blbl_bin)]['mc'] for mt2blbl_bin in mt2blbl_bins) 
            y_data_tot    = sum( results[(met_bin, mt2ll_bin, mt2blbl_bin)]['data'] for mt2blbl_bin in mt2blbl_bins) 
            scale = (y_data_tot / y_mc_tot).val
            ndof -= 1 # scale reduces NDOF
            s_string =  "$%s$ & $%s$" % ( t_str(met_bin, "\\ETmiss"), t_str(mt2ll_bin, "M_{T2}(ll)") )

            for mt2blbl_bin in mt2blbl_bins:
                y_mc   = results[(met_bin, mt2ll_bin, mt2blbl_bin)]['mc'] 
                y_data   = results[(met_bin, mt2ll_bin, mt2blbl_bin)]['data'] 
                tot_rel_sys = sqrt(sum([s.val**2 for s in results[(met_bin, mt2ll_bin, mt2blbl_bin)]['rel_sys'].values()]))
                if y_data>0:
                    try:
                        r = y_data/(y_mc*scale)
                        d_chi2 = ( (r.val-1)/sqrt( r.sigma**2 + tot_rel_sys**2) )**2
                    except ZeroDivisionError:
                        r = 0
                        d_chi2 = 0 
                chi2 += d_chi2
                ndof += 1
                s_string += " & %3.2f & $\\pm$ & %3.2f &$\\pm$& %3.2f" % ( r.val, r.sigma, r.val*tot_rel_sys)

            corrTable.write(s_string+"\\\\\n")

        corrTable.write("  \\hline \n")
        print met_bin, chi2/ndof

    corrTable.write("\\end{tabular} \n")
    corrTable.write("\\caption{ Data/MC ratios} \n")


#            r= (sum(y_data.values())/sum(y_mc.values()))
#            var+=r*r
#            dof += 1

