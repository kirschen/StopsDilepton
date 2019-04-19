import os

runOnGentT2 = True

if os.environ['USER'] in ['schoef', 'rschoefbeck', 'schoefbeck']:
    # Where you store cmg output
    cmg_directory      = "/scratch/rschoefbeck/cmgTuples/80X_1l_9"
    # Where postprocessed data goes 
    data_output_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    #data_output_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    # Where you store the data
    data_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    # Where the plots go
    plot_directory      = "/afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton"
    #plot_directory      = "/afs/cern.ch/work/s/schoef/www/"
    # Analysis result files
    analysis_results        =  '/afs/hephy.at/data/dspitzbart02/StopsDilepton/results/80X_v35/' #Path to analysis results
    dpm_directory           = '/dpm/oeaw.ac.at/home/cms/store/user/schoef/'
    cern_proxy_certificate  = '/afs/cern.ch/user/s/schoef/private/.proxy'
    # directory with veto lists
    veto_lists = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/vetoLists/"
    # 715 release for limit calculation 
    combineReleaseLocation = '/afs/hephy.at/work/r/rschoefbeck/CMS/tmp/CMSSW_7_1_5/src'
    runOnGentT2 = False
    MVA_preprocessing_directory  = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_preprocessing'
    MVA_model_directory          = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_models'

if os.environ['USER'] in ['dspitzbart', 'dspitzba']:
    # Where you store cmg output
    cmg_directory      = "/scratch/rschoefbeck/cmgTuples/80X_1l_9"
    # Where postprocessed data goes 
    data_output_directory      = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    #data_output_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    # Where you store the data
    data_directory      = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    # Where the plots go
    plot_directory      = "/afs/hephy.at/user/d/dspitzbart/www/stopsDileptonLegacy/"
    #plot_directory      = "/afs/cern.ch/work/d/dspitzba/www/stopsDilepton/"
    # Analysis result files
    analysis_results        = '/afs/hephy.at/data/dspitzbart02/StopsDileptonLegacy/results/v1/' #Path to analysis results
    dpm_directory           = '/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/'
    cern_proxy_certificate  = '/afs/cern.ch/user/d/dspitzba/private/.proxy'
    #postprocessing_output_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postprocessing_output_directory = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    if 'cern' in os.getenv("HOSTNAME"):
      postprocessing_output_directory = "/eos/home-d/dspitzba/nanoTuples/"
    # directory with veto lists
    veto_lists = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/vetoLists/"
    MVA_preprocessing_directory  = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_preprocessing'
    MVA_model_directory          = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_models'
    # 715 release for limit calculation 
    combineReleaseLocation = '/afs/hephy.at/work/d/dspitzbart/stops/CMSSW_7_4_7/src'
    if 'cern' in os.getenv("HOSTNAME"):
      analysis_results        = '/afs/cern.ch/work/d/dspitzba/StopsDilepton/results/80X_v30'
      combineReleaseLocation = '/afs/cern.ch/work/d/dspitzba/CMS/stop/CMSSW_7_4_7/src'
      plot_directory      = "/eos/home-d/dspitzba/plots/"
    runOnGentT2 = False

if os.environ['USER'] in ['dfreisinger']:
    # Where you store cmg output
    cmg_directory      = "/scratch/rschoefbeck/cmgTuples/80X_1l_9"
    # Where postprocessed data goes 
    data_output_directory      = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    #data_output_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    # Where you store the data
    data_directory      = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    # Where the plots go
    plot_directory      = "/afs/hephy.at/user/d/dfreisinger/www/stopsDileptonLegacy/"
    #plot_directory      = "/afs/cern.ch/work/d/dspitzba/www/stopsDilepton/"
    # Analysis result files
    analysis_results        = '/afs/hephy.at/work/d/dfreisinger/StopsDileptonLegacy/results/v1/' #Path to analysis results
    dpm_directory           = '/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/'
    cern_proxy_certificate  = '/afs/cern.ch/user/d/dspitzba/private/.proxy'
    # directory with veto lists
    veto_lists = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/vetoLists/"
    MVA_preprocessing_directory  = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_preprocessing'
    MVA_model_directory          = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_models'
    # 715 release for limit calculation 
    combineReleaseLocation = '/afs/hephy.at/work/d/dfreisinger/cms/CMSSW_7_4_7/src'
    if 'cern' in os.getenv("HOSTNAME"):
      analysis_results        = '/afs/cern.ch/work/d/dspitzba/StopsDilepton/results/80X_v30'
      combineReleaseLocation = '/afs/cern.ch/work/d/dspitzba/CMS/stop/CMSSW_7_4_7/src'
    runOnGentT2 = False

if os.environ['USER'] in ['mdoppler']:
    # Where you store cmg output
    cmg_directory      = "/scratch/rschoefbeck/cmgTuples/80X_1l_9"
    # Where postprocessed data goes 
    data_output_directory      = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    #data_output_directory      = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
    # Where you store the data
    data_directory      = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
    # Where the plots go
    plot_directory      = "/afs/hephy.at/user/m/mdoppler/www/stopsDileptonLegacy/"
    #plot_directory      = "/afs/cern.ch/work/d/dspitzba/www/stopsDilepton/"
    # Analysis result files
    analysis_results        = '/afs/hephy.at/work/m/mdoppler/StopsDileptonLegacy/results/v1/' #Path to analysis results
    dpm_directory           = '/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/'
    cern_proxy_certificate  = '/afs/cern.ch/user/d/dspitzba/private/.proxy'
    # directory with veto lists
    veto_lists = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/vetoLists/"
    MVA_preprocessing_directory  = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_preprocessing'
    MVA_model_directory          = '/afs/hephy.at/work/g/gungersback/StopsDilepton/MVA_models'
    # 715 release for limit calculation 
    combineReleaseLocation = '/afs/hephy.at/work/d/dfreisinger/cms/CMSSW_7_4_7/src'
    if 'cern' in os.getenv("HOSTNAME"):
      analysis_results        = '/afs/cern.ch/work/d/dspitzba/StopsDilepton/results/80X_v30'
      combineReleaseLocation = '/afs/cern.ch/work/d/dspitzba/CMS/stop/CMSSW_7_4_7/src'
    runOnGentT2 = False
