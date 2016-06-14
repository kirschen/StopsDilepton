import ROOT

from RootTools.core.standard import *
maxN = -1
doubleMu = Sample.fromCMGOutput("doubeMu", baseDirectory = "/scratch/rschoefbeck/cmgTuples/763_1l_ptError/DoubleMuon_Run2015D-16Dec2015-v1", maxN = maxN)
DY = Sample.fromCMGOutput("DY", baseDirectory = "/scratch/rschoefbeck/cmgTuples/763_1l_ptError/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1", maxN = maxN)

from StopsDilepton.tools.objectSelection import *

muonSelection= "&&".join(muonSelectorString(index = i) for i in [0,1])
eleSelection= "&&".join(eleSelectorString(index = i) for i in [0,1])


onZ = "abs(sqrt(2.*{l}_pt[0]*{l}_pt[1]*(cosh({l}_eta[0]-{l}_eta[1])-cos({l}_phi[0]-{l}_phi[1]))) - 91.2)<15".format(l = "LepGood")

h_muon_data = doubleMu.get1DHistoFromDraw( "max(LepGood_ptError[0], LepGood_ptError[1])", binning = [10**(i/10.) for i in range(0, 40)], binningIsExplicit = True , selectionString = "&&".join([muonSelection, onZ]), addOverFlowBin = 'upper')
h_muon_data.style = styles.lineStyle(ROOT.kBlack)
h_muon_data.legendText = "Muons, data"
h_muon_MC   = DY.get1DHistoFromDraw( "max(LepGood_ptError[0], LepGood_ptError[1])", binning = [10**(i/10.) for i in range(0, 40)], binningIsExplicit = True , selectionString = "&&".join([muonSelection, onZ]), addOverFlowBin = 'upper' )
h_muon_MC.style = styles.lineStyle(ROOT.kRed)
h_muon_MC.legendText = "Muons, simulation"
h_ele_data = doubleMu.get1DHistoFromDraw( "max(LepGood_ptError[0], LepGood_ptError[1])", binning = [10**(i/10.) for i in range(0, 40)], binningIsExplicit = True , selectionString = "&&".join([eleSelection, onZ]), addOverFlowBin = 'upper' )
h_ele_data.style = styles.lineStyle(ROOT.kBlue)
h_ele_data.legendText = "Ele, data"
h_ele_MC   = DY.get1DHistoFromDraw( "max(LepGood_ptError[0], LepGood_ptError[1])", binning = [10**(i/10.) for i in range(0, 40)], binningIsExplicit = True , selectionString = "&&".join([eleSelection, onZ]), addOverFlowBin = 'upper' )
h_ele_MC.style = styles.lineStyle(ROOT.kGreen)
h_ele_MC.legendText = "Ele, simulation"

Plot.setDefaults(addOverFlowBin="upper")

plotting.draw(
    Plot.fromHisto( "ptError",
        [ [h_muon_data], [ h_muon_MC], [ h_ele_data], [ h_ele_MC ] ], texX = "pTError"
    ), 
    plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/etc/", 
    ratio = None, 
    logX = True, logY = True, sorting = False, 
    scaling = {1:0, 2:0, 3:0},
)
