import os
import sys
import random
import subprocess
sys.dont_write_bytecode = True
from optparse import OptionParser

#----------------------------------------
#INPUT command-line arguments 
#----------------------------------------
parser = OptionParser()
parser.add_option("--s1Conf",   "--s1Conf",     dest="s1Conf",action="store_true",default=False, help="Get HLT Configuration") 
parser.add_option("--s2Crab",   "--s2Crab",     dest="s2Crab",action="store_true",default=False, help="Crab submission")
parser.add_option("--s3Hist", "--s3Hist",   dest="s3Hist",action="store_true",default=False, help="Hists")
(options, args) = parser.parse_args()

s1Conf = options.s1Conf
s2Crab = options.s2Crab
s3Hist = options.s3Hist

eosDir = "/store/group/phys_egamma/ec/rverma/phase2"
#----------------------------------------
# Steo-1: Get HLT Configuration file
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgHLTPhaseIIDev 
#----------------------------------------
sample   = "/TT_TuneCP5_14TeV-powheg-pythia8/Phase2Spring23DIGIRECOMiniAOD-noPU_131X_mcRun4_realistic_v5-v1/GEN-SIM-DIGI-RAW-MINIAOD"
#sample   = "/RelValTTbar_14TeV/CMSSW_13_1_0-131X_mcRun4_realistic_v5_2026D95noPU-v1/GEN-SIM-DIGI-RAW"
#sample   = "/RelValTTbar_14TeV/CMSSW_13_1_0-PU_131X_mcRun4_realistic_v5_2026D95PU200-v1/GEN-SIM-DIGI-RAW"
samp_    = sample.split("/")[1].replace("/", "")
#samp     = "%s_TkElectron"%samp_ 
#samp     = "%s_Phase2Setup"%samp_ 
samp     = "%s_L1New"%samp_ 

cond    ='--conditions auto:phase2_realistic_T21'
custom  = "--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev"
common  = "--processName=HLTX --eventcontent FEVTDEBUGHLT --geometry Extended2026D88 --era Phase2C17I13M9 -n 10 --nThreads 1 --no_exec --inputCommands \'keep *, drop *_hlt*_*_HLT, drop triggerTriggerFilterObjectWithRefs_l1t*_*_HLT\'"

def getFile(sample):
    os.system("voms-proxy-init --voms cms --valid 168:00")
    das = "dasgoclient --query='file dataset=%s status=*'"%sample
    print(das)
    std_output, std_error = subprocess.Popen(das,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return random.choice(files_)

if s1Conf:
    inFile = getFile(sample)
    inFile_ = "root://cms-xrd-global.cern.ch/%s"%inFile
    #inFile_ = "file:2560000/8c0c4efa-ab57-4152-b313-4ae24aaaf04e.root"
    print(inFile_)
    cmd = "cmsDriver.py Phase2 -s HLT:75e33 %s %s %s --filein=%s"%(cond, custom, common, inFile_)
    print(cmd)
    os.system(cmd)
    #os.system("cmsRun hlt_%s.py"%t)

#----------------------------------------
# Step-2: Crab submission 
#----------------------------------------
crab = """
from CRABClient.UserUtilities import config
config = config()

# config.section_('General')
config.General.requestName = 'crab_%s'
config.General.workArea = 'crab_%s'
config.General.transferOutputs = True
config.General.transferLogs = True

# config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'rerunL1_only_cfg.py'
#config.JobType.psetName = 'Phase2_HLT.py'
#config.JobType.numCores = 4

# config.Data.inputDBS = 'phys03'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxMemoryMB = 4000

# config.JobType.numCores = 8
config.Data.inputDataset ='%s'
# config.Data.splitting = 'Automatic'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1

config.Data.outLFNDirBase = '%s'
config.Data.publication = False
config.Site.storageSite = 'T2_CH_CERN'
"""
if s2Crab:
    os.system("rm -rf crab_*")
    os.system("source /cvmfs/cms.cern.ch/crab3/crab.sh")
    outFile = open("crab_%s.py"%samp, "w")
    dirName = "%s"%(samp)
    eosDir_ = "%s/s2Crab"%eosDir
    outStr  = crab%(dirName, dirName, sample, eosDir_)
    print(outStr)
    print("/eos/cms/%s"%eosDir_) 
    outFile.write(outStr)
    #os.system("crab submit %s"%outFile)
    outFile.close()

#----------------------------------------
# Step-3: Edm to ntuples 
#----------------------------------------
def getFile2(dir_):
    dir_ = '/eos/cms/store/group/phys_egamma/ec/rverma/phase2/s2Crab/CRAB_UserFiles/crab_crab_TT_TuneCP5_14TeV-powheg-pythia8_L1NewHLT/230909_153646/0000/'
    edm = "find %s -type f | grep root"%dir_
    std_output, std_error = subprocess.Popen(edm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files

if s3Hist:
    crabEOSDir = "/eos/cms%s/s2Crab/%s/crab_crab_%s"%(eosDir, samp_, samp)
    edmFiles = getFile2(crabEOSDir)
    histDir = "/eos/cms%s/s3Hist/%s"%(eosDir, samp)
    os.system("rm -r %s"%histDir)
    os.system("mkdir -p %s"%histDir)
    isCond = True
    if isCond:
        if os.path.exists("tmpSub"):
            os.system("rm -r tmpSub")
        os.system("mkdir -p tmpSub/log")
        condorLogDir = "log"
        shFile = open("tmpSub/makeHist.sh", 'w')
        shFile.write('#!/bin/bash\n')
        shFile.write('printf "Start Running Histogramming at ";/bin/date\n')
        shFile.write("cd /afs/cern.ch/work/r/rverma/public/cms-egamma-hlt/phase2/CMSSW_13_1_0/src\n")
        shFile.write("eval `scramv1 runtime -sh`\n")
        shFile.write("cd -\n")
        shFile.write('echo $1\n')
        shFile.write('python3 lastFilterEffHist.py $1 -o out.root\n')
        shFile.write('xrdcp -f out.root $2')

        os.system("cp lastFilterEffHist.py tmpSub")
        os.system("cp /tmp/x509up_u93032 tmpSub")

        jdlName = 'submitJobs.jdl'
        jdlFile = open('tmpSub/%s'%jdlName,'w')
        jdlFile.write('Executable =  makeHist.sh \n')
        common_command = \
        'Universe   = vanilla\n\
        should_transfer_files = YES\n\
        when_to_transfer_output = ON_EXIT\n\
        Transfer_Input_Files = lastFilterEffHist.py, makeHist.sh\n\
        x509userproxy        = x509up_u93032\n\
        Output = %s/log_$(cluster)_$(process).stdout\n\
        Error  = %s/log_$(cluster)_$(process).stderr\n\
        Log  = %s/log_$(cluster)_$(process).condor\n\n'%(condorLogDir, condorLogDir, condorLogDir)
        jdlFile.write(common_command)
        for edm in edmFiles.split(" "): 
            if len(edm) ==0: continue
            oHist = edm.split("/")[-1].replace(".root", "_Hist.root")
            args =  'Arguments  = %s %s/%s\n' %(edm,  histDir, oHist)
            args += "Queue 1\n\n"
            jdlFile.write(args)
        jdlFile.close() 
    else:
        os.system("python3 lastFilterEffHist.py %s -o %s/Phase2_HLT_All.root"%(edmFiles, histDir))


