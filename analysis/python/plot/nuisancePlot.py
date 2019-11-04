#!/usr/bin/env python
import ROOT
import os

from StopsDilepton.tools.user            import plot_directory

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--nuisanceFile',        action='store',      default='nuisances.txt')
argParser.add_argument('--outName',             action='store',      default='nuisances')
args = argParser.parse_args()

nuisancePath = '/'.join(args.nuisanceFile.split('/')[:-1])

#pullsFile = args.nuisanceFile.replace('.txt','')
pullsFile = os.path.join(plot_directory, 'pulls_new', args.outName)
nuisanceFile = args.nuisanceFile.split('/')

def getNuisancesFromFile(nuisanceFile):
  nuisanceList = []
  with open(nuisanceFile) as f:
    for line in f:
      print line
      if 'name' in line: continue
      sysName = line.split()[0]
      pull    = line.split(',')[0].split()[-1]
      pullErr = line.split(',')[1].split()[0].replace('*','').replace('!','')
      nuisanceList.append((sysName, float(pull), float(pullErr)))
  return nuisanceList

def plotNuisances(nuisanceList, name):
  h = ROOT.TH1F("h","",len(nuisanceList),0,len(nuisanceList))
  for i, (sysName, pull, pullErr) in enumerate(nuisanceList):
    h.GetXaxis().SetBinLabel(i+1, sysName);
    h.SetBinContent(i+1, pull);
    h.SetBinError(i+1, pullErr);
  h.LabelsOption("v")

  ROOT.gStyle.SetPadLeftMargin(0.08);
  ROOT.gStyle.SetPadRightMargin(0.02);
  ROOT.gStyle.SetPadTopMargin(0.05);
  ROOT.gStyle.SetPadBottomMargin(0.5);

  c = ROOT.TCanvas("c1", "", 0, 0, 1000, 400);
  h.SetMinimum(-2.6);
  h.SetMaximum(2.6);
  h.SetStats(0);
  h.SetMarkerStyle(20);
  h.SetMarkerColor(ROOT.kBlack);
  h.SetMarkerSize(1.2);
  h.SetLineWidth(2);
  h.SetLineColor(ROOT.kBlack);
  h.GetXaxis().SetLabelSize(0.1);
  h.GetYaxis().SetTitle("Pull");
  h.GetYaxis().SetTitleOffset(0.5);
  h.GetYaxis().SetTitleSize(0.07);
  h.GetYaxis().SetLabelSize(0.07);
  h.GetYaxis().CenterTitle();
  h.GetYaxis().SetTickLength(0.015);
  h.Draw("PE1X0");
  lineZ = ROOT.TLine(0,0,len(nuisanceList),0)
  lineO = ROOT.TLine(0,-1,len(nuisanceList),-1)
  lineMO = ROOT.TLine(0,1,len(nuisanceList),1)
  lineT = ROOT.TLine(0,-2,len(nuisanceList),-2)
  lineMT = ROOT.TLine(0,2,len(nuisanceList),2)
  for l in [lineZ,lineO,lineMO,lineT,lineMT]:
    l.SetLineColor(ROOT.kGray)
  lineZ.Draw('l same')
  lineO.Draw('l same')
  lineMO.Draw('l same')
  lineT.Draw('l same')
  lineMT.Draw('l same')
  h.Draw("PE1X0 same")
  c.SaveAs(name);

nuisanceList     = getNuisancesFromFile(args.nuisanceFile)
print nuisanceList
nuisanceListStat = [i for i in nuisanceList if (i[0].count('Stat_') or i[0].count('prop_'))] 
nuisanceListSys  = [i for i in nuisanceList if not (i[0].count('Stat_') or i[0].count('prop_'))]

plotNuisances(nuisanceList,     pullsFile+'_pulls_all.png')
plotNuisances(nuisanceListStat, pullsFile+'_pulls_stat.png')
plotNuisances(nuisanceListSys,  pullsFile+'_pulls_sys.png')
plotNuisances(nuisanceList,     pullsFile+'_pulls_all.pdf')
plotNuisances(nuisanceListStat, pullsFile+'_pulls_stat.pdf')
plotNuisances(nuisanceListSys,  pullsFile+'_pulls_sys.pdf')
