# standard importd
import ROOT
import os
import pickle

cuts=[
  ("no cuts",  "no cuts",       "(1)"),
  ("==2 relIso03<0.12 leptons,l1 pt > 30, l2pt > 20",  "$n_{\\textrm{lep.}==2}$",       "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12&&l1_pt>30&&l2_pt>20"),
  ("opposite sign",              "opposite charge",       "isOS==1"),
  ("looseLeptonVeto",            "loose lepton veto",       "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2"),
  ("m(ll)>20",                   "$M(ll)>20$ GeV",       "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF",     "$|M(ll)-M_{Z}| > 15$ GeV (SF)",       "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)>=15 || isEMu==1 )"),
  (">=2 jets",                   "$n_{jet}>=2$",       "nJetGood>=2"),
  (">=1 b-tags (CSVv2)",         "$n_{b-tag}>=1$",       "nBTag>=1"),
  ("miniIso <=0.2",                         "miniIso <= 0.2",                           "l1_miniRelIso <= 0.2 && l2_miniRelIso <= 0.2"),
  ("MET_significance >= 12",     "$E_{T}^{miss}$ significance",       "MET_significance>=12"),
 # ("MET>80",                     "$\\ETmiss>80$ GeV",       "met_pt>80"),
 # ("MET/sqrt(HT)>5",             "$\\ETmiss/\\sqrt{H_{T}}>5$",       "met_pt/sqrt(ht)>5."),
  ("dPhiJetMET",                 "$\\phi(\\ETmiss, jets)$ veto",       "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  ("badEEJetVeto",             "badEEJetVeto", ""),
  #("HEMJetVetoWide",             "HEMJetVetoWide", ""),
  ("MT2(ll) > 140",              "$M_{T2}(ll)>140$ GeV",       "dl_mt2ll>140"),
    ]

#adding pickl files for 3 years

samples  = ['Data', 'TTZ','TTXNoZ','multiBoson', 'DY_HT_LO', 'Top_pow']
#path = "/afs/hephy.at/work/p/phussain/CMS/CMSSW_10_2_9/src/StopsDilepton/plots/plotsPriya/cutflow"
path = "/afs/hephy.at/user/p/phussain/www/stopsDilepton/analysisPlots/cutFlow/v03/"
if not os.path.exists( path ):
    os.makedirs(path)
cutFlowFile = os.path.join( path, 'cutFlow_combined.tex' )
print path

# pkl files
file16= os.path.join(path, '2016/cutFlow_2016.pkl')
file17= os.path.join(path, '2017/cutFlow_2017.pkl')
file18= os.path.join(path, '2018/cutFlow_2018.pkl')


value={}
values16 = pickle.load(file(file16, "r"))
values17 = pickle.load(file(file17, "r"))
values18 = pickle.load(file(file18, "r"))
print values16
#print "  ".join([sample for sample in samples])
for i, c in enumerate(cuts): #have 11 cuts
    cut = c[0]
    value[i]={}
    if i ==11 : #(badeeJetVetocut)
      for j, s in enumerate(samples):
        value[i][j] = values16[i-1][j]+values17[i][j]+values18[i-1][j] 
  #  elif "HEMJetVetoWide" in cut:
  #    for s in samples:
  #      value[i][s] = values16[i-2][s]+values17[i-1][s]+values18[i-1][s] 
    elif i==12:
      for j,s in enumerate(samples):
        print "", values16[i-1][j], values17[i][j], values18[i-1][j]
        value[i][j] = values16[i-1][j]+values17[i][j]+values18[i-1][j] 
    else:
      for j, s in enumerate(samples):
        value[i][j] = values16[i][j]+values17[i][j]+values18[i][j] 

#    print "  ".join([cut] + [str(value[i][sample]) for sample in samples])

# writing the tex file for combined values

with open(cutFlowFile, "w") as cf:
    cf.write("\\begin{tabular}{r|"+"|l"*len(samples)+"} \n")
    cf.write( 30*" "+"& "+ " & ".join([ "%13s"%s for s in samples ] )+"\\\\\\hline\n" )
    print 30*" "+ "".join([ "%13s"%s for s in samples ] )

    for i, c in enumerate(cuts):
        r=[]
        for t,s in enumerate(samples):
            #selection = "&&".join(c[2] for c in cuts[:i+1])
            #selection = "&&".join(c[2] for c in cuts)
            #if selection=="":selection="(1)"

            y = value[i][t]
            r.append(y)
        cf.write("%30s"%c[1]+ "& "+" & ".join([ " %12.1f"%r[j] for j in range(len(r))] )+"\\\\\n")
        print "%30s"%c[1]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )

    cf.write("\\end{tabular} \n")

