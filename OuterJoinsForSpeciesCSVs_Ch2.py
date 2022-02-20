'''
Takes in folder of species .csvs to be combined
Joins them all based on identially named Lon and Lat fields (outer joins)
Outputs to .csv named PercentofLayers

Note_ would like to fix species column names because at the moment they have to be fixed manually
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

scenName = 'Scenario12'

##########
dir_with_csvs = 'C:/Dissertation Project/ScenariosQGIS/'+scenName+'/inputCSVs'
os.chdir(dir_with_csvs)

#List of csvs in folder
def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith(suffix) ]
csvfiles = find_csv_filenames(dir_with_csvs)

#Set and empty data frame
listofdf = []

#### CHOOSE ONE based on the column names of your files
#df_total = ps.DataFrame({'lat': [],'long' : []})
df_total = ps.DataFrame({'Center Lat': [],'Center Lon' : []})


for fn in csvfiles:
    fileInfo = QFileInfo(fn)
    baseName = fileInfo.baseName()
    df = ps.read_csv(fn, keep_default_na=False, na_values=[""])
    listofdf.append(ps.read_csv(fn, keep_default_na=False, na_values=[""]))
    #join new df to df_total with left join
    #### CHOOSE ONE based on column name
    #merges does an outer join every time
    #df_total = ps.merge(left=df, right=df_total, how='outer', left_on= ['lat', 'long'], right_on=['lat','long'])
    df_total = ps.merge(left=df, right=df_total, how='outer', left_on= ['Center Lat', 'Center Lon'], right_on=['Center Lat','Center Lon'])


#replace NaN with zeros
df_total.fillna(0)

#export to csv
# Note_ would like to fix species column names because at the moment they have to be fixed manually
df_total.to_csv('C:/Dissertation Project/ScenariosQGIS/'+scenName+'/PercentofLayers.csv', index = False)

