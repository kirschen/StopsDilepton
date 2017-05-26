import ROOT, os

import pickle, shutil
from RootTools.core.standard                import *
from array import array

from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.tools.user import combineReleaseLocation, analysis_results, plot_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--particle',           action='store',      default='S',            nargs='?', choices=['S','PS'], help="scalar (S) or pseudoscalar (PS)?")
argParser.add_argument('--mChi',               action='store',      default=1,           help='Which DM particle mass?')
argParser.add_argument('--plot_directory',     action='store',      default='DMLimits')
argParser.add_argument('--blinded',            action='store_true')
argParser.add_argument('--cardDir',            action='store',      default='TTbarDM')
args = argParser.parse_args()

#ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro('../../../../RootTools/plot/scripts/tdrstyle.C')
ROOT.setTDRStyle()

categories = []
mChi_list = []
mPhi_list = []

for s in DMsamples:
    if not s[0] in mChi_list: mChi_list.append(s[0])
    if not s[1] in mPhi_list: mPhi_list.append(s[1])
    if not s[2] in categories: categories.append(s[2])

res = pickle.load(file(os.path.join(analysis_results,"fitAll","cardFiles",args.cardDir,"calculatedLimits.pkl")))

mChi = int(args.mChi)
tp = args.particle

mass        = []
obs         = []
exp         = []
exp1Up      = []
exp2Up      = []
exp1Down    = []
exp2Down    = []
zeros       = []

for s in sorted(DMsamples):
    if s[0] == mChi:
        if s[2] == tp:
            mass.append(s[1])
            try:
                res[(s[0],s[1],s[2])].has_key('0.500')
                exp.append(res[(s[0],s[1],s[2])]['0.500'])
                exp1Up.append(res[(s[0],s[1],s[2])]['0.840'] - res[(s[0],s[1],s[2])]['0.500'])
                exp2Up.append(res[(s[0],s[1],s[2])]['0.975'] - res[(s[0],s[1],s[2])]['0.500'])
                exp1Down.append(res[(s[0],s[1],s[2])]['0.500'] - res[(s[0],s[1],s[2])]['0.160'])
                exp2Down.append(res[(s[0],s[1],s[2])]['0.500'] - res[(s[0],s[1],s[2])]['0.025'])
                obs.append(res[(s[0],s[1],s[2])]['-1.000'])
                zeros.append(0)
            except KeyError:
                print "Result not found for",(s[0],s[1],s[2])

a_mass      = array('d',mass)
a_obs       = array('d',obs) 
a_exp       = array('d',exp) 
a_exp1Up    = array('d',exp1Up) 
a_exp2Up    = array('d',exp2Up) 
a_exp1Down  = array('d',exp1Down) 
a_exp2Down  = array('d',exp2Down) 
a_zeros     = array('d',zeros)

exp2Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp2Down, a_exp2Up)
exp1Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp1Down, a_exp1Up)
exp         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_zeros, a_zeros)
obs         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_obs, a_zeros, a_zeros, a_zeros, a_zeros)


exp2Sigma.SetFillColor(ROOT.kYellow)
exp1Sigma.SetFillColor(ROOT.kGreen)

exp.SetLineWidth(2)
exp.SetLineStyle(2)
obs.SetLineWidth(2)

can = ROOT.TCanvas("can","",700,700)
can.SetLogy()
can.SetLogx()

one = ROOT.TH1F("one","",1,0,10000)
one.SetBinContent(1,1)
one.SetLineWidth(2)
one.SetLineColor(ROOT.kGray+1)
one.SetLineStyle(3)
one.Draw('hist')

#h2 = ROOT.TH1F('h2','h2',10,10,1000)

#limits = Plot.fromHisto(name = "brazil_limits", histos = [[h]], texX = "m_{1} (GeV)", texY = "95% ..." )
#
#plotting.draw( limits, \
#        plot_directory = os.path.join(plot_directory, 'DMLimits'),
#        logX = True, logY = True,
#        sorting = False,
#        #ratio = ratio,
#        extensions = ["pdf", "png", "root"],
#        yRange = (0.01,100),
#        widths = {'x_width':700, 'y_width':700}
#        #drawObjects = drawObjects,
#        #legend = legend,
#        #canvasModifications = canvasModifications
#    )

mg = ROOT.TMultiGraph()
mg.SetTitle("Exclusion graphs")
mg.Add(exp2Sigma)
mg.Add(exp1Sigma)
mg.SetMaximum(500)
mg.SetMinimum(0.05)
mg.Draw("a3 same")
if tp == 'S': tp_ = 'm_{#phi}'
elif tp == 'PS': tp_ = 'm_{a}'
mg.GetXaxis().SetTitle(tp_+" (GeV)")
mg.GetYaxis().SetTitle("95% CL upper limit on #mu=#sigma/#sigma_{TH}")
mg.GetXaxis().SetRangeUser(10,1000)

one.Draw("hist same")
exp.Draw("l same")
if not args.blinded: obs.Draw("l same")
leg_size = 0.04 * 4


leg = ROOT.TLegend(0.2,0.9-leg_size,0.4,0.9)
leg.SetBorderSize(1)
leg.SetFillColor(0)
leg.SetLineColor(0)
leg.SetTextSize(0.035)

leg.AddEntry(exp,"Expected",'l')
leg.AddEntry(obs,"Observed",'l')
leg.AddEntry(exp1Sigma,"Exp #pm 1 #sigma",'f')
leg.AddEntry(exp2Sigma,"Exp #pm 2 #sigma",'f')
leg.Draw()

none = ROOT.TH1F()

leg2 = ROOT.TLegend(0.4,0.82,0.6,0.9)
leg2.SetBorderSize(1)
leg2.SetFillColor(0)
leg2.SetLineColor(0)
leg2.SetTextSize(0.035)
if tp == 'S': tp_ = 'Scalar'
elif tp == 'PS': tp_ = 'Pseudoscalar'
leg2.AddEntry(none,tp_,'')
leg2.AddEntry(none,"m_{#chi} = "+str(mChi)+" GeV",'')
leg2.Draw()

extraText = ""

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.04)
latex1.SetTextAlign(11) # align right
latex1.DrawLatex(0.16,0.96,'CMS #bf{#it{'+extraText+'}}')
latex1.DrawLatex(0.73,0.96,"#bf{35.9fb^{-1}} (13TeV)")

plot_dir = os.path.join(plot_directory,args.plot_directory)
if not os.path.isdir(plot_dir):
    os.makedirs(plot_dir)

if not args.blinded:
    plot_dir += '/brazil_%s_mChi%s'%(tp,str(mChi))
else:
    plot_dir += '/brazil_%s_mChi%s_blinded'%(tp,str(mChi))

filetypes = [".pdf",".png",".root"]

for f in filetypes:
    can.Print(plot_dir+f)


