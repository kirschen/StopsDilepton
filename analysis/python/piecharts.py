import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy, sys
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import *

from StopsDilepton.tools.texHelpers import latexmaker_2 
from StopsDilepton.tools.localInfo import *
from StopsDilepton.tools.helpers import getChain, getYieldFromChain, getVarValue

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *

backgrounds = [DY_HT_LO,TTJets_Lep,TTZ,singleTop, diBoson, triBoson, TTXNoZ, WJetsToLNu_HT, QCD_HT]
#backgrounds = [TTZ,DY_HT_LO]

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################

btagcoeff          = 0.89
metcut             = 80.
metsignifcut       = 5.
dphicut            = 0.25
mllcut             = 20
ngoodleptons       = 2
luminosity         = 2100.
#njetscut           = [">=2",'4m']
#nMedBjetscut       = [">=2",'2m']
#nLooseBjetscut     = [">=2",'2m']
flavour            = "MuMu"


presel_met         = 'met_pt>'+str(metcut)
#presel_njet        = 'nGoodJets'+njetscut[0]
#presel_nMedBjet    = 'nBTags'+nMedBjetscut[0]
presel_ngoodlep    = '((nGoodMuons+nGoodElectrons)=='+str(ngoodleptons)+')'
presel_mll         = 'dl_mass>'+str(mllcut)
presel_metsig      = 'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>'+str(metsignifcut)
presel_OS          = 'isOS'
presel_dPhi        = 'cos(met_phi-Jet_phi[0])<cos('+str(dphicut)+')&&cos(met_phi-Jet_phi[1])<cos('+str(dphicut)+')'

preselection = presel_met+'&&'+presel_ngoodlep+'&&'+presel_mll+'&&'+presel_OS+'&&'+presel_metsig+'&&'+presel_dPhi

datacut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds:
  s['chain'] = getChain(s,histname="")


#######################################################
#         Define piecharts you want to make           #
#######################################################
mt2llcuts = [0.,80.,100.,120.,140.,200.]
piechart = {}
for cut in mt2llcuts:
  piechart[str(cut)] = {\
    "EE":{\
      "(0,0)" :{},
      "(1,0)" :{},
      "(1,1)" :{},
      "(>=2,0)" :{},
      "(>=2,>=1)" :{},
    },
    "MuMu":{\
      "(0,0)" :{},
      "(1,0)" :{},
      "(1,1)" :{},
      "(>=2,0)" :{},
      "(>=2,>=1)" :{},
    },
    "EMu":{\
      "(0,0)" :{},
      "(1,0)" :{},
      "(1,1)" :{},
      "(>=2,0)" :{},
      "(>=2,>=1)" :{},
    }
}

#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds:
  for cut in piechart.keys():
    for flavor in piechart[cut].keys():
      for piece in piechart[cut][flavor].keys():
        piechart[cut][flavor][piece][s["name"]] = 0
  chain = s["chain"]

  print '\n', "Looping over %s" % s["name"]

  #for MC
  weight = str(luminosity/1000.)+'*weightPU'+'*reweightTopPt'
  

  for cut in piechart.keys():
    for flavor in piechart[cut].keys():
      if flavor == "EE":
        flavourcut = 'isEE==1&&nGoodElectrons==2&&nGoodMuons==0&&HLT_ee_DZ'
      elif flavor == "EMu":
        flavourcut = 'isEMu==1&&nGoodElectrons==1&&nGoodMuons==1&&HLT_mue'
      elif flavor == "MuMu":
        flavourcut = 'isMuMu==1&&nGoodElectrons==0&&nGoodMuons==2&&HLT_mumuIso'
        
      yield_ = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,flavourcut]),weight=weight)
      
      yield_0j_0bj = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,"nGoodJets==0","nBTags==0","dl_mt2ll>="+cut,flavourcut]),weight=weight)
      yield_1j_0bj = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,"nGoodJets==1","nBTags==0","dl_mt2ll>="+cut,flavourcut]),weight=weight)
      yield_1j_1bj = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,"nGoodJets==1","nBTags==1","dl_mt2ll>="+cut,flavourcut]),weight=weight)
      yield_2mj_0bj = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,"nGoodJets>=2","nBTags==0","dl_mt2ll>="+cut,flavourcut]),weight=weight)
      yield_2mj_1mbj = getYieldFromChain(getChain(s,histname=""), cutString = '&&'.join([preselection,"nGoodJets>=2","nBTags>=1","dl_mt2ll>="+cut,flavourcut]),weight=weight)

      piechart[cut][flavor]["(0,0)"][s["name"]] =     yield_0j_0bj
      piechart[cut][flavor]["(1,0)"][s["name"]] =     yield_1j_0bj
      piechart[cut][flavor]["(1,1)"][s["name"]] =     yield_1j_1bj
      piechart[cut][flavor]["(>=2,0)"][s["name"]] =   yield_2mj_0bj
      piechart[cut][flavor]["(>=2,>=1)"][s["name"]] = yield_2mj_1mbj

def makefigure(piechart,mt2llcut):


  diBoson["color"]       = "yellow"
  WJetsToLNu_HT["color"] = "lightsalmon"
  TTZ["color"]           = "deeppink"
  TTXNoZ["color"]        = "deeppink"
  singleTop["color"]     = "grey"
  QCD_HT["color"]         = "darkred"
  DY_HT_LO["color"]      = "yellowgreen"
  TTJets_Lep["color"]    = "cyan"
  triBoson["color"]      = "gold"


  piechart = piechart[str(mt2llcut)]

  fig1 = plt.figure(figsize=(11,11))
  gridx= len(piechart["EE"])+1
  gridy= 5  #jet multiplicity, SF and OF and add one for legend
  colors = [b["color"] for b in sorted(backgrounds)]
  for ikey,key in enumerate(piechart.keys()):
    plt.subplot(gridx,gridy,ikey+2)
    plt.text(0.5,0.5,key,fontsize=20)
    plt.axis("off")
    k = ikey+gridy+2
    for icolumn,column in enumerate(sorted(piechart[key].keys())):
      if ikey == 0:
        plt.subplot(gridx,gridy,k-1)
        plt.text(0.5,0.5,column,fontsize=15)
        plt.axis('off')
      bkgs = [b['name'] for b in sorted(backgrounds)]
      bkgrates = [piechart[key][column][b["name"]] for b in sorted(backgrounds)]
      if k%gridy==0: k+=1
      plt.subplot(gridx,gridy,k)
      if 0<sum(bkgrates)<1 : bkgrates = [i*(1./sum(bkgrates)) for i in bkgrates]
      patches, texts = plt.pie(bkgrates,colors=colors)
      plt.axis('equal')
      k+=gridy

  plt.subplot(gridx,gridy,1)
  plt.text(0.5,0.5,"mt2ll>"+str(mt2llcut), fontsize=13)
  plt.axis('off')
  plt.subplot(gridx,gridy,2*gridy)
  
  # yellow_patch       = mpatches.Patch(color="yellow",label=bkgs[0])
  # grey_patch         = mpatches.Patch(color='0.75',label=)
  # lightsalmoon_patch = mpatches.Patch(color='lightsalmon', label)
  # darkred_patch      = mpatches.Patch(color='darkred',label)
  # deeppink_patch     = mpatches.Patch(color='deeppink',label)
  # yellowgreen_patch  = mpatches.Patch(color='yellowgreen',label)
  # cyan_patch         = mpatches.Patch(color='cyan',label)


  #plt.legend([yellowgreen_patch,gold_patch,lightskyblue_patch,lightcoral_patch,mediumblue_patch,red_patch,magenta_patch],bkgs)
  plt.legend(patches,bkgs)
  plt.axis('off')
  plt.savefig('./piecharts/piecharts_mt2llcut_'+str(int(mt2llcut))+'.png')
  
for cut in mt2llcuts:
  makefigure(piechart,cut)
  latexmaker_2(piechart,cut,"EE")
  latexmaker_2(piechart,cut,"MuMu")
  latexmaker_2(piechart,cut,"EMu")
