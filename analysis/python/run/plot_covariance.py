# We calculate first SF, then EMu

import shutil, os
import ROOT
from array import array
from StopsDilepton.tools.user import combineReleaseLocation, analysis_results, plot_directory

ROOT.gStyle.SetOptStat("")

fname = analysis_results + '/signalOnly/cardFiles/T2tt/T2tt_1200_50.txt'
releaseLocation = combineReleaseLocation

postFit = False
makeTable = True

if postFit: postfix = "_postfit"
else: postfix = ''

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
    #workspaceCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;text2workspace.py --X-allow-no-signal --X-allow-no-background myshapecard.txt"
    workspaceCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;text2workspace.py --channel-masks --X-allow-no-signal --X-allow-no-background myshapecard.txt"
    #Run fit
    #fitCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 2000 --saveOverall --preFitValue 0  myshapecard.root"
    fitCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 2000 --setPhysicsModelParameterRange mask_signal=1 --saveOverall myshapecard.root"

    
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
if postFit: tt = f1.Get("shapes_fit_b")
else: tt = f1.Get("shapes_prefit")
h2 = tt.Get("overall_total_covar")

binNames = []
matrix = {}
nbins = h2.GetNbinsX()
for i in range(1, nbins+1):
    binNames.append(h2.GetXaxis().GetBinLabel(i))
    matrix[h2.GetXaxis().GetBinLabel(i)] = {}
    for j in range(1, nbins+1):
        matrix[h2.GetXaxis().GetBinLabel(i)][h2.GetXaxis().GetBinLabel(j)] = h2.GetBinContent(i,j)

sorted_cov = ROOT.TH2D('cov','',nbins,0,nbins,nbins,0,nbins)
binNames = natural_sort(binNames)

for i,k in enumerate(binNames):
    for j,l in enumerate(binNames):
        sorted_cov.SetBinContent(i+1,j+1,matrix[k][l])

if postFit: sorted_cov.GetZaxis().SetRangeUser(0.00005, 30)
else: sorted_cov.GetZaxis().SetRangeUser(0.005, 3000)
c = ROOT.TCanvas('c','c',700,700)
c.SetLogz()

h2.Draw("colz")

c2 = ROOT.TCanvas('c2','c2',700,700)

pad1=ROOT.TPad("pad1","Main",0.,0.,.95,1.)
#pad1.SetLeftMargin(0.15)
#pad1.SetBottomMargin(0.02)
pad1.Draw()
pad1.cd()
pad1.SetLogz()

sorted_cov.Draw("colz")

plot_dir = plot_directory + '/covariance/'
if not os.path.isdir(plot_dir):
    os.mkdir(plot_dir)

outname = fname.split('.')[-2].split('/')[-1]
filetypes = ['.png','.pdf','.root']
for f in filetypes:
    c2.Print(plot_dir+outname+postfix+f)

# Calculate correlation matrix

import numpy, math
cov = numpy.zeros((sorted_cov.GetNbinsX(),sorted_cov.GetNbinsX()))
diag = numpy.zeros((sorted_cov.GetNbinsX(),sorted_cov.GetNbinsX()))

for i,k in enumerate(binNames):
    diag[i][i] = math.sqrt(matrix[k][k])
    for j,l in enumerate(binNames):
        cov[i][j] = matrix[k][l]

diag_inv = numpy.linalg.inv(diag)

corr = numpy.dot(diag_inv, cov)
corr = numpy.dot(corr, diag_inv)

sorted_corr = ROOT.TH2D('corr','',nbins,0,nbins,nbins,0,nbins)
for i,k in enumerate(binNames):
    for j,l in enumerate(binNames):
        sorted_corr.SetBinContent(i+1,j+1,corr[i][j])

sorted_corr.GetZaxis().SetRangeUser(-0.1, 1.1)

c3 = ROOT.TCanvas('c3','c3',700,700)

pad2=ROOT.TPad("pad2","Main",0.,0.,.95,1.)
pad2.Draw()
pad2.cd()
sorted_corr.Draw("colz")

outname = fname.split('.')[-2].split('/')[-1] + '_correlation'
filetypes = ['.png','.pdf','.root']
for f in filetypes:
    c3.Print(plot_dir+outname+postfix+f)


SRnames = []
for i in range(nbins/2):
    SRnames.append("SF"+str(i))
    SRnames.append("EMu"+str(i))

print SRnames

if makeTable:
    texdir = os.path.join(plot_dir,'matrices/')
    if not os.path.exists(texdir): os.makedirs(texdir)
    ofile = texdir+fname.split('.')[-2].split('/')[-1] + '.tex'
    with open(ofile, "w") as f:
          f.write("\\documentclass[a4paper,10pt,oneside]{article} \n \\usepackage{caption} \n \\usepackage{rotating} \n \\begin{document} \n")

          f.write("\\begin{table} \n\\resizebox{\\textwidth}{!}{ \\begin{tabular}{c||" + "c"*len(SRnames) + "} \n")
          f.write("& " + " & ".join(x for x in SRnames) + "\\\\ \n \\hline \\hline \n")
          for i,sr in enumerate(SRnames):
            f.write(sr + "& " + " & ".join(str(round(x,1)) for x in cov[i]) + "\\\\ \n") # \n \\hline
          f.write(" \\end{tabular}}")
          f.write(" \\caption{Covariance matrix} \n ")
          f.write(" \\end{table} ")
          
          f.write("\\begin{table} \n\\resizebox{\\textwidth}{!}{ \\begin{tabular}{c||" + "c"*len(SRnames) + "} \n")
          f.write("& " + " & ".join(x for x in SRnames) + "\\\\ \n \\hline \\hline \n")
          for i,sr in enumerate(SRnames):
            f.write(sr + "& " + " & ".join(str(round(x,2)) for x in corr[i]) + "\\\\ \n") # \n \\hline
          f.write(" \\end{tabular}}")
          f.write(" \\caption{Correlation matrix} \n ")
          f.write(" \\end{table} ")


          f.write(" \\end{document}")
    
    os.system("cd "+texdir+";pdflatex "+ofile)
