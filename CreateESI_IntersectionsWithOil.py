##Combine rasters into ESI, calculate intersections with surface oil files
import processing
import glob, os
from PyQt5.QtCore import QFileInfo
from qgis.core import QgsRasterLayer, QgsRectangle
from pandas import DataFrame

#File path where folder of rasters are located
myDir = "C:/Dissertation Project/ScenariosQGIS"

#Scenario name
scenName = "Scenario28 - Fish,Mammal,Turtle,Larval,Coral"

# Chose directory for the folder with with rasters to combine (.tif extension)
os.chdir(myDir + "/" + scenName + "/inputESIs")

# Choose file location and name for output raster
output = myDir + "/" + scenName + "/inputESIs/Combined/" + "/Combined.tif"

#folder where oil blowout files are located (all files in this folder with .csv extension)
myPath = "C:\\Dissertation Project\\Distributions\\OilSpillDistributions\\ArcMapOutputs\\"

# path to place oil blowout polygons from scenarios
polyPath = myDir + "/" + scenName + "/outputs"

# Create list of oil concentration values for polygon (in ppb)
xValues = [1, 5, 10, 25, 50, 100, 150, 200, 400, 800, 1500, 2000]

#Create list of Oil Spill Names
oilSpillNames = ["WFS", "DWH", "WGOM", "Fall"]



#### No user inputs below this line

#create empty list for cost
clist = []

#create empty raster list
rlist = []

# set initial minimum extent, will be modified when add rasters
extent = QgsRectangle()
extent.setMinimal()

# Create empty list for Headers
myHeaders = []

# Creates list of all .tif files within selected directory
for raster in glob.glob("*.tif"):
    fileInfo = QFileInfo(raster)
    baseName = fileInfo.baseName()
    rlayer = QgsRasterLayer(raster, baseName)
    # Combine raster layers to list
    rlist.append(rlayer)
    # Combine raster extents
    extent.combineExtentWith(rlayer.extent())
    clist.append(fileInfo.absoluteFilePath())
    myHeaders.append(baseName)

# Get parameters of new combined extent    
xmin = extent.xMinimum()
xmax = extent.xMaximum()
ymin = extent.yMinimum()
ymax = extent.yMaximum()

# Run r.series algorithm and set relevant parameters
processing.run("grass7:r.series",
                {"input":rlist,
                "-n":False,
                "method":10,
                "range":'-10000000000,10000000000', 
                "GRASS_REGION_PARAMETER":"%f,%f,%f,%f"% (xmin, xmax, ymin, ymax), 
                "GRASS_REGION_CELLSIZE_PARAMETER":0,
                "output":output})
                

#Add combined file to clist
clist.append(output)

# Create empty list for cost values to be placed in
costValues = []    

# Create list for Headers (first column is just 1)
myHeaders = ["holder"]

# for loop for Oil Spills
for k in oilSpillNames:

    # create string for pulling file names, and renaming files
    myString = k

    # location of shape file with points
    fn = myPath + myString + "maxMatrix.shp"
    # Add layer to QGIS
    layer = iface.addVectorLayer (fn, '', 'ogr')

    # for loop for X Values
    for i in xValues:

        layer.selectByExpression('"overmax" > ' + str(i))

        #path to save layer to (will change with loop)
        path = myDir + "/" + scenName + "/outputs/" + myString + str(i) + 'max.shp'
        #save layer to path
        _writer = QgsVectorFileWriter.writeAsVectorFormat(layer,path,
        'utf-8',driverName='ESRI Shapefile', onlySelected=True)

        #path to save polygon to
        outpath = myDir + "/" + scenName + "/outputs/" + myString + str(i) + '.shp'
        # create polygon
        processing.run("grass7:v.hull", {'input':path,'where':'','-f':True,
        'output':outpath,'GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
        'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':3,
        'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':True})

        #add polygon to qgis
        myLayer = iface.addVectorLayer (outpath, '', 'ogr')

                
        #for loop for cost files
        for j in clist:
            ##take output and zonal statistics with raster
            processing.run("qgis:zonalstatistics", {'INPUT_RASTER':j,'RASTER_BAND':1,'INPUT_VECTOR':outpath,'COLUMN_PREFIX':'XVALUE_','STATS':[1]})

            #there is only one feature in each polygon, so get feature 0
            feat = myLayer.getFeature(0)
            myfeat = feat.attributes()
            myfeat.append(i)
            myfeat.append(myString)
            myfeat.append(scenName)
            
            myHeaders.append("cost"+str(j))
        
        #Add nested list of costvalues for j to overall cost values        
        costValues.append(myfeat)
   
#end loop

#Add static columns to list
columnList = ["cat"] +  myHeaders + ["combine", "x", "oil", "scen"]

#convert costValues to dataframe
df = DataFrame (costValues,columns=columnList)

#export dataframe
df.to_csv(myDir + "/" + scenName + "/CostValues.csv")


