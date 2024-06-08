import ROOT

# Paths to the ROOT files
file1 = "hist.root"
file2 = "hist_CCC.root"

# Open the ROOT files
root_file1 = ROOT.TFile.Open(file1)
root_file2 = ROOT.TFile.Open(file2)

# Read histograms
hist_eg_trkDEta_1 = root_file1.Get("eg_trkDEta")
hist_eg_trkDEta_2 = root_file2.Get("eg_trkDEta")


# Create canvas
c1 = ROOT.TCanvas("c1", "c1", 800, 600)

ROOT.gPad.SetLogy(True)
# Draw eg_trkDEta histograms
hist_eg_trkDEta_1.SetLineColor(ROOT.kRed)
hist_eg_trkDEta_2.SetLineColor(ROOT.kBlue)
hist_eg_trkDEta_1.SetTitle("Overlay of eg_trkDEta")
hist_eg_trkDEta_1.GetXaxis().SetTitle("eg_trkDEta")
hist_eg_trkDEta_1.GetYaxis().SetTitle("Counts")
hist_eg_trkDEta_1.Draw("HIST")
hist_eg_trkDEta_2.Draw("HIST SAME")
legend1 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
legend1.AddEntry(hist_eg_trkDEta_1, "file1 eg_trkDEta", "l")
legend1.AddEntry(hist_eg_trkDEta_2, "file2 eg_trkDEta", "l")
legend1.Draw()
c1.SaveAs("eg_trkDEta_overlay.pdf")

