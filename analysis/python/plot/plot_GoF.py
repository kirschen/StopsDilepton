'''
Caclulate and plot the goodness-of-fit
'''

import shutil, os
import ROOT
from array import array
from StopsDilepton.tools.user import analysis_results, plot_directory
from StopsDilepton.tools.helpers import getObjFromFile

ROOT.gStyle.SetOptStat("")

#'aggregated/fitAll/cardFiles/T2tt/T2tt_800_100.txt'
#'aggregated/signalOnly/cardFiles/T2tt/T2tt_800_100.txt'
fname = analysis_results + '/COMBINED/fitAll/cardFiles/T2tt/observed/T2tt_800_100_shapeCard.txt'
releaseLocation = '.'


def calcGoF(fname=None, algorithm="saturated"):
    import uuid, os
    ustr          = str(uuid.uuid4())
    uniqueDirname = os.path.join(releaseLocation, ustr)
    print "Creating %s"%uniqueDirname
    os.makedirs(uniqueDirname)

    if fname is not None:  # Assume card is already written when fname is not none
      filename = os.path.abspath(fname)
    else:
      filename = fname if fname else os.path.join(uniqueDirname, ustr+".txt")
      self.writeToFile(filename)
    #covFilename = filename.replace('.txt', '_mlfit.root')
    #shapeFilename = filename.replace('.txt', '_shape.txt')
    
    assert os.path.exists(filename), "File not found: %s"%filename

    dataCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M GoodnessOfFit %s --algo=%s"%(filename,algorithm)
    toyCommand  = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M GoodnessOfFit %s --algo=%s -t 300"%(filename,algorithm)
    
    print dataCommand
    os.system(dataCommand)
    os.system(toyCommand)
    
    res = os.path.isfile(uniqueDirname+"/higgsCombineTest.GoodnessOfFit.mH120.root")
    if not res:
        print "[cardFileWrite] Did not succeed reeding result."
        return 0
    
    dataTree = getObjFromFile(uniqueDirname+"/higgsCombineTest.GoodnessOfFit.mH120.root","limit")
    dataTree.GetEntry(0)
    dataGoF  = dataTree.limit
    print dataGoF
    toyTree  = getObjFromFile(uniqueDirname+"/higgsCombineTest.GoodnessOfFit.mH120.123456.root","limit")
    
    toyHist = ROOT.TH1F("toyHist","expected (toys)", 100,int(1.2*dataGoF),int(0.8*dataGoF))
    dataHist = ROOT.TH1F("dataHist","observed", 100,int(1.2*dataGoF),int(0.8*dataGoF))
    dataHist.Fill(dataGoF,0.001)
    for i in range(toyTree.GetEntries()):
        toyTree.GetEntry(i)
        toyHist.Fill(toyTree.limit)
    toyHist.SetBinContent(100,toyHist.GetBinContent(100)+toyHist.GetBinContent(101))
    toyHist.Scale(1/toyHist.Integral())
    
    
    shutil.rmtree(uniqueDirname)
    return toyHist, dataHist

c = ROOT.TCanvas('c','c',700,700)

expected, observed = calcGoF(fname=fname, algorithm="saturated")

expected.GetXaxis().SetTitle("q_{GoF}")
expected.GetYaxis().SetTitle("a.u.")
expected.Draw("hist")
expected.SetLineWidth(2)
expected.SetMarkerSize(0)
observed.SetMarkerStyle(23)
observed.SetMarkerSize(2)
observed.SetLineWidth(0)
observed.SetMarkerColor(ROOT.kBlue)
observed.Draw("same")

p_value = expected.Integral(expected.GetXaxis().FindBin(observed.GetMean()),100)
print p_value

#0.16,0.5
leg = ROOT.TLegend(0.6,0.80,0.98,0.95)
leg.SetFillColor(ROOT.kWhite)
leg.SetShadowColor(ROOT.kWhite)
leg.SetBorderSize(1)
leg.SetTextSize(0.035)

dummy = ROOT.TH1F()
dummy.SetLineWidth(0)
dummy.SetMarkerSize(0)

leg.AddEntry(expected)
leg.AddEntry(observed)
leg.AddEntry(dummy,'p-value '+str(round(p_value,2)))
leg.Draw()

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.04)
latex1.SetTextAlign(11)

latex1.DrawLatex(0.16,0.96,'CMS #bf{#it{Preliminary}}')
latex1.DrawLatex(0.73,0.96,'#bf{137fb^{-1} (13TeV)}')

plot_dir = plot_directory + '/GoodnessOfFit_newCorr/'
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

outname = fname.split('.')[-2].split('/')[-1]
filetypes = ['.png','.pdf','.root']
for f in filetypes:
    c.Print(plot_dir+outname+f)


