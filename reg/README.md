# cms-egamma-reg
EGamma offline energy regression

* source setWorkflow.sh

### Change pid to 11 or 22 according to the input data in 
Analysis/HLTAnalyserPy/python/EgHLTRun3Tree.py, L-198

* python3 runWorkflow --s1Conf
* python3 runWorkflow --s2Crab
* python3 runWorkflow --s3Ntuple 
* python3 runWorkflow --s4Flat
* python3 runWorkflow --s5Reg 
* python3 runWorkflow --s6Plot 
* python3 runWorkflow --s7NewGT
