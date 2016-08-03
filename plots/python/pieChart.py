import ROOT, os
from array import array

import warnings
warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )

def makePieChart(plotdir, name, yields, mode, samples, withLabels=False):
  if not sum(yields[mode][s.name] for s in samples) > 0: return

  # Get pieChartNames if MC takes up more than 1% of the total
  for s in samples:
    s.pieChartLabel = (s.texName if hasattr(s, 'texName') else s.name) if yields[mode][s.name] > 0.01*yields[mode]['MC'] else ''

  # Convert labels to array which can be read by ROOT
  labels_  = [array( 'c', (s.pieChartLabel + '\0' )) for s in samples]
  labels   = array( 'l', map(lambda x: x.buffer_info()[0], labels_))

  c        = ROOT.TCanvas("pie", "pie", 1000, 1000)
  piechart = ROOT.TPie(name, name, len(samples), array('f', [yields[mode][s.name] for s in samples]), array('i', [s.color for s in samples]), labels)

  piechart.SetRadius(0.3 if withLabels else 0.45)
  piechart.SetTextSize(0.02)
  piechart.SetLabelsOffset(.02 if withLabels else 1.);
  piechart.Draw("NOLrsc>")

  c.Print(os.path.join(plotdir, name + ".png"))
  c.Print(os.path.join(plotdir, name + ".pdf"))
