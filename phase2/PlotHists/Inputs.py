import sys
import ROOT
sys.dont_write_bytecode = True
eosDir  ="/eos/cms/store/group/phys_egamma/ec/rverma/phase2"

#---------------
# Plotting 
#---------------
outPlotDir  = "%s/%s"%(eosDir, "plots")
#For plotting efficiency
forOverlay = {}
forOverlay["Phase2"] =ROOT.TFile.Open("%s/s3Hist/RelValTTbar_14TeV_Phase2Setup/Phase2_HLT_All.root"%eosDir)
forOverlay["L1"]     =ROOT.TFile.Open("%s/s3Hist/RelValTTbar_14TeV_Phase2Setup/Phase2_HLT_All.root"%eosDir)

forRatio = []
#forRatio.append(["EGamma_Run2023C", "EGamma_Run2022G"])
#forRatio.append(["EGamma0_Run2023C", "EGamma1_Run2023C"])
#forRatio.append(["HLT_Ele30_WPTight_Gsf/EGamma_Run2023C", "HLT_Ele32_WPTight_Gsf/EGamma_Run2023C"])


filters = []
filters.append("hltEle32WPTightGsfTrackIsoFilter")  
filters.append("hltEle32WPTightGsfTrackIsoL1SeededFilter")  
filters.append("hltEGL1SingleEGOrFilter")   
filters.append("hltEle32WPTightClusterShapeFilter") 
filters.append("hltEle32WPTightHEFilter")   
filters.append("hltEle32WPTightEcalIsoFilter")  
filters.append("hltEle32WPTightHcalIsoFilter")  
filters.append("hltEle32WPTightPixelMatchFilter")   
filters.append("hltEle32WPTightPMS2Filter") 
filters.append("hltEle32WPTightGsfOneOEMinusOneOPFilter")   
filters.append("hltEle32WPTightGsfDetaFilter")  
filters.append("hltEle32WPTightGsfDphiFilter")  
filters.append("hltEle32WPTightBestGsfNLayerITFilter")  
filters.append("hltEle32WPTightBestGsfChi2Filter")  
filters.append("hltEle32WPTightGsfTrackIsoFromL1TracksFilter")  

numPtEE = []
numPtEB = []
for f in filters:
    numPtEE.append("num_ele_pt_%s_EE"%f)
    numPtEB.append("num_ele_pt_%s_EB"%f)
numEta = []
for f in filters:
    numEta.append("num_ele_eta_%s"%f)
