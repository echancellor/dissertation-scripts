'''

This module creates a data melt from a set of species point data (.csv files)
Uses a defined dictionary to map species nicknames to species names
Exports combined data melt to a data frame and a .csv file
Seaborn package:
--Countplot of non zero points by species
--Boxplot distribution of all species for probability of occurrence and proportion of suitable habitat
--Swarm plot  

Boxplots created from this script used for Fig 2.4A (A,B)

'''

import os
import gdal
import sys
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer
)
import pandas as ps
from PyQt5.QtCore import QFileInfo
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#File name for (Scenario12 is fish species)
scenName = 'Scenario12'

dir_with_csvs = 'C:/Dissertation Project/ScenariosQGIS/'+scenName+'/inputCSVs'

#Chose directory
os.chdir(dir_with_csvs)

#List of csvs in folder to combine
def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith(suffix) ]
csvfiles = find_csv_filenames(dir_with_csvs)

listofdf = []

# Create a dictionary with species names and nicknames
# where the key is the species name and the value is the nickname.
fishnick = {
"albicans": "A.sailfish",
"thynnus": "B.tuna",
"nigricans": "B.marlin",
"hippurus": "Mahi-mahi",
"dumerili": "G.amberjack",
"cavalla": "K.mackerel",
"warmingii": "W.lantern",
"ocellatus": "R.drum",
"morio": "R.grouper",
"campechanus": "R.snapper",
"cephalus": "S.mullet",
"gladius": "Swordfish",
"chamaeleonticeps": "Tilefish"
}

# create an Empty DataFrame object
df_total = ps.DataFrame()

#Creates the data melt file, comment out if file is created
for fn in csvfiles:
    fileInfo = QFileInfo(fn)
    baseName = fileInfo.baseName()
    df = ps.read_csv(fn, keep_default_na=False, na_values=[""])
    listofdf.append(ps.read_csv(fn, keep_default_na=False, na_values=[""]))
    #join new df to df_total with left join
    #### CHOOSE ONE
    #df_total = ps.merge(left=df, right=df_total, how='outer', left_on= ['lat', 'long'], right_on=['lat','long'])
    df_total = ps.concat([df_total, df])

#replace NaN with zeros
df_total.fillna(0)

#export to csv
df_total.to_csv('C:/Dissertation Project/ScenariosQGIS/'+scenName+'/dataMelt.csv', index = False)

#import file FROM .csv   (once data melt is created once, can comment out that part of procedure)
fn = 'C:/Dissertation Project/ScenariosQGIS/'+scenName+'/dataMelt.csv'
df_total = ps.read_csv(fn, keep_default_na=False, na_values=[""])

# Match the Species field to nickname and put
# the nickname in a new column called Species Name
df_total['Species Name'] = df_total.Species.map(fishnick)

#Remove rows with zeros for plotting - used for Suit Prob and Overall
df_suitProb = df_total[df_total['suitPr50'] > 0] # select rows based on condition

#Countplot by species
sns.countplot(x="Species", data=df_suitProb)

#Boxplot of suitable probability 
g = sns.catplot(x="Species Name", y="suitPr50", kind="box",
            data=df_suitProb)
g.set_ylabels("Proportion of Suitable Habitat", fontsize = 20) #.set_ylabels instead of .set_ylabel because a facet grid item
g.set_xlabels("Fish Species", fontsize = 20)

#Boxplot of overall probability 
h = sns.catplot(x="Species Name", y="over 50", kind="box",
            data=df_suitProb)
h.set_ylabels("Probability of Occurrence", fontsize = 20) #.set_ylabels instead of .set_ylabel because a facet grid item
h.set_xlabels("Fish Species", fontsize = 20)

##Creates a swarm plot from the data (not good visual for this data)
sns.swarmplot(x="Species Name", y="suitPr50", data=df_suitProb)

# display the plot
plt.show()
