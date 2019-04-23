import ROOT
name = 'h'
#f_mc = ROOT.TF1(name+'_mc', "[3]+[0]*((1+(x-[1])**2/((2.+6.*[4])*[2]**2))**(-2.5-3.*[4])*ROOT::Math::tgamma(2.5+3.*[4]))/(sqrt(pi)*sqrt(2.+6.*[4])*[2]*ROOT::Math::tgamma(2.+3.*[4]))",-70,70)
f_mc = ROOT.TF1(name+'_mc', "[3]+[0]*((1+(x-[1])**2/((2+6*[4])*[2]**2))**(-2.5-3*[4])*ROOT::Math::tgamma(2.5+3*[4]))/(sqrt(pi)*sqrt(2+6*[4])*[2]*ROOT::Math::tgamma(2+3*[4]))", -70, 70)
#f_mc = ROOT.TF1(name+'_mc', "[3]+[0]*exp(-0.5*((x-[1])/[2])**2)")
f_mc.SetParameter(0, 100)
f_mc.SetParameter(1, 0)
#f_mc.SetParLimits(1,-20,20)
f_mc.SetParameter(2, 20)
#f_mc.SetParLimits(2,10,50)
f_mc.SetParameter(3, 0)
f_mc.SetParameter(4, 20)
f_mc.SetParLimits(4,1,20)
f_mc.Draw()
ROOT.c1.SetLogy()
ROOT.c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/etc/gamma.png')
