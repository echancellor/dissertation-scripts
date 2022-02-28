'''
This module takes in a costValues.csv which is created from CreateESI_IntersectionsWithOil.py
This module makes the figures 3.4-3.9
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



## Takes in csv file  
# These are my filefolders for my different scenarios, comment out all except the one I want
#scenName = "Scenario21 - SpeciesRichness_Proportion"
#scenName = "Scenario22 - Turtles_Proportion"
#scenName = "Scenario23 - Mammals_Proportion(Correct)"
#scenName = "Scenario24 - Fisheries_Proportion"
#scenName = "Scenario21 - SpeciesRichness_Proportion"
scenName = "Scenario25 - UnweightedFish"
#scenName = "Scenario26 - FishWeighted2"
#scenName = "Scenario28 - Fish,Mammal,Turtle,Larval,Coral"

#graphName = "Fish Species - Weighted Species = 2"
#graphName = "Fish, Mammals, Turtles, Larval Fish, Corals"
graphName = "Fish Species - Unweighted"

oilSpillNames = ['DWH','Fall','WFS','WGOM']

# Create a dictionary with species names and nicknames
# where the key is the species name and the value is the nickname.
fishnick = {
"atlanticsail": "A.sailfish",
"bluefin": "B.tuna",
"bluemarlin": "B.marlin",
"dolphinfish": "Mahi-mahi",
"greatamber": "G.amberjack",
"kingmack": "K.mackerel",
"lantern": "W.lantern",
"reddrum": "R.drum",
"redgroup": "R.grouper",
"snapper": "R.snapper",
"stripemullet": "S.mullet",
"swordfish": "Swordfish",
"tilefish": "Tilefish"
}



#### All Hard code changes above this line
sns.set()

fn = "C:/Dissertation Project/ScenariosQGIS/"+scenName+"/CostValues.csv"

df = ps.read_csv(fn, keep_default_na=False, na_values=[""])

df1 = df.fillna(0)


#########################
###Adding weights
## fill this in for weights
#myWeights = "1,1,2,2,2,2,2,1,1,2,1,2,2"
#
##multiply the columns of the dataframe by the weights
#df_2 = df1[:,1:13] *= np.array(myWeights)

#export dataframe
#df_2.to_csv(myDir + "/" + scenName + "/CostValuesWeights.csv")
####################

dfcol = df1.columns.values

#df2 = ps.melt(df1, id_vars =['x','oil', 'combine', 'scen', 'cat', 'Unnamed: 0'])

#df2.to_csv('C:/Dissertation Project/ScenariosQGIS/'+scenName+'/CostValues3.csv', index = False)


#####Extra bit of code to only include some species from a modified CostValues2  - 8/19/2021
fn = "C:/Dissertation Project/ScenariosQGIS/"+scenName+"/CostValues3.csv"

#don't need to read file every time - uncomment for file
#df3 = ps.read_csv(fn, keep_default_na=False, na_values=[""])

# Match the Species field to nickname and put
# the nickname in a new column called Species Name
df3['Species Name'] = df3.variable.map(fishnick)

# Remove rows with x < 25
#selecting rows based on condition 
rslt_df = df3[df3['x'] >= 24] 
rslt_df2 = rslt_df[rslt_df['x'] <= 1001]



# By ESI, which scenario is the worst
#Box plot of distribution per oil scenario per component
#with sns.axes_style(style='ticks'):
#    g = sns.factorplot("x", "value", "oil", data=df3, kind="box")
#    g.set_axis_labels("oil concentration (ppb)", "ESI Score");
#    g._legend.set_title('Spill Scenario')
#    g.fig.subplots_adjust(top=.8)
##set overall title
##g.fig.suptitle('Species Richness C-ESI  Components by Oil Blowout Scenario')
#g.fig.suptitle(graphName+' C-ESI  Components by Oil Blowout Scenario')
sns.color_palette("Paired")
            
#Create 1 x 4 for lines for each species with x factor for each spill
g = sns.relplot(x="x", y="value", hue="Species Name", kind="line",
            col="oil", data=rslt_df2, col_wrap=1, palette="Paired");
g.set_axis_labels("max concentration (ppb)","Proportion of C-ESI")
g._legend.set_title('C-ESI component')
#move overall title up
#set overall title
#g.fig.suptitle('Species Richness C-ESI by Oil Blowout Scenario')
g.fig.suptitle(graphName+' C-ESI by Oil Blowout Scenario')

# dict of line positions and annotations
la = {0: [53.16, 68.22, 100, .1, '0.5 ppb PAH',100, .06, '1.0 ppb PAH', 295.09, 305, .3, '10 ppb PAH'], 1: [10, 0.5, 100, .5, 'text_b', 100, .45, 0],
      2: [25, 0.6, 100, .5, 'text_c',100,.45,0], 3: [35, 0.7, 100, .5, 'text_d',100,.45,0]}

# flatten axes into a 1-d array
axes = g.axes.flatten()

# iterate through the axes
for i, ax in enumerate(axes):
    ax.axvline(la[0][0], ls='--', color='green')
    ax.axvline(la[0][1], ls='--', color='magenta')
    ax.axvline(la[0][8], ls='--', color='blue')
    ax.text(la[i][2], la[i][3], la[0][4], color='green')
    ax.text(la[i][5], la[i][6], la[0][7], color='magenta')
    ax.text(la[0][9], la[0][10], la[0][11], color='blue')
#plt.axvline(46.94, 0,2, label="test")
#g.map(plt.axvline, x=46.94, ls='--', c='red', label=".5 ppb PAH")


g.fig.subplots_adjust(top=.9)
g.fig.subplots_adjust(bottom=.1)
##Create individual plot line for each species for each spill
#g = sns.relplot(x="x", y="value", hue="variable",
#            col="oil", row="variable", aspect = .75,
#            kind="line", estimator=None, data=df2);
#g.set_axis_labels("max concentration","ESI score")
#g._legend.set_title('ESI component')
#

#with sns.axes_style('white'):
#    g = sns.factorplot("x", "value", data=df2, row="oil", aspect=3.0, kind='bar',
#                       hue='variable')
#    g.set_ylabels('ESI Score at Concentration X')
#
#

plt.show()

  
