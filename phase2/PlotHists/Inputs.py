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
forOverlay["Phase2"] =ROOT.TFile.Open("/eos/cms/store/group/phys_egamma/ec/rverma/phase2/s3Hist/TT_TuneCP5_14TeV-powheg-pythia8_L1New//all.root")
#forOverlay["Phase2"] =ROOT.TFile.Open("%s/s3Hist/RelValTTbar_14TeV_Phase2Setup/Phase2_HLT_All.root"%eosDir)
#forOverlay["L1"]     =ROOT.TFile.Open("%s/s3Hist/RelValTTbar_14TeV_TkElectron/Phase2_HLT_All.root"%eosDir)
#forOverlay["L1"]     =ROOT.TFile.Open("%s/s3Hist/RelValTTbar_14TeV_Q24/Phase2_HLT_All.root"%eosDir)

forRatio = []
#forRatio.append(["Phase2", "L1"])
#forRatio.append(["EGamma0_Run2023C", "EGamma1_Run2023C"])
#forRatio.append(["HLT_Ele30_WPTight_Gsf/EGamma_Run2023C", "HLT_Ele32_WPTight_Gsf/EGamma_Run2023C"])

filters = ['hltEGL1SeedsForSingleEleIsolatedFilter', 'hltEG32EtUnseededFilter', 'hltEle32WPTightClusterShapeUnseededFilter', 'hltEle32WPTightClusterShapeSigmavvUnseededFilter', 'hltEle32WPTightClusterShapeSigmawwUnseededFilter', 'hltEle32WPTightHgcalHEUnseededFilter', 'hltEle32WPTightHEUnseededFilter', 'hltEle32WPTightEcalIsoUnseededFilter', 'hltEle32WPTightHgcalIsoUnseededFilter', 'hltEle32WPTightHcalIsoUnseededFilter', 'hltEle32WPTightPixelMatchUnseededFilter', 'hltEle32WPTightPMS2UnseededFilter', 'hltEle32WPTightGsfOneOEMinusOneOPUnseededFilter', 'hltEle32WPTightGsfDetaUnseededFilter', 'hltEle32WPTightGsfDphiUnseededFilter', 'hltEle32WPTightBestGsfNLayerITUnseededFilter', 'hltEle32WPTightBestGsfChi2UnseededFilter', 'hltEle32WPTightGsfTrackIsoFromL1TracksUnseededFilter', 'hltEle32WPTightGsfTrackIsoUnseededFilter']
#filters = ['hltEGL1SeedsForSingleEleIsolatedFilter', 'hltEG32EtL1SeededFilter', 'hltEle32WPTightClusterShapeL1SeededFilter', 'hltEle32WPTightClusterShapeSigmavvL1SeededFilter', 'hltEle32WPTightClusterShapeSigmawwL1SeededFilter', 'hltEle32WPTightHgcalHEL1SeededFilter', 'hltEle32WPTightHEL1SeededFilter', 'hltEle32WPTightEcalIsoL1SeededFilter', 'hltEle32WPTightHgcalIsoL1SeededFilter', 'hltEle32WPTightHcalIsoL1SeededFilter', 'hltEle32WPTightPixelMatchL1SeededFilter', 'hltEle32WPTightPMS2L1SeededFilter', 'hltEle32WPTightGsfOneOEMinusOneOPL1SeededFilter', 'hltEle32WPTightGsfDetaL1SeededFilter', 'hltEle32WPTightGsfDphiL1SeededFilter', 'hltEle32WPTightBestGsfNLayerITL1SeededFilter', 'hltEle32WPTightBestGsfChi2L1SeededFilter', 'hltEle32WPTightGsfTrackIsoFromL1TracksL1SeededFilter', 'hltEle32WPTightGsfTrackIsoL1SeededFilter'] 

filters.append('l1tTkEmSingle51Filter')
filters.append('l1tTkEleSingle36Filter')
filters.append('l1tTkIsoEleSingle28Filter')

numPtEE = []
numPtEB = []
for f in filters:
    numPtEE.append("num_ele_pt_%s_EE"%f)
    numPtEB.append("num_ele_pt_%s_EB"%f)
numEta = []
for f in filters:
    numEta.append("num_ele_eta_%s"%f)
