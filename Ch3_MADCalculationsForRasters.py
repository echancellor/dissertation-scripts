## Script takes in a file of raster of the same resolution (.tif) files
# Calculates the pair-wise Mean Average Difference between each set of rasters
# Converts results to a pandas dataframe for graphing
# Exports dataframe to a csv file


## import dependencies
import processing
import numpy as np
from osgeo import gdal, gdal_array, osr, ogr
import glob, os
from PyQt5.QtCore import QFileInfo
from qgis.core import QgsRasterLayer, QgsRectangle
#import plotly.graph_objects as go
import pandas as pd


# File path with list of rasters to perform dissimilarity on
#NOTE: File names must have \ or [// for folder separation, not /
path = "C:/Dissertation Project/Distributions/SpeciesDistributions/OverallPrRasters-DissimilarityFishMammals"

#File path for rasters of ranges to go
output_path = 'C:/Dissertation Project/Distributions/SpeciesDistributions/DifferenceRastersOutput5'

#File name and path for polygon shape file of area to calculate
#In this example, the Gulf of Mexico
fn = "C:/Dissertation Project/iho/iho.shp"

#File path for csv file of results
csv_path = 'C:/Dissertation Project/Distributions/SpeciesDistributions/DifferenceRastersOutput5'


###ALL USER INPUTS ARE ABOVE THIS LINE
#Makes a List of .tifs in specified folder
def find_tif_filenames(path_to_dir, suffix=".tif"):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith(suffix) ]

rasterfiles = find_tif_filenames(path)

# Create a copy list of .tif files in this location
rasterfiles2 = rasterfiles

# Chose directory with rasters for combine
os.chdir(path)

#Creates null extent
extent = QgsRectangle()
extent.setMinimal()

#define empty set list for layer
rlist = []
#define empty set list for baseName
rasterlist = []

# populates rlist and rasterlist from directory of rasters, updates extent to match rasters
for raster in glob.glob("*.tif"):
    fileInfo = QFileInfo(raster)
    fname = fileInfo.baseName()  
    rasterlist.append(fname[0:4]) #first five letters
    #rasterlist.append(fileInfo.baseName())
    baseName = fileInfo.baseName()
    rlayer = QgsRasterLayer(raster, baseName)
    # Combine raster layers to list
    rlist.append(rlayer)
    # Combine raster extents
    extent.combineExtentWith(rlayer.extent())
    #clist.append(fileInfo.absoluteFilePath())
#
#Get extent from the updated extent (for below loop)    
xmin = extent.xMinimum()
xmax = extent.xMaximum()
ymin = extent.yMinimum()
ymax = extent.yMaximum()

#copy of rasterlist and rlist for loop
rasterlist2 = rasterlist.copy()
rlist2 = rlist.copy()

#Create two iterators for loop
itr1 = iter(rasterlist)
itr2 = iter(rasterlist2)

#For loop to create a difference raster for each pair of rasters and save to output folder
for layer in rlist:
    #name of first file
    itrl = iter(rasterlist)
    name1 = next(itr1)
    #create an iterative list from rasterlist2
    itr2 = iter(rasterlist2)
    for layer2 in rlist2:
        name2 = next(itr2)
        output = output_path + "/" + name1+name2+".tif"
        #list of two raster layers for the pairwise comparison
        runlist = [layer,layer2]
        # Run algorithm and set relevant parameters, method 9 is range
        processing.run("grass7:r.series",
                        {"input":runlist,
                        "-n":False,
                        "method":9,
                        "range":'-10000000000,10000000000', 
                        "GRASS_REGION_PARAMETER":"%f,%f,%f,%f"% (xmin, xmax, ymin, ymax), 
                        "GRASS_REGION_CELLSIZE_PARAMETER":0,
                        "output":output})
    #remove first file name from second set
    rasterlist2.pop(0)
    #remove first layer from second set
    rlist2.pop(0)
                    


#list of .tif difference rasters created from above loop
rangerasters = find_tif_filenames(output_path)

#find mean intersection between each difference raster and the provided polygon, 
#intersection value is saved as an attribute in the polygon fn file

for fn3 in rangerasters:
    lyr_name3 = fn3.replace('.tif', '')  #remove .tif from file name
    processing.run("qgis:zonalstatistics", {'INPUT_RASTER':output_path + "/" + fn3,
    'RASTER_BAND':1,
    'INPUT_VECTOR':fn,'COLUMN_PREFIX':lyr_name3,'STATS':[2]})  #'STATS' = 1 for sum or 2 for mean

## Load the fn file with saved interection attributes (created above) to QGIS
#A QGIS Project must be open
layer = iface.addVectorLayer(fn, 'iho', 'ogr')

##get the attributes from the added layer and put them in a dataframe
fid = 0 # the first feature (zero based indexing!)
iterator = layer.getFeatures(QgsFeatureRequest().setFilterFid(fid))
feature = next(iterator)

#initialize empty list for field names
flist = []
#initialize empty list for value names
vlist = []
#for each field in the feature, add field name to flist, add value to to vlist
for field in layer.fields():
    flist.append(field.name())
    idx = layer.fields().indexFromName(field.name())
    vlist.append(feature.attributes()[idx])
    
#convert costValues to dataframe
df = pd.DataFrame ([flist,vlist])
df = df.transpose()

#export dataframe
df.to_csv(output_path + "/MeanAverageDifference_Values.csv")


