import ROOT,os
import ctypes

def getContours(h, plotDir):
    _h = h.Clone()
    contlist = [0.5,1,2]
    idx = contlist.index(1)
    c_contlist = ((ctypes.c_double)*(len(contlist)))(*contlist)
    ctmp = ROOT.TCanvas()
    _h.SetContour(len(contlist),c_contlist)
    _h.Draw("contzlist")
    _h.GetZaxis().SetRangeUser(0.01,3)
    ctmp.Update()
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    graph_list = contours.At(idx)
    contours = []
    np = 0
    for i in range(graph_list.GetEntries()):
            contours.append( graph_list.At(i).Clone("cont_"+str(i)) )
    for c in contours:
        c.Draw('same')
    ctmp.Print(os.path.join(plotDir, h.GetName()+".png"))
    _h.Draw("colz")
    for c in contours:
        c.Draw('same')
    ctmp.Print(os.path.join(plotDir, h.GetName()+"_colz.png"))
    del ctmp
    return contours

def cleanContour(g, model="T2tt"):
    x, y = ROOT.Double(), ROOT.Double()
    remove=[]
    for i in range(g.GetN()):
        g.GetPoint(i, x, y)
        if model=="T2tt":
            if  (x<250) or x-y<200 or y>450 or x>900:
                remove.append(i)
        elif model=="T8bbllnunu_XCha0p5_XSlep0p05":
            pass
            #if y>150 or x<400 or (x<500 and y>50):
            #if x<440 or y>100 or x >1200:#x<480 or y>150 or x >1200
            #    remove.append(i)
        elif model=="T8bbllnunu_XCha0p5_XSlep0p09":
            if x>1300 or y>300 or x <500:#x<480 or y>150 or x >1200
                remove.append(i)
        elif model=="T8bbllnunu_XCha0p5_XSlep0p5":
            pass
            #if y > (x-170):
            #    remove.append(i)
        elif model=="T8bbllnunu_XCha0p5_XSlep0p95":
            pass
            #if y > (x-100) or x>1450 or x<700:
            #if x<700 or x > 1400:
            #    remove.append(i)
        else: print model, "not implemented"
    for i in reversed(remove):
        g.RemovePoint(i)
    #if model=="T8bbllnunu_XCha0p5_XSlep0p05":
    #    for i in range(g.GetN()):
    #        print i, x, y
    #    #g.SetPoint(500,15)
