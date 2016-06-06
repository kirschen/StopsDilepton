import ROOT

from RootTools.core.standard import *
outliers = "(run==259862&&lumi==486&&evt==854513396||run==257461&&lumi==70&&evt==78280773||run==258177&&lumi==765&&evt==1117067242||run==260534&&lumi==139&&evt==256062502||run==257819&&lumi==34&&evt==53233332)"
doubleMu = Sample.fromCMGOutput("doubeMu", baseDirectory = "/scratch/rschoefbeck/cmgTuples/763_1l/DoubleMuon_Run2015D-16Dec2015-v1/", selectionString = outliers)
