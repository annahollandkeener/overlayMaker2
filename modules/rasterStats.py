#imports
import os
from qgis.core import QgsVectorLayer
import processing
from processing.core.Processing import Processing
from modules import rasterSubtractor
from qgis.core import QgsRasterLayer, QgsProject
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from osgeo import gdal
import pandas as pd
import matplotlib.pyplot as plt



#make sure not to use blocks with inner domes designated 

#take in the overlay and blocks 
#reclassify into zones (<0, 0 to 1, 1 to 2, 2 to 3, >3)
#calculate zonal histogram 
#turn into csv
#for each block in the block column, sum up total pixels
#then for each histo_# count, add to a list
#create a histogram from this list
#add the histogram to a list

#display all histograms in list at once


def rasterHist(overlay, blocks, outputFolder, reclass = None):
    if reclass == None:
        reclass = ['-1000','0','1','0','1','2','1','2','3','2','3','4','3','1000','5']
    
    ranges = ['<0', '0-1', '1-2', '2-3', ">3"]

    baseName = os.path.basename(overlay).split(".")[0] + "_"

    #reclassifying overlay based on block zones
    reclassRast = processing.run("native:reclassifybytable", {'INPUT_RASTER':overlay,'RASTER_BAND':1,'TABLE':reclass,'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'CREATE_OPTIONS':None,'OUTPUT':'TEMPORARY_OUTPUT'})

    #calculating zonal histogram from reclassified raster 
    zonalHistOP = outputFolder + "/" + baseName + "zonalHist.gpkg"
    zonalHist = processing.run("native:zonalhistogram", {'INPUT_RASTER':reclassRast['OUTPUT'],'RASTER_BAND':1,'INPUT_VECTOR':blocks,'COLUMN_PREFIX':'CLASS_','OUTPUT':zonalHistOP})

    #zonalHist transform to csv
    zonalHistCSV = outputFolder + "/" + baseName + "zonalHist_CSV"
    options = gdal.VectorTranslateOptions(format='CSV', layerCreationOptions=['GEOMETRY=AS_WKT'])
    gdal.VectorTranslate(zonalHistCSV, zonalHistOP, options=options)

    #locating csv because apparently the creation of the csv from gpkg creates a folder to hold the csv
    zonalHistCSV2 = zonalHistCSV + "/" + "updated_blocks_overlay_zonalHist.csv"
    #reading the csv
    df = pd.read_csv(zonalHistCSV2)

    # Display the first few rows of the DataFrame
    print(df.head())

    histogramData = []

    row = 0

    for block in df['block']:
        counts = []
        classNum = 1
        
        while (classNum <= 5):
            className = 'CLASS_' + str(classNum)
            counts.append(int(df.loc[row, className]))
            classNum += 1
            
        histogramData.append(counts)

        row += 1
        
    #setting up window to hold multiple histograms
    n_cols = 2
    n_rows = (len(histogramData) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8, 2.5   * n_rows))
    axes = axes.flatten()

    histNameNum = 0 
    histNames = df['block'].to_list()

    colors = ['blue', 'lightgreen', 'green', 'yellow', 'red']

    for i, data in enumerate(histogramData):
        if i < len(axes): # Ensure we don't try to plot on non-existent axes
            ax = axes[i]
            ax.bar(ranges, data, color = colors, edgecolor='black')
            ax.set_title(histNames[histNameNum])
            ax.set_xlabel('Range')
            ax.set_ylabel('Frequency')
            ax.set_ylim(0, 5000000)
            ax.ticklabel_format(axis='y', style='plain', scilimits=None, useOffset=None, useLocale=None, useMathText=None)
            histNameNum += 1

    plt.tight_layout()
    plt.show()














#takes in a vector layer of blocks 
#splits the vector layers blocks into individual files and puts them in a list
#for each individual block vector layer
    #get the base name
    #add base name to dictionary

    #create a list that will hold the raster stats for this block

    #clips dem to block 
    #get total number of pixels in block 
    #for 4 zones (<0, 0 to 1, 1 to 2, 2 to 3, >3)
        #creates a separate raster for each range with raster calc
        #counts number of pixels in this range
        #divides number of pixels in range by total number of pixels in block
        #multiplies this by 100 to get percent
        #adds this percent to the raster stats list
    
    #enters the raster stats list into the dictionary for the corresponding block 
    #creates a histogram for number of pixels in each range
    #adds this histogram to a list of histograms

#for each histogram in the list of histograms, add to the same display window
#display the window of all histograms
