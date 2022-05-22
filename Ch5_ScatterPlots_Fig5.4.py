'''
This module creates the Scatterplots of Proportions - Figures 5.4

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


g = sns.relplot(x="propOil", y="combPropM", kind="scatter",
            data=df_total2, palette="Paired");
g.set_axis_labels("Oil Production Proportion", "C-ESI Mammals (Total C-ESI)")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["propOil"])/2
yval=max(df_ss_oil["combPropM"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")


g = sns.relplot(x="ESIPropA", y="propOil", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI MFTLC (Proportion within Area)", "Oil Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropA"])/2
yval=max(df_ss_oil["propOil"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")

            
g = sns.relplot(x="ESIPropM", y="propOil", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI Mammals (Proportion within Area)", "Oil Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropM"])/2
yval=max(df_ss_oil["propOil"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")
            
g = sns.relplot(x="ESIPropF", y="propOil", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI Fisheries (Proportion within Area)", "Oil Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropF"])/2
yval=max(df_ss_oil["propOil"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")
            
g = sns.relplot(x="ESIPropA", y="propGas", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI MFTLC (Proportion within Area)", "Gas Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropA"])/2
yval=max(df_ss_oil["propGas"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")
            
g = sns.relplot(x="ESIPropM", y="propGas", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI Mammals (Proportion within Area)", "Gas Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropM"])/2
yval=max(df_ss_oil["propGas"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")
            
g = sns.relplot(x="ESIPropF", y="propGas", kind="scatter",
            data=df_ss_oil, palette="Paired");
g.set_axis_labels("C-ESI Fisheries (Proportion within Area)", "Gas Production Proportion")
g.fig.subplots_adjust(bottom=.1)
g.fig.subplots_adjust(left=.2)
xval=max(df_ss_oil["ESIPropF"])/2
yval=max(df_ss_oil["propGas"])/2
plt.axvline(xval, 0,1, label="test", color="orange")
plt.axhline(yval, 0,1, label="test", color="orange")


plt.show()
            
