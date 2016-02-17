import ROOT
#Make TDR style plots
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

## user so that the code runs for different people
from StopsDilepton.tools.user import *

## preselection with >= 2 jets and >=1 b-jet
preselectionHadronic = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1'

## let's require opposite-sign di-muons off the Z-peak. You can also remove this selection and select later in the loop.
## However, if you don't preselect, the event loop will be slow because you process all events.
preselection = "&&".join([preselectionHadronic, "isMuMu", "isOS", "abs(dl_mass-91.2)>15."])
print "Using cut %s"%preselection

## load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
#from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *

backgrounds = [TTJets_25ns, diBosons_25ns, singleTop_25ns, DY_50ns] ## The inclusive 25ns DY was missing -> I replace it with 50ns for now
signals = []
data = DoubleMuon_Run2015B
samples = backgrounds + signals + [data]
print "Samples I know of: %s"% ", ".join(s['name'] for s in samples)

lumiScaleFactor = data['lumi']/1000. #The 'weight' in the MC samples is for 1fb^-1, so we need to scale it according to the lumi in the data sample
print "Data amounts to %5.2f/pb, therefore I scale with %5.5f"%(data['lumi'],lumiScaleFactor)

## Here is an extremly simple implementation of getVarValue which just gets a number from a leaf in a TTree/TChain. I implement it, so that this script is mostly self-contained.
## If you ask for a branch that has Status "0", you'll get 0. This can be quite dangerous, so I'm careful when using SetBranchStatus (below).
def getVarValue(chain, var, n=0):
    return chain.GetLeaf(var).GetValue(n)

##Let's load the TChains. I use 'getChain' below, but I commented it and now do it by hand
##Get the TChains for each sample. I
#for s in backgrounds+signals+[data]:
#  s['chain'] = getChain(s,histname="")
for s in samples:
    s['chain'] = ROOT.TChain("Events")
    for b in s['bins']:
        filenames = s['dir']+'/'+b+'/*.root'
        print "Sample %s: Adding filenames %s"%(s['name'], filenames)
        s['chain'].Add(filenames)
## Let's mute everything and turn back on what we need. You can remove it for flexibility but that will make it a little slower.
    s['chain'].SetBranchStatus("*",0)
    for b in ["weight", "nJet", "Jet_*", "met*", "dl_*", "is*"]:
        s['chain'].SetBranchStatus(b,1)

    print "Have a total of %i events for sample %s"%(s['chain'].GetEntries(), s['name'])
    print
## Here I define the plots. Each plot is a dictionary with the relevant information. There's hundreds ways of doing this book-keeping.
## It can easily be expanded (e.g. you can give it a y-axis title, or a boolean whether it's a log-plot etc.)
plots = [\
    {'title':'p_T(ll) (GeV)', 'name':'dl_pt', 'leaf':'dl_pt', 'binning': [26,0,520], 'histo':{}},
]
## Each plot has a dictionary 'histo'. This is where the ROOT.TH1F will go. We need one per sample. Let's define them so that we can fill them in the loop:
for s in samples:
    for p in plots:
        p['histo'][s['name']] = ROOT.TH1F("histo_"+s["name"], "histo_"+s["name"], *(p['binning']))  #Here we call the actual ROOT::TH1F constructor

#Let's do the event loop now:
for s in samples:
    chain = s["chain"]  #For convinience
    print "Looping over %s" % s["name"]
    ## Now we get the eList with all the events that satisfy the preselection. I have 'getEList' for that. I comment it and do it by hand.
    #eList = getEList(chain, preselection)

    ## TH1::Draw creates an eList if you omit the variable that you draw. It's created in the ROOT namespace as ROOT.eListTMP. I retrieve it from the gDirectory because I need to delete it later.
    chain.Draw('>>eList', preselection)
    eList = ROOT.gDirectory.Get("eList")

    ## Now we loop over the events which pass the cut (= are in the eList)
    nEvents = eList.GetN()
    print "Found %i events in %s after preselection %s" % (eList.GetN(),s["name"],preselection)
    for ev in range(nEvents):
        if ev%10000==0:print "At %i/%i"%(ev,nEvents)
        #Note the nested GetEntry. Here is where the eList (=preselection) is applied: I ask the eList for the element in position 'ev'. This gives me the event number in the Chain I want to 'GetEntry' to.
        chain.GetEntry(eList.GetEntry(ev))

        # mt2Calc.reset() # omitted for now

        ## Calculate the weight. It's 1 for data
        weight = lumiScaleFactor*getVarValue(chain, "weight") if not (s.has_key('isData') and  s['isData']) else 1

        for p in plots:
            ## Now let's fill the histos. Each 'plot' has TH1F per sample (accessed with the sample name) -> p['histo'][s['name']]
            ## I use getVarValue above and the 'leaf' member of the plot to get the acutal number of the variable.
            p['histo'][s['name']].Fill(getVarValue(chain, p['leaf']), weight)

    del eList #Don't forget, otherwise it will be deleted in python (it goes out of scope) but survive with 'NoneType' in the ROOT namespace.

# #Some coloring -> I'm too lazy to make a better implementation now
TTJets_25ns["color"] = 7
WJetsHTToLNu_25ns["color"] = 42
diBosons_25ns["color"] = ROOT.kMagenta
singleTop_25ns["color"] = 40
DY_25ns["color"] = 8
DY_50ns["color"] = 8

for p in plots:
    #Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    bkg_stack = ROOT.THStack("bkgs","bkgs")
    for b in reversed(backgrounds):
        p['histo'][b['name']].SetFillColor(b["color"])
        p['histo'][b['name']].SetMarkerColor(b["color"])
        p['histo'][b['name']].SetMarkerSize(0)
#    plots[pk]['histo'][b['name']].GetYaxis().SetRangeUser(10**-2.5, 2*plots[pk]['histo'][b['name']].GetMaximum())
        bkg_stack.Add(p['histo'][b['name']],"h")
        l.AddEntry(p['histo'][b['name']], b["name"])
    p['histo'][data['name']].SetMarkerStyle(20)
    #Plot!
    c1 = ROOT.TCanvas()
    bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
    bkg_stack.SetMinimum(10**-1.5)
    bkg_stack.Draw('e')
    bkg_stack.GetXaxis().SetTitle(p['title'])
    binning = p['binning']
    bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
    c1.SetLogy()
    p['histo'][data['name']].Draw('esame')
#  signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
#  signalPlot = plots[pk]['histo'][signal].Clone()
#  signalPlot.Scale(100)
#  signalPlot.Draw("same")
#  l.AddEntry(signalPlot, signal+" x 100")
    l.Draw()
    c1.Print(plotDir+"/"+p["name"]+".png")
