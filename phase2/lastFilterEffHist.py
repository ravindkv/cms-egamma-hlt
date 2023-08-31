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

    den_ele_eta_ele32 = ROOT.TH1D("den_ele_eta",";#eta;nEntries",40,-4,4)
    den_ele_pt_EB = ROOT.TH1D("den_ele_pt_EB",";pT;nEntries",100,0,500)
    den_ele_pt_EE = ROOT.TH1D("den_ele_pt_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfTrackIsoFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfTrackIsoFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfTrackIsoL1SeededFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfTrackIsoL1SeededFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEGL1SingleEGOrFilter = ROOT.TH1D("num_ele_eta_hltEGL1SingleEGOrFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEGL1SingleEGOrFilter_EB = ROOT.TH1D("num_ele_pt_hltEGL1SingleEGOrFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEGL1SingleEGOrFilter_EE = ROOT.TH1D("num_ele_pt_hltEGL1SingleEGOrFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightClusterShapeFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightClusterShapeFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightClusterShapeFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightClusterShapeFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightClusterShapeFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightClusterShapeFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightHEFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightHEFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightHEFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightHEFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightHEFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightHEFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightEcalIsoFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightEcalIsoFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightEcalIsoFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightEcalIsoFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightEcalIsoFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightEcalIsoFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightHcalIsoFilter = ROOT.TH1D("num_ele_eta_hltEle32WPTightHcalIsoFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightHcalIsoFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightHcalIsoFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightHcalIsoFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightHcalIsoFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightPixelMatchFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightPixelMatchFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightPixelMatchFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightPixelMatchFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightPixelMatchFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightPixelMatchFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightPMS2Filter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightPMS2Filter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightPMS2Filter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightPMS2Filter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightPMS2Filter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightPMS2Filter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfOneOEMinusOneOPFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfOneOEMinusOneOPFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfDetaFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfDetaFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfDetaFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfDetaFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfDetaFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfDetaFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfDphiFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfDphiFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfDphiFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfDphiFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfDphiFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfDphiFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightBestGsfNLayerITFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightBestGsfNLayerITFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightBestGsfChi2Filter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightBestGsfChi2Filter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EE",";pT;nEntries",100,0,500)

    num_ele_eta_hltEle32WPTightGsfTrackIsoFromL1TracksFilter  = ROOT.TH1D("num_ele_eta_hltEle32WPTightGsfTrackIsoFromL1TracksFilter",";#eta;nEntries",40,-4,4)
    num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EB = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EB",";pT;nEntries",100,0,500)
    num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EE = ROOT.TH1D("num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EE",";pT;nEntries",100,0,500)

    hcalclusIsolation = ROOT.TH1D("hcalclusIsolation", ";hcalclusIsolation;nEntries",300,0,300)

    start_time = time.time() 
   
    for event_nr,event in enumerate(events):

        if event_nr%100==0:
           elapsed_time = time.time()-start_time
           est_finish = "n/a"
           if event_nr!=0 or elapsed_time==0:
                remaining = float(events.size()-event_nr)/event_nr*elapsed_time 
                est_finish = time.ctime(remaining+start_time+elapsed_time)
                print("{} / {} time: {:.1f}s, est finish {}".format(event_nr,events.size(),elapsed_time,est_finish))

        event.getByLabel(ele_label,ele_handle)
        event.getByLabel(hlt_label,hlt_handle)
        event.getByLabel(hltevt_label,hltevt_handle)
        event.getByLabel(gen_label,gen_handle)

        eles = ele_handle.product()
        hlts = hlt_handle.product()
        hltsevt = hltevt_handle.product()
        genobjs=gen_handle.product()

        trigdict=event.object().triggerNames(hlts).triggerNames()

        eg_trig_objs_hltEGL1SingleEGOrFilter = getListFilterPassedObj("hltEGL1SeedsForSingleEleIsolatedFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfTrackIsoFilter = getListFilterPassedObj("hltEle32WPTightGsfTrackIsoUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfTrackIsoL1SeededFilter = getListFilterPassedObj("hltEle32WPTightGsfTrackIsoL1SeededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightClusterShapeFilter = getListFilterPassedObj("hltEle32WPTightClusterShapeUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightHEFilter = getListFilterPassedObj("hltEle32WPTightHEUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightEcalIsoFilter = getListFilterPassedObj("hltEle32WPTightEcalIsoUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightHcalIsoFilter = getListFilterPassedObj("hltEle32WPTightHcalIsoUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightPixelMatchFilter  = getListFilterPassedObj("hltEle32WPTightPixelMatchUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightPMS2Filter  = getListFilterPassedObj("hltEle32WPTightPMS2UnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfOneOEMinusOneOPFilter  = getListFilterPassedObj("hltEle32WPTightGsfOneOEMinusOneOPUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfDetaFilter  = getListFilterPassedObj("hltEle32WPTightGsfDetaUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfDphiFilter  = getListFilterPassedObj("hltEle32WPTightGsfDphiUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightBestGsfNLayerITFilter  = getListFilterPassedObj("hltEle32WPTightBestGsfNLayerITUnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightBestGsfChi2Filter  = getListFilterPassedObj("hltEle32WPTightBestGsfChi2UnseededFilter",hltsevt)
        eg_trig_objs_hltEle32WPTightGsfTrackIsoFromL1TracksFilter  = getListFilterPassedObj("hltEle32WPTightGsfTrackIsoFromL1TracksUnseededFilter",hltsevt)

        for eg in eles:
          #print ("in the ele loop.. found ele, pt = ", eg.pt() )      

          #check if the electron matches with any trigger object that passed a given filter 
          matched_objs_hltEle32WPTightGsfTrackIsoFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfTrackIsoFilter)
          nmatch_hltEle32WPTightGsfTrackIsoFilter = len(matched_objs_hltEle32WPTightGsfTrackIsoFilter)
          matched_objs_hltEle32WPTightGsfTrackIsoL1SeededFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfTrackIsoL1SeededFilter)
          nmatch_hltEle32WPTightGsfTrackIsoL1SeededFilter = len(matched_objs_hltEle32WPTightGsfTrackIsoL1SeededFilter)

          matched_objs_hltEGL1SingleEGOrFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEGL1SingleEGOrFilter)
          nmatch_hltEGL1SingleEGOrFilter = len(matched_objs_hltEGL1SingleEGOrFilter)

          matched_objs_hltEle32WPTightClusterShapeFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightClusterShapeFilter)
          nmatch_hltEle32WPTightClusterShapeFilter = len(matched_objs_hltEle32WPTightClusterShapeFilter)

          matched_objs_hltEle32WPTightHEFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightHEFilter)
          nmatch_hltEle32WPTightHEFilter = len(matched_objs_hltEle32WPTightHEFilter)

          matched_objs_hltEle32WPTightEcalIsoFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightEcalIsoFilter)
          nmatch_hltEle32WPTightEcalIsoFilter = len(matched_objs_hltEle32WPTightEcalIsoFilter)

          matched_objs_hltEle32WPTightHcalIsoFilter = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightHcalIsoFilter)
          nmatch_hltEle32WPTightHcalIsoFilter = len(matched_objs_hltEle32WPTightHcalIsoFilter)

          matched_objs_hltEle32WPTightPixelMatchFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightPixelMatchFilter )
          nmatch_hltEle32WPTightPixelMatchFilter  = len(matched_objs_hltEle32WPTightPixelMatchFilter)

          matched_objs_hltEle32WPTightPMS2Filter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightPMS2Filter )
          nmatch_hltEle32WPTightPMS2Filter  = len(matched_objs_hltEle32WPTightPMS2Filter)

          matched_objs_hltEle32WPTightGsfOneOEMinusOneOPFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfOneOEMinusOneOPFilter )
          nmatch_hltEle32WPTightGsfOneOEMinusOneOPFilter  = len(matched_objs_hltEle32WPTightGsfOneOEMinusOneOPFilter)

          matched_objs_hltEle32WPTightGsfDetaFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfDetaFilter )
          nmatch_hltEle32WPTightGsfDetaFilter  = len(matched_objs_hltEle32WPTightGsfDetaFilter)

          matched_objs_hltEle32WPTightGsfDphiFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfDphiFilter )
          nmatch_hltEle32WPTightGsfDphiFilter  = len(matched_objs_hltEle32WPTightGsfDphiFilter)

          matched_objs_hltEle32WPTightBestGsfNLayerITFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightBestGsfNLayerITFilter )
          nmatch_hltEle32WPTightBestGsfNLayerITFilter  = len(matched_objs_hltEle32WPTightBestGsfNLayerITFilter)

          matched_objs_hltEle32WPTightBestGsfChi2Filter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightBestGsfChi2Filter )
          nmatch_hltEle32WPTightBestGsfChi2Filter  = len(matched_objs_hltEle32WPTightBestGsfChi2Filter)

          matched_objs_hltEle32WPTightGsfTrackIsoFromL1TracksFilter  = match_trig_objs(eg.eta(),eg.phi(),eg_trig_objs_hltEle32WPTightGsfTrackIsoFromL1TracksFilter )
          nmatch_hltEle32WPTightGsfTrackIsoFromL1TracksFilter  = len(matched_objs_hltEle32WPTightGsfTrackIsoFromL1TracksFilter)
          
          gen_match_ele = match_to_gen(eg.eta(),eg.phi(),gen_handle.product(),pid=11)[0]
          gen_pt = match_to_gen(eg.eta(),eg.phi(),gen_handle.product(),pid=11)[2]
          if (gen_match_ele):

                  if (eg.pt()>=40.0 and (abs(eg.eta()) < 1.44) ):
                          hcalclusIsolation.Fill(eg.var("hltEgammaHcalPFClusterIsoUnseeded"))

                  #print ("this ele is gen matched")
                  ## Fill denominators
                  if (abs(eg.eta()) < 1.44 ): den_ele_pt_EB.Fill(gen_pt)
                  if ( (abs(eg.eta())>1.56) and (abs(eg.eta())<2.4) ): den_ele_pt_EE.Fill(gen_pt)
                  if (eg.pt()>=40.0 and eg.pt()<500.0): 
                          den_ele_eta_ele32.Fill(eg.eta())

                  ## Fill numerators
                  if (nmatch_hltEle32WPTightClusterShapeFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightClusterShapeFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightClusterShapeFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightClusterShapeFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightHEFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightHEFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightHEFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightHEFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightEcalIsoFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightEcalIsoFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightEcalIsoFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightEcalIsoFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightHcalIsoFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightHcalIsoFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightHcalIsoFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightHcalIsoFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightPixelMatchFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightPixelMatchFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightPixelMatchFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightPixelMatchFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightPMS2Filter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightPMS2Filter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightPMS2Filter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightPMS2Filter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightGsfOneOEMinusOneOPFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfOneOEMinusOneOPFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightGsfDetaFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfDetaFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfDetaFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfDetaFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightGsfDphiFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfDphiFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfDphiFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfDphiFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightBestGsfNLayerITFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightBestGsfNLayerITFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightBestGsfChi2Filter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightBestGsfChi2Filter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightGsfTrackIsoFromL1TracksFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfTrackIsoFromL1TracksFilter.Fill(eg.eta())

                  if (nmatch_hltEle32WPTightGsfTrackIsoFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfTrackIsoFilter.Fill(eg.eta())
                  if (nmatch_hltEle32WPTightGsfTrackIsoL1SeededFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500): 
                        num_ele_eta_hltEle32WPTightGsfTrackIsoL1SeededFilter.Fill(eg.eta())

                  if (nmatch_hltEGL1SingleEGOrFilter>0) :
                      if (abs(eg.eta()) < 1.44 ): num_ele_pt_hltEGL1SingleEGOrFilter_EB.Fill(gen_pt)
                      if ( (abs(eg.eta()) > 1.56 ) and (abs(eg.eta())<2.4)): num_ele_pt_hltEGL1SingleEGOrFilter_EE.Fill(gen_pt)
                      if (eg.pt()>=40.0 and eg.pt()<500.0): 
                        num_ele_eta_hltEGL1SingleEGOrFilter.Fill(eg.eta())


    output_file = TFile( args.output, 'recreate' )

    den_ele_eta_ele32.Write()
    den_ele_pt_EB.Write()
    den_ele_pt_EE.Write()

    num_ele_eta_hltEle32WPTightGsfTrackIsoFilter.Write()
    num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfTrackIsoFilter_EE.Write()

    num_ele_eta_hltEle32WPTightGsfTrackIsoL1SeededFilter.Write()
    num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfTrackIsoL1SeededFilter_EE.Write()
    num_ele_eta_hltEGL1SingleEGOrFilter.Write()
    num_ele_pt_hltEGL1SingleEGOrFilter_EB.Write()
    num_ele_pt_hltEGL1SingleEGOrFilter_EE.Write()

    num_ele_pt_hltEle32WPTightClusterShapeFilter_EB.Write()
    num_ele_pt_hltEle32WPTightClusterShapeFilter_EE.Write()
    num_ele_eta_hltEle32WPTightClusterShapeFilter.Write()

    num_ele_pt_hltEle32WPTightHEFilter_EB.Write()
    num_ele_pt_hltEle32WPTightHEFilter_EE.Write()
    num_ele_eta_hltEle32WPTightHEFilter.Write()

    num_ele_pt_hltEle32WPTightEcalIsoFilter_EB.Write()
    num_ele_pt_hltEle32WPTightEcalIsoFilter_EE.Write()
    num_ele_eta_hltEle32WPTightEcalIsoFilter.Write()

    num_ele_pt_hltEle32WPTightHcalIsoFilter_EB.Write()
    num_ele_pt_hltEle32WPTightHcalIsoFilter_EE.Write()
    num_ele_eta_hltEle32WPTightHcalIsoFilter.Write()

    num_ele_pt_hltEle32WPTightPixelMatchFilter_EB.Write()
    num_ele_pt_hltEle32WPTightPixelMatchFilter_EE.Write()
    num_ele_eta_hltEle32WPTightPixelMatchFilter.Write()

    num_ele_pt_hltEle32WPTightPMS2Filter_EB.Write()
    num_ele_pt_hltEle32WPTightPMS2Filter_EE.Write()
    num_ele_eta_hltEle32WPTightPMS2Filter.Write()

    num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfOneOEMinusOneOPFilter_EE.Write()
    num_ele_eta_hltEle32WPTightGsfOneOEMinusOneOPFilter.Write()

    num_ele_pt_hltEle32WPTightGsfDetaFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfDetaFilter_EE.Write()
    num_ele_eta_hltEle32WPTightGsfDetaFilter.Write()

    num_ele_pt_hltEle32WPTightGsfDphiFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfDphiFilter_EE.Write()
    num_ele_eta_hltEle32WPTightGsfDphiFilter.Write()

    num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EB.Write()
    num_ele_pt_hltEle32WPTightBestGsfNLayerITFilter_EE.Write()
    num_ele_eta_hltEle32WPTightBestGsfNLayerITFilter.Write()

    num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EB.Write()
    num_ele_pt_hltEle32WPTightBestGsfChi2Filter_EE.Write()
    num_ele_eta_hltEle32WPTightBestGsfChi2Filter.Write()

    num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EB.Write()
    num_ele_pt_hltEle32WPTightGsfTrackIsoFromL1TracksFilter_EE.Write()
    num_ele_eta_hltEle32WPTightGsfTrackIsoFromL1TracksFilter.Write()

    hcalclusIsolation.Write()

    output_file.Close()
