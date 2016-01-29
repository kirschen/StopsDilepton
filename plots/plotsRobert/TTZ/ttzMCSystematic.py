import ROOT
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l import *
from StopsDilepton.tools.helpers import getChain, getYieldFromChain, getEList, getChunks, closestOSDLMassToMZ, mZ, deltaR, getObjFromFile
from StopsDilepton.tools.objectSelection import getLeptons, getOtherLeptons, leptonVars, getGoodJets
from math import sqrt

sample = TTZToLLNuNu

c = ROOT.TChain('tree')
chunks, sumWeight = getChunks(TTZToLLNuNu)
for chunk in chunks:
  c.Add(chunk['file'])

targetLumi=2100
lumiScaleFactor = sample.xSection*targetLumi/float(sumWeight)

preselection="Sum$(Jet_pt>30&&abs(Jet_eta)<2.5)>=3"
postfix="corrSys_Q2PDFshape"
maxN = None

Muon_mediumMuonId = 1
Muon_relIso03 = 0.1
Muon_sip3d = 4.0
Muon_dxy = 0.05
Muon_dz = 0.1

def looseMuID(l, ptCut=10, absEtaCut=2.4):
  return \
    l["pt"]>=ptCut\
    and abs(l["pdgId"])==13\
    and abs(l["eta"])<absEtaCut\
    and l["mediumMuonId"]==Muon_mediumMuonId \
    and l["relIso03"]<Muon_relIso03 \
    and l["sip3d"]<Muon_sip3d\
    and abs(l["dxy"])<Muon_dxy\
    and abs(l["dz"])<Muon_dz\


def cmgMVAEleID(l,mva_cuts):
  aeta = abs(l["eta"])
  for abs_e, mva in mva_cuts.iteritems():
    if aeta>=abs_e[0] and aeta<abs_e[1] and l["mvaIdSpring15"] >mva: return True
  return False

ele_MVAID_cuts_vloose = {(0,0.8):-0.16 , (0.8, 1.479):-0.65, (1.57, 999): -0.74}
ele_MVAID_cuts_loose = {(0,0.8):0.35 , (0.8, 1.479):0.20, (1.57, 999): -0.52}
ele_MVAID_cuts_tight = {(0,0.8):0.87 , (0.8, 1.479):0.60, (1.57, 999):  0.17}


def looseEleID(l, ptCut=10, absEtaCut=2.5):
  if  l["pt"]>=ptCut  and abs(l["eta"])<absEtaCut and abs(l["pdgId"])==11 and l["convVeto"] and cmgMVAEleID(l, ele_MVAID_cuts_loose):
    if abs(l['eta'])<1.479:
      return l["relIso03"]<0.076 and abs(l["sip3d"])<4.0 and abs(l['dz'])< 0.373  and abs(l['dxy'])< 0.0118 and l["lostHits"]<=2
    else:
      return l["relIso03"]<0.0678  and abs(l["sip3d"])<4.0 and abs(l['dz'])<  0.602   and abs(l['dxy'])<  0.0739 and l["lostHits"]<=1
  else: return False

eList = getEList(c, preselection) 
nEvents = eList.GetN()
print "Found %i events after preselection %s, looping over %i" % (eList.GetN(),preselection,nEvents)

bins = [
(3,3,0,0),
(3,3,1,1),
(3,3,2,-1),
(4,-1,0,0),
(4,-1,1,1),
(4,-1,2,-1),
]

def getBinName(b):
  res=""
  if b[0]==b[1]:res+="=="+str(b[0])+'j'
  elif b[1]<0:
    res+="#geq"+str(b[0])+'j'
  res+=", "
  if b[2]==b[3]:res+="=="+str(b[2])+'b'
  elif b[3]<0:
    res+="#geq"+str(b[2])+'b'

  return res

def getBin(nJets, nBTags):
  for i, b in enumerate(bins):
    if nJets>=b[0] and (nJets<=b[1] or b[1]<0) and nBTags>=b[2] and (nBTags<=b[3] or b[3]<0):return i
  return -1

central = ROOT.TH1F("central", "central",len(bins),0,len(bins))
for i in range(len(bins)):
  central.GetXaxis().SetBinLabel(i+1, getBinName(bins[i]))

lhe={}
#for i in range(110):
#  lhe[i] = ROOT.TH1F("lhe_"+str(i), "lhe_"+str(i), len(bins),0,len(bins))
#  for j in range(len(bins)):
#    lhe[i].GetXaxis().SetBinLabel(j+1, getBinName(bins[j]))

def getLHEWeights(c):
  res={}
  for i in range(110):#c.GetLeaf("nLHEweight").GetValue()):
    res[int(c.GetLeaf("LHEweight_id").GetValue(i))] = c.GetLeaf("LHEweight_wgt").GetValue(i)
  return res

for ev in range(nEvents)[:maxN]:
  if ev%10000==0:print "At %i/%i"%(ev,nEvents)
  c.GetEntry(eList.GetEntry(ev))
  weight = c.GetLeaf('genWeight').GetValue()*lumiScaleFactor
  leptons = getLeptons(c, leptonVars+['relIso03'])+getOtherLeptons(c, leptonVars+['relIso03'])
  ele = filter(lambda l:looseEleID(l), leptons)
  mu  = filter(lambda l:looseMuID(l), leptons)
  ele = filter(lambda e:min([999]+[deltaR(m, e) for m in mu])>0.1, ele)
  lep = mu+ele
  lep.sort(key=lambda l:-l['pt'])
  if not (len(lep)==3 and abs( closestOSDLMassToMZ(lep) - mZ)< 10): continue

  jets = getGoodJets(c)
  bTaggedJets = filter(lambda l:l['btagCSV']>0.605, jets) 
  nJets = len(jets) 
  nBTags = len(bTaggedJets)
  nBin = getBin(nJets, nBTags)
  if nBin<0:continue 
#  print "#e %i #m %i #j %i  #b %i n-bin %i"%(len(ele), len(mu), nJets, nBTags, nBin)
  central.Fill(nBin, weight) 
  lhe_original = c.GetLeaf('LHEweight_original').GetValue()
  w = getLHEWeights(c)
  for i in w.keys():
    if i not in lhe.keys():
      lhe[i] = ROOT.TH1F("lhe_"+str(i), "lhe_"+str(i), len(bins),0,len(bins))
    lhe[i].Fill(nBin,weight*w[i]/lhe_original)
#    print ev, c.GetLeaf('LHEweight_wgt').GetValue(i)/lhe_original
#    lhe[i].Fill(nBin, c.GetLeaf('LHEweight_wgt').GetValue(i)/lhe_original)

for i in lhe.keys():
  for j in range(len(bins)):
    lhe[i].GetXaxis().SetBinLabel(j+1, getBinName(bins[j]))

#p10 https://indico.cern.ch/event/459797/contribution/2/attachments/1181555/1710844/mcaod-Nov4-2015.pdf
#Computing Q2
q2  = central.Clone("q2")
pdf = central.Clone("pdf")
pdfKeys = filter(lambda k:k>=2000, lhe.keys())

#for i in pdfKeys:
for i in lhe.keys():
  lhe[i].Scale(central.Integral()/lhe[i].Integral())

for j, b in enumerate(bins):
  maxQ2=0.
  for i in [1001,1002,1003,1004,1005,1007,1009]:
    diff = abs(lhe[i].GetBinContent(j+1) - central.GetBinContent(j+1))
    if diff>maxQ2:maxQ2=diff
    print j, getBinName(b), lhe[i].GetBinContent(j+1), central.GetBinContent(j+1), maxQ2
  q2.SetBinError(j+1, diff )
  mean = sum([lhe[i].GetBinContent(j+1) for i in pdfKeys])/float(len(pdfKeys))
  var  = sum([(lhe[i].GetBinContent(j+1) - mean)**2 for i in pdfKeys])/(float(len(pdfKeys)) - 1.)
  pdf.SetBinError(j+1, sqrt(var) ) 

ROOT.gStyle.SetPadRightMargin(0.15)

c1 = ROOT.TCanvas()
l=ROOT.TLegend(0.2,0.7,0.6,0.9)
l.SetBorderSize(0)
l.AddEntry(central, "TT+Z")
l.AddEntry(pdf, "PDF uncertainty")
l.AddEntry(q2, "Q2 uncertainty")
#central.SetMarkerStyle(0)
#central.SetMarkerSize(0)
central.Draw()
q2.SetLineColor(ROOT.kBlue)
q2.SetFillColor(ROOT.kBlue)
q2.SetMarkerStyle(0)
q2.SetMarkerSize(0)
q2.Draw('e3same')
pdf.SetLineColor(ROOT.kRed)
pdf.SetFillColor(ROOT.kRed)
pdf.SetMarkerStyle(0)
pdf.SetMarkerSize(0)
pdf.Draw('e3same')
central.Draw('same')
l.Draw()
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ"+postfix+".png")
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ"+postfix+".pdf")
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ"+postfix+".root")
del c1

for i in range(len(bins)):
  central.SetBinError(i+1, 0)
  pdf.SetBinError(i+1,pdf.GetBinError(i+1)/central.GetBinContent(i+1))
  q2.SetBinError(i+1,q2.GetBinError(i+1)/central.GetBinContent(i+1))
  pdf.SetBinContent(i+1,1)
  q2.SetBinContent(i+1,1)

unc={}
for k  in ["center", "jesUp", "jesDown", "jer", "jerUp", "jerDown", "btag_bq", "btag_bqUp", "btag_bqDown", "btag_lq", "btag_lqUp", "btag_lqDown"]:
  unc[k] = getObjFromFile("systematics_updated.root", k)  

jes = unc['jesUp'].Clone("unc_jes")
unc['jesDown'].Scale(-1)
jes.Add(unc['jesDown'])
jes.Divide(unc['center'])

jer = unc['center'].Clone("unc_jer")
jer.Scale(-1)
jer.Add(unc['jer'])
jer.Divide(unc['center'])

btag_bq = unc['btag_bqUp'].Clone("unc_btag_bq")
unc['btag_bqDown'].Scale(-1)
btag_bq.Add(unc['btag_bqDown'])
btag_bq.Divide(unc['btag_bq'])
btag_bq.Scale(0.5)
#btag_bq.Scale(0.5)

btag_lq = unc['btag_lqUp'].Clone("unc_btag_lq")
unc['btag_lqDown'].Scale(-1)
btag_lq.Add(unc['btag_lqDown'])
btag_lq.Divide(unc['btag_lq'])
btag_lq.Scale(0.5)
#btag_lq.Scale(0.5)

#Add in quadrature
for j in range(len(bins)):
  for h in [jes, jer, btag_bq, btag_lq]:
    h.SetBinError(j+1, abs(h.GetBinContent(j+1)))
    h.SetBinContent(j+1, 1)

sys = [ ["PDF", pdf, ROOT.kRed], ["Q^{2}", q2, ROOT.kBlue], ["JES", jes, ROOT.kYellow], ["JER", jer, ROOT.kOrange], ["B-tag SF(l)", btag_lq, ROOT.kGreen-7], ["B-tag SF(b)", btag_bq, ROOT.kCyan]]


print 15*" "+"  ".join(["%12s"%s[0] for s in sys])
for i, b in enumerate(bins):
  print "%20s  "%(getBinName(b))+"         ".join(["{:.1%}".format(s[1].GetBinError(i+1)).rjust(5) for s in sys]) 

def addQuadrature(s1, s2):
  res = s1.Clone()
  for i in range(int(s1.GetNbinsX())):
    res.SetBinContent(i+1, 1)
    res.SetBinError(i+1, sqrt(s1.GetBinError(i+1)**2+s2.GetBinError(i+1)**2))
  return res

for i in reversed(range(1,len(sys))):
  for j in range(i-1):
    sys[i][1] = addQuadrature(sys[i][1], sys[j][1])

c1 = ROOT.TCanvas()
l1=ROOT.TLegend(0.36,0.76,0.65,0.9)
l1.SetBorderSize(0)
l2=ROOT.TLegend(0.65,0.76,0.85,0.9)
l2.SetBorderSize(0)
l3=ROOT.TLegend(0.2,0.76,0.4,0.9)
l3.SetBorderSize(0)

opt=''
i=0
stuff=[]
empty = q2.Clone('empty')
empty.Reset()
empty.GetYaxis().SetRangeUser(0.75, 1.4)
empty.SetLineColor(0)
empty.SetFillColor(0)
empty.SetMarkerStyle(0)
empty.SetMarkerSize(0)
empty.Draw()
empty.GetYaxis().SetTitle("Relative uncertainty")
for  name, h, color in reversed(sys):
#  h.GetYaxis().SetRangeUser(0.6, 1.6)
  h.SetLineColor(color)
  h.SetFillColor(color)
  h.SetMarkerStyle(0)
  h.SetMarkerSize(0)
  if i<=1: l1.AddEntry(h, name)
  elif i<=3: l2.AddEntry(h, name)
  else: l3.AddEntry(h, name)
  i+=1
  for j in range(int(h.GetNbinsX())):
    b = ROOT.TBox(h.GetXaxis().GetBinLowEdge(j+1), 1-h.GetBinError(j+1), h.GetXaxis().GetBinUpEdge(j+1), 1+h.GetBinError(j+1))
    b.SetFillColor(color)
    stuff.append(b)

for b in stuff:
  b.Draw('same')

l1.Draw()
l2.Draw()
l3.Draw()
c1.RedrawAxis()
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ_div"+postfix+".png")
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ_div"+postfix+".pdf")
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/TTZ_div"+postfix+".root")
del c1
