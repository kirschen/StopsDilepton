#!/usr/bin/env python
import ROOT

def getNuisancesFromFile(nuisanceFile):
  nuisanceList = []
  with open(nuisanceFile) as f:
    for line in f:
      if 'name' in line: continue
      sysName = line.split()[0]
      pull    = line.split(',')[0].split()[-1]
      pullErr = line.split(',')[1].split()[0].replace('*','').replace('!','')
      nuisanceList.append((sysName, float(pull), float(pullErr)))
  return nuisanceList

def plotNuisances(nuisanceList, name):
  h = ROOT.TH1F("h","",len(nuisanceList)+2,0,len(nuisanceList)+2)

  for i, (sysName, pull, pullErr) in enumerate(nuisanceList):
    h.GetXaxis().SetBinLabel(i+1, sysName);
    h.SetBinContent(i+1, pull);
    h.SetBinError(i+1, pullErr);

  ROOT.gStyle.SetPadLeftMargin(0.08);
  ROOT.gStyle.SetPadRightMargin(0.02);
  ROOT.gStyle.SetPadTopMargin(0.05);
  ROOT.gStyle.SetPadBottomMargin(0.4);

  c = ROOT.TCanvas("c1", "", 0, 0, 1500, 400);
  h.SetMinimum(-2.1);
  h.SetMaximum(2.1);
  h.SetStats(0);
  h.SetMarkerStyle(20);
  h.SetMarkerColor(2);
  h.SetMarkerSize(2.0);
  h.SetLineWidth(2);
  h.GetXaxis().SetLabelSize(0.1);
  h.GetYaxis().SetTitle("Pull");
  h.GetYaxis().SetTitleOffset(0.5);
  h.GetYaxis().SetTitleSize(0.07);
  h.GetYaxis().SetLabelSize(0.07);
  h.GetYaxis().CenterTitle();
  h.GetYaxis().SetTickLength(0.015);
  h.Draw("PE1X0");
  c.SaveAs(name);

nuisanceList     = getNuisancesFromFile('nuisances.txt')
nuisanceListStat = [i for i in nuisanceList if i[0].count('Stat')] 
nuisanceListSys  = [i for i in nuisanceList if not i[0].count('Stat')]

plotNuisances(nuisanceList, 'pulls_all.png')
plotNuisances(nuisanceListStat, 'pulls_stat.png')
plotNuisances(nuisanceListSys, 'pulls_sys.png')
