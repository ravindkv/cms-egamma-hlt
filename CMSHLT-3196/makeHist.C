#include <iostream>
#include <vector>
#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TCanvas.h>
#include <TLegend.h>

void makeHist() {
    gROOT->SetBatch(true);
    // Open the ROOT file
    //TFile *file = TFile::Open("ntup_CCC.root");
    TFile *file = TFile::Open("ntup.root");
    if (!file || file->IsZombie()) {
        std::cerr << "Error opening file" << std::endl;
        //return 1;
    }

    //TFile* fOut = new TFile("hist_CCC.root", "RECREATE");
    TFile* fOut = new TFile("hist.root", "RECREATE");
    // Access the tree
    TTree *tree = (TTree*)file->Get("egHLTRun3Tree"); // Replace with the actual tree name

    // Variables to hold the branch data
    UInt_t           nrEgs;
    Float_t         eg_et[100];   //[nrEgs]
    Float_t         eg_energy[100];   //[nrEgs]
    Float_t         eg_rawEnergy[100];   //[nrEgs]
    Float_t         eg_eta[100];   //[nrEgs]
    Float_t         eg_phi[100];   //[nrEgs]
    Float_t         eg_phiWidth[100];   //[nrEgs]
    Float_t         eg_sigmaIEtaIEta[100];   //[nrEgs]
    Float_t         eg_sigmaIPhiIPhi[100];   //[nrEgs]
    Float_t         eg_sigmaIEtaIEtaNoise[100];   //[nrEgs]
    Float_t         eg_sigmaIPhiIPhiNoise[100];   //[nrEgs]
    Float_t         eg_ecalPFIsol[100];   //[nrEgs]
    Float_t         eg_hcalPFIsol[100];   //[nrEgs]
    Float_t         eg_trkIsol[100];   //[nrEgs]
    Float_t         eg_trkChi2[100];   //[nrEgs]
    Float_t         eg_trkMissHits[100];   //[nrEgs]
    Float_t         eg_trkValidHits[100];   //[nrEgs]
    Float_t         eg_invESeedInvP[100];   //[nrEgs]
    Float_t         eg_invEInvP[100];   //[nrEgs]
    Float_t         eg_trkDEta[100];   //[nrEgs]
    Float_t         eg_trkDEtaSeed[100];   //[nrEgs]
    Float_t         eg_trkDPhi[100];   //[nrEgs]
    Float_t         eg_trkNrLayerIT[100];   //[nrEgs]
    Float_t         eg_pms2[100];   //[nrEgs]
    Float_t         eg_hcalHForHoverE[100];   //[nrEgs]
    Float_t         eg_bestTrkChi2[100];   //[nrEgs]
    Float_t         eg_bestTrkDEta[100];   //[nrEgs]
    Float_t         eg_bestTrkDEtaSeed[100];   //[nrEgs]
    Float_t         eg_bestTrkDPhi[100];   //[nrEgs]
    Float_t         eg_bestTrkMissHits[100];   //[nrEgs]
    Float_t         eg_bestTrkNrLayerIT[100];   //[nrEgs]
    Float_t         eg_bestTrkESeedInvP[100];   //[nrEgs]
    Float_t         eg_bestTrkInvEInvP[100];   //[nrEgs]
    Float_t         eg_bestTrkValitHits[100];   //[nrEgs]
    Float_t         eg_clusterMaxDR[100];   //[nrEgs]
    Float_t         eg_r9Frac[100];   //[nrEgs]
    Float_t         eg_r9Full[100];   //[nrEgs]

    TBranch        *b_nrEgs;   //!
    TBranch        *b_eg_et;   //!
    TBranch        *b_eg_energy;   //!
    TBranch        *b_eg_rawEnergy;   //!
    TBranch        *b_eg_eta;   //!
    TBranch        *b_eg_phi;   //!
    TBranch        *b_eg_phiWidth;   //!
    TBranch        *b_eg_sigmaIEtaIEta;   //!
    TBranch        *b_eg_sigmaIPhiIPhi;   //!
    TBranch        *b_eg_sigmaIEtaIEtaNoise;   //!
    TBranch        *b_eg_sigmaIPhiIPhiNoise;   //!
    TBranch        *b_eg_ecalPFIsol;   //!
    TBranch        *b_eg_hcalPFIsol;   //!
    TBranch        *b_eg_trkIsol;   //!
    TBranch        *b_eg_trkChi2;   //!
    TBranch        *b_eg_trkMissHits;   //!
    TBranch        *b_eg_trkValidHits;   //!
    TBranch        *b_eg_invESeedInvP;   //!
    TBranch        *b_eg_invEInvP;   //!
    TBranch        *b_eg_trkDEta;   //!
    TBranch        *b_eg_trkDEtaSeed;   //!
    TBranch        *b_eg_trkDPhi;   //!
    TBranch        *b_eg_trkNrLayerIT;   //!
    TBranch        *b_eg_pms2;   //!
    TBranch        *b_eg_hcalHForHoverE;   //!
    TBranch        *b_eg_bestTrkChi2;   //!
    TBranch        *b_eg_bestTrkDEta;   //!
    TBranch        *b_eg_bestTrkDEtaSeed;   //!
    TBranch        *b_eg_bestTrkDPhi;   //!
    TBranch        *b_eg_bestTrkMissHits;   //!
    TBranch        *b_eg_bestTrkNrLayerIT;   //!
    TBranch        *b_eg_bestTrkESeedInvP;   //!
    TBranch        *b_eg_bestTrkInvEInvP;   //!
    TBranch        *b_eg_bestTrkValitHits;   //!
    TBranch        *b_eg_clusterMaxDR;   //!
    TBranch        *b_eg_r9Frac;   //!
    TBranch        *b_eg_r9Full;   //!

    tree->SetBranchStatus("*",0);
    tree->SetBranchStatus("eg_*",1);
    tree->SetBranchStatus("nrEgs",1);

    tree->SetBranchAddress("nrEgs", &nrEgs, &b_nrEgs);
    tree->SetBranchAddress("eg_et", eg_et, &b_eg_et);
    tree->SetBranchAddress("eg_energy", eg_energy, &b_eg_energy);
    tree->SetBranchAddress("eg_rawEnergy", eg_rawEnergy, &b_eg_rawEnergy);
    tree->SetBranchAddress("eg_eta", eg_eta, &b_eg_eta);
    tree->SetBranchAddress("eg_phi", eg_phi, &b_eg_phi);
    tree->SetBranchAddress("eg_phiWidth", eg_phiWidth, &b_eg_phiWidth);
    tree->SetBranchAddress("eg_sigmaIEtaIEta", eg_sigmaIEtaIEta, &b_eg_sigmaIEtaIEta);
    tree->SetBranchAddress("eg_sigmaIPhiIPhi", eg_sigmaIPhiIPhi, &b_eg_sigmaIPhiIPhi);
    tree->SetBranchAddress("eg_sigmaIEtaIEtaNoise", eg_sigmaIEtaIEtaNoise, &b_eg_sigmaIEtaIEtaNoise);
    tree->SetBranchAddress("eg_sigmaIPhiIPhiNoise", eg_sigmaIPhiIPhiNoise, &b_eg_sigmaIPhiIPhiNoise);
    tree->SetBranchAddress("eg_ecalPFIsol", eg_ecalPFIsol, &b_eg_ecalPFIsol);
    tree->SetBranchAddress("eg_hcalPFIsol", eg_hcalPFIsol, &b_eg_hcalPFIsol);
    tree->SetBranchAddress("eg_trkIsol", eg_trkIsol, &b_eg_trkIsol);
    tree->SetBranchAddress("eg_trkChi2", eg_trkChi2, &b_eg_trkChi2);
    tree->SetBranchAddress("eg_trkMissHits", eg_trkMissHits, &b_eg_trkMissHits);
    tree->SetBranchAddress("eg_trkValidHits", eg_trkValidHits, &b_eg_trkValidHits);
    tree->SetBranchAddress("eg_invESeedInvP", eg_invESeedInvP, &b_eg_invESeedInvP);
    tree->SetBranchAddress("eg_invEInvP", eg_invEInvP, &b_eg_invEInvP);
    tree->SetBranchAddress("eg_trkDEta", eg_trkDEta, &b_eg_trkDEta);
    tree->SetBranchAddress("eg_trkDEtaSeed", eg_trkDEtaSeed, &b_eg_trkDEtaSeed);
    tree->SetBranchAddress("eg_trkDPhi", eg_trkDPhi, &b_eg_trkDPhi);
    tree->SetBranchAddress("eg_trkNrLayerIT", eg_trkNrLayerIT, &b_eg_trkNrLayerIT);
    tree->SetBranchAddress("eg_pms2", eg_pms2, &b_eg_pms2);
    tree->SetBranchAddress("eg_hcalHForHoverE", eg_hcalHForHoverE, &b_eg_hcalHForHoverE);
    tree->SetBranchAddress("eg_bestTrkChi2", eg_bestTrkChi2, &b_eg_bestTrkChi2);
    tree->SetBranchAddress("eg_bestTrkDEta", eg_bestTrkDEta, &b_eg_bestTrkDEta);
    tree->SetBranchAddress("eg_bestTrkDEtaSeed", eg_bestTrkDEtaSeed, &b_eg_bestTrkDEtaSeed);
    tree->SetBranchAddress("eg_bestTrkDPhi", eg_bestTrkDPhi, &b_eg_bestTrkDPhi);
    tree->SetBranchAddress("eg_bestTrkMissHits", eg_bestTrkMissHits, &b_eg_bestTrkMissHits);
    tree->SetBranchAddress("eg_bestTrkNrLayerIT", eg_bestTrkNrLayerIT, &b_eg_bestTrkNrLayerIT);
    tree->SetBranchAddress("eg_bestTrkESeedInvP", eg_bestTrkESeedInvP, &b_eg_bestTrkESeedInvP);
    tree->SetBranchAddress("eg_bestTrkInvEInvP", eg_bestTrkInvEInvP, &b_eg_bestTrkInvEInvP);
    tree->SetBranchAddress("eg_bestTrkValitHits", eg_bestTrkValitHits, &b_eg_bestTrkValitHits);
    tree->SetBranchAddress("eg_clusterMaxDR", eg_clusterMaxDR, &b_eg_clusterMaxDR);
    tree->SetBranchAddress("eg_r9Frac", eg_r9Frac, &b_eg_r9Frac);
    tree->SetBranchAddress("eg_r9Full", eg_r9Full, &b_eg_r9Full);

    std::map<string, TH1F*> hMap;
    map<string, vector<float>> varBins;
    varBins["eg_et"] = {50, 0.0, 500.0};
    varBins["eg_pms2"] = {50, 0.0, 1000.0};
    varBins["eg_trkIsol"] = {50, 0.0, 25.0};
    varBins["eg_trkChi2"] = {50, 0.0, 25.0};
    varBins["eg_trkMissHits"] = {50, 0.0, 10.0};
    varBins["eg_trkValidHits"] = {50, 0.0, 50.0};
    varBins["eg_trkNrLayerIT"] = {50, 0.0, 10.0};
    varBins["eg_trkDEta"] = {50, 0.0, 0.01};
    varBins["eg_trkDEtaSeed"] = {50, 0.0, 0.01};
    varBins["eg_trkDPhi"] = {50, 0.0, 0.01};
    for (auto vIt = varBins.begin(); vIt != varBins.end(); ++vIt) {
        int N = vIt->second[0];
        float m = vIt->second[1];
        float M = vIt->second[2];
        hMap[vIt->first] = new TH1F((vIt->first).c_str(), vIt->first.c_str(), N, m, M);
    }

    // Loop over the entries in the tree
    Long64_t nEntries = tree->GetEntries();
    cout<<"Events = "<<nEntries<<endl;
    for (Long64_t i = 0; i < nEntries; ++i) {
        tree->GetEntry(i);
        //if(i>20000) break;
        if(i%10000==0)cout<<i<<endl; 
        for (size_t j = 0; j < nrEgs; ++j) {
            for (auto vIt = varBins.begin(); vIt != varBins.end(); ++vIt) {
                Float_t val = 0.0;
                if(vIt->first == "eg_et") val = eg_et[j];
                if(vIt->first == "eg_pms2") val = eg_pms2[j];
                if(vIt->first == "eg_trkDEta") val = eg_trkDEta[j];
                if(vIt->first == "eg_trkDPhi") val = eg_trkDPhi[j];
                if(vIt->first == "eg_trkDEtaSeed") val = eg_trkDEtaSeed[j];

                if(vIt->first == "eg_trkIsol") val = eg_trkIsol[j];
                if(vIt->first == "eg_trkChi2") val = eg_trkChi2[j];
                if(vIt->first == "eg_trkMissHits") val = eg_trkMissHits[j];
                if(vIt->first == "eg_trkValidHits") val = eg_trkValidHits[j];
                if(vIt->first == "eg_trkNrLayerIT") val = eg_trkNrLayerIT[j];
                if(val >= varBins[vIt->first][2]){;
                    val  = 0.99 * varBins[vIt->first][2];
                }
                hMap[vIt->first]->Fill(val);
                
            }//hMap loop
        }//eg loop
    }//for loop
   fOut->Write();
   file->Close();
}

