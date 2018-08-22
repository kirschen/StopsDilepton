For MVA studies we only use MC, no Data (at least for now).

Samples for SM backgrounds are defined in
`StopsDilepton.samples.nanoTuples_Summer16_postProcessed`
Signal samples (so far only T2tt) are in
`StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed`

# Getting estimates
First, get estimates using the following command:
```
python run_estimate.py --selectEstimator TTJets --MVAselection MVA_T2tt_default --MVAcut 0.5
```
This fills caches with several jobs in parallel, so don't run more than one of those jobs on one machine at a time. We use `TTJets`, `DY`, `TTZ`, `multiboson` and `other`. Four MVA classifiers are implemented so far, the interesting ones as a start are: `MVA_T2tt_default`, `MVA_T2tt_lep_pt`.
The MVAcut flag defines the lower cut on this classifier.

If you run over a lot of points you can also write a script that submits to the batch system.
In that case, use no multithreading (`--noMultiThreading`) and submit one job per signal region (0-25) with `--selectRegion`.
```
python run_estimate.py --selectEstimator DY --MVAselection MVA_T2tt_default --MVAcut 0.5 --selectRegion 0 --noMultiThreading
```
Right now, we use regions 0-25.

# Running limits
To run limits (and at the same time get estimates for the signal point) for e.g. the T2tt mStop=800, mNeutralino=0 point use:
```
python run_limit.py --signal T2tt --only T2tt_800_0 --expected --MVAselection MVA_T2tt_default --MVAcut 0.5
```
You need to have set-up the right release for running the combine tool (see recipe README) and also correctly set the path in
`StopsDilepton.tools.user`.
Calculated limits are stored in a pickle file in your results directory.

Happy running!
