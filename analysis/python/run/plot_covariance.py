'''
Calculate covariance matrices following https://twiki.cern.ch/twiki/bin/view/CMS/SimplifiedLikelihood
'''

import shutil, os
import ROOT
from array import array
from StopsDilepton.tools.user import combineReleaseLocation, analysis_results, plot_directory

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--postFit",          dest="postFit",     default=False,               action='store_true',   help="")
parser.add_option("--aggregate",        dest="aggregate",   default=False,               action='store_true',   help="")
parser.add_option("--onlySR",           dest="onlySR",      default=False,               action='store_true',   help="")
parser.add_option("--datacard",         dest="datacard",    default="T2tt_1100_150",     action='store',        help="Which datacard?")
parser.add_option("--overwrite",        dest="overwrite",   default=False,               action='store_true',   help="Overwrite existing mlfit root file")
(options, args) = parser.parse_args()


ROOT.gStyle.SetOptStat("")

#'aggregated/fitAll/cardFiles/T2tt/T2tt_800_100.txt'
#'aggregated/signalOnly/cardFiles/T2tt/T2tt_800_100.txt'

if options.aggregate:
    agg = "/aggregated/"
else:
    agg = "/"

fname = analysis_results + '%sfitAll/cardFiles/T2tt_newCorr/%s.txt'%(agg,options.datacard)
#fname = analysis_results + '%sfitAll/cardFiles/T2tt/%s.txt'%(agg,options.datacard)
releaseLocation = '/afs/hephy.at/work/d/dspitzbart/higgs/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/'

postFit = options.postFit
makeTable = True
aggregate = options.aggregate
onlySR = options.onlySR

nSR = 26
if aggregate: nSR = 3

postfix = ''

if postFit: postfix += "_postfit"
if aggregate: postfix += '_aggregated'
if onlySR: postfix += '_onlySR'

postfix += ''

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
    shapeFilename = filename.replace('.txt', '_shape.txt')
    
    assert os.path.exists(filename), "File not found: %s"%filename
    combineCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combineCards.py %s -S > myshapecard.txt "%fname

    #set workspace
    if postFit:
        workspaceCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;text2workspace.py --channel-masks --X-allow-no-signal --X-allow-no-background myshapecard.txt"
    else:
        workspaceCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;text2workspace.py --X-allow-no-signal --X-allow-no-background myshapecard.txt"

    #Run fit
    if postFit:
        masks = ['mask_ch1_Bin'+str(i)+'=1' for i in range(nSR)]
        maskString = ','.join(masks)
        fitCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 5000 --setPhysicsModelParameters "+maskString+" --saveOverall myshapecard.root"
        print fitCommand
    else:
        fitCommand = "cd "+uniqueDirname+";eval `scramv1 runtime -sh`;combine -M MaxLikelihoodFit --saveShapes --saveWithUnc --numToysForShape 5000 --saveOverall --preFitValue 0  myshapecard.root"

    
    print combineCommand
    os.system(combineCommand)
    os.system(workspaceCommand)
    os.system(fitCommand)

    tempResFile = uniqueDirname+"/mlfit.root"
    tempShapeFile = uniqueDirname+"/myshapecard.txt"
    res = os.path.isfile(tempResFile)
    if res:
        shutil.copyfile(tempResFile, covFilename)
        shutil.copyfile(tempShapeFile, shapeFilename)
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

if not os.path.isfile(fname.replace(".txt","_mlfit.root")) or options.overwrite:
    calcCovariance(fname=fname, options="")

f1 = ROOT.TFile(fname.replace(".txt","_mlfit.root"))
if postFit: tt = f1.Get("shapes_fit_b")
else: tt = f1.Get("shapes_prefit")
h2 = tt.Get("overall_total_covar")

binNames = []
matrix = {}
nbins = h2.GetNbinsX()
#if onlySR: nbins = nSR

for i in range(1, nbins+1):
    binNames.append(h2.GetXaxis().GetBinLabel(i))
    matrix[h2.GetXaxis().GetBinLabel(i)] = {}
    for j in range(1, nbins+1):
        matrix[h2.GetXaxis().GetBinLabel(i)][h2.GetXaxis().GetBinLabel(j)] = h2.GetBinContent(i,j)

if onlySR: nbins = nSR
sorted_cov = ROOT.TH2D('cov','',nbins,0,nbins,nbins,0,nbins)
binNames = natural_sort(binNames)

SRnames = []
if aggregate:
    for i in range(nbins):
        SRnames.append("All"+str(i))
else:
    for i in range(nbins/2):
        SRnames.append("SF"+str(i))
        SRnames.append("EMu"+str(i))

print SRnames
print len(SRnames)
print binNames


for i,k in enumerate(binNames):
    print i
    if i < nSR:
        sorted_cov.GetXaxis().SetBinLabel(i+1,SRnames[i])
        sorted_cov.GetYaxis().SetBinLabel(i+1,SRnames[i])
    for j,l in enumerate(binNames):
        sorted_cov.SetBinContent(i+1,j+1,matrix[k][l])
        #sorted_cov.GetXaxis().SetBinLabel(i+1,l)

sorted_cov.GetXaxis().LabelsOption("v")

if postFit: sorted_cov.GetZaxis().SetRangeUser(0.005, 3000) #0.00005, 30
else: sorted_cov.GetZaxis().SetRangeUser(0.005, 3000)
c = ROOT.TCanvas('c','c',700,700)
c.SetLogz()

h2.Draw("colz")

c2 = ROOT.TCanvas('c2','c2',700,700)

pad1=ROOT.TPad("pad1","Main",0.,0.,1.,1.)
pad1.SetRightMargin(0.15)
pad1.SetTopMargin(0.06)
#pad1.SetLeftMargin(0.15)
#pad1.SetBottomMargin(0.02)
pad1.Draw()
pad1.cd()
pad1.SetLogz()

sorted_cov.Draw("colz")

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.04)
latex1.SetTextAlign(11) # align right

latex1.DrawLatex(0.10,0.95,'CMS #bf{#it{Supplementary}}')
latex1.DrawLatex(0.60,0.95,"#bf{36 fb^{-1} (13TeV)}")


plot_dir = plot_directory + '/covariance_newCorr/'
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

print binNames[:nbins]
for i,k in enumerate(binNames[:nbins]):
    diag[i][i] = math.sqrt(matrix[k][k])
    for j,l in enumerate(binNames[:nbins]):
        cov[i][j] = matrix[k][l]

diag_inv = numpy.linalg.inv(diag)

corr = numpy.dot(diag_inv, cov)
corr = numpy.dot(corr, diag_inv)

sorted_corr = ROOT.TH2D('corr','',nbins,0,nbins,nbins,0,nbins)
for i,k in enumerate(binNames[:nbins]):
    for j,l in enumerate(binNames[:nbins]):
        sorted_corr.SetBinContent(i+1,j+1,corr[i][j])

sorted_corr.GetZaxis().SetRangeUser(-1.05, 1.05)

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
if aggregate:
    for i in range(nbins):
        SRnames.append("All"+str(i))
else:
    for i in range(nbins/2):
        SRnames.append("SF"+str(i))
        SRnames.append("EMu"+str(i))


print SRnames

if makeTable:
    texdir = os.path.join(plot_dir,'matrices/')
    if not os.path.exists(texdir): os.makedirs(texdir)
    ofile = texdir+fname.split('.')[-2].split('/')[-1] + postfix + '.tex'
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

f1.Close()
