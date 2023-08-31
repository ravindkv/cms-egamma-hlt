#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgHLTPhaseIIDev
#----------------------------------------
#Setup egamma regression packages 
#----------------------------------------
#export SCRAM_ARCH=slc7_amd64_gcc10
cms=CMSSW_13_1_0
cmsrel $cms 
cd $cms/src 
eval `scramv1 runtime -sh`
git cms-init
git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
scram b -j`nproc`
cp runWorkflow.py $cms/src 

