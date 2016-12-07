import ROOT,pickle
import time

from StopsDilepton.samples.heppy_dpm_samples import mc_heppy_mapper

s = mc_heppy_mapper
samples = s.heppy_sample_names

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
