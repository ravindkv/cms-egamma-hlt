import os
from PlotFunc import *
from Inputs import *
from PlotCMSLumi import *
from PlotTDRStyle import *
from ROOT import TFile, TLegend, gPad, gROOT, TCanvas, THStack, TF1, TH1F, TGraphAsymmErrors

padGap = 0.01
iPeriod = 4;
iPosX = 10;
ModTDRStyle()
xPadRange = [0.0,1.0]
yPadRange = [0.0,0.30-padGap, 0.30+padGap,1.0]

os.system("rm -r %s"%outPlotDir)
os.system("mkdir -p %s"%outPlotDir)

def makeEff(varName):
    gROOT.SetBatch(True)
    canvas = TCanvas()
    if len(forRatio)>0: 
        canvas.Divide(1, 2)
        canvas.cd(1)
        gPad.SetRightMargin(0.03);
        gPad.SetPad(xPadRange[0],yPadRange[2],xPadRange[1],yPadRange[3]);
        gPad.SetTopMargin(0.09);
        gPad.SetBottomMargin(padGap);
        #gPad.SetTickx(0);
        gPad.SetLogy(True)
        gPad.RedrawAxis();
    else:
        canvas.cd()

    #get effs 
    effs = []
    ints = []
    name = "Default" 
    f1 = TFile.Open("%s/%s"%(histDir, forOverlay[name]))
    eff   = getHist(f1, "%s"%varName).Clone("%s_%s"%(varName, forOverlay[name]))
    effs.append(eff)
    for i in range(eff.GetNbinsX()):
        ints.append(eff.GetBinContent(i))
    name = "CCC" 
    f2 = TFile.Open("%s/%s"%(histDir, forOverlay[name]))
    eff   = getHist(f2, "%s"%varName).Clone("%s_%s"%(varName, forOverlay[name]))
    print(eff.Integral())
    effs.append(eff)
    for i in range(eff.GetNbinsX()):
        ints.append(eff.GetBinContent(i))
    
    print(effs)
    #plot effs
    leg = TLegend(0.45,0.70,0.80,0.92); 
    decoLegend(leg, 4, 0.027)
    for index, eff in enumerate(effs): 
        xTitle = varName
        yTitle = "Events"
        decoHist(eff, xTitle, yTitle, index+1)
        if index==0:
            eff.Draw("HIST")
            eff.SetMaximum(100*max(ints))
            #eff.SetMinimum(0.2)
            #eff.GetXaxis().SetRangeUser(10, 400)
        else:
            eff.Draw("HISTSAME")
        leg.AddEntry(eff, "%s"%(eff.GetName()), "L")
    
    #Draw CMS, Lumi, channel
    extraText  = "Preliminary"
    year = "XYZ"
    lumi_13TeV = getLumiLabel(year)
    CMS_lumi(lumi_13TeV, canvas, iPeriod, iPosX, extraText)
    leg.Draw()
    
    #Ratio lots
    if len(forRatio)>0: 
        canvas.cd(2)
        #gPad.SetLogy(True)
        gPad.SetTopMargin(padGap); 
        gPad.SetBottomMargin(0.30); 
        gPad.SetRightMargin(0.03);
        #gPad.SetTickx(0);
        gPad.SetPad(xPadRange[0],yPadRange[0],xPadRange[1],yPadRange[2]);
        gPad.RedrawAxis();
        rLeg = TLegend(0.25,0.75,0.55,0.85); 
        decoLegend(rLeg, 4, 0.085)
        rLeg.SetNColumns(3)
        baseLine = TF1("baseLine","1", -100, 10000);
        baseLine.SetLineColor(3);
        hRatio = getRatio(effs[0], effs[1])
        for i in range(hRatio.GetNbinsX()):
            print(hRatio.GetBinContent(i))
        decoHistRatio(hRatio, xTitle, "Ratio", 1)
        hRatio.GetYaxis().SetRangeUser(0.5, 1.5)
        hRatio.Draw("P")
        #baseLine.Draw("same")
    pdf = "./plots/effPlot_%s.pdf"%(varName)
    outComb = "./plots/comb.pdf"
    png = pdf.replace("pdf", "png")
    canvas.SaveAs(pdf)
    #canvas.SaveAs(png)

for vName in varNames:
    makeEff(vName)
os.system('pdfunite plots/effPlot_eg_*.pdf comb.pdf')
