import ROOT
import array

def makeTGraph( x, y ):

    if len(x)!=len(y):
        raise RuntimeError( "Need same length! Got %i and %i"%(len(x), len(y) ) )

    return ROOT.TGraph(len(x), array.array('d', x), array.array('d', y))


if __name__ == "__main__":
    x = [1,2,3]
    y = [1,2,3]

    g = makeTGraph( x, y )
    c1 = ROOT.TCanvas()
    g.Draw("AC*")

    c1.Print('/afs/hephy.at/user/g/gungersback/www/etc/test.png')

def saveTGraph( x, y, pathstring= '/afs/hephy.at/user/g/gungersback/www/etc', filename='test.png'):

    if len(x)!=len(y):
        raise RuntimeError( "Need same length! Got %i and %i"%(len(x), len(y) ) )
    
    g = makeTGraph( x, y )
    c1 = ROOT.TCanvas()
    g.Draw("AC*")

    c1.Print(pathstring + '/' +  filename)

    return g


if __name__ == "__main__":
    x = [1,2,3]
    y = [1,2,3]

    g = makeTGraph( x, y )
    c1 = ROOT.TCanvas()
    g.Draw("AC*")

    c1.Print('/afs/hephy.at/user/g/gungersback/www/etc/test.png')

#import ROOT
#import numpy as np
#
#x = np.linspace(0, 4*n.pi,101)
#y = np.cos(x)
#g = ROOT.TGraph(len(x), x,y)
#g.SetTitle("cosine in x=[%.1f, %.1f]" % (x[0], x[-1]))
#g.GetXaxis().SetTitle("x")
#g.GetYaxis().SetTitle("y")
#c1 = ROOT.TCanvas()
#g.Draw("AL")
#c1.Print('/afs/hephy.at/user/g/gungersback/www/root_test.png')

