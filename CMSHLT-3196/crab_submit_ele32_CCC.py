from WMCore.Configuration import Configuration
config = Configuration()
config.section_('General')
config.General.workArea = 'crab_edm_CCC'
config.General.requestName = '2023_Run2023D0v1'
config.General.transferOutputs = True
#config.General.transferLogs = True
config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.allowUndistributedCMSSW = True
config.JobType.sendExternalFolder = True
config.JobType.psetName = './data_hlt_CCC.py'
#config.JobType.outputFiles= ['detailedInfo.log']
config.JobType.numCores=4
config.section_('Data')
config.Data.outLFNDirBase = '/store/group/phys_egamma/tnpTuples/rverma/crab_bpix_ele32/2023/data/'
config.Data.inputDataset = '/EGamma0/Run2023D-v1/RAW'
#config.Data.lumiMask = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'
config.Data.allowNonValidInputDataset = True
config.Data.unitsPerJob = 35
config.Data.splitting = 'LumiBased'
config.Data.inputDBS = 'global'
config.Data.publication = False
config.section_('Site')
config.Site.storageSite = 'T2_CH_CERN'
config.section_('User')
config.section_('Debug')

