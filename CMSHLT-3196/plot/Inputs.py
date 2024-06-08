import sys
import ROOT
sys.dont_write_bytecode = True
#eosDir  ="/eos/cms/store/group/phys_egamma/ec/rverma/phase2"
eosDir  ="./"
histDir = "/afs/cern.ch/work/r/rverma/public/cms-egamma-hlt/CMSHLT-3196/CMSSW_13_0_10/src"

#---------------
# Plotting 
#---------------
outPlotDir  = "%s/%s"%(eosDir, "plots")
#For plotting efficiency
forOverlay = {}
forOverlay["Default"] = "hist.root"
forOverlay["CCC"] = "hist_CCC.root"

forRatio = []
forRatio.append(["Default", "CCC"])

varNames = []
varNames.append("eg_et")
varNames.append("eg_pms2")
varNames.append("eg_trkIsol")
varNames.append("eg_trkChi2")
varNames.append("eg_trkMissHits")
varNames.append("eg_trkValidHits")
varNames.append("eg_trkNrLayerIT")
varNames.append("eg_trkDEta")
varNames.append("eg_trkDEtaSeed")
varNames.append("eg_trkDPhi")
