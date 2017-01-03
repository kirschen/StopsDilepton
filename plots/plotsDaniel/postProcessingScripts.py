import ROOT,pickle
import time

from StopsDilepton.samples.heppy_dpm_samples import mc_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import T2tt_heppy_mapper

#from StopsDilepton.samples.heppy_dpm_samples import data_heppy_mapper


mc = mc_heppy_mapper
mc_samples = mc.heppy_sample_names

signal = T2tt_heppy_mapper
signal_samples = signal.heppy_sample_names

#data = data_heppy_mapper
#data_samples = data.heppy_sample_names
data_samples = []

samples = data_samples + mc_samples

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
