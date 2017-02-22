import ROOT,pickle
import time

from StopsDilepton.samples.heppy_dpm_samples import mc_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import T2tt_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import data_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import ttbarDM_heppy_mapper

from StopsDilepton.tools.helpers import natural_sort

mc = mc_heppy_mapper
mc_samples = mc.heppy_sample_names

SUSY_signal = T2tt_heppy_mapper
SUSY_signal_samples = SUSY_signal.heppy_sample_names

DM_signal = ttbarDM_heppy_mapper
DM_signal_samples = DM_signal.heppy_sample_names

data = data_heppy_mapper
data_samples = data.heppy_sample_names

#data_samples = []

samples = data_samples + mc_samples + DM_signal_samples + SUSY_signal_samples
#samples = mc_samples

def getPPString(sampleName, processType, jobtitle='2l_PP', vetoString='supercomplicatedstringnevertobefoundinasample', additionalOptions=''):
  sm = sorted([a for a in samples if sampleName in a])
  #print sm
  strings = []
  veto_list = []
  for st in sm:
    sample_str = ''
    if st not in veto_list and vetoString not in st:
      if st +'_ext' in sm:
        sample_str = st + ' ' + st + '_ext'
        veto_list.append(st)
        veto_list.append(st+'_ext')
      else:
        sample_str = st
        veto_list.append(st)
      
      time_stamp = time.time()*1e6
      if processType == 'local':
        command_str = 'python cmgPostProcessing.py '+additionalOptions+' --samples ' + sample_str
      elif processType == 'batch':
        command_str = 'submitBatch.py --dpm --title=\'2l_PP\' \"python cmgPostProcessing.py '+additionalOptions+' --samples ' + sample_str + '\"'
      elif processType == 'nohup':
        command_str = 'nohup krenew -t -K 10 -- bash -c \" python cmgPostProcessing.py '+additionalOptions+' --samples ' + sample_str + '> out_%0.2X.log\" &' %time_stamp
      print command_str

def getTexTable(samples, filename="samples.tex", vetoString='supercomplicatedstringnevertobefoundinasample'):
    replaceMap =    {
                    "RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6":"[Summer16mAOD]",
                    "RunIISummer16MiniAODv2-PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1":"[Summer16mAOD*]"
                    }
                 
    l = []
    for sample in sorted(samples.sample_map.keys()):
        dataset = sample.dataset
        for r in replaceMap.keys():
            if r in dataset: dataset = dataset.replace(r, replaceMap[r])
        sampleString = "{:10} & \\verb {:120} & {:8} \\\\ \n".format('',dataset,round(sample.xSection,3))
        if not vetoString in dataset:
            l.append(sampleString)

    with open(filename, 'w') as f:
        #f.write("\\documentclass[a4paper,10pt,oneside]{article} \n \\usepackage{caption} \n \\usepackage{rotating} \n \\begin{document} \n")
        f.write("\\begin{table} \n \\tiny \\center \n \\begin{tabular}{l|l|l}  \n")
        f.write("process & dataset path & $\sigma \cdot BR$ (pb)\\\\ \\hline \n")
        for s in natural_sort(l):
            f.write(s)
        f.write(" \\end{tabular} \\\\ \n \\vspace{2mm} \n")
        for r in replaceMap.keys():
            f.write("\\verb {} = \\verb {} \\\\ \n".format(replaceMap[r],r))
        f.write(" \\caption{Samples} \n \\label{samples-backgrounds2016} \n ")
        f.write(" \n \\end{table} ")
        #f.write(" \\end{document}")
    return natural_sort(l)

