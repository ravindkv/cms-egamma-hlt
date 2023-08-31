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
sample   = "/RelValTTbar_14TeV/CMSSW_13_1_0-131X_mcRun4_realistic_v5_2026D95noPU-v1/GEN-SIM-DIGI-RAW"
samp_    = sample.split("/")[1].replace("/", "")
samp     = "%s_Phase2Setup"%samp_ 

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
config.JobType.psetName = 'Phase2_HLT.py'
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
    os.system("mkdir -p %s"%histDir)
    for edm in edmFiles.split(" "):
        print(edm)
        fName =  edm.split("/")[-1]
        #os.system("python3 lastFilterEffHist.py %s -o %s/%s"%(edm, histDir, fName))
    hAddOut = "%s/Phase2_HLT_All.root"%histDir
    hAddIn  = "%s/Phase2_HLT*.root"%histDir
    os.system("rm %s"%hAddOut)
    os.system("hadd -f %s %s"%(hAddOut, hAddIn))
    print(hAddOut)


