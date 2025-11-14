#IMPORTS
import os
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsField, QgsVectorFileWriter, QgsCoordinateTransformContext
from qgis.PyQt.QtCore import QVariant
import processing
from processing.core.Processing import Processing
from qgis.core import QgsRasterLayer, QgsProject
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from osgeo import gdal
import pandas as pd
import matplotlib.pyplot as plt
from qgis.core import edit, QgsVectorDataProvider, QgsVariantUtils
import math

#import tests
import testFunctions

#Starting processing
Processing.initialize()

#RASTER SUBTRACTOR: Creates a raster overlay
def rasterSubtractor(dem, waterTable, outputFolder, opt = 0):
    print("\n~ Performing Raster Subtraction ~")
    #subtracting flat raster of blocks from DEM using raster calculator
    
    outputPath = outputFolder + "/overlay_option_" + str(opt) + ".tif"
    
    topDEM = QgsRasterLayer(dem, "topDEM")

    bottomDEM = QgsRasterLayer(waterTable, "bottomDEM")
    
    top = QgsRasterCalculatorEntry()
    top.raster = topDEM
    top.bandNumber = 1
    top.ref = 'top_raster@1'
    
    bottom = QgsRasterCalculatorEntry()
    bottom.raster = bottomDEM
    bottom.bandNumber = 1
    bottom.ref = 'bottom_raster@1'

    transform_context = QgsProject.instance().transformContext()
    
    calc=QgsRasterCalculator(('"top_raster@1" - "bottom_raster@1"'), outputPath, 'GTiff', bottomDEM.extent(), bottomDEM.width(), bottomDEM.height(), [top, bottom], transform_context)

    calc.processCalculation()
    
    print("OVERLAY GENERATED: '" + outputPath)

    return outputPath

#RASTER HISTOGRAM GENERATOR: Creates a histogram for an overlay/raster for specified blocks
def rasterHist(overlay, blocks, progressFolder, outputFolder, reclass = None, histPlotName = str):
    print("\n~ Performing Raster Histogram Generation ~")
    
    if reclass == None:
        reclass = ['-1000','0','1','0','1','2','1','2','3','2','3','4','3','1000','5']
    
    ranges = ['<0', '0-1', '1-2', '2-3', ">3"]

    baseName = os.path.basename(overlay).split(".")[0] + "_"

    #reclassifying overlay based on block zones
    reclassRast = processing.run("native:reclassifybytable", {'INPUT_RASTER':overlay,'RASTER_BAND':1,'TABLE':reclass,'NO_DATA':-9999,'RANGE_BOUNDARIES':0,'NODATA_FOR_MISSING':False,'DATA_TYPE':5,'CREATE_OPTIONS':None,'OUTPUT':progressFolder + "/" + baseName + "reclass.gpkg"})

    #turning reclass raster into a raster layer object
    reclassRastRL = QgsRasterLayer(reclassRast['OUTPUT'], "reclassified raster", "gdal")

    #calculating zonal histogram from reclassified raster 
    zonalHistOP = progressFolder + "/" + baseName + "zonalHist.gpkg"
    zonalHist = processing.run("native:zonalhistogram", {'INPUT_RASTER':reclassRast['OUTPUT'],'RASTER_BAND':1,'INPUT_VECTOR':blocks,'COLUMN_PREFIX':'CLASS_','OUTPUT':zonalHistOP})

    #getting pixel size in order to get area
    pixel_size_x = reclassRastRL.rasterUnitsPerPixelX()
    pixel_size_y = reclassRastRL.rasterUnitsPerPixelY()
    pixelAreaFT = pixel_size_x * pixel_size_y
    pixelAreaAcres = pixelAreaFT / 43560
    

    #zonalHist transform to csv
    zonalHistCSV = progressFolder + "/" + baseName + "zonalHist_CSV"
    options = gdal.VectorTranslateOptions(format='CSV', layerCreationOptions=['GEOMETRY=AS_WKT'])
    gdal.VectorTranslate(zonalHistCSV, zonalHistOP, options=options)

    #locating csv because apparently the creation of the csv from gpkg creates a folder to hold the csv
    zonalHistCSV2 = zonalHistCSV + "/" + baseName + "zonalHist.csv"

    #reading the csv
    df = pd.read_csv(zonalHistCSV2)

    histogramData = []
    fullAreas = []
    maxes = []

    row = 0

    for block in df['block']:
        counts = []
        classNum = 1
        blockAreaAcres = 0
        
        while (classNum <= 5):
            className = 'CLASS_' + str(classNum)
            #turnign pixel count into acres and adding it to a list to be used in the histogram
            counts.append(round(int(df.loc[row, className]) * pixelAreaAcres, 2))
           
            blockAreaAcres += (int(df.loc[row, className]) * pixelAreaAcres)

            classNum += 1
            
        histogramData.append(counts)
        fullAreas.append(round(blockAreaAcres, 2))
        maxes.append(max(counts))

        row += 1

    #I WANT TO MAKE IT SO THAT ALL OF THE OVERLAY OPTION HISTOGRAMS ARE ON ONE WINDOW
    subFigRows = math.ceil(len(histogramData))

    #setting up window to hold multiple histograms
    n_cols = 2
    n_rows = (len(histogramData) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8, 2.5   * n_rows))
    axes = axes.flatten()

    histNameNum = 0 
    histNames = df['block'].to_list()

    #bar colors
    cmap = plt.cm.get_cmap('rainbow')
    colors = [cmap(i / len(ranges)) for i in range(len(ranges))]

    for i, data in enumerate(histogramData):
        if i < len(axes): # Ensure we don't try to plot on non-existent axes
            ax = axes[i]
            ax.bar(ranges, data, color = colors, edgecolor='black')
            ax.set_title(histNames[histNameNum])
            ax.set_xlabel('Depth to Water Table')
            ax.set_ylabel('Acres')
            ax.set_ylim(0, maxes[i] + (fullAreas[i] / 100))
            ax.ticklabel_format(axis='y', style='plain', scilimits=None, useOffset=None, useLocale=None, useMathText=None)
            histNameNum += 1

    plt.tight_layout()
    histogramWindowName = outputFolder + "/" + baseName + "hist"
    plt.suptitle(histPlotName)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(histogramWindowName)
    plt.show()

    print(f"HISTOGRAM GENERATED: {histogramWindowName}")

#FLAT WATER TABLE GENERATOR: Creates a flat water table raster for specified blocks
def flatWT(blocks, outputFolder):
    
    print("\n~ Performing flat water table generation ~")

    #saving sources of clipped domes in order to merge later
    #flatWTList = []
    
    #for each selected layer (blocks)...
    baseName = os.path.basename(blocks).split(".")[0]
    
    #creating output paths for flat rasterized blocks and overlay
    outputPath = outputFolder  + '/flatRaster_' + baseName + '.tif'

    #create a flat raster based on the waterlevel of each blocks
    blockFlatRaster = processing.run("gdal:rasterize", {'INPUT':blocks,'FIELD':'wl','BURN':0,'USE_Z':False,'UNITS':1,'WIDTH':3,'HEIGHT':3,'EXTENT':None,'NODATA':0,'OPTIONS':None,'DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':outputPath})

    print(">>> FLAT WATER TABLE GENERATED!: " + blockFlatRaster['OUTPUT'] + "\n")

    return blockFlatRaster['OUTPUT']

#DOMED WATER TABLE GENERATOR: Creates a domed water table raster for specified blocks
def domedWT(domedBlocks = [], outputFolder = str, columnIndicator = 2, opt = int):
    print("\n~ Performing creation of domed water table: Option " + str(opt) + " ~")
    
    #saving sources of clipped domes in order to merge later
    clippedDomes = []
        
    for dome in domedBlocks:
        #getting name of vector layer from path
        baseName = os.path.basename(dome).split(".")[0]
        
        #saving the vector in a variable
        domeLayer = QgsVectorLayer(dome, baseName, "ogr")
        
        #checking for validity of layer and skipping if necessary
        if not domeLayer.isValid():
            print("\n" + baseName + " is not valid. \nSkipping...\n")
            continue
        
        #getting extent of domed block 
        extent = domeLayer.extent()
        
        #setting up path and instructions for TIN interpolation tool
        interpolationData = dome + '|layername=' + baseName +'::~::0::~::' + str(columnIndicator) + '::~::2'

        #calculating rough dome and adding to map viewer
        roughOutput = outputFolder + "/" + baseName + "_domeRough_" + str(opt) + ".tif"
        clippedOutput = outputFolder + "/" + baseName + "_domeClipped_" + str(opt) + ".tif"
        
        domeRough = processing.run("qgis:tininterpolation", {'INTERPOLATION_DATA':interpolationData,'METHOD':0,'EXTENT':extent,'PIXEL_SIZE':15,'OUTPUT': roughOutput})
        #print("Rough dome created: " + domeRough['OUTPUT'])

        #clipping dome to block
        domeClipped = processing.run("gdal:cliprasterbyextent", {'INPUT':domeRough['OUTPUT'],'PROJWIN': extent,'OVERCRS':False,'NODATA':None,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':clippedOutput})
        
        #adding final clipped dome to a list
        clippedDomes.append(domeClipped['OUTPUT'])

    #merging all domes    
    merge = processing.run("gdal:merge", {'INPUT':clippedDomes,'PCT':False,'SEPARATE':False,'NODATA_INPUT':None,'NODATA_OUTPUT':0,'OPTIONS':None,'EXTRA':'','DATA_TYPE':5,'OUTPUT':outputFolder + '/all_domedWT_merged_' + str(opt) + "ft.tif"})
    
    print("COMPLETED DOME: " + merge['OUTPUT'] + "\n")

    return merge

#ROAD CALC: Creates a vector layer showing roads in the project area in need of potential raising
#******UNDER CONSTRUCTION********
def roadCalc(dem, roads, WT, outputFolder):
    print("\n~ Performing calculation of affected roads in project area ~\n")

    #getting basename of file being used
    baseName = os.path.basename(roads).split(".")[0] + "_overlay"
        
    outputPath = outputFolder + "/" + baseName

    roadRasterOP = "'" + outputFolder + "/" + "roadRaster.tif'"
    print(roadRasterOP)

    #clipping dem to roads
    processing.run("gdal:rasterize", {'INPUT':'C:/Users/annah/Downloads/CarolinaRanch_roads.shp','FIELD':'','BURN':1,'USE_Z':False,'UNITS':1,'WIDTH':3,'HEIGHT':3,'EXTENT':None,'NODATA':0,'OPTIONS':None,'DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'C:/Users/annah/Downloads/rr2.tif'})
    roadsRaster = processing.run("gdal:cliprasterbymasklayer", {'INPUT':dem,'MASK':roads,'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':'C:/wfh/python/overlayMaker/RR'})

    #subtracting proposed water table from rasterized version of the roads
    #roadsOverlay = rasterSubtractor.rasterSubtractor(roadsRaster['OUTPUT'], WT, outputPath)

