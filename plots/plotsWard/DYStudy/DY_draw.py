import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain, getVarValue, getYieldFromChain
from StopsDilepton.tools.localInfo import *
from datetime import datetime

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'


#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makeTexFile = True
mt2llcutscaling = False
noscaling = False

btagcoeff          = 0.89
metcut             = 80.
metsignifcut       = 5.
dphicut            = 0.25
mllcut             = 20
ngoodleptons       = 2
#luminosity         = 1549.
flavour            = "MuMu"

presel_met         = 'met_pt>'+str(metcut)
presel_njet        = 'nGoodJets>=2'
presel_metsig      = 'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>'+str(metsignifcut)
presel_mll         = 'dl_mass>'+str(mllcut)
presel_OS          = 'isOS'
presel_dPhi        = 'cos(met_phi-Jet_phi[0])<cos('+str(dphicut)+')&&cos(met_phi-Jet_phi[1])<cos('+str(dphicut)+')'


if flavour=="MuMu": 
  presel_flavour     = 'isMuMu==1&&nGoodElectrons==0&&nGoodMuons==2&&HLT_mumuIso'
  data = [DoubleMuon_Run2015D]
elif flavour=="EE": 
  presel_flavour     = 'isEE==1&&nGoodElectrons==2&&nGoodMuons==0&&HLT_ee_DZ'
  data = [DoubleEG_Run2015D]

luminosity = data[0]["lumi"]

datacut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"

preselection = presel_njet+'&&'+presel_OS+'&&'+presel_mll+'&&'+presel_dPhi+'&&'+presel_met+'&&'+presel_metsig+'&&'+presel_flavour

backgrounds = [DY_HT_LO,TTJets,WJetsToLNu,singleTop,QCD_Mu5,TTX,diBoson]
#backgrounds = [DY_HT_LO,TTJets]

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+data:
  s['chain'] = getChain(s,histname="")

mt2llbinning = "(15,0,300)"
mllbinning = "(50,0,150)"

plots = {\
  'dl_mt2ll':{\
    '_onZ_0b': {'title':'MT2ll (GeV)', 'name':'MT2ll_onZ_b==0b',"legend":"(onZ,0 b-tag)", 'binning': mt2llbinning, 'histo':{}},
    '_offZ_0b': {'title':'MT2ll (GeV)', 'name':'MT2ll_offZ_b==0b',"legend":"(offZ,0 b-tag)",'binning': mt2llbinning, 'histo':{}},
    '_onZ_1mb': {'title':'MT2ll (GeV)', 'name':'MT2ll_onZ_b>=1', "legend":"(onZ,>0 b-tag)", 'binning': mt2llbinning, 'histo':{}},
    '_offZ_1mb': {'title':'MT2ll (GeV)', 'name':'MT2ll_offZ_b>=1', "legend":"(offZ,>0 b-tag)", 'binning': mt2llbinning, 'histo':{}},
    },
  'dl_mass':{\
    '_onZ_0b': {'title':'m_{ll} (GeV)', 'name':'Mll_onZ_b==0b', "legend":"(onZ,0 b-tag)",'binning': mllbinning, 'histo':{}},
    '_offZ_0b': {'title':'m_{ll} (GeV)', 'name':'Mll_offZ_b==0b', "legend":"(offZ,0 b-tag)", 'binning': mllbinning, 'histo':{}},
    '_onZ_1mb': {'title':'m_{ll} (GeV)', 'name':'Mll_onZ_b>=1', "legend":"(onZ,>0 b-tag)", 'binning': mllbinning, 'histo':{}},
    '_offZ_1mb': {'title':'m_{ll} (GeV)', 'name':'Mll_offZ_b>=1', "legend":"(offZ,>0 b-tag)", 'binning': mllbinning, 'histo':{}},
    },
  }


#######################################################
#            Start filling in the histograms          #
#######################################################
weight = str(luminosity/1000.)+'*weightPU'+'*reweightTopPt'

datayield_onZ_0b = getYieldFromChain(getChain(data[0],histname=""), cutString = "&&".join([preselection, datacut,'abs(dl_mass-91.2)<=15&&nBTags==0']), weight="1.") 
bkgyield_onZ_0b  = 0. 
for s in backgrounds:
  bkgyield_onZ_0b+= getYieldFromChain(getChain(s,histname=""), "&&".join([preselection,'abs(dl_mass-91.2)<=15&&nBTags==0']), weight=weight)

datayield_offZ_0b = getYieldFromChain(getChain(data[0],histname=""), cutString = "&&".join([preselection, datacut,'abs(dl_mass-91.2)>15&&nBTags==0']), weight="1.") 
bkgyield_offZ_0b  = 0. 
for s in backgrounds:
  bkgyield_offZ_0b+= getYieldFromChain(getChain(s,histname=""), "&&".join([preselection,'abs(dl_mass-91.2)>15&&nBTags==0']), weight=weight)

datayield_onZ_1mb = getYieldFromChain(getChain(data[0],histname=""), cutString = "&&".join([preselection, datacut,'abs(dl_mass-91.2)<=15&&nBTags>=1']), weight="1.") 
bkgyield_onZ_1mb  = 0. 
for s in backgrounds:
  bkgyield_onZ_1mb+= getYieldFromChain(getChain(s,histname=""), "&&".join([preselection,'abs(dl_mass-91.2)<=15&&nBTags>=1']), weight=weight)

datayield_offZ_1mb = getYieldFromChain(getChain(data[0],histname=""), cutString = "&&".join([preselection, datacut,'abs(dl_mass-91.2)>15&&nBTags>=1']), weight="1.") 
bkgyield_offZ_1mb  = 0. 
for s in backgrounds:
  bkgyield_offZ_1mb+= getYieldFromChain(getChain(s,histname=""), "&&".join([preselection,'abs(dl_mass-91.2)>15&&nBTags>=1']), weight=weight)
  

scaleFac_onZ_0b   = datayield_onZ_0b/bkgyield_onZ_0b
scaleFac_offZ_0b  = datayield_offZ_0b/bkgyield_offZ_0b
scaleFac_onZ_1mb  = datayield_onZ_1mb/bkgyield_onZ_1mb
scaleFac_offZ_1mb = datayield_offZ_1mb/bkgyield_offZ_1mb

print "scaleFac onZ,0b is ", scaleFac_onZ_0b, datayield_onZ_0b, bkgyield_onZ_0b
print "scaleFac offZ,0b is ", scaleFac_offZ_0b, datayield_offZ_0b, bkgyield_offZ_0b
print "scaleFac onZ,1mb is ", scaleFac_onZ_1mb, datayield_onZ_1mb, bkgyield_onZ_1mb
print "scaleFac offZ,1mb is ", scaleFac_offZ_1mb, datayield_offZ_1mb, bkgyield_offZ_1mb
  

for s in backgrounds+data:
  chain = s["chain"]
  for plot in plots.keys():

    weight = weight if s in backgrounds else "1."

    if s in data: preselection+="&&"+datacut
    chain.Draw(plot+">>"+plot+"_onZ_0b"+s["name"]+plots[plot]['_onZ_0b']['binning'],'('+weight+')*('+preselection+'&&abs(dl_mass-91.2)<=15&&nBTags==0)')
    plots[plot]['_onZ_0b']['histo'][s["name"]] = ROOT.gDirectory.Get(plot+"_onZ_0b"+s["name"])

    chain.Draw(plot+">>"+plot+"_offZ_0b"+s["name"]+plots[plot]['_offZ_0b']['binning'],'('+weight+')*('+preselection+'&&abs(dl_mass-91.2)>15&&nBTags==0)')
    plots[plot]['_offZ_0b']['histo'][s["name"]] = ROOT.gDirectory.Get(plot+"_offZ_0b"+s["name"])

    chain.Draw(plot+">>"+plot+"_onZ_1mb"+s["name"]+plots[plot]['_onZ_1mb']['binning'],'('+weight+')*('+preselection+'&&abs(dl_mass-91.2)<=15&&nBTags>=1)')
    plots[plot]['_onZ_1mb']['histo'][s["name"]] = ROOT.gDirectory.Get(plot+"_onZ_1mb"+s["name"])
 
    chain.Draw(plot+">>"+plot+"_offZ_1mb"+s["name"]+plots[plot]['_offZ_1mb']['binning'],'('+weight+')*('+preselection+'&&abs(dl_mass-91.2)>15&&nBTags>=1)')
    plots[plot]['_offZ_1mb']['histo'][s["name"]] = ROOT.gDirectory.Get(plot+"_offZ_1mb"+s["name"])
    

    for selection in plots[plot].keys():
      #plots[plot][selection]['histo'][s['name']].Sumw2()

      nbinsx        = plots[plot][selection]['histo'][s['name']].GetNbinsX()
      lastbin       = plots[plot][selection]['histo'][s['name']].GetBinContent(nbinsx)
      error         = plots[plot][selection]['histo'][s['name']].GetBinError(nbinsx)
      overflowbin   = plots[plot][selection]['histo'][s['name']].GetBinContent(nbinsx+1)
      overflowerror = plots[plot][selection]['histo'][s['name']].GetBinError(nbinsx+1)
      plots[plot][selection]['histo'][s['name']].SetBinContent(nbinsx,lastbin+overflowbin)
      plots[plot][selection]['histo'][s['name']].SetBinError(nbinsx,sqrt(error**2+overflowerror**2))
      plots[plot][selection]['histo'][s['name']].SetBinContent(nbinsx+1,0.)
      plots[plot][selection]['histo'][s['name']].SetBinError(nbinsx+1,0.)

processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################

legendtextsize = 0.032

ROOT.gStyle.SetErrorX(0.5)

lumitagpos = [0.4,0.95,0.6,1.0]
channeltagpos = [0.45,0.8,0.6,0.85]
legendpos = [0.6,0.65,1.0,0.95]
scalepos = [0.8,0.95,1.0,1.0]

if makedraw1D:
  for plot in plots.keys():
    for selection in plots[plot].keys():
    #Make a stack for backgrounds
      l=ROOT.TLegend(legendpos[0],legendpos[1],legendpos[2],legendpos[3])
      l.SetFillColor(0)
      l.SetShadowColor(ROOT.kWhite)
      l.SetBorderSize(1)
      l.SetTextSize(legendtextsize)

    #Plot!
      c1 = ROOT.TCanvas()
      c1.SetLogy()
      c1.SetRightMargin(0)
      c1.SetTopMargin(0.05)

      bkg_stack = ROOT.THStack("bkgs","bkgs")
      
      for b in sorted(backgrounds,key=lambda sort:plots[plot][selection]['histo'][sort['name']].Integral()):
        #plots[plot][selection]['histo'][b["name"]].SetLineColor(b['color'])
        if selection == "_onZ_0b": plots[plot][selection]['histo'][b["name"]].Scale(scaleFac_onZ_0b)
        elif selection == "_offZ_0b": plots[plot][selection]['histo'][b["name"]].Scale(scaleFac_offZ_0b)
        elif selection == "_onZ_1mb": plots[plot][selection]['histo'][b["name"]].Scale(scaleFac_onZ_1mb)
        elif selection == "_offZ_1mb": plots[plot][selection]['histo'][b["name"]].Scale(scaleFac_offZ_1mb)
        plots[plot][selection]['histo'][b["name"]].SetFillColor(b["color"])
        plots[plot][selection]['histo'][b["name"]].SetMarkerColor(b["color"])
        plots[plot][selection]['histo'][b["name"]].SetMarkerSize(0)      
        bkg_stack.Add(plots[plot][selection]['histo'][b["name"]],"h")
        l.AddEntry(plots[plot][selection]['histo'][b["name"]], b["texName"],"f")
      
      plots[plot][selection]['histo'][data[0]["name"]].SetMarkerColor(ROOT.kBlack)
      
      bkg_stack.SetMaximum(1000*bkg_stack.GetMaximum())
      bkg_stack.SetMinimum(0.01)
      bkg_stack.Draw()
    
      bkg_stack.GetXaxis().SetTitle(plots[plot][selection]['title'])
      bkg_stack.GetYaxis().SetTitle("Events (A.U.)")
      plots[plot][selection]['histo'][data[0]["name"]].Draw("pesame")
      
      channeltag = ROOT.TPaveText(channeltagpos[0],channeltagpos[1],channeltagpos[2],channeltagpos[3],"NDC")
      lumitag = ROOT.TPaveText(lumitagpos[0],lumitagpos[1],lumitagpos[2],lumitagpos[3],"NDC")
      scaletag = ROOT.TPaveText(scalepos[0],scalepos[1],scalepos[2],scalepos[3],"NDC")
      channeltag.AddText(flavour)
      lumitag.AddText("lumi: "+str(luminosity)+' pb^{-1}')
      if selection == "_onZ_0b": scaletag.AddText("Scale Factor: " +str(round(scaleFac_onZ_0b,2)))
      elif selection == "_offZ_0b": scaletag.AddText("Scale Factor: " +str(round(scaleFac_offZ_0b,2)))
      elif selection == "_onZ_1mb": scaletag.AddText("Scale Factor: " +str(round(scaleFac_onZ_1mb,2)))
      elif selection == "_offZ_1mb": scaletag.AddText("Scale Factor: " +str(round(scaleFac_offZ_1mb,2)))
      channeltag.SetFillColor(ROOT.kWhite)
      channeltag.SetShadowColor(ROOT.kWhite)
      channeltag.SetBorderSize(0)
      lumitag.SetFillColor(ROOT.kWhite)
      lumitag.SetShadowColor(ROOT.kWhite)
      lumitag.SetBorderSize(0)
      scaletag.SetShadowColor(ROOT.kWhite)
      scaletag.SetFillColor(ROOT.kWhite)
      scaletag.SetBorderSize(0)
      channeltag.Draw()
      lumitag.Draw()
      scaletag.Draw()

      l.Draw()
      ROOT.gPad.RedrawAxis()
      path = plotDir+'/test/DYstudy/njet_2m_isOS'+'_ngoodlep_'+str(ngoodleptons)+'_dPhi_0.25_met_'+str(int(metcut))+'_metsig_'+str(int(metsignifcut))+'_mll_'+str(int(mllcut))+'/'
      if not os.path.exists(path): os.makedirs(path)
      c1.Print(path+flavour+selection+"_"+plot+".png")

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
