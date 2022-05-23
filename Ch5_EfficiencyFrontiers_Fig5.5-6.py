'''
This module creates the efficiency frontier figures in Chapter 5  (Figures 5.5 and 5.6)

Takes in Production by Well with gridblockID, oil production by well, 
and natural gas production by well.
Aggregates and sums production by gridblockID

Takes in selected C-ESI with proportion of ESI value assigned to gridblock

Joins C-ESI and Production by gridblock by key

Creates single sector oil production plot
Creates single sector conservation plot
Creates combined sector oil production plot
Creates combined sector conservation plot

'''

import os
import gdal
import sys
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer
)
import pandas as pd
from PyQt5.QtCore import QFileInfo
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



#Open seaborn set
sns.set()

#set oil production file name   NOTE  file name must have \\ or / no \
fn_oil = "C:\\Dissertation Project\\Distributions\\Oil_Gas_Production\\ProductionbyWell_0.5latlonConversion.csv"

#set ESI file names
#All
fn_All = "C:\\Dissertation Project\\ScenariosQGIS\\Scenario28 - Fish,Mammal,Turtle,Larval,Coral\\CESI-ProportionWithKey.csv"
#Mammal
fn_Mam = "C:\\Dissertation Project\\ScenariosQGIS\\Scenario23 - Mammals_Proportion(Correct)\\CESI-ProportionWithKey.csv"
#Fisheries
fn_Rev = "C:\\Dissertation Project\\ScenariosQGIS\\Scenario24 - Fisheries_Proportion\\CESI-ProportionWithKey.05.csv"


#load files from file names and create dataframe
df_oil = pd.read_csv(fn_oil, keep_default_na=False, na_values=[""])

df_All = pd.read_csv(fn_All, keep_default_na=False, na_values=[""])
df_Mam = pd.read_csv(fn_Mam, keep_default_na=False, na_values=[""])
df_Rev = pd.read_csv(fn_Rev, keep_default_na=False, na_values=[""])

#convert NA in files to zeros
df_o = df_oil.fillna(0)
df_A = df_All.fillna(0)
df_M = df_Mam.fillna(0)
df_R = df_Rev.fillna(0)

#Aggregate oil production by well by gridblock (OilKey)
df_o2 = df_o.groupby('OilKey').sum()

#export to csv if you want it
df_o2.to_csv("C:\\Dissertation Project\\Distributions\\Oil_Gas_Production\\ProductionbyGridblock.csv")

#Join df_C and df_o2 by key using pandas (pd)  _outer join  - whole area
df_merge2 = pd.merge(left=df_A, right=df_o2, how='outer', left_on= ['C-ESIKey'], right_on=['OilKey'])
df_merge2 = pd.merge(left=df_M, right=df_merge2, how='outer', left_on= ['C-ESIKey'], right_on=['C-ESIKey'])
df_merge2 = pd.merge(left=df_R, right=df_merge2, how='outer', left_on= ['C-ESIKey'], right_on=['C-ESIKey'])

#Join df_C and df_o2 by key using pandas (pd)  -inner join - only oil production
df_merge = pd.merge(left=df_A, right=df_o2, how='right', left_on= ['C-ESIKey'], right_on=['OilKey'])
df_merge = pd.merge(left=df_M, right=df_merge, how='right', left_on= ['C-ESIKey'], right_on=['C-ESIKey'])
df_merge = pd.merge(left=df_R, right=df_merge, how='right', left_on= ['C-ESIKey'], right_on=['C-ESIKey'])

#convert NA to zeros (if keys in one that aren't in the other
df_total = df_merge.fillna(0)

df_total2 = df_merge2.fillna(0)


#Create columns for Percent of ESI within the Area
df_total['ESIPropA'] = df_total['sumA']/sum(df_total['sumA'])
df_total['ESIPropM'] = df_total['sumM']/sum(df_total['sumM'])
df_total['ESIPropF'] = df_total['sumF']/sum(df_total['sumF'])

#export to csv if you want it
df_total.to_csv("C:\\Dissertation Project\\Distributions\\Oil_Gas_Production\\ProductionbyGridblockJoin.csv")

df_total2.to_csv("C:\\Dissertation Project\\Distributions\\Oil_Gas_Production\\ProductionbyGridblockJoin2.csv")


#######################################
#Single Sector Calculations - selects cells based on oil production only
#######################################

#Sort database by oilProp (descending order)
#Create field that is cumulative sum (CS) of oilProp
#Create field that is 1-cumulative sum of C-ESI

df_ss_oil = df_total.sort_values('propOil', ascending=True)
##new field for oilProp CS (will need this to be 1-)
df_ss_oil['oilPropCS'] = df_ss_oil['propOil'].cumsum()
df_ss_oil['oilPropNegCS'] = 1 - df_ss_oil['oilPropCS']
##new fields for CESI Prop CS 
df_ss_oil['ESIPropCS'] = df_ss_oil['ESIPropA'].cumsum()
df_ss_oil['ESIPropCSM'] = df_ss_oil['ESIPropM'].cumsum()
df_ss_oil['ESIPropCSF'] = df_ss_oil['ESIPropF'].cumsum()
df_ss_oil['type'] = "Oil Prodution Only"


df_ss_gas = df_total.sort_values('propGas', ascending=True)
##new field for oilProp CS (will need this to be 1-)
df_ss_gas['gasPropCS'] = df_ss_gas['propGas'].cumsum()
df_ss_gas['gasPropNegCS'] = 1 - df_ss_gas['gasPropCS']
##new fields for CESI Prop CS 
df_ss_gas['ESIPropCS'] = df_ss_gas['ESIPropA'].cumsum()
df_ss_gas['ESIPropCSM'] = df_ss_gas['ESIPropM'].cumsum()
df_ss_gas['ESIPropCSF'] = df_ss_gas['ESIPropF'].cumsum()
df_ss_gas['type'] = "Gas Prodution Only"


            
bars=df_ss_oil["propOil"]

x_pos = np.arange(len(df_ss_oil["propOil"]))

g = sns.relplot(x=x_pos, y="oilPropNegCS", kind="line",
            data=df_ss_oil, palette="Paired");

g = sns.relplot(x="ESIPropCSM", y="oilPropNegCS", kind="line",
            data=df_ss_oil, palette="Paired");

##Graph it!
g = sns.relplot(x="ESIPropCSM", y="oilPropNegCS", kind="line",
            data=df_ss_oil, palette="Paired");
            
g.set_axis_labels("C-ESI Mammals Proportion", "Oil Production Proportion")
g.fig.suptitle('Single Sector - Oil Production')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)



#######################################
#Single Sector Calculations - selects cells based on Mammals ESI only
#######################################

#Mammals
df_ss_Mam = df_total.sort_values('combPropM', ascending=True)
##new field for CS (will need this to be 1-), this field is cum sum based on the order of this field
df_ss_Mam['ESIPropCS'] = df_ss_Mam['combPropM'].cumsum()
df_ss_Mam['ESIPropNegCS'] = 1 - df_ss_Mam['ESIPropCS']
##new field for oil CS, this field is cum sum based on the other field
df_ss_Mam['oilPropCS'] = df_ss_Mam['propOil'].cumsum()
df_ss_Mam['type'] = "Mammals C-ESI only"

#Graph it!  Mammals vs Oil Production
g = sns.relplot(x="oilPropCS", y="ESIPropNegCS", kind="line",
            data=df_ss_Mam, palette="Paired");
            
g.set_axis_labels("C-ESI Total Proportion", "Oil Production Proportion")
g.fig.suptitle('Single Sector - Mammal Conservation')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)



########################################
#Multi Sector Oil Calculations - selects based on Oil including ESI
########################################

#All
#Create field that is OilProduction - C-ESI (for each C-ESI)
#Create field that is 1-cumulative sum of C-ESI
df_copy = df_total
df_copy['ESIPropA_inv'] = 1 - df_copy['ESIPropA'] 
df_copy['MSoilfieldA'] = df_copy['propOil'] + (.2*df_copy['ESIPropA_inv']) 
df_ms = df_copy.sort_values('MSoilfieldA', ascending=True)
##new field for CS (will need this to be 1-), this field is cum sum based on the order of this field
df_ms['ESIPropCS'] = df_ms['ESIPropA'].cumsum()
df_ms['type'] = "Prod and C-ESI"

##new field for oil CS, this field is cum sum based on the other field
df_ms['oilPropCS'] = df_ms['propOil'].cumsum()
df_ms['oilPropNegCS'] = 1 - df_ms['oilPropCS']

##Can't merge because you want the order to stay
graphAllMS = pd.DataFrame()
graphAllMS["x1"] = df_ms['ESIPropCS']
graphAllMS["y1"] = df_ms['oilPropNegCS']
graphAllMS["Sector Type"] = df_ms['type']

graphAllSS = pd.DataFrame()
graphAllSS["x1"] = df_ss_oil['ESIPropCS']
graphAllSS["y1"] = df_ss_oil['oilPropNegCS']
graphAllSS["Sector Type"] = df_ss_oil['type']

graphAll = graphAllSS.append(graphAllMS)

#Graph it!
g = sns.relplot(x="ESIPropCS", y="oilPropNegCS", kind="line",
            data=df_ms, palette="Paired");
g.set_axis_labels("C-ESI Total Proportion", "Oil Production Proportion")
g.fig.suptitle('Mutiple Sector - Oil Production with C-ESI Included')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)

#Graph it!
g = sns.relplot(x="x1", y="y1", kind="line", hue="Sector Type",
            data=graphAll);
g.set_axis_labels("C-ESI Total Proportion", "Oil Production Proportion")
g.fig.suptitle('Tradeoff Curves for Fish/Mam/Tur/Larvae/Coral C-ESI')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)

########################################
#Mammal multi sector Selects by oil plus mammals
#######################################

df_copy = df_total
df_copy['ESIPropM_inv'] = 1 - df_copy['ESIPropM'] 
df_copy['MSoilfieldM'] = df_copy['propOil'] + (.2*df_copy['ESIPropM_inv']) 
df_ms = df_copy.sort_values('MSoilfieldM', ascending=True)
##new field for CS (will need this to be 1-), this field is cum sum based on the order of this field
df_ms['ESIPropCS'] = df_ms['ESIPropM'].cumsum()
##new field for oil CS, this field is cum sum based on the other field
df_ms['oilPropCS'] = df_ms['propOil'].cumsum()
df_ms['oilPropNegCS'] = 1 - df_ms['oilPropCS']
df_ms['type'] = "Oil Prod + C-ESI"

##Can't merge because you want the order to stay
graphAllMS = pd.DataFrame()
graphAllMS["x1"] = df_ms['ESIPropCS']
graphAllMS["y1"] = df_ms['oilPropNegCS']
graphAllMS["Sector Type"] = df_ms['type']

graphAllSS = pd.DataFrame()
graphAllSS["x1"] = df_ss_oil['ESIPropCSM']
graphAllSS["y1"] = df_ss_oil['oilPropNegCS']
graphAllSS["Sector Type"] = df_ss_oil['type']

graphAll = graphAllSS.append(graphAllMS)

#Graph it!
g = sns.relplot(x="ESIPropCS", y="oilPropNegCS", kind="line",
            data=df_ms, palette="Paired");
g.set_axis_labels("C-ESI Mammals Proportion", "Oil Production Proportion")
g.fig.suptitle('Production including Mammals C-ESI')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)

#Graph it!
g = sns.relplot(x="x1", y="y1", kind="line", hue="Sector Type",
            data=graphAll);
g.set_axis_labels("C-ESI Mammals (Proportion within Area)", "Oil Production Proportion")
g.fig.suptitle('Tradeoff Curves for Mammals C-ESI')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)

########################################
#Fisheries Multi-Sector curve
########################################
df_copy = df_total
df_copy['ESIPropF_inv'] = 1 - df_copy['ESIPropF'] 
df_copy['MSoilfieldF'] = df_copy['propOil'] + (.3*df_copy['ESIPropF_inv']) 
df_ms = df_copy.sort_values('MSoilfieldF', ascending=True)
##new field for CS (will need this to be 1-), this field is cum sum based on the order of this field
df_ms['ESIPropCS'] = df_ms['ESIPropF'].cumsum()
##new field for oil CS, this field is cum sum based on the other field
df_ms['oilPropCS'] = df_ms['propOil'].cumsum()
df_ms['oilPropNegCS'] = 1 - df_ms['oilPropCS']
df_ms['type'] = "Oil Prod + C-ESI"

##Can't merge because you want the order to stay
graphAllMS = pd.DataFrame()
graphAllMS["x1"] = df_ms['ESIPropCS']
graphAllMS["y1"] = df_ms['oilPropNegCS']
graphAllMS["Sector Type"] = df_ms['type']

graphAllSS = pd.DataFrame()
graphAllSS["x1"] = df_ss_oil['ESIPropCSF']
graphAllSS["y1"] = df_ss_oil['oilPropNegCS']
graphAllSS["Sector Type"] = df_ss_oil['type']

graphAll = graphAllSS.append(graphAllMS)


#Graph it!
g = sns.relplot(x="x1", y="y1", kind="line", hue="Sector Type",
            data=graphAll);
g.set_axis_labels("C-ESI Fisheries Proportion", "Oil Production Proportion")
g.fig.suptitle('Tradeoff Curves for Fisheries C-ESI')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)

#export to csv if you want it
df_ms.to_csv("C:\\Dissertation Project\\Distributions\\Oil_Gas_Production\\Join_MS.csv")

## Merge these to plot on same graph
line_mergeA = pd.merge(left=df_A, right=df_o2, how='right', left_on= ['C-ESIKey'], right_on=['OilKey'])

#######################################
#Choosing mammal sites with Oil weight component
#######################################
#Mammals
df_copy = df_total
df_copy['propOil_inv'] = 1 - df_copy['propOil'] 
df_copy['MSMammalsO'] = df_copy['combPropM'] + (.3*df_copy['propOil_inv']) 
df_ms_Mam = df_total.sort_values('MSMammalsO', ascending=True)
##new field for CS (will need this to be 1-), this field is cum sum based on the order of this field
df_ms_Mam['ESIPropCS'] = df_ms_Mam['combPropM'].cumsum()
df_ms_Mam['ESIPropNegCS'] = 1 - df_ms_Mam['ESIPropCS']
##new field for oil CS, this field is cum sum based on the other field
df_ms_Mam['oilPropCS'] = df_ms_Mam['propOil'].cumsum()
df_ms_Mam['type'] = "Mammals C-ESI + Oil Production"

##Can't merge because you want the order to stay
graphAllMS = pd.DataFrame()
graphAllMS["x1"] = df_ms_Mam['oilPropCS']
graphAllMS["y1"] = df_ms_Mam['ESIPropNegCS']
graphAllMS["Sector Type"] = df_ms_Mam['type']

graphAllSS = pd.DataFrame()
graphAllSS["x1"] = df_ss_Mam['oilPropCS']
graphAllSS["y1"] = df_ss_Mam['ESIPropNegCS']
graphAllSS["Sector Type"] = df_ss_Mam['type']


graphAll = graphAllSS.append(graphAllMS)

#Graph it!
g = sns.relplot(x="x1", y="y1", kind="line", hue="Sector Type",
            data=graphAll);
g.set_axis_labels("Oil Production Proportion", "Mammals C-ESI Proportion")
g.fig.suptitle('Tradeoff Curves for Mammals vs Oil Production')
g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)



#show
plt.show()