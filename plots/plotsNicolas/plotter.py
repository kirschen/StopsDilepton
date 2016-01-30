import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain,getWeight,getVarValue,getEList
from StopsDilepton.tools.localInfo import *
from datetime import datetime

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'


#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2

#######################################################
#            Flavour Selection                        #
#######################################################

def flavourSelector(boo, preselection):
    if (boo == 'EE'):
        preselection += '&&isEE==1'
    if (boo == 'MuMu'):
        preselection += '&&isMuMu==1'
    if (boo == 'OF'):
        preselection += '&&isEMu==1'
    if (boo == 'SF'):
        preselection += '&&(isEE==1 || isMuMu==1)'
    if (boo == 'All'):
        preselection += ''
    return preselection

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
preselection = 'met_pt>40'
lumi = 10
reduceStat = 1000 #recude the statistics, i.e. 10 is ten times less samples to look at
scaleSignal = 1
preselection = flavourSelector('EE', preselection) #(EE, MuMu, OF, SF, All)
print preselection

#######################################################
#                 Load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
backgrounds = [diBosons_25ns,WJetsToLNu_25ns,TTX_25ns,singleTop_25ns, QCDMu_25ns, DY_25ns, TTLep_25ns]
#backgrounds = []
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = [SMS_T2tt_2J_mStop425_mLSP325]
#data = [DoubleEG_25ns,DoubleMuon_25ns,MuonEG_25ns]
#data = []



#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
    s['chain'] = getChain(s,histname="") # A TChain is basically a TTree that contains a lot of data


plots = {\
    'met': {'name':'MET', 'xtitle': "E_{T}^{miss}", 'unit': "GeV" ,'binning': [25, 0, 800] , 'variable': 'met_pt' , 'histo':{}}
    }


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
    for plot in plots:
        plots[plot]['histo'][s['name']] = ROOT.TH1F(plot + "_" + s["name"], plot + "_" + s["name"], *(plots[plot]['binning']))


#######################################################
#            Start filling in the histograms          #
#######################################################
for i,s in enumerate(backgrounds+signals): #Enumerate returns a couple (index of key in array, dictionary)
    chain = s["chain"]
    print "Looping over %s" % s["name"]
    eList = getEList(chain, preselection) #Returns a list with events that pass the selection
    nEvents = eList.GetN()/reduceStat
    for ev in range(nEvents):
        chain.GetEntry(eList.GetEntry(ev))
        m_ll = getVarValue(chain, "dl_mass")
        ZVetoCut = abs(91.2-m_ll) > 15
        isSF = True if (getVarValue(chain, "isEE") == 1 or getVarValue(chain, "isMuMu") == 1) else False
        if (not isSF):
            ZVetoCut = True
        weight = reduceStat*getVarValue(chain, "weight")*lumi
        if (ZVetoCut):
            for plot in plots.keys():
                variable = getVarValue(chain, plots[plot]['variable'])
                plots[plot]['histo'][s["name"]].Fill(variable, weight)
    print (plots[plot]['histo'][s['name']].GetEntries())

    print("I finished a background: " + s["name"])
processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring
TTLep_25ns["color"]=7
DY_25ns["color"]=8
DYHT_25ns["color"]=9
QCDMu_25ns["color"]=46
singleTop_25ns["color"]=40
diBosons_25ns["color"]=ROOT.kOrange
TTX_25ns['color']=ROOT.kPink
WJetsToLNu_25ns['color']=ROOT.kRed-10
SMS_T2tt_2J_mStop425_mLSP325['color']=ROOT.kRed

TTLep_25ns['legname']= 't#bar{t} + Jets'
DY_25ns['legname']= 'Drell-Yan'
QCDMu_25ns['legname']= 'QCD'
singleTop_25ns['legname']= 'Single t'
diBosons_25ns['legname']= 'WW + WZ + ZZ'
TTX_25ns['legname']= 'TTX'
WJetsToLNu_25ns['legname']= 'W + Jets'
SMS_T2tt_2J_mStop425_mLSP325['legname']= 'T2tt (425, 325)' + ' X ' + str(scaleSignal) if (scaleSignal != 1) else 'T2tt (425, 325)'

legendtextsize = 0.032

#Create the bg-stack and set all the options:

for plot in plots.keys():
    plots[plot]['stack'] = ROOT.THStack()
    plots[plot]['legend'] = ROOT.TLegend(0.6,0.6,0.89,0.89)
    leg = plots[plot]['legend']
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    for s in backgrounds:
        bghist = plots[plot]['histo'][s['name']]

        bghist.SetFillColor(s['color'])
        bghist.SetLineColor(ROOT.kBlack)
        bghist.SetLineWidth(2)

        leg.AddEntry(bghist, s['legname'], "F")

        plots[plot]['stack'].Add(bghist)
    for s in signals:
        sighist = plots[plot]['histo'][s['name']]
        sighist.SetLineColor(s['color'])
        sighist.SetLineWidth(2)

        leg.AddEntry(sighist, s['legname'], "L")

#Plot!

for plot in plots.keys():
    c1 = ROOT.TCanvas()
    c1.SetLogy()
    bgstack = plots[plot]['stack']
    bgstack.Draw("HIST")
    n_bg_entries = (bgstack.GetStack().Last()).GetEntries()
    if (n_bg_entries != 0):
        bossHist = bgstack
    for i,s in enumerate(signals):
        sighist = plots[plot]['histo'][s['name']]
        sighist.Scale(scaleSignal)
        if (i == 0 and n_bg_entries == 0):
            sighist.Draw("HIST")
            bossHist = sighist
        else:
            sighist.Draw("HIST SAME")


    bossHist.GetXaxis().SetTitle(plots[plot]['xtitle'])
    binning = plots[plot]['binning']
    ytitle = "# Events / " + str((binning[2]- binning[1])/binning[0]) + " " + plots[plot]['unit']
    bossHist.GetYaxis().SetTitle(ytitle)

    bossHist.SetMaximum(2*bossHist.GetMaximum())
    bossHist.SetMinimum(10**-1.5)

#  for s in backgrounds+signals:
#    integral = plots[plot]['histo']

    plots[plot]['legend'].Draw("SAME")

    ROOT.gStyle.SetOptStat(0)
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Update()
    c1.Print("test.png")
    c1.Print("test.png")



# if makedraw1D:
#   for plot in plots.keys():
#     for s in backgrounds+signals:
#       integral = plots[plot]['histo'][s['name']].Integral()
#       plots[plot]['histo'][s['name']].Scale(1./integral)

#       #Make a stack for backgrounds
#     l=ROOT.TLegend(0.6,0.8,1.0,1.0)
#     l.SetFillColor(0)
#     l.SetShadowColor(ROOT.kWhite)
#     l.SetBorderSize(1)
#     l.SetTextSize(legendtextsize)

#     #Plot!
#     c1 = ROOT.TCanvas()
#     for i,b in enumerate(backgrounds+signals):
#       plots[plot]['histo'][b["name"]].SetLineColor(b["color"])
#       plots[plot]['histo'][b["name"]].SetLineWidth(3)
#       plots[plot]['histo'][b["name"]].SetMarkerSize(0)
#       plots[plot]['histo'][b["name"]].Draw("same")
#       l.AddEntry(plots[plot]['histo'][b["name"]],b['name'])
#       if i == 0:
#         plots[plot]['histo'][b["name"]].GetXaxis().SetTitle(plots[plot]['title'])
#         plots[plot]['histo'][b["name"]].GetYaxis().SetTitle("Events (A.U.)")
#         if plot!="met": plots[plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.001,2)
#         else:           plots[plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.00001,2)
#     c1.SetLogy()
#     l.Draw()
#     c1.Print("./"+plots[plot]['name']+".png")

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
