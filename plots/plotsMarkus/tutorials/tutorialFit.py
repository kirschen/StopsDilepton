# Tutorial about fitting functions to histogram
import ROOT, time, math

# Define function f1
f1=ROOT.TF1("f1","gaus",0,3)
f1.SetParameters(10.,1.5,0.5)
f1.Draw()

# Draw histogram hist1 from function f1
(f1.GetHistogram()).Draw()

hist1 = ROOT.TH1F("hist1", "Gauss distribution with fit function; x; y", 50, 0, 3)
hist1.FillRandom("f1", 10000)
hist1.Draw()

# Fit function definition
def user_func(x,par):
    arg=0
    if par[2]:
        arg=(x[0]-par[1])/par[2]
    return par[0]*math.exp(-0.5*arg*arg)

f1 = ROOT.TF1("f1",user_func,0,3,3)

# Perform fit
f1.SetParameters(10,hist1.GetMean(),hist1.GetRMS())
hist1.Fit("f1")

# Show Fit Parameters
ROOT.gStyle.SetOptFit(1111)
hist1.Draw()

# Legend
legend = ROOT.TLegend(0.75, 0.7, 0.98, .5);
legend.SetHeader("The Legend","C"); # option "C" allows to center the header
legend.AddEntry(hist1,"Histogram of a Gauss distribution");
legend.AddEntry(f1,"Fit Function");
legend.Draw();

# SAVE plot to PNG-File
ROOT.c1.SaveAs("~/www/histogramWithFit.png")

# wait a little longer...
time.sleep(10)
