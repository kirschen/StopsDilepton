import ROOT
import ctypes

def getContours(h):
  _h = h.Clone()
  contlist = [0.5,1.0,1.5]
  idx = contlist.index(1.0)
  c_contlist = ((ctypes.c_double)*(len(contlist)))(*contlist)
  ctmp = ROOT.TCanvas()
  _h.SetContour(len(contlist),c_contlist)
  _h.Draw("contzlist")
  ctmp.Update()
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
    if  y>350 or (x<400):
      remove.append(i)
  for i in reversed(remove):
    g.RemovePoint(i)
