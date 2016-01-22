import ROOT
import ctypes

def getContours(h):
  _h = h.Clone()
  contlist = [0.8,1.0,1.2]
  idx = contlist.index(1.0)
  c_contlist = ((ctypes.c_double)*(len(contlist)))(*contlist)
  ctmp = ROOT.TCanvas()
  _h.SetContour(len(contlist),c_contlist)
  _h.Draw("contzlist")
  _h.GetZaxis().SetRangeUser(0.01,3)
  ctmp.Update()
  ctmp.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/"+h.GetName()+".png")
  _h.Draw("colz")
  ctmp.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/"+h.GetName()+"_colz.png")
  contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
  graph_list = contours.At(idx)
  contours = []
  np = 0
  idx_graph = 0
  for i in range(graph_list.GetEntries()):
      contours.append( graph_list.At(i).Clone("cont_"+str(i)) )
      if contours[i].GetN()>np:
          np=contours[i].GetN()
          idx_graph = i
  del ctmp
  return contours

def cleanContour(g):
  x, y = ROOT.Double(), ROOT.Double()
  remove=[]
  for i in range(g.GetN()):
    g.GetPoint(i, x, y)
    if  (x<250) or x-y<200 or y>450 or x>900:
      remove.append(i)
  for i in reversed(remove):
    g.RemovePoint(i)
