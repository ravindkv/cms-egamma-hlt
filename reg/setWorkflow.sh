#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html#setup
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
#----------------------------------------
#Setup egamma regression packages 
#----------------------------------------
export SCRAM_ARCH=slc7_amd64_gcc10
cmsrel CMSSW_12_6_3
cd CMSSW_12_6_3/src

##Setup for creating hltConfig and produce edm files from GEN-SIM-RAW
eval `scramv1 runtime -sh`
git cms-addpkg HLTrigger
scramv1 b -j 8
git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
git cms-merge-topic Sam-Harper:L1NtupleFWLiteFixes_1230pre5
scramv1 b -j 8

#Setup for producing ntuple from edm files
git clone -b RegNtupleRun3 ssh://git@gitlab.cern.ch:7999/rverma/HLTAnalyserPy.git Analysis/HLTAnalyserPy
scramv1 b -j 8

#Setup for making flat ntuple and doing regression
git clone -b Run3_2023_rverma_CMSSW_12_6_3 git@github.com:ravindkv/EgRegresTrainerLegacy.git 
cd EgRegresTrainerLegacy
gmake RegressionTrainerExe -j 8
gmake RegressionApplierExe -j 8
cd .. && cp ../../runWorkflow.py .


