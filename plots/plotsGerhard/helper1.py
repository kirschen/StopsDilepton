import ROOT
import numpy as np

# plot graph
x = np.linspace(0, 4*n.pi,101)
y = np.cos(x)
g = ROOT.TGraph(len(x), x,y)
g.SetTitle("cosine in x=[%.1f, %.1f]" % (x[0], x[-1]))
g.GetXaxis().SetTitle("x")
g.GetYaxis().SetTitle("y")
c1 = ROOT.TCanvas()
g.Draw("AL")
c1.Print('/afs/hephy.at/user/g/gungersback/www/root_test.png')

# plot hist - with SetBinContent
xbin = 10
xmin = -5
xmax = 5
height = np.random.normal(0,1,xbin)

histo = ROOT.TH1F("histo","",xbin,xmin,xmax)
histo.SetTitle('SetTitle')
histo.GetXaxis().SetTitle('vals')
histo.GetYaxis().SetTitle('events')
for i in range(xbin):
    histo.SetBinContent(i+1,height[i])
c2 = ROOT.TCanvas()
histo.Draw() #or ('colz')                                                 
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist.png')

# plot hist - with Fill Method
xbin = 10
xmin = -5
xmax = 5
values = np.random.normal(0,1, 1000)

histo = ROOT.TH1F("histo","",xbin,xmin,xmax)
histo.SetTitle('SetTitle')
histo.GetXaxis().SetTitle('vals')
histo.GetYaxis().SetTitle('events')
for i in range(len(values)):
    histo.Fill(values[i])
c2 = ROOT.TCanvas()
histo.Draw() #or ('colz')                                                 
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist2.png')

# plot hist - with multiple Fill, and log scale
xbin = 10
xmin = -5
xmax = 5
values = np.random.normal(0,1, 1000)
values2= np.random.normal(1,2,1000)
c2 = ROOT.TCanvas()
histo1 = ROOT.TH1F("histo","",xbin,xmin,xmax)
histo1.SetLineColor(ROOT.kRed)
histo1.SetLineStyle(3)
histo1.SetLineWidth(2)
for i in range(len(values)):
    histo1.Fill(values[i])
histo1.Draw()
histo2 = ROOT.TH1F("histo","",xbin,xmin,xmax)
histo2.SetLineColor(ROOT.kBlue)    
histo2.SetLineStyle(2)
histo2.SetLineWidth(2)
for i in range(len(values)):
    histo2.Fill(values2[i])

histo2.Draw('same') #or ('colz')                                                 
c2.SetLogy()
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist2.png')

# plot hist  - normalized
xbin = 10
xmin = -5
xmax = 5
values = np.random.normal(0,1, 1000)

histo = ROOT.TH1F("histo","",xbin,xmin,xmax)

histo.SetTitle('SetTitle')
histo.GetXaxis().SetTitle('vals')
histo.GetYaxis().SetTitle('events')
for i in range(len(values)):
    histo.Fill(values[i])
c2 = ROOT.TCanvas()
histo.Scale(1/1000.) 
histo.Draw() #or ('colz')                                                 
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist_normal.png')

# plot hist - with legend
xbin = 10
xmin = -5
xmax = 5
values = np.random.normal(0,1, 1000)
values2= np.random.normal(1,2,1000)
c2 = ROOT.TCanvas()
histo1 = ROOT.TH1F("histo1","signal",xbin,xmin,xmax)
histo1.SetLineColor(ROOT.kRed)
histo1.SetLineStyle(3)
histo1.SetLineWidth(2)
for i in range(len(values)):
    histo1.Fill(values[i])
histo1.Draw()
histo2 = ROOT.TH1F("histo2","background",xbin,xmin,xmax)
histo2.SetLineColor(ROOT.kBlue)
histo2.SetLineStyle(2)
histo2.SetLineWidth(2)
for i in range(len(values)):
    histo2.Fill(values2[i])

histo2.Draw('same') #or ('colz')                                                 
leg = ROOT.TLegend(.73,.32,.97,.53)
#leg.SetBorderSize(0) # no border
#leg.SetFillColor(0)
#leg.SetFillStyle(0)
#leg.SetTextFont(42)
#leg.SetTextSize(0.035)
leg.AddEntry(histo1,"Signal","L")
leg.AddEntry(histo2,"Background","L")        
leg.Draw()
c2.SetLogy()
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist2.png')

# plot hist - without Stat box
xbin = 10
xmin = -5
xmax = 5
values = np.random.normal(0,1, 1000)

histo = ROOT.TH1F("histo","",xbin,xmin,xmax)
histo.SetTitle('SetTitle')
histo.GetXaxis().SetTitle('vals')
histo.GetYaxis().SetTitle('events')
for i in range(len(values)):
    histo.Fill(values[i])
c2 = ROOT.TCanvas()                               
style = ROOT.gStyle
style.SetOptStat(0)
histo.SetObjectStat( False )
histo.Draw() #or ('colz')                                                 
c2.Print('/afs/hephy.at/user/g/gungersback/www/root_hist2.png')

