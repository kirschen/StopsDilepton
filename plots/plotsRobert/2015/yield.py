import ROOT
c = ROOT.TChain("Events")
c.Add('/data/rschoefbeck/cmgTuples/postProcessed_Spring15_pass2/dilep/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_*.root')

preselection = "dl_mass>20&&(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1&&dl_mass>20&&met_pt>80&&met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>5.)"

c.Draw("1>>htmp",'('+preselection+')*weight','goff')
print "nEvents %i weighted yield %f"%(c.GetEntries(preselection), ROOT.htmp.Integral())
