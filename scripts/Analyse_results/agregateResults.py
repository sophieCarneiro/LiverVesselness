from pathlib import Path
import os
import glob
import sys

from analyseBenchmarkTools import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf

import numpy as np

# List all benchmark per filter
pathDirectory = sys.argv[1]
print(pathDirectory)

# List
print(pathDirectory +"/**/*.summary.csv")
pathListMetrics = sorted(glob.glob(f"{pathDirectory}/**/*metrics_summary.pkl",recursive=True))
pathListCM = sorted(glob.glob(f"{pathDirectory}/**/*cm_summary.pkl",recursive=True))
pathListROC = sorted(glob.glob(f"{pathDirectory}/**/*roc_summary.pkl",recursive=True))
pathListROC_rescaled = sorted(glob.glob(f"{pathDirectory}/**/*roc_rescaled_summary.pkl",recursive=True))

pathListBestMean = sorted( glob.glob(f"{pathDirectory}/**/*Organ_Best_mean_MCC.pkl",recursive=True) )

#pathListMetrics,pathListCM,pathListROC,pathListROC_rescaled = (list(t) for t in zip(*sorted(zip(list1, list2))))
"""
print("hello")
print(pathListMetrics)
print("----")
print(pathListCM)
print("----")
print(pathListROC)
print("----")
print(pathListROC_rescaled)
print("----")
"""
#for pathMetrics,pathCM,pathROC,pathRoc_rescaled in zip(pathListMetrics,pathListCM,pathListROC,pathListROC_rescaled):
#    print(pathMetrics,pathCM,pathROC,pathRoc_rescaled)

# prepare plots
DFmetrics = loadPickleToDF( pathListMetrics[0] )

print(DFmetrics)
labelsDict = dict()
labelsDict["Organ"] = "Organ"
labelsDict["VN"] = "Vessels \n neighbourhood"
labelsDict["Vlarge"] = "Large \n vessels"
labelsDict["Vsmall"] = "Small \n vessels"
labelsDict["Vmedium"] = "Medium \n vessels"
labelsDict["Bifurcations"] = "Bifurcations"
labelsDict["UnetBullit"] = "Unet Bullit"
labelsDict["UnetDVN"] = "Unet DVN"
labels = [ labelsDict[i] for i in DFmetrics["Region"].unique() ]

plt.rcParams.update({'font.size':45})

#fig,axes = plt.subplots(4,1)
plotDict = dict()

figs = []
figSize = 30
figs.append(plt.figure(figsize=(figSize,figSize)))
figs.append(plt.figure(figsize=(figSize,figSize)))
figs.append(plt.figure(figsize=(figSize,figSize)))
figs.append(plt.figure(figsize=(figSize,figSize)))
figs.append(plt.figure(figsize=(figSize,figSize)))
figs.append(plt.figure(figsize=(figSize,figSize)))

print(figs)

plotDict["MCC"] = figs[0].add_subplot(111)
plotDict["Dice"] = figs[1].add_subplot(111)
plotDict["AUC"] = figs[2].add_subplot(111)
plotDict["TPR"] = figs[3].add_subplot(111)
plotDict["ROC"] = figs[4].add_subplot(111)
plotDict["ROC_rescaled"] = figs[5].add_subplot(111)

# plot color
color = dict()
color["Frangi"] = "tab:blue"
color["Sato"] = "tab:orange"
color["Meijering"] = "tab:olive"
color["Zhang"] =  "tab:red"
color["Jerman"] = "tab:purple"
color["RORPO"] = "tab:brown"
color["OOF"] = "tab:cyan"
color["OOFGM"] = "tab:cyan"
# same thing, but naming convention different
color["Baseline"] = "k"
color["Rescale"] = "k"

color["UnetBullit"] = "dodgerblue"
color["UnetDVN"] = "darkviolet" 

lineStyle = dict()
lineStyle["Frangi"] = "solid"
lineStyle["Sato"] = "dotted"
lineStyle["Meijering"] = "dashed"
lineStyle["Zhang"] = "solid"
lineStyle["Jerman"] = "solid"
lineStyle["RORPO"] = "dashdot"
lineStyle["OOF"] = "solid"
lineStyle["OOFGM"] = "solid"
# same thing, but naming convention different
lineStyle["Baseline"] = "solid"
lineStyle["Rescale"] = "solid"

lineStyle["UnetDVN"] = "solid"
lineStyle["UnetBullit"] = "solid"

zorder = dict()

zorder["Baseline"] = 1
zorder["Rescale"] = 1

zorder["Meijering"] = 2
zorder["Sato"] = 3
zorder["OOF"] = 4
zorder["OOFGM"] = 4
zorder["RORPO"] = 5
zorder["Jerman"] = 6
zorder["Frangi"] = 7 
zorder["Zhang"] = 8

zorder["UnetDVN"] = 9
zorder["UnetBullit"] = 10
 


# plot y ticks
y_loc = np.linspace(0,1,10)
y_ticks = [ "{:.1f}".format(y_loc[i]) for i in range( len(y_loc) ) ]
y_lims = [0, 1]

print("labels")
print(labels)
x = np.arange(len(labels)) * 100
width = 70
error_kw=dict(lw=1, capsize=1, capthick=1)

xLabelsSize = 65
xTicksLabelsSize = 50
yLabelsSize = 65
yTicksLabelSize = 55
legendLabelSize = 55
lineThickness=5

# retrive couple of infos
# FilterName
count=0
nbFilters = 7
lenBar = width / nbFilters
offset = width / 2

PSsummary = []
ParamSummary = []
for pathMetrics, pathCM, pathROC, pathRoc_rescaled, pathBestMean in zip(pathListMetrics,pathListCM,pathListROC,pathListROC_rescaled,pathListBestMean):

    DFmetrics = loadPickleToDF(pathMetrics)
    DFROC = loadPickleToDF(pathROC)
    DFROC_rescaled = loadPickleToDF(pathRoc_rescaled)

    DFbestMean = loadPickleToDF(pathBestMean)

    tempString = pathMetrics.split("/")[-1]
    tempString = tempString.split("_")
    dbName = tempString[0]

    # TODO : quick fix for bad naming convention
    # Be careful about the naming for good parsing
    if(dbName == "Ircad"):
        optimStep = tempString[2]
        filterName = tempString[3]
        aoiName = tempString[4]
    elif(dbName == "Vascu" or dbName == "vascu"):
        optimStep = tempString[2]
        filterName = tempString[3]
        aoiName = tempString[4]    
    else:
        optimStep = tempString[1]
        filterName = tempString[2]
        aoiName = tempString[3]
    if(filterName == "Rescale"):
        filterName = "Baseline"
    print("-------")
    print("dbName:",dbName,"|optimStep",optimStep,"|FilterName",filterName,"|ROI",aoiName)

    # plot MCC
    # retrieve MCC infos
    print(DFmetrics.columns)
    print(DFmetrics)

    metric = DFmetrics["optimMetric"].unique()
    mean_MCC = DFmetrics["mean_MCC"]
    std_MCC = DFmetrics["std_MCC"]

    print(mean_MCC.iloc[:-1])
    print(std_MCC.iloc[:-1])
    print(filterName)
    print(x[:-1])
    
    plotDict["MCC"].bar(x[:-1]+count*lenBar-offset,mean_MCC.iloc[:-1],lenBar,label=filterName,yerr=std_MCC.iloc[:-1],error_kw=error_kw,color=color[filterName])

    plotDict["MCC"].set_ylabel('mean MCC',fontsize=yLabelsSize)
    plotDict["MCC"].set_ylim(y_lims)
    plotDict["MCC"].set_yticks(y_loc)
    plotDict["MCC"].set_yticklabels(y_ticks,fontsize=15)
    plotDict["MCC"].set_xticks(x[:-1])
    plotDict["MCC"].set_xticklabels(labels[:-1],rotation=30, ha='right',fontsize=xTicksLabelsSize)
    plotDict["MCC"].legend(ncol=3,fontsize=legendLabelSize)
    
    # make little parameter summary
    temp = DFmetrics[DFmetrics["Region"]=="Organ"]
    temp2 = DFROC[DFROC["Region"] == "Organ"]
    PSsummary.append( [filterName, temp["Region"].item(), temp["ParameterSet"].item(),temp2["mean_Threshold"].item(), temp["mean_MCC"].item()] )

    # plot Dice
    # retrieve Dice  infos
    metric = DFmetrics["optimMetric"].unique()
    print(metric)
    mean_Dice = DFmetrics["mean_Dice"]
    std_Dice = DFmetrics["std_Dice"]
    plotDict["Dice"].bar(x+count*lenBar-offset,mean_Dice,lenBar,label=filterName,yerr=std_Dice,error_kw=error_kw,color=color[filterName])
    
    plotDict["Dice"].set_ylabel('mean Dice',fontsize=yLabelsSize)
    plotDict["Dice"].set_ylim(y_lims)
    plotDict["Dice"].set_yticks(y_loc)
    plotDict["Dice"].set_yticklabels(y_ticks,fontsize=yTicksLabelSize)
    plotDict["Dice"].set_xticks(x)
    plotDict["Dice"].set_xticklabels(labels,rotation=30, ha='right',fontsize=xTicksLabelsSize)
    plotDict["Dice"].legend(ncol=3,fontsize=legendLabelSize)

    # plot AUC
    
    # retrieve AUC  infos
    metric = DFmetrics["optimMetric"].unique()
    print(metric)
    mean_AUC = DFmetrics["mean_AUC"]
    plotDict["AUC"].bar(x[:-1]+count*lenBar-offset,mean_AUC.iloc[:-1],lenBar,label=filterName,error_kw=error_kw,color=color[filterName])
    
    plotDict["AUC"].set_ylabel('AUC',fontsize=yLabelsSize)

    plotDict["AUC"].set_ylim(y_lims)
    plotDict["AUC"].set_yticks(y_loc)
    plotDict["AUC"].set_yticklabels(y_ticks,fontsize=yTicksLabelSize)
    
    plotDict["AUC"].set_xticks(x[:-1])
    plotDict["AUC"].set_xticklabels(labels[:-1],rotation=30, ha='right',fontsize=xTicksLabelsSize)
    plotDict["AUC"].legend(ncol=3)
    
    # plot TPR
    # retrieve TPR  infos
    metric = DFmetrics["optimMetric"].unique()
    print(metric)
    mean_TPR = DFmetrics["mean_TPR"]
    std_TPR = DFmetrics["std_TPR"]
    plotDict["TPR"].bar(x+count*lenBar-offset,mean_TPR,lenBar,label=filterName,yerr=std_TPR,error_kw=error_kw,color=color[filterName])
    
    plotDict["TPR"].set_ylabel('mean True positive rate',fontsize=yLabelsSize)
    plotDict["TPR"].set_ylim(y_lims)
    plotDict["TPR"].set_yticks(y_loc)
    plotDict["TPR"].set_yticklabels(y_ticks,fontsize=20)
    
    plotDict["TPR"].set_xticks(x)
    plotDict["TPR"].set_xticklabels(labels,rotation=30, ha='right',fontsize=xTicksLabelsSize)
    plotDict["TPR"].legend(ncol=3,fontsize=legendLabelSize)

    # plot ROC

    TPR = DFROC[ DFROC["Region"] == "Organ" ]["TPR"].item()#[1:-2]
    FPR = DFROC[ DFROC["Region"] == "Organ" ]["FPR"].item()#[1:-2]

    nbThreshold = len(TPR)+1 # first and last values are removed, but only first shifts the indexes.

    plotDict["ROC"].plot(FPR,TPR,label=filterName,color=color[filterName],zorder=zorder[filterName],linewidth=lineThickness,linestyle=lineStyle[filterName])
    #plotDict["ROC"].legend(ncol=3,fontsize=legendLabelSize)
    plotDict["ROC"].set_ylabel("True positive rate",fontsize=yLabelsSize)
    plotDict["ROC"].set_xlabel("False positive rate",fontsize=xLabelsSize)

    TPR = DFROC_rescaled[ DFROC_rescaled["Region"] == "Organ" ]["TPR"].item()#[1:-2]
    FPR = DFROC_rescaled[ DFROC_rescaled["Region"] == "Organ" ]["FPR"].item()#[1:-2]

    plotDict["ROC_rescaled"].plot(FPR,TPR,label=filterName,color=color[filterName],zorder=zorder[filterName],linewidth=lineThickness,linestyle=lineStyle[filterName])
    #plotDict["ROC"].legend(ncol=3,fontsize=legendLabelSize)
    plotDict["ROC_rescaled"].set_ylabel("True positive rate",fontsize=yLabelsSize)
    plotDict["ROC_rescaled"].set_xlabel("False positive rate",fontsize=xLabelsSize)
    #plotDict["ROC_rescaled"].set_xlim([0,10])

    # retrieving parameters min and max
    print(DFbestMean)

    id_min = DFbestMean["mean_MCC"].idxmin()
    id_max = DFbestMean["mean_MCC"].idxmax()
    minLine = DFbestMean.loc[id_min]
    maxLine = DFbestMean.loc[id_max]

    minMCC = minLine["mean_MCC"]
    maxMCC = maxLine["mean_MCC"]

    minParam = minLine["VolumeName"]
    maxParam = maxLine["VolumeName"]

    ParamSummary.append( [filterName,minMCC,maxMCC,minParam,maxParam] )

    count += 1
    
#plt.gca().set_aspect('equal', adjustable='box')
pdf = matplotlib.backends.backend_pdf.PdfPages(pathDirectory+f"/{dbName}_aggregated_summary.pdf")
for i,key in enumerate(plotDict):
    figs[i].savefig( pathDirectory + f"/{dbName}_aggregated_{key}_summary.pdf")
    pdf.savefig(figs[i])
pdf.close()

print("saving results at",pathDirectory+f"/{dbName}_aggregated_bestPS_summary.csv")
dfPSsummary = pd.DataFrame(PSsummary,columns=["FilterName","AOI","Parameters","mean_Threshold","mean_MCC"])
print(dfPSsummary)
dfPSsummary.to_csv(pathDirectory+f"/{dbName}_aggregated_bestPS_summary.csv",index=False)

# --------------------------------

dfParamMean = pd.DataFrame(ParamSummary,columns=["FilterName","minMCC","maxMCC","minParam","maxParam"])
print(dfParamMean)
dfParamMean.to_csv(pathDirectory+f"/{dbName}_aggregated_bestParam_summary.csv",index=False)
