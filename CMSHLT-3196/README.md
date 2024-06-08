# CMSHLT-3196: SiStripClusterChargeCut

Effect of SiStripClusterChargeCut

## EDM file from the RAW
* ssh rverma@lxplus7.cern.ch
* cmsrel CMSSW_13_0_10
* cd CMSSW_13_0_10/src
* cmsenv

* git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
* cp customizeHLTforCMSHLT3196.py HLTrigger/Configuration/python/
* scram build -j 4  
* voms-proxy-init --voms cms --valid 168:00

* source hltGetConfiguration.sh
* cmsRun hlt.py
* cmsRun hlt_CCC.py

## Submit CRAB jobs to produce many EDM files
* source /cvmfs/cms.cern.ch/crab3/crab.sh
* crab submit crab_submit_ele32_CCC.py

## Make ntuple from the EDM files
* ssh rverma@lxplus9.cern.ch
* cd CMSSW_13_0_10/src
* git cms-merge-topic Sam-Harper:L1NtupleFWLiteFixes_1230pre5
* git clone git@github.com:ravindkv/HLTAnalyserPy.git Analysis/HLTAnalyserPy
* scram build -j 4  
* python Analysis/HLTAnalyserPy/test/makeRun3Ntup.py -o ntup_CCC.root edm_CCC.root

## Make hist from ntuple
* root -b -q -l makeHist.C

## Creat and submit condor jobs to make ntuple and histograms
* python createJobs.py
* cd tmpSub
* condor_submit submitJobs.jdl

