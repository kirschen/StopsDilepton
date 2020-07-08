submitCondor.py $@ --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/16/   --queue nextweek nanoPostProcessing_Summer16.sh
#submitCondor.py $@ --dpm              --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/mc17/   --queue testmatch nanoPostProcessing_Fall17.sh
#submitCondor.py $@ --dpm              --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/mc18/   --queue testmatch nanoPostProcessing_Autumn18.sh

submitCondor.py $@ --dpm --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/data16/ --queue nextweek nanoPostProcessing_Run2016.sh
#submitCondor.py $@ --dpm              --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/data17/ --queue testmatch nanoPostProcessing_Run2017.sh
#submitCondor.py $@ --dpm              --maxRetries 10 --resubmitFailedJobs --discSpace 5000 --execFile submit_on_lxplus.sh --output /afs/cern.ch/work/k/kirschen/public/condor_logs/data18/ --queue testmatch nanoPostProcessing_Run2018.sh

