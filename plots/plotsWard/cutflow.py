import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy, sys
from math import *

from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts
from StopsDilepton.tools.user import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *


def main():
    if sys.argv[1]=='425' : cutflow(SMS_T2tt_2J_mStop425_mLSP325)
    if sys.argv[1]=='500' : cutflow(SMS_T2tt_2J_mStop500_mLSP325)
    if sys.argv[1]=='650' : cutflow(SMS_T2tt_2J_mStop650_mLSP325)
    if sys.argv[1]=='850' : cutflow(SMS_T2tt_2J_mStop850_mLSP100)

def cutflow(sig):
    #######################################################
    #        SELECT WHAT YOU WANT TO DO HERE              #
    #######################################################
    reduceStat = 100 #recude the statistics, i.e. 10 is ten times less samples to look at


    #######################################################
    #         Define cutflow you want to make             #
    #######################################################
    mt2llcut = 80.
    metcut = 40.
    lumi = 10000.

    baselineamount = { 'samples':{}, 'SoverB': None,}

    cutflow = {\
        'metsig':{'baseline': 0.,
                            'cuts': {\
                                3:{'samples':{}, 'SoverB': None},
                                4:{'samples':{}, 'SoverB': None},
                                5:{'samples':{}, 'SoverB': None},
                                6:{'samples':{}, 'SoverB': None},
                                7:{'samples':{}, 'SoverB': None},
                                8:{'samples':{}, 'SoverB': None},
                                9:{'samples':{}, 'SoverB': None},
                                10:{'samples':{}, 'SoverB': None},
                                10:{'samples':{}, 'SoverB': None},
                                },
                            'event': None,
                            },
        'nbjets':{'baseline': 1.,
                            'cuts': {\
                                0:{'samples':{}, 'SoverB': None},
                                1:{'samples':{}, 'SoverB': None},
                                2:{'samples':{}, 'SoverB': None},
                                3:{'samples':{}, 'SoverB': None},
                                4:{'samples':{}, 'SoverB': None},
                                5:{'samples':{}, 'SoverB': None},
                                },
                            'event': None,
                            },
        'njets': {'baseline': 2.,
                            'cuts': {\
                                1:{'samples':{}, 'SoverB': None},
                                2:{'samples':{}, 'SoverB': None},
                                3:{'samples':{}, 'SoverB': None},
                                4:{'samples':{}, 'SoverB': None},
                                5:{'samples':{}, 'SoverB': None},
                                6:{'samples':{}, 'SoverB': None},
                                7:{'samples':{}, 'SoverB': None},
                                },
                            'event': None,
                            },
        'ht':    {'baseline': 0.,
                            'cuts': {\
                                50: {'samples':{}, 'SoverB': None},
                                100:{'samples':{}, 'SoverB': None},
                                200:{'samples':{}, 'SoverB': None},
                                300:{'samples':{}, 'SoverB': None},
                                400:{'samples':{}, 'SoverB': None},
                                500:{'samples':{}, 'SoverB': None},
                                },
                            'event': None,
                            },
    }

    #preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
    #For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
    preselection = 'met_pt>'+str(metcut)+'&&Sum$(LepGood_pt>20)==2'

    #######################################################
    #                 load all the samples                #
    #######################################################
    backgrounds = [singleTop_50ns,DY_50ns,TTJets_50ns]
    #signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
    signal = [sig]

    #######################################################
    #            get the TChains for each sample          #
    #######################################################
    for s in backgrounds+signal:
        s['chain'] = getChain(s,histname="")


    #######################################################
    #            Start filling in the histograms          #
    #######################################################
    for s in backgrounds+signal:
        for cuttype in cutflow.keys():
            for cut in cutflow[cuttype]['cuts'].keys():
                cutflow[cuttype]['cuts'][cut]['samples'][s["name"]] = 0

        baselineamount['samples'][s['name']] = 0

        chain = s["chain"]
        #Using Event loop
        #get EList after preselection
        print "Looping over %s" % s["name"]
        eList = getEList(chain, preselection)
        nEvents = eList.GetN()/reduceStat
        print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)

        for ev in range(nEvents):
            increment = 50
            if nEvents>increment and ev%(nEvents/increment)==0:
                sys.stdout.write('\r' + "=" * (ev / (nEvents/increment)) +  " " * ((nEvents - ev)/ (nEvents/increment)) + "]" +  str(round((ev+1) / (float(nEvents)/100),2)) + "%")
                sys.stdout.flush()
                sys.stdout.write('\r')
            chain.GetEntry(eList.GetEntry(ev))
            mt2Calc.reset()
            #event weight (L= 4fb^-1)
            weight = reduceStat*getVarValue(chain, "weight")

            weight = weight*(lumi/4000.)

            #MET
            met = getVarValue(chain, "met_pt")
            metPhi = getVarValue(chain, "met_phi")
            #jetpt
            leadingjetpt = getVarValue(chain, "Jet_pt",0)
            subleadingjetpt = getVarValue(chain, "Jet_pt",1)
            #Leptons
            allLeptons = getLeptons(chain)
            muons = filter(looseMuID, allLeptons)
            electrons = filter(looseEleID, allLeptons)
            nlep = len(allLeptons)

            #SF and OF channels
            leptons = {\
                'mu':   {'name': 'mumu', 'file': muons},
                'e':   {'name': 'ee', 'file': electrons},
                'emu': {'name': 'emu', 'file': [electrons,muons]},
                }
            for lep in leptons.keys():
                twoleptons = False
                #Same Flavor
                if lep != 'emu':
                    if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:

                        twoleptons = True
                        l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
                        l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
                        leadingleptonpt = l0pt
                        subleadingleptonpt = l1pt
                        mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                        zveto = True
                #Opposite Flavor
                if lep == 'emu':
                    if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:

                        twoleptons = True
                        l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
                        l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
                        if l1pt > l0pt :
                            leadingleptonpt = l1pt
                            subleadingleptonpt = l0pt
                        else:
                            leadingleptonpt = l0pt
                            subleadingleptonpt = l1pt
                        mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                        zveto = False
                if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-91.2)>15):
                    mt2Calc.setMet(met,metPhi)
                    mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
                    mt2ll = mt2Calc.mt2ll()
                    jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                    bjetspt = filter(lambda j:j['btagCSV']>0.89, jets)
                    nobjets = filter(lambda j:j['btagCSV']<=0.89, jets)
                    nmuons = len(muons)
                    nelectrons = len(electrons)
                    ht = sum([j['pt'] for j in jets])


                    if len(jets)<1: continue
                    if mt2ll<mt2llcut: continue

                    cutflow['metsig']['event'] = met/sqrt(ht)
                    cutflow['nbjets']['event'] = len(bjetspt)
                    cutflow['njets']['event'] = len(jets)
                    cutflow['ht']['event'] = ht

                    for cuttype in cutflow.keys():
                        eventisgood = True
                        for cuttype2 in cutflow.keys():
                            if cuttype2 != cuttype:
                                if cutflow[cuttype2]['event'] < cutflow[cuttype2]['baseline']:
                                    eventisgood = False
                        if eventisgood:
                            for cut in cutflow[cuttype]['cuts']:
                                if cutflow[cuttype]['event'] >= cut:
                                    cutflow[cuttype]['cuts'][cut]['samples'][s['name']] += weight

                    baselineisgood = True
                    for cuttype in cutflow.keys():
                        if cutflow[cuttype]['event'] < cutflow[cuttype]['baseline']:
                            baselineisgood = False
                    if baselineisgood:
                        baselineamount['samples'][s['name']] += weight

        del eList

    sigtot = baselineamount['samples'][signal[0]['name']]
    bkgtot = sum(baselineamount['samples'].values()) - sigtot

    if bkgtot > 0: baselineamount['SoverB'] = 100 * (sigtot/sqrt(bkgtot))
    else:          baselineamount['SoverB'] = 0.

    for cuttype in cutflow.keys():
        for cut in cutflow[cuttype]['cuts']:
            sigtot = cutflow[cuttype]['cuts'][cut]['samples'][signal[0]['name']]
            bkgtot = sum(cutflow[cuttype]["cuts"][cut]['samples'].values()) - sigtot
            if bkgtot > 0: cutflow[cuttype]['cuts'][cut]['SoverB'] = 100 * (sigtot/sqrt(bkgtot))
            else:          cutflow[cuttype]['cuts'][cut]['SoverB'] = 0.

    maketable(baselineamount, cutflow, mt2llcut, metcut,signal,lumi)


def maketable(baselineamount,cutflow,mt2llcut,metcut,signal,lumi):

    output = open('./cutflows/cutflow_'+signal[0]['name']+'.txt','w')

    output.write("[Lumi = "+str(lumi/1000)+" fb{-1}]" + "\n" + '\n')

    extra = ''
    firstline = []
    secondline = []
    thirdline = []
    firstline.append("MET>"+str(metcut)+", MT2ll>"+str(mt2llcut))
    secondline.append("Nominal")
    thirdline.append("*"*33)

    for i in range(len(baselineamount['samples'].keys())+2):
        extra +='{'+str(i)+':^33} '
    for j in sorted(baselineamount['samples'].keys()):
        firstline.append(j)
        secondline.append(int(baselineamount['samples'][j]))
        thirdline.append("*"*33)
    firstline.append('S/sqrt(B) x 100')
    secondline.append(round(baselineamount['SoverB'],2))
    thirdline.append("*"*33)
    output.write(extra.format(*firstline)+'\n')
    output.write(extra.format(*thirdline)+'\n')
    output.write(extra.format(*secondline)+'\n')
    output.write(extra.format(*thirdline)+'\n')
    for cuttype in cutflow.keys():
        for cut in sorted(cutflow[cuttype]['cuts'].keys()):
            line = []
            line.append(cuttype+">="+str(cut))
            for s in sorted(baselineamount['samples'].keys()):
                line.append(str(round(cutflow[cuttype]['cuts'][cut]['samples'][s],2)))
            line.append(str(round(cutflow[cuttype]['cuts'][cut]['SoverB'],2)))
            output.write(extra.format(*line)+'\n')
        output.write('\n')

    output.close()


if __name__ == '__main__':
        main()
