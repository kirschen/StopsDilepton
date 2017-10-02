import ROOT, os, math

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
argParser.add_argument('--cardDir',            action='store',      default='TTbarDM_preAppFix_DYttZflat')
argParser.add_argument('--xsec',            action='store_true')
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
obsUp       = []
obsDown     = []
exp         = []
exp1Up      = []
exp2Up      = []
exp1Down    = []
exp2Down    = []
xsecs       = []
zeros       = []

from StopsDilepton.tools.xSecDM import *
xSecDM_ = xSecDM()

for s in sorted(DMsamples):
    if s[0] == mChi:
        if s[2] == tp:
            mass.append(s[1])
            try:
                res[(s[0],s[1],s[2])].has_key('0.500')
                if args.xsec: xsec = xSecDM_.getXSec(tp,s[1],s[0])
                else: xsec = 1

                # x-sec line
                xsecs.append(xsec)

                # expected line and bands
                exp.append(xsec*(res[(s[0],s[1],s[2])]['0.500']))
                exp1Up.append(xsec*(res[(s[0],s[1],s[2])]['0.840'] - res[(s[0],s[1],s[2])]['0.500']))
                exp2Up.append(xsec*(res[(s[0],s[1],s[2])]['0.975'] - res[(s[0],s[1],s[2])]['0.500']))
                exp1Down.append(xsec*(res[(s[0],s[1],s[2])]['0.500'] - res[(s[0],s[1],s[2])]['0.160']))
                exp2Down.append(xsec*(res[(s[0],s[1],s[2])]['0.500'] - res[(s[0],s[1],s[2])]['0.025']))

                # observed line and theory uncertainty band
                obs.append(xsec*(res[(s[0],s[1],s[2])]['-1.000']))
                obsUp.append(xsec*res[(s[0],s[1],s[2])]['-1.000']*math.sqrt(0.3**2 + (xSecDM_.getXSec(tp,s[1],s[0],sigma=1)/xSecDM_.getXSec(tp,s[1],s[0]) - 1)**2))
                obsDown.append(xsec*res[(s[0],s[1],s[2])]['-1.000']*math.sqrt(0.3**2 + (1 - xSecDM_.getXSec(tp,s[1],s[0],sigma=-1)/xSecDM_.getXSec(tp,s[1],s[0]))**2))

                # technicality
                zeros.append(0)

            except KeyError:
                print "Result not found for",(s[0],s[1],s[2])

a_mass      = array('d',mass)
a_obs       = array('d',obs)
a_obsUp     = array('d',obsUp)
a_obsDown   = array('d',obsDown)
a_exp       = array('d',exp) 
a_exp1Up    = array('d',exp1Up) 
a_exp2Up    = array('d',exp2Up) 
a_exp1Down  = array('d',exp1Down) 
a_exp2Down  = array('d',exp2Down) 
a_zeros     = array('d',zeros)
a_xsecs     = array('d',xsecs)

exp2Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp2Down, a_exp2Up)
exp1Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_exp1Down, a_exp1Up)
exp         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_exp, a_zeros, a_zeros, a_zeros, a_zeros)
obs         = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_obs, a_zeros, a_zeros, a_zeros, a_zeros)
obs1Sigma   = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_obs, a_zeros, a_zeros, a_obsDown, a_obsUp)
xsecs       = ROOT.TGraphAsymmErrors(len(zeros), a_mass, a_xsecs, a_zeros, a_zeros, a_zeros, a_zeros)

exp2Sigma.SetFillColor(ROOT.kOrange)
exp1Sigma.SetFillColor(ROOT.kGreen+1)
obs1Sigma.SetFillStyle(3345)
obs1Sigma.SetFillColor(ROOT.kGray+2)
obs1Sigma.SetLineWidth(2)
obs1Sigma.SetMarkerSize(0)
#obs1Sigma.SetFillColorAlpha(ROOT.kGray, 0.5)

exp.SetLineWidth(2)
exp.SetLineStyle(2)
obs.SetLineWidth(2)
xsecs.SetLineWidth(2)
xsecs.SetLineColor(ROOT.kRed+1)
#xsecs.SetLineStyle(3)

can = ROOT.TCanvas("can","",700,700)
can.SetLogy()
can.SetLogx()

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
mg.Add(obs1Sigma)
y_max = 500
y_min = 0.05
if mChi == 10:
    y_max = 5000
    y_min = 0.2
elif mChi == 50:
    y_max = 50000
    y_min = 0.2
mg.SetMaximum(y_max)
mg.SetMinimum(y_min)
mg.Draw("a3 same")
if tp == 'S': tp_ = 'm_{#phi}'
elif tp == 'PS': tp_ = 'm_{a}'
mg.GetXaxis().SetTitle(tp_+" (GeV)")
mg.GetYaxis().SetTitle("95% CL upper limit #sigma/#sigma_{theory}")
mg.GetXaxis().SetRangeUser(10,1000)

xsecs.Draw("l same")
exp.Draw("l same")
if not args.blinded: obs.Draw("l same")
leg_size = 0.04 * 4


leg = ROOT.TLegend(0.185,0.82-leg_size,0.5,0.82)
leg.SetBorderSize(1)
leg.SetFillColor(0)
leg.SetLineColor(0)
leg.SetTextSize(0.03)

#leg.AddEntry(obs,"#bf{Observed}",'l')
leg.AddEntry(obs1Sigma,"#bf{Observed #pm theory uncertainty}")
leg.AddEntry(exp,"#bf{Median expected}",'l')
leg.AddEntry(exp1Sigma,"#bf{68% expected}",'f')
leg.AddEntry(exp2Sigma,"#bf{95% expected}",'f')
leg.Draw()

none = ROOT.TH1F()

#leg2 = ROOT.TLegend(0.5,0.9-leg_size,0.8,0.9)
#leg2.SetBorderSize(1)
#leg2.SetFillColor(0)
#leg2.SetLineColor(0)
#leg2.SetTextSize(0.035)
if tp == 'S': tp_ = 'Scalar mediator'
elif tp == 'PS': tp_ = 'Pseudoscalar mediator'
#leg2.AddEntry(none,tp_,'')
#leg2.AddEntry(none,'#bf{Dirac DM}','')
#leg2.AddEntry(none,"#bf{m_{#chi} = "+str(mChi)+" GeV}",'')
#leg2.AddEntry(none,'#bf{g_{q} = 1, g_{#chi} = 1}','')
#leg2.Draw()

extraText = ""
#extraText = "Preliminary"

latex2 = ROOT.TLatex()
latex2.SetNDC()
latex2.SetTextSize(0.03)
latex2.SetTextAlign(11) # align right
latex2.DrawLatex(0.20,0.89,'#bf{'+tp_+', Dirac DM, m_{#chi} = '+str(mChi)+' GeV, g_{q} = 1, g_{DM} = 1}')
latex2.DrawLatex(0.20,0.83,'#bf{95% CL upper limits}')
#latex2.DrawLatex(0.22,0.84,'#bf{m_{#chi} = '+str(mChi)+' GeV, g_{q} = 1, g_{#chi} = 1}')

latex1 = ROOT.TLatex()
latex1.SetNDC()
latex1.SetTextSize(0.04)
latex1.SetTextAlign(11) # align right
latex1.DrawLatex(0.16,0.96,'CMS #bf{#it{'+extraText+'}}')
latex1.DrawLatex(0.71,0.96,"#bf{35.9 fb^{-1} (13 TeV)}")

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


