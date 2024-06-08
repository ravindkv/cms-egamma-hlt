import os
import sys
import itertools
sys.dont_write_bytecode = True

#crabDir = "/eos/cms/store/group/phys_egamma/tnpTuples/rverma/crab_bpix_ele32/2023/data/EGamma0/crab_2023_Run2023D0v1/240525_235427/0000/"
crabDir = "/eos/cms/store/group/phys_egamma/tnpTuples/rverma/crab_bpix_ele32/2023/data/EGamma0/crab_2023_Run2023D0v1/240606_114914/0000/" 
print(crabDir)

def break_range(start, end, n):
    # Calculate the size of each smaller range
    step = (end - start) / n
    ranges = []
    for i in range(n):
        range_start = start + i * step
        range_end = start + (i + 1) * step
        ranges.append((range_start, range_end))
    return ranges

if __name__ == "__main__":
    #---------------------------
    # Create tar file
    #---------------------------
    if os.path.exists("tmpSub"):
        os.system("rm -r tmpSub")
        print("Deleted dir: tmpSub")
    os.system("mkdir -p tmpSub/log")
    print("Created dir: tmpSub")
    condorLogDir = "log"
    cmssw_base = os.environ.get("CMSSW_BASE")
    cmssw_version = cmssw_base.split('/')[-1].strip()
    tarFile = "tmpSub/egm_tnp_analysis.tar.gz"
    os.system("tar --exclude-tag-under=FILE -zcvf %s  --exclude ./ntup --exclude ./plot --exclude ./hist --exclude ./.git --exclude ./Analysis/HLTAnalyserPy/.git --exclude ./tmpSub --exclude ./Analysis/HLTAnalyserPy/python/__pycache__ ."%(tarFile))

    #---------------------------
    # Create executable file 
    #---------------------------
    shFile = open("tmpSub/tnpEGM_fitter.sh", 'w')
    shFile.write('#!/bin/bash\n')
    shFile.write('printf "Start Running TnP at ";/bin/date\n')
    shFile.write('echo ${_CONDOR_SCRATCH_DIR}\n')
    shFile.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    #shFile.write('export SCRAM_ARCH=slc7_amd64_gcc700\n')
    shFile.write('scramv1 project CMSSW %s\n'%cmssw_version)
    shFile.write('mv egm_tnp_analysis.tar.gz %s/src\n'%cmssw_version)
    shFile.write('cd %s/src\n'%cmssw_version)
    #shFile.write('cmssw-el7\n')
    shFile.write('eval `scramv1 runtime -sh`\n')
    shFile.write('tar --strip-components=1 -zxf egm_tnp_analysis.tar.gz\n')
    shFile.write('echo $1 $2\n')
    shFile.write('scram b -j 4\n')
    shFile.write('fList=""\n')
    shFile.write('for ((m=$1; m<$2; m++)); do\n')
    shFile.write('    fList="$fList %s/output_$m.root"\n'%crabDir)
    shFile.write('done\n')
    shFile.write('echo $fList\n')
    shFile.write('python3 Analysis/HLTAnalyserPy/test/makeRun3Ntup.py -o ntup.root  $fList\n')
    shFile.write('root -b -q makeHist.C\n')
    shFile.write('xrdcp -f ntup.root %s/ntup_$1_$2.root\n'%crabDir)
    shFile.write('xrdcp -f hist.root %s/hist_$1_$2.root\n'%crabDir)
    shFile.write('printf "Done at ";/bin/date\n')
    shFile.write('cd ../../\n') 
    shFile.write('rm -rf %s\n'%cmssw_version)

    #---------------------------
    # Create job files 
    #---------------------------
    os.system("cp /tmp/x509up_u93032 tmpSub")
    jdlName = 'submitJobs.jdl'
    jdlFile = open('tmpSub/%s'%jdlName,'w')
    jdlFile.write('Executable =  tnpEGM_fitter.sh \n')
    common_command = \
    'Universe   = vanilla\n\
    should_transfer_files = YES\n\
    when_to_transfer_output = ON_EXIT\n\
    Transfer_Input_Files = egm_tnp_analysis.tar.gz, tnpEGM_fitter.sh\n\
    x509userproxy        = x509up_u93032\n\
    +MaxRuntime = 60*60*24\n\
    Output = %s/log_$(cluster)_$(process).stdout\n\
    Error  = %s/log_$(cluster)_$(process).stderr\n\
    Log  = %s/log_$(cluster)_$(process).condor\n\n'%(condorLogDir, condorLogDir, condorLogDir)
    jdlFile.write(common_command)

    start = 0
    end = 1000
    n = 100
    ranges = break_range(start, end, n)
    for r in ranges:
        args =  'Arguments  = %s  %s\n' %(int(r[0]), int(r[1]))
        args += "Queue 1\n\n"
        jdlFile.write(args)
    jdlFile.close() 

    print('\ncd tmpSub && condor_submit submitJobs.jdl\n')


