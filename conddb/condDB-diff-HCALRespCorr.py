import xml.etree.ElementTree as ET
import subprocess

#payload_new = "fc57187a7e4d5335d5a0a6cab8e38bcd3fdf2da9" ## https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/tags/HcalRespCorrs_2024_v2.0_data
#payload_old = "d7eb3d6deeff33cacd8c8bc2f2d46523bb05f310" ## https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/tags/HcalRespCorrs_v2.0_hlt
## tag taken from https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts/140X_dataRun3_HLT_HCALRespCorrs_w23_v1/140X_dataRun3_HLT_v3 

payload_new = "d936bb82f0702af1eee99a5929f3a3de0028ba37" 
tag_new = "HcalRespCorrs_2024_v1.0_mc"
payload_old = "bfce584236533231143e2e5063ba82b610533343" 
tag_old  = "HcalRespCorrs_2023_v1.0_mc" 
containers = [
    "HBcontainer", "HEcontainer", "HOcontainer", "HFcontainer",
    "HTcontainer", "ZDCcontainer", "CALIBcontainer", "CASTORcontainer"
]

def get_xml(tag):
    command = "conddb dump %s"%tag
    print(command)
    ## save to a file
    fName = "%s.xml"%tag
    with open(fName, "w") as f:
        f.write(subprocess.check_output(command, shell=True, text=True))
    return fName

def parse_xml_to_dict(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    def parse_element(element):
        if len(element) == 0:
            return element.text
        result = {}
        for child in element:
            child_result = parse_element(child)
            tag = child.tag
            if tag not in result:
                result[tag] = child_result
            else:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_result)
        return result

    return parse_element(root)

def transform_to_accessible_dict(data):
    
    def extract_items(container):
        if "item" in container:
            items = container["item"]
            if not isinstance(items, list):
                items = [items]
            return {int(item["mId"]): float(item["mValue"]) for item in items}
        return {}

    transformed = {}
    for container_name in containers:
        if container_name in data:
            transformed[container_name] = extract_items(data[container_name])
    return transformed



# Parse XML and transform
parsed_data_new = parse_xml_to_dict(get_xml(payload_new))
data_new = parsed_data_new["cmsCondPayload"]["HcalCondObjectContainer-HcalRespCorr-"]
transformed_data_new = transform_to_accessible_dict(data_new)

parsed_data_old = parse_xml_to_dict(get_xml(payload_old))
data_old = parsed_data_old["cmsCondPayload"]["HcalCondObjectContainer-HcalRespCorr-"]
transformed_data_old = transform_to_accessible_dict(data_old)

# Accessing specific data
m_id = 1409286229
value = transformed_data_new["ZDCcontainer"].get(m_id, None)
print(f"Value for mId {m_id}: {value}")

import ROOT
histos_new = {}
histos_old = {}
for container in containers:
    name = container.replace("container", "")
    histos_new[container] = ROOT.TH1F(name+"_new", name, 10, 0, 2)
    histos_old[container] = ROOT.TH1F(name+"_old", name, 10, 0, 2)
    histos_new[container].SetLineColor(ROOT.kRed)
    histos_old[container].SetLineColor(ROOT.kBlue)
    first = 0
    print(f"Container: {container}")
    for m_id in transformed_data_new[container]:
        if not first:
            first = int(m_id)
        if m_id == 0: continue
        ratio =  transformed_data_new[container][m_id] / transformed_data_old[container].get(m_id, None)
        histos_new[container].Fill(transformed_data_new[container][m_id])
        histos_old[container].Fill(transformed_data_old[container][m_id])
        if max(abs(ratio-1),abs(1/(1E-9+ratio)-1))>3:
            print("mId:" ,m_id, "Ratio:", ratio, "New:", transformed_data_new[container][m_id], "Old:", transformed_data_old[container].get(m_id, None))

# Save histograms
output_file = ROOT.TFile("output.root", "RECREATE")
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

padGap = 0.01
xPadRange = [0.0,1.0]
yPadRange = [0.0,0.30-padGap, 0.30+padGap,1.0]
c1 = ROOT.TCanvas("c1", "c1", 800, 800)
c1.Divide(1,2)

for container in containers:
    leg = ROOT.TLegend(0.45, 0.70, 0.97, 0.90)
    max_y = max(histos_new[container].GetMaximum(), histos_old[container].GetMaximum())
    histos_new[container].SetMaximum(max_y*1.6)
    histos_old[container].SetLineWidth(3)
    histos_new[container].SetLineWidth(3)
    histos_new[container].Write()
    histos_old[container].Write()
    c1.cd(1)
    ROOT.gPad.SetPad(xPadRange[0],yPadRange[2],xPadRange[1],yPadRange[3]);
    histos_new[container].GetXaxis().SetRangeUser(0, 2)
    histos_new[container].GetXaxis().SetTitle(tag_new.split("_")[0]);
    histos_new[container].Draw()
    histos_old[container].Draw("same")
    mean_new = round(histos_new[container].GetMean(),3)
    mean_old = round(histos_old[container].GetMean(),3)
    leg.AddEntry(histos_new[container], "#splitline{New (%s)}{Mean = %s: %s}"%(payload_new, mean_new, tag_new), "l")
    leg.AddEntry(histos_old[container], "#splitline{Old (%s)}{Mean = %s: %s}"%(payload_old, mean_old, tag_old), "l")
    leg.Draw()

    c1.cd(2)
    ROOT.gPad.SetPad(xPadRange[0],yPadRange[0],xPadRange[1],yPadRange[2]);
    hRatio = histos_new[container].Clone()
    hRatio.Divide(histos_old[container])
    hRatio.GetYaxis().SetRangeUser(0, 2)
    hRatio.GetXaxis().SetRangeUser(0, 2)
    hRatio.GetXaxis().SetTitle(tag_new.split("_")[0]);
    hRatio.GetYaxis().SetTitle("New/Old")
    hRatio.SetMarkerStyle(20); 

    hRatio.GetXaxis().SetTitleSize(0.11);
    hRatio.GetXaxis().SetLabelSize(0.10);
    hRatio.GetXaxis().SetLabelFont(42);
    hRatio.GetXaxis().SetTitleOffset(1);
    hRatio.GetXaxis().SetLabelOffset(0.01);
    hRatio.GetYaxis().SetTitleSize(0.11);
    hRatio.GetYaxis().SetLabelSize(0.09);
    hRatio.GetYaxis().SetLabelFont(42);
    hRatio.GetYaxis().SetNdivisions(6,5,0);
    hRatio.GetYaxis().SetTitleOffset(0.4);
    hRatio.GetYaxis().SetLabelOffset(0.01);
 
    baseLine = ROOT.TF1("baseLine","1", -100, 10000);
    baseLine.SetLineColor(3);
    hRatio.Draw("P")
    baseLine.Draw("same")
    c1.SaveAs(container+".png")
    c1.SaveAs(container+".pdf")
    c1.Write()
output_file.Close()
print("Histograms saved in output.root")


