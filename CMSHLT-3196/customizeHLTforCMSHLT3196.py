def customizeHLTforCMSHLT3196(process):
    for espLabel in [
        'hltESPChi2ChargeMeasurementEstimator30',
        'hltESPChi2ChargeMeasurementEstimator2000',
        'hltESPChi2ChargeMeasurementEstimator16',
    ]:
        esProd = getattr(process, espLabel)
        esProd.pTChargeCutThreshold = 15
        esProd.clusterChargeCut.refToPSet_ = 'HLTSiStripClusterChargeCutLoose'
    return process
