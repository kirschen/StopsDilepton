# Signal production

nanoAOD samples need to be in the respective python file in the Samples repository.
To obtain the normalization for each mass-point, run `getWeightsForSignals.py`, e.g.
```
python getWeightsForSignals.py --year 2016 --sample SMS_T8bbstausnu_XCha0p5_mStop_200to1800_XStau0p25
```
After this, you can post-process the signal samples without each job having to obtain the normalizations again.
Post-processing is run e.g.
```
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2016 --processingEra stops_2016_nano_v0p15 --skipGenLepMatching --susySignal --fastSim --sample SMS_T8bbstausnu_XCha0p5_mStop_200to1800_XStau0p25
```
If you want to run on HEPHY batch, you can use `#SPLIT N` to split into N subjobs.
To obtain ISR weights you need to run over the post-processed samples (the number of ISR jets is not contained in nanoAOD and is only added with nanoAOD tools).
```
python getWeightsForSignals.py --year 2016 --sample SMS_T8bbstausnu_XCha0p5_mStop_200to1800_XStau0p25 --ppSamplePath /afs/hephy.at/data/cms01/nanoTuples/stops_2016_nano_v0p15/dilep/
```
Now, you can post-process again, and the sample will automatically have the correct ISR weights.
```
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2016 --processingEra stops_2016_nano_v0p16 --skipGenLepMatching --susySignal --fastSim --sample SMS_T8bbstausnu_XCha0p5_mStop_200to1800_XStau0p25
```
There is no need to redo the `getWeightsForSignals` step.

The last step of processing is to split the sample into seperate files for each mass-point.
Be careful with the `--T2tt` flag, working on a proper flag for the stau-snu sample.
```
python nanoSignalSplitting.py --year 2016 --fastSim --T2tt --processingEra stops_2016_nano_v0p16 --skim dilep --samples SMS_T2tt_mStop_150to250
```
More examples can be found in `nanoSignalSplitting.sh`.
