import os
from CRABClient.UserUtilities import getUsernameFromSiteDB
from WMCore.Configuration import Configuration
config = Configuration()

# Set variables
production_label = os.environ["CRAB_PROD_LABEL"]
dataset=os.environ["CRAB_DATASET"]
unitsPerJob = int(os.environ["CRAB_UNITS_PER_JOB"])
if "CRAB_TOTAL_UNITS" in os.environ: totalUnits = os.environ["CRAB_TOTAL_UNITS"]

config.section_("General")
config.General.transferLogs = True
config.General.requestName = production_label
config.General.workArea = 'crab_' + os.environ['ORIG_PROD_LABEL'] + "_" + os.environ["MAOD_SAMPLE_NAME"]# config.General.requestName

config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'nanoAOD_101X_HEmiss_MC_NANO.py'
config.JobType.outputFiles = ['nanoAOD.root']

config.section_("Data")
config.Data.inputDataset = dataset

config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
#if "IS_DATA" in os.environ:
#    config.Data.lumiMask = 'json/Cert_314472-316723_13TeV_PromptReco_Collisions18_JSON.txt'
config.Data.ignoreLocality = False

config.Data.outLFNDirBase = '/store/user/%s/nanoAOD/%s/' % (getUsernameFromSiteDB(), os.environ['ORIG_PROD_LABEL'])
config.Data.publication = True
config.Data.unitsPerJob = unitsPerJob#10
if "CRAB_TOTAL_UNITS" in os.environ: config.Data.totalUnits = int(totalUnits)#8

config.section_("Site")
#config.Site.blacklist = ['T2_US_Purdue', 'T2_US_Nebraska', 'T2_US_MIT', 'T2_US_Caltech']
config.Site.storageSite = 'T2_AT_Vienna'

config.section_("User")

config.section_("Debug")


