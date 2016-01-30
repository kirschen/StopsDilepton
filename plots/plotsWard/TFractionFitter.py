import ROOT,numpy

data = ROOT.TH1F("data","data",50,-5,5)
mc0 = ROOT.TH1F("mc0","mc0",50,-5,5)
mc1 = ROOT.TH1F("mc1","mc1",50,-5,5)

r = ROOT.TRandom3()

for i in range(100000):
        data.Fill(r.Gaus(3,2.5))
        data.Fill(r.Gaus(-3,2.5))
        data.Fill(r.Gaus(-3,2.5))
        mc0.Fill(r.Gaus(3,2.5))
        mc1.Fill(r.Gaus(-3,2.5))

mc = ROOT.TObjArray(2)
mc.Add(mc0);
mc.Add(mc1);
fit = ROOT.TFractionFitter(data, mc);
fit.Constrain(1,0.0,1.0);

fit.Fit()
result = fit.GetPlot();



mc0_frac = numpy.zeros(1,dtype=float)
mc0_frac_err = numpy.zeros(1,dtype=float)
mc1_frac = numpy.zeros(1,dtype=float)
mc1_frac_err = numpy.zeros(1,dtype=float)

fit.GetResult(0,mc0_frac,mc0_frac_err)
fit.GetResult(1,mc1_frac,mc1_frac_err)


mc0_weight = mc0_frac[0] * data.Integral() / mc0.Integral()
mc1_weight = mc1_frac[0] * data.Integral() / mc1.Integral()
mc0_weight_err = mc0_frac_err[0] * data.Integral() / mc0.Integral()
mc1_weight_err = mc1_frac_err[0] * data.Integral() / mc1.Integral()

print "weight of mc0 is: ", mc0_weight, " +- ", mc0_weight_err
print "weight of mc0 is: ", mc1_weight, " +- ", mc1_weight_err

mc0_fit = mc0.Clone()
mc0_fit.Scale(mc0_weight)
mc1_fit = mc1.Clone()
mc1_fit.Scale(mc1_weight)

mc0_fit.SetLineWidth(3)
mc1_fit.SetLineWidth(3)
mc0_fit.SetLineColor(ROOT.kRed)
mc1_fit.SetLineColor(ROOT.kGreen)

total_fit = mc0_fit.Clone()
total_fit.Add(mc1_fit)

total_fit.SetLineColor(ROOT.kViolet)
total_fit.SetLineWidth(3)

c2 = ROOT.TCanvas()
c2.SetLogy()
data.SetLineColor(ROOT.kBlack)
data.SetMarkerSize(2)
data.Draw("Ep");
mc0.SetLineColor(ROOT.kRed)
mc1.SetLineColor(ROOT.kGreen)
result.Draw("same");
mc0.Draw("epsame")
mc1.Draw("epsame")
mc0_fit.Draw("histsame")
mc1_fit.Draw("histsame")
total_fit.Draw("histsame")
c2.SaveAs("c2.png")
