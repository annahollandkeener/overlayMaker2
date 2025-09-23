#IMPORTS
import os
from qgis.core import QgsVectorLayer
import processing
from processing.core.Processing import Processing
from qgis.core import QgsRasterLayer, QgsProject
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from osgeo import gdal
import pandas as pd
import matplotlib.pyplot as plt

#Starting processing
Processing.initialize()

#RASTER SUBTRACTOR: Creates a raster overlay
def rasterSubtractor(dem, waterTable, outputFolder):
    print("\n~ Performing Raster Subtraction ~\n")
    #subtracting flat raster of blocks from DEM using raster calculator
    #getting basename of file being used
    baseName = os.path.basename(waterTable).split(".")[0] + "_overlay"
    
    outputPath = outputFolder + "/" + baseName
    
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
    
    print("\nOVERLAY GENERATED!: '" + outputPath + "'\n")

    return calc

#RASTER HISTOGRAM GENERATOR: Creates a histogram for an overlay/raster for specified blocks
def rasterHist(overlay, blocks, outputFolder, reclass = None):
    print("\n~ Performing Raster Histogram Generation ~\n")
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
def domedWT(domedBlocks, outputFolder):
    print("\n~ Performing creation of domed water table ~\n")
    
    #saving sources of clipped domes in order to merge later
    clippedDomes = []
    
    print("\nNumber of blocks to be domed: " + str(len(domedBlocks)) +"\n")
    
    for dome in domedBlocks:
        print(dome)
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
        interpolationData = dome + '::~::0::~::1::~::2'
        
        #setting outputs for each stage of the overlay
        outputPathRough = outputFolder + '/roughDome_' + baseName + '.tif'
        outputPathClipped = outputFolder + '/domed_clipped_' + baseName + '.tif'
        
        #calculating rough dome and adding to map viewer
        domeRough = processing.run("qgis:tininterpolation", {'INTERPOLATION_DATA':interpolationData,'METHOD':0,'EXTENT':extent,'PIXEL_SIZE':15,'OUTPUT': outputPathRough})
        
        
        #SMOOTHING UNNECESSARY AFTER LOOKING AT ELEV PROFILE OF DOME 
        # calculating smooth dome and adding to map viewer
        '''domeSmooth = processing.run("grass:r.resamp.filter", {'input':outputPathRough,'filter':[0],'radius':'200','x_radius':'','y_radius':'','-n':False,'output':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})
        #processing.run("grass:r.resamp.filter", {'input':outputPathRough,'filter':[0],'radius':'200','x_radius':'','y_radius':'','-n':False,'output': 'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})        
        '''
        #clipping dome to block and adding to map viewer
        #domeClipped = processing.run("gdal:cliprasterbymasklayer", {'INPUT':domeRough['OUTPUT'],'MASK':dome,'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':extent,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        domeClipped = processing.run("gdal:cliprasterbyextent", {'INPUT':domeRough['OUTPUT'],'PROJWIN': extent,'OVERCRS':False,'NODATA':None,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        #adding final clipped dome to a list
        clippedDomes.append(domeClipped['OUTPUT'])

    print(clippedDomes)
    #merging all domes    
    merge = processing.run("gdal:merge", {'INPUT':clippedDomes,'PCT':False,'SEPARATE':False,'NODATA_INPUT':None,'NODATA_OUTPUT':0,'OPTIONS':None,'EXTRA':'','DATA_TYPE':5,'OUTPUT':outputFolder + '/all_domedWT_merged.tif'})
    
    print("COMPLETED DOME: " + baseName)

    return merge

#ROAD CALC: Creates a vector layer showing roads in the project area in need of potential raising
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









        
        
        




