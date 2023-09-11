#!/usr/bin/env python

#RUN it like this
#python3 filename.py  inputFile.root   -o=outFile.root 

from array import array
import re
import argparse
import sys
import math
from DataFormats.FWLite import Events, Handle
import ROOT
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F
import json
import FWCore.ParameterSet.Config as cms
from CondCore.CondDB.CondDB_cfi import *
from PhysicsTools.PythonAnalysis import *
import time

def getListFilterPassedObj(filterName,hltsevt):
        eg_trig_objs = []
        #get a list of trigger objects that passed a given filter
        filterIndex = getFilterIndex(hltsevt,filterName)
        if (filterIndex < hltsevt.sizeFilters() ):
                for filterKey in hltsevt.filterKeys(filterIndex):
                        obj = hltsevt.getObjects()[filterKey]
                        eg_trig_objs.append(obj)
        return eg_trig_objs


#from https://github.com/cms-egamma/EgammaDAS2020/blob/solutions/test/egFWLiteExercise2a.py
def match_trig_objs(eta,phi,trig_objs,max_dr=0.1):    
    max_dr2 = max_dr*max_dr
    matched_objs = [obj for obj in trig_objs if ROOT.reco.deltaR2(eta,phi,obj.eta(),obj.phi()) < max_dr2]
    return matched_objs


#from https://github.com/Sam-Harper/usercode/blob/100XNtup/SHNtupliser/test/checkTrigsAOD.py
def getFilterIndex(trigEvt,filterName):
    for index in range(0,trigEvt.sizeFilters()):
        if filterName==trigEvt.filterLabel(index):
                #print 'filtername found' 
                return index
    return trigEvt.sizeFilters()


def get_genparts(genparts,pid=11,antipart=True,status=1):
    """                               
    returns a list of the gen particles matching the given criteria from hard process                                                                                                 
    might not work for all generators as depends on isHardProcess()                                                                                                                 
    """
    selected = []
    if genparts==None:
        return selected

    for part in genparts:
        pdg_id = part.pdgId()
        if pdg_id == pid or (antipart and abs(pdg_id) == abs(pid)):
            if part.isHardProcess():
                if status == 1:
                    selected.append(part)
    return selected


def match_to_gen(eta,phi,genparts,pid=11,antipart=True,max_dr=0.1,status=1):
    """ 
    Matches an eta,phi to gen level particle from the hard process                                                                                                                  
    might not work for all generaters as depends on isHardProcess()                                                                                                                  
    """
    best_match = None
    best_dr2 = max_dr*max_dr
    best_pt = -1
    selected_parts = get_genparts(genparts,pid,antipart,status)
    for part in selected_parts:
        dr2 = ROOT.reco.deltaR2(eta,phi,part.eta(),part.phi())
        if dr2 < best_dr2:
            best_match = part
            best_dr2 = dr2
            best_pt=part.pt()
    return best_match,best_dr2,best_pt


def getFilters(cmsPath):
    filts = []
    for fil in cmsPath.split(",")[0].split("+"):
        if "Filter" in fil:
            filts.append(fil.replace("process.", ""))
    return filts


if __name__ == "__main__":

    oldargv = sys.argv[:]
    sys.argv = [ '-b-' ]
    sys.argv = oldargv
    ROOT.gSystem.Load("libFWCoreFWLite.so");
    ROOT.gSystem.Load("libDataFormatsFWLite.so");
    ROOT.FWLiteEnabler.enable()

    parser = argparse.ArgumentParser(description='example e/gamma HLT analyser')
    parser.add_argument('in_filename',nargs="+",help='input filename')
    parser.add_argument("-o", "--output", help="Directs the output to a name of your choice")

    args = parser.parse_args()



    #ele_handle, ele_label = Handle("std::vector<trigger::EgammaObject>"), "hltEgammaHLTExtra"
    ele_handle, ele_label = Handle("std::vector<trigger::EgammaObject>"), "hltEgammaHLTExtra:Unseeded"
    hlt_handle, hlt_label = Handle("edm::TriggerResults"), "TriggerResults::HLTX"
    hltevt_handle, hltevt_label = Handle("trigger::TriggerEvent"), "hltTriggerSummaryAOD::HLTX"
    gen_handle, gen_label = Handle("std::vector<reco::GenParticle>"), "genParticles"

    to_remove=[]
    for file in args.in_filename:
        file_temp = ROOT.TFile(file)
        if ( file_temp.IsZombie() ) :
            to_remove.append(file)

    new_list = [x for x in args.in_filename if x not in to_remove]

    events = Events(new_list)

    #process.HLT_Ele32_WPTight_Unseeded = cms.Path(process.HLTBeginSequence+process.hltPreEle32WPTightUnseeded+process.HLTEle32WPTightUnseededSequence+process.HLTEndSequence)
    HLTEle32WPTightUnseededSequence = "cms.Sequence(process.HLTL1Sequence+process.hltEGL1SeedsForSingleEleIsolatedFilter+process.HLTDoFullUnpackingEgammaEcalSequence+process.HLTPFClusteringForEgammaUnseeded+process.HLTHgcalTiclPFClusteringForEgammaUnseeded+process.hltEgammaCandidatesWrapperUnseeded+process.hltEG32EtUnseededFilter+process.hltEle32WPTightClusterShapeUnseededFilter+process.hltEle32WPTightClusterShapeSigmavvUnseededFilter+process.hltEle32WPTightClusterShapeSigmawwUnseededFilter+process.hltEle32WPTightHgcalHEUnseededFilter+process.HLTDoLocalHcalSequence+process.HLTFastJetForEgamma+process.hltEle32WPTightHEUnseededFilter+process.hltEle32WPTightEcalIsoUnseededFilter+process.hltEle32WPTightHgcalIsoUnseededFilter+process.HLTPFHcalClusteringForEgamma+process.hltEle32WPTightHcalIsoUnseededFilter+process.HLTElePixelMatchUnseededSequence+process.hltEle32WPTightPixelMatchUnseededFilter+process.hltEle32WPTightPMS2UnseededFilter+process.HLTGsfElectronUnseededSequence+process.hltEle32WPTightGsfOneOEMinusOneOPUnseededFilter+process.hltEle32WPTightGsfDetaUnseededFilter+process.hltEle32WPTightGsfDphiUnseededFilter+process.hltEle32WPTightBestGsfNLayerITUnseededFilter+process.hltEle32WPTightBestGsfChi2UnseededFilter+process.hltEle32WPTightGsfTrackIsoFromL1TracksUnseededFilter+process.HLTTrackingV61Sequence+process.hltEle32WPTightGsfTrackIsoUnseededFilter, process.HLTEle32WPTightUnseededTask)"
    #HLTEle32WPTightL1SeededSequence = "cms.Sequence(process.HLTL1Sequence+process.hltEGL1SeedsForSingleEleIsolatedFilter+process.HLTDoFullUnpackingEgammaEcalL1SeededSequence+process.HLTPFClusteringForEgammaL1Seeded+process.HLTHgcalTiclPFClusteringForEgammaL1Seeded+process.hltEgammaCandidatesWrapperL1Seeded+process.hltEG32EtL1SeededFilter+process.hltEle32WPTightClusterShapeL1SeededFilter+process.hltEle32WPTightClusterShapeSigmavvL1SeededFilter+process.hltEle32WPTightClusterShapeSigmawwL1SeededFilter+process.hltEle32WPTightHgcalHEL1SeededFilter+process.HLTDoLocalHcalSequence+process.HLTFastJetForEgamma+process.hltEle32WPTightHEL1SeededFilter+process.hltEle32WPTightEcalIsoL1SeededFilter+process.hltEle32WPTightHgcalIsoL1SeededFilter+process.HLTPFHcalClusteringForEgamma+process.hltEle32WPTightHcalIsoL1SeededFilter+process.HLTElePixelMatchL1SeededSequence+process.hltEle32WPTightPixelMatchL1SeededFilter+process.hltEle32WPTightPMS2L1SeededFilter+process.HLTGsfElectronL1SeededSequence+process.hltEle32WPTightGsfOneOEMinusOneOPL1SeededFilter+process.hltEle32WPTightGsfDetaL1SeededFilter+process.hltEle32WPTightGsfDphiL1SeededFilter+process.hltEle32WPTightBestGsfNLayerITL1SeededFilter+process.hltEle32WPTightBestGsfChi2L1SeededFilter+process.hltEle32WPTightGsfTrackIsoFromL1TracksL1SeededFilter+process.HLTTrackingV61Sequence+process.hltEle32WPTightGsfTrackIsoL1SeededFilter, process.HLTEle32WPTightL1SeededTaski)"
    filt32 = getFilters(HLTEle32WPTightUnseededSequence)
    #filt32 = getFilters(HLTEle32WPTightL1SeededSequence)
    filt32.append("l1tTkEmSingle51Filter")
    filt32.append("l1tTkEleSingle36Filter")
    filt32.append("l1tTkIsoEleSingle28Filter")
    #filt32 = ['hltEG32EtUnseededFilter']
    print(filt32)
    ptBins  = array('d', [5,10,15,20,22,26,28,30,32,34,36,38,40,45,50,60,80,100,150,250,500])
    #ptBins  = array('d', [5,10,15,20,22,26,28,30,32,34,36,38,40,45,50,60,80,100,150,250,500])
    etaBins = array('d', [-2.5,-2.4,-2.3,-2.2,-2.1,-2.0,-1.9,-1.8,-1.7,-1.56,-1.44,-1.3,-1.2,-1.1,-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.44,1.56,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5])
    den_ele_eta_ele32   = ROOT.TH1D("den_ele_eta", "#eta",len(etaBins)-1, etaBins)
    den_ele_pt_EB       = ROOT.TH1D("den_ele_pt_EB","pT", len(ptBins)-1,  ptBins)
    den_ele_pt_EE       = ROOT.TH1D("den_ele_pt_EE","pT", len(ptBins)-1,  ptBins)

    for f32 in filt32:
        #declare histograms
        exec('num_ele_eta_%s     = ROOT.TH1D("num_ele_eta_%s",   "#eta", %s, %s)'%(f32, f32, len(etaBins)-1, etaBins))
        exec('num_ele_pt_%s_EB   = ROOT.TH1D("num_ele_pt_%s_EB", "pT",   %s, %s)'%(f32, f32, len(ptBins)-1,  ptBins))
        exec('num_ele_pt_%s_EE   = ROOT.TH1D("num_ele_pt_%s_EE", "pT",   %s, %s)'%(f32, f32, len(ptBins)-1,  ptBins))

    percent_step = 1
    start_time = time.time() 
    total_entries = events.size()  
    for event_nr,event in enumerate(events):
        current_percent = (event_nr + 1) / total_entries * 100
        if current_percent % percent_step == 0:
           elapsed_time = time.time()-start_time
           est_finish = "n/a"
           if event_nr!=0 or elapsed_time==0:
                remaining = float(events.size()-event_nr)/event_nr*elapsed_time 
                est_finish = time.ctime(remaining+start_time+elapsed_time)
                print("{} / {} time: {:.1f}s, est finish {}".format(event_nr+1,events.size(),elapsed_time,est_finish))

        event.getByLabel(ele_label,ele_handle)
        event.getByLabel(hlt_label,hlt_handle)
        event.getByLabel(hltevt_label,hltevt_handle)
        event.getByLabel(gen_label,gen_handle)

        eles = ele_handle.product()
        hlts = hlt_handle.product()
        hltsevt = hltevt_handle.product()
        genobjs=gen_handle.product()

        trigdict=event.object().triggerNames(hlts).triggerNames()
        #Get trigger objects
        for f32 in filt32:
            exec('eg_trig_objs_%s= getListFilterPassedObj("%s",hltsevt)'%(f32, f32))
        #Loop over egamma candiates
        for eg in eles:
            gen_match_ele = match_to_gen(eg.eta(),eg.phi(),gen_handle.product(),pid=11)[0]
            gen_pt = match_to_gen(eg.eta(),eg.phi(),gen_handle.product(),pid=11)[2]
            if (gen_match_ele):
                if (abs(eg.eta()) > 1.44 and abs(eg.eta()) < 1.56): continue 
                if (gen_pt<30.0): continue
                for ind, f32 in enumerate(filt32):
                    exec('matched_objs_%s = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_%s)'%(f32, f32))
                    nMatched = eval('len(matched_objs_%s)'%f32)
                    if (abs(eg.eta()) <= 1.44): 
                        if ind==0: 
                            den_ele_pt_EB.Fill(gen_pt)
                        if nMatched> 0:
                            exec('num_ele_pt_%s_EB.Fill(%s)'%(f32, gen_pt))
                    if (abs(eg.eta())>=1.56): 
                        if ind==0:
                            den_ele_pt_EE.Fill(gen_pt)
                        if nMatched> 0:
                            exec('num_ele_pt_%s_EE.Fill(%s)'%(f32, gen_pt))
                    if ind==0:
                        den_ele_eta_ele32.Fill(eg.eta())
                    if nMatched> 0:
                        exec('num_ele_eta_%s.Fill(%s)'%(f32, eg.eta()))
                    
    output_file = TFile( args.output, 'recreate' )
    den_ele_eta_ele32.Write()
    den_ele_pt_EB.Write()
    den_ele_pt_EE.Write()
    for f32 in filt32:
        exec('num_ele_eta_%s.Write()'%f32)
        exec('num_ele_pt_%s_EB.Write()'%f32)
        exec('num_ele_pt_%s_EE.Write()'%f32)
    output_file.Close()
