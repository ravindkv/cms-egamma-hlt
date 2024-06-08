import ROOT as rt
import numpy as np
import sys
from ctypes import c_double

#-----------------------------------------
#Get, add, substract histograms 
#-----------------------------------------
def getHist(inFile, name):
    try:
        hPass = inFile.Get(name)
        hPass.GetXaxis().SetTitle(name)
    except Exception:
        print ("Error: Hist not found. \nFile: %s HistName: %s"%(inFile, name))
        sys.exit()
    #hPass.Scale(1/hPass.Integral())
    return hPass

def divideGraphs(graph1, graph2): #from ChatGPT
    result_graph = rt.TGraphAsymmErrors()
    # Loop over the points in graph1 and graph2
    n_points = graph1.GetN()
    for i in range(n_points):
        # Get the values and errors for each point in graph1
        x1 = c_double(0.0)
        y1 = c_double(0.0)
        exl1 = graph1.GetErrorXlow(i)
        exh1 = graph1.GetErrorXhigh(i)
        eyl1 = graph1.GetErrorYlow(i)
        eyh1 = graph1.GetErrorYhigh(i)
        graph1.GetPoint(i, x1, y1)

        # Get the values and errors for the corresponding point in graph2
        x2 = c_double(0.0)
        y2 = c_double(0.0)
        exl2 = graph2.GetErrorXlow(i)
        exh2 = graph2.GetErrorXhigh(i)
        eyl2 = graph2.GetErrorYlow(i)
        eyh2 = graph2.GetErrorYhigh(i)
        graph2.GetPoint(i, x2, y2)

        # Perform the division of y values and errors
        result_y = y1.value / y2.value if y2.value != 0 else 0.0
        result_eyl = (eyl1 / y2.value) if y2.value != 0 else 0.0
        result_eyh = (eyh1 / y2.value) if y2.value != 0 else 0.0
        
        # Set the values and errors to the result graph
        result_graph.SetPoint(i, x1.value, result_y)
        result_graph.SetPointError(i, exl1, exh1, result_eyl, result_eyh)
    return result_graph


#-----------------------------------------
#Get ratio of two eff histograms
#-----------------------------------------
def getRatio(h1, h2):
    print("h1 = %s"%h1.Integral())
    ratio = h1.Clone()
    print("h2 = %s"%h2.Integral())
    ratio.Divide(h2)
    return ratio


#-----------------------------------------
#Decorate a histogram
#-----------------------------------------
def decoHist(hist, xTit, yTit, color):
    hist.GetXaxis().SetTitle(xTit);
    hist.GetYaxis().SetTitle(yTit);
    #hist.SetFillColor(color);
    hist.SetLineColor(color);
    hist.SetMarkerColor(color);
    hist.GetXaxis().SetTitle(xTit);
    hist.GetYaxis().SetTitle(yTit)
    #hist.GetYaxis().CenterTitle()
    hist.GetXaxis().SetTitleOffset(1.0)
    hist.GetYaxis().SetTitleOffset(1.2)
    hist.GetXaxis().SetTitleSize(0.05);
    hist.GetYaxis().SetTitleSize(0.05);
    hist.GetXaxis().SetTitleSize(0.05);
    hist.GetYaxis().SetTitleSize(0.05);
    hist.GetXaxis().SetTickLength(0.04);
    hist.GetXaxis().SetMoreLogLabels();
    hist.GetXaxis().SetNoExponent()

def decoHistRatio(hist, xTit, yTit, color):
    #hist.SetFillColor(color);
    hist.SetLineColor(color);
    hist.GetXaxis().SetTitle(xTit);
    hist.GetYaxis().SetTitle(yTit);
    hist.GetXaxis().SetTitleSize(0.11);
    hist.GetXaxis().SetLabelSize(0.10);
    hist.GetXaxis().SetLabelFont(42);
    #hist.GetXaxis().SetLabelColor(kBlack);
    #hist.GetXaxis().SetAxisColor(kBlack);
    #hist.GetYaxis().SetRangeUser(0.0, 2.0);
    hist.GetXaxis().SetTitleOffset(1);
    hist.GetXaxis().SetLabelOffset(0.01);
    hist.SetMarkerStyle(20); 
    hist.SetMarkerColor(color)
    #hist.SetMarkerSize(1.2);
    hist.GetYaxis().SetTitleSize(0.11);
    hist.GetYaxis().SetLabelSize(0.10);
    hist.GetYaxis().SetLabelFont(42);
    #hist.GetYaxis().SetAxisColor(1);
    hist.GetYaxis().SetNdivisions(6,5,0);
    hist.GetXaxis().SetTickLength(0.08);
    hist.GetYaxis().SetTitleOffset(0.6);
    hist.GetYaxis().SetLabelOffset(0.01);
    hist.GetXaxis().SetMoreLogLabels()
    hist.GetYaxis().CenterTitle();
    hist.GetXaxis().SetNoExponent()

#-----------------------------------------
#Legends for all histograms, graphs
#-----------------------------------------
def decoLegend(legend, nCol, textSize):
    #legend.SetNColumns(nCol);
    legend.SetFillStyle(0);
    legend.SetBorderSize(0);
    #legend.SetFillColor(kBlack);
    legend.SetTextFont(42);
    legend.SetTextAngle(0);
    legend.SetTextSize(textSize);
    legend.SetTextAlign(12);
    return legend

def getLumiLabel(year):
    #lumi = "2022G vs 2023C fb^{-1}"
    lumi = "/EGamma0/Run2023D-v1/RAW"
    if "16Pre" in year:
        lumi = "19.5 fb^{-1} (2016Pre)"
    if "16Post" in year:
        lumi = "16.8 fb^{-1} (2016Post)"
    if "17" in year:
        lumi = "41.5 fb^{-1} (2017)"
    if "18" in year:
        lumi = "59.8 fb^{-1} (2018)"
    if "__" in year:
        lumi = "138 fb^{-1} (Run2)"
    if "2023" in year:
        lumi = "X fb^{-1} (2023)"
    return lumi

def getChLabel(decay, channel):
    nDict   = {"Semilep": "1", "Dilep":2}
    chDict  = {"Mu": "#mu", "Ele": "e"}
    colDict = {"Mu": rt.kBlue, "Ele": rt.kRed}
    name = ""
    for ch in channel.split("__"):
        name += "%s#color[%i]{%s}"%(nDict[decay], colDict[ch], chDict[ch])
    name += ", p_{T}^{miss} #geq 20 GeV"
    return name
