# We calculate first SF, then EMu

import shutil, os
import ROOT
from array import array
from StopsDilepton.tools.user import combineReleaseLocation, analysis_results, plot_directory

#ROOT.gROOT.LoadMacro('../../../tools/scripts/tdrstyle.C')
#ROOT.setTDRStyle()
ROOT.gStyle.SetOptStat("")


fname = analysis_results + '/signalOnly/cardFiles/T2tt/T2tt_750_500.txt'
releaseLocation = combineReleaseLocation

def calcCovariance(fname=None, options=""):
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
    covFilename = filename.replace('.txt', '_mlfit.root')

    assert os.path.exists(filename), "File not found: %s"%filename
    combineCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combineCards.py %s -S > myshapecard.txt "%fname
    #set workspace
    workspaceCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;text2workspace.py --X-allow-no-signal --X-allow-no-background myshapecard.txt"
    #workspaceCommand = "text2workspace.py --channel-masks --X-allow-no-signal --X-allow-no-background myshapecard.txt"
    #Run fit
    fitCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 2000 --saveOverall --preFitValue 0  myshapecard.root"
    
    print combineCommand
    os.system(combineCommand)
    os.system(workspaceCommand)
    os.system(fitCommand)

    tempResFile = uniqueDirname+"/mlfit.root"
    res = os.path.isfile(tempResFile)
    if res: shutil.copyfile(tempResFile, covFilename)
    else: print "[cardFileWrite] Did not succeed reeding result."

    shutil.rmtree(uniqueDirname)
    return res

import re
def natural_sort(list, key=lambda s:s):
    """
    Sort the list into natural alphanumeric order.
    http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
    """
    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text 
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]
    sort_key = get_alphanum_key_func(key)

    lc = sorted(list, key=sort_key)
    return lc



NRGBs = 5
NCont = 255
stops = array("d",[0.00, 0.34, 0.61, 0.84, 1.00])
red= array("d",[0.50, 0.50, 1.00, 1.00, 1.00])
green = array("d",[ 0.50, 1.00, 1.00, 0.60, 0.50])
blue = array("d",[1.00, 1.00, 0.50, 0.40, 0.50])
ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
ROOT.gStyle.SetNumberContours(NCont)

if not os.path.isfile(fname.replace(".txt","_mlfit.root")):
    calcCovariance(fname=fname, options="")

f1 = ROOT.TFile(fname.replace(".txt","_mlfit.root"))
tt = f1.Get("shapes_prefit")
h2 = tt.Get("overall_total_covar")

binNames = []
matrix = {}
nbins = h2.GetNbinsX()
for i in range(1, nbins+1):
    binNames.append(h2.GetXaxis().GetBinLabel(i))
    matrix[h2.GetXaxis().GetBinLabel(i)] = {}
    for j in range(1, nbins+1):
        matrix[h2.GetXaxis().GetBinLabel(i)][h2.GetXaxis().GetBinLabel(j)] = h2.GetBinContent(i,j)

sorted_cov = ROOT.TH2D('cov','',26,0,26,26,0,26)
binNames = natural_sort(binNames)

for i,k in enumerate(binNames):
    for j,l in enumerate(binNames):
        sorted_cov.SetBinContent(i+1,j+1,matrix[k][l])

c = ROOT.TCanvas('c','c',700,700)
c.SetLogz()

h2.Draw("colz")

c2 = ROOT.TCanvas('c2','c2',700,700)
c2.SetLogz()

sorted_cov.Draw("colz")

print binNames

plot_dir = plot_directory + '/covariance/'
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

outname = fname.split('.')[-2].split('/')[-1]
filetypes = ['.png','.pdf','.root']
for f in filetypes:
    c2.Print(plot_dir+outname+f)

