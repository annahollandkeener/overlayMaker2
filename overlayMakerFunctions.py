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
def domedWT(domedBlocks, outputFolder, columnIndicator = 2):
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
        interpolationData = dome + '::~::0::~::' + str(columnIndicator) + '::~::2'
        
        #setting outputs for each stage of the overlay
        outputPathRough = outputFolder + '/roughDome_' + baseName + '.tif'
        outputPathClipped = outputFolder + '/domed_clipped_' + baseName + '.tif'
        
        #calculating rough dome and adding to map viewer
        domeRough = processing.run("qgis:tininterpolation", {'INTERPOLATION_DATA':interpolationData,'METHOD':0,'EXTENT':extent,'PIXEL_SIZE':15,'OUTPUT': outputPathRough})
        
        
        #clipping dome to block and adding to map viewer
        domeClipped = processing.run("gdal:cliprasterbyextent", {'INPUT':domeRough['OUTPUT'],'PROJWIN': extent,'OVERCRS':False,'NODATA':None,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        #adding final clipped dome to a list
        clippedDomes.append(domeClipped['OUTPUT'])

    print(clippedDomes)
    #merging all domes    
    merge = processing.run("gdal:merge", {'INPUT':clippedDomes,'PCT':False,'SEPARATE':False,'NODATA_INPUT':None,'NODATA_OUTPUT':0,'OPTIONS':None,'EXTRA':'','DATA_TYPE':5,'OUTPUT':outputFolder + '/all_domedWT_merged.tif'})
    
    print("COMPLETED DOME: " + merge['OUTPUT'])

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

#AUTO OVERLAY: takes in blocks and a dem and outputs 5 overlay options and associated histograms
def autoOverlay(blocks, dem, outputFolder):
    testOutputPath = "C:/Users/annah/Downloads/testmaterials/autoOverlay/output"


    outputPath = outputFolder + "/demStats"

    #adding other wl columns for overlay options
    overlayOptions = [0, 1, 2, -1, -2]

    #LIST FOR HOLDING MERGED BLOCKS WITH INNER AND OUTER BOUNDARIES
    domeBlocks = []

    #calculating DEM stats: count, sum, mean, stdv
    demStats = processing.run("native:zonalstatisticsfb", {'INPUT':blocks,'INPUT_RASTER':dem,'RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2,4],'OUTPUT':outputPath})
    print("Zonal Stats for initial blocks located here: " + demStats['OUTPUT'])
    print(demStats)

    #adding wl column to block (mean - 1stdv)
    target_field = 'wl'

    demStatsVL = QgsVectorLayer(demStats['OUTPUT'], "DEMStats")
    
    with edit(demStatsVL):
        for feature in demStatsVL.getFeatures():
            print(feature['_mean'] - feature['_stdev'])
            feature.setAttribute(feature.fieldNameIndex('wl'), feature['_mean'] - feature['_stdev'])
            demStatsVL.updateFeature(feature)
    
    print(f"Attribute calculated for {target_field} field")

    #splitting each block into its own layer
    splitBlocksInput = demStats["OUTPUT"] + '|layername=demStats'
    splitBlocksOutput = "C:/Users/annah/Downloads/testmaterials/autoOverlay/split"
    splitBlocks = processing.run("native:splitvectorlayer", {'INPUT':splitBlocksInput,'FIELD':'block','PREFIX_FIELD':True,'FILE_TYPE':1,'OUTPUT':splitBlocksOutput})
    print(splitBlocks['OUTPUT_LAYERS'])
    i = 0
    #making grid for each block to determine highest point and add this as a dome feature to the block
    for b in splitBlocks['OUTPUT_LAYERS']:
        
        print(i)
        block = QgsVectorLayer(b, "block", "ogr")

        #creating grid 
        grid = processing.run("native:creategrid", {'TYPE':0,'EXTENT':block.extent(),'HSPACING':610,'VSPACING':610,'HOVERLAY':0,'VOVERLAY':0,'CRS':QgsCoordinateReferenceSystem(block.crs()),'OUTPUT':'TEMPORARY_OUTPUT'})

        #
        clippedGrid = processing.run("native:clip", {'INPUT':grid['OUTPUT'],'OVERLAY':block,'OUTPUT':'TEMPORARY_OUTPUT'})
    
        #buffering the grid
        buffered = processing.run("native:buffer", {'INPUT':clippedGrid['OUTPUT'],'DISTANCE':599.99959999999948,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':'TEMPORARY_OUTPUT'})
        #zonal stats on the grid vectors
        TODStats = processing.run("native:zonalstatisticsfb", {'INPUT':buffered['OUTPUT'],'INPUT_RASTER':dem,'RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2,4],'OUTPUT':testOutputPath + "_" + str(i)})
        #Making this into a vector layer

        TODStatsVL = QgsVectorLayer(TODStats['OUTPUT'], "TODStatsVL" + str(i), "ogr")
        print(TODStatsVL)
        
    
        #adding a wl column for easy merging
        wl = QgsField("wl", QVariant.Int) 

        #editing vector layer
        TODStatsVL.startEditing()

        #using data provider to add wl column
        TODStatsVLpr = TODStatsVL.dataProvider()
        TODStatsVLpr.addAttributes([wl])

        #closing out editing and saving
        TODStatsVL.updateFields()
        TODStatsVL.commitChanges()

           
        #getting index of max mean value in attribute table
        meanIndex = TODStatsVL.fields().indexFromName("_mean")
        #getting max mean 
        maxMean = TODStatsVL.maximumValue(meanIndex)

        print(maxMean)
   
        #getting feature id of max mean
        found_feature_id = None
        for feature in TODStatsVL.getFeatures():
            if feature['_mean'] == maxMean:
                found_feature_id = feature.id()
                print("FOUND FEATURE ID: " + str(found_feature_id))
                break
        
        #creating an instance of that feature
        maxMeanFeature = TODStatsVL.getFeature(found_feature_id)
        print(maxMeanFeature)

        TODStatsVL.selectByIds([found_feature_id])

        #creating a new vecotr file for dome top
        if TODStatsVL.selectedFeatureCount() > 0:
           
            print("FEATURES SELECTED: " + str(TODStatsVL.selectedFeatureCount()))
            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "ESRI Shapefile"
            save_options.layerName = "new_layer_name"
            save_options.onlySelectedFeatures = True  # Set to True to export only selected features
            save_options.destCRS = TODStatsVL.crs() # Export with the same CRS
            save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
            save_options.layerOptions = ["OVERWRITE=YES"]
            transform_context = QgsProject.instance().transformContext()

            TODOutputPath = testOutputPath + "_" + str(i) + "_TOD"
            topOfDome = QgsVectorFileWriter.writeAsVectorFormatV3(layer=TODStatsVL, fileName=TODOutputPath, transformContext=transform_context, options=save_options)
        else:
            print("no features selected")

        print(topOfDome)
        

        #JUST MERGE THE TOD WITH THE BLOCK, BUT CLIP GRID TO BLOCK BECAUSE ITS CURRENTLY SELECTING OUTSIDE OF BLOCK FOR MAX MEAN
        
        domeBlockMerged = processing.run("native:mergevectorlayers", {'LAYERS':[b, topOfDome[2]],'CRS':None,'OUTPUT':testOutputPath + "_domedBlockMerged_" + str(i)})
        domeBlockMergedVL = QgsVectorLayer(domeBlockMerged['OUTPUT'], "domeBlockMergedVL", "ogr")

        #variable for getting the index of the wl columns so we can have the proper TIN interp settings later
        wlIndexes = []

        #make sure to include the base overlay option 
        attribute = domeBlockMergedVL.fields().indexOf('wl')
        blockAttrIndex = domeBlockMergedVL.fields().indexOf('block')
        wlIndexes.append(attribute)
        
        #editing vector layer
        domeBlockMergedVL.startEditing()

        #creating data provider to add wl data 
        domeBlockMergedVLpr = domeBlockMergedVL.dataProvider()

        innerID = 0
        TODwL = 0
        blockName = ''

        for feature in domeBlockMergedVL.getFeatures():
            if QgsVariantUtils.isNull(feature['wl']) == False:
                print("OUTER FOUND")
                print(feature)
                TODwL = feature['_mean']
                blockName = feature['block']
            else:
                print("INNER FOUND")
                print(feature['block'])
                innerID = feature.id()

        #setting top of dome water level to mean 
        domeBlockMergedVL.changeAttributeValue(innerID, attribute, TODwL)
        #changing inner block name to match overall block name
        domeBlockMergedVL.changeAttributeValue(innerID, blockAttrIndex, blockName + "_inner")
        
        domeBlockMergedVL.updateFields()
        
        #adds in the column then fills
        for overlay in overlayOptions:
            wlFieldName = "wl_" + str(overlay)

            print(wlFieldName)

            wlField = QgsField(wlFieldName, QVariant.Int) 
            print(wlField)

            domeBlockMergedVLpr.addAttributes([wlField])
            domeBlockMergedVL.updateFields()            
        
            #and fills with corresponding overlay calc 
            for feature in domeBlockMergedVL.getFeatures():
                wlIndexes.append(feature.fieldNameIndex(wlFieldName))
    
                feature.setAttribute(feature.fieldNameIndex(wlFieldName), int(float(feature['wl'])) + overlay)
                
                domeBlockMergedVL.updateFeature(feature)

        domeBlockMergedVL.commitChanges()
        domeBlocks.append(domeBlockMerged['OUTPUT'])

        i += 1
        break

        #SCRIPT NOW SUCCESSFULLY CREATES DOME AND MERGES WITH BLOCK
        #IT MAKE THE WL OF THE BLOCK ITS MEAN - 1 STDV
        #IT MAKES THE WL OF THE INNER THE MEAN OF THE BLOCK
        
        #----> THINGS TO LOOK INTO:
        #NEED TO CHANGE UP NAMES FOR OVERLAY FUNCTION / ALL FUNCTIONS IN ORDER TO AVOID OVERWRITING
        # SCRIPT KINDA STRANGELY STARTS WITH A RANDOM BLOCK EVERY TIME
        #NEED TO ADDRESS THE ROUNDING OF THE WL DURING CALCS TO PRESERVE THE HALF FT INTERVALS
        #WOULD BE NICE TO CREATE FOLDERS TO PUT OUTPUTS IN FOR ORGANIZATION
        #EVENTUALLY WOULD BE SMART TO MAKE DEBUGGING FUNCTIONS, ESPECIALLY FOR INPUTS TO TELL THE USER WHAT WENT WRONG
        #ALSO WOULD BE GOOD TO RUN BACK THROUGH AND MAKE SURE EVERYTHING IS WELL COMMENTED
       
    #going through every option 
    n = 0 
    print(domeBlocks)
    for index in wlIndexes:
        #creating domes for each overlay option 
        domedWTOutputPath = outputFolder
        domedWaterTable = domedWT(domeBlocks, domedWTOutputPath, index)
        

        #creating overlay
        domedOverlayOutputPath = outputFolder
        overlay = rasterSubtractor(dem, domedWaterTable['OUTPUT'], domedOverlayOutputPath)
        n += 1

    #--------------NOT DEBUGGED YET---------------------------------------------------------


'''
        #creating histogram
        rasterHistOutput = outputFolder + "/rasterHist_" + str(overlayOptions[n])
        rasterHist(overlay, blocks, rasterHistOutput)

        
#--------------NOT DEBUGGED YET---------------------------------------------------------

'''





        
        
        




