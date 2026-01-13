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
from qgis.core import edit, QgsVectorDataProvider, QgsVariantUtils, QgsUnitTypes
from PyQt5.QtCore import QMetaType 



#FUNCTION IMPORTS
from model import domedWT, rasterHist, rasterSubtractor
import testFunctions


class OMModel:
    def __init__(self, app):
        self.app = app
        #Starting processing
        Processing.initialize()

    def overlayMaker(blocks, dem, outputFolder, overlayOptions = []):
        print("\n------------------------------------------------------------------------------------------------------------------------------------------")
        print("\n---------------------------------------------STARTING OVERLAYMAKER------------------------------------------------------------------------")
        print("\n------------------------------------------------------------------------------------------------------------------------------------------")

        #----------testing inputs begin----------

        testFunctions.hasRequiredColumnTest(blocks, 'block')
        wlColumnPresent = testFunctions.hasOptionalColumnTest(blocks, 'wl')

        #----------testing inputs end----------
        
        #-----------FOLDER CREATION---------------------------------------------------

        #-----------OUTPUT FOLDER------------
        autoOverlayFolder = outputFolder + "/autoOverlay"

        if not os.path.exists(autoOverlayFolder):
            os.makedirs(autoOverlayFolder)
            outputFolder = autoOverlayFolder
        else:
            # Folder already exists, find a unique name by appending a number
            folder_name, _ = os.path.splitext(autoOverlayFolder) # Split to handle potential extensions, though not typical for folders
            
            counter = 1

            folderExists = True

            while folderExists == True:

                new_folder_path = f"{folder_name} ({counter})"

                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)

                    outputFolder = new_folder_path

                    folderExists = False

                else:
                    counter += 1

        #------------PROCESSING--------------------
        #Making Processing folder
        ProcessingFolder = outputFolder + "/Processing"
        os.mkdir(ProcessingFolder)

        #--------------PROCESSING -> DEM STATS-----------------
        demStatsFolder = ProcessingFolder + "/Initial Block DEM Stats"
        os.mkdir(demStatsFolder)

        #--------------PROCESSING -> TOD-----------------
        #Making TOD folder
        TODFolder = ProcessingFolder + "/TOD"
        os.mkdir(TODFolder)

        #Making TOD Stats folder
        TODStatsFolder = TODFolder + "/TOD Stats"
        os.mkdir(TODStatsFolder)

        #Making TOD Vectors folder
        TODVectorsFolder = TODFolder + "/TOD Vectors"
        os.mkdir(TODVectorsFolder)

        #-------------PROCESSING -> DOMES-------------------

        #Making dome folder
        domesFolder = ProcessingFolder + "/Domes"
        os.mkdir(domesFolder)

        #Making merged dome vector folder
        blocksInnerOuter = domesFolder + "/Merged Dome Vectors"
        os.mkdir(blocksInnerOuter)

        #Making domed water table raster folder
        domedWTOutputPath = domesFolder + "/Domed Water Tables"
        os.mkdir(domedWTOutputPath)

        #-------------PROCESSING -> HISTOGRAMS-------------------

        #Making histogram progress folder
        histogramsProgFolder = ProcessingFolder + "/Histograms"
        os.mkdir(histogramsProgFolder)

        #-------------OVERLAYS-------------------
        #Making Completed Overlays folder
        overlaysFolder = outputFolder + "/Completed Overlays"
        os.mkdir(overlaysFolder)

        #-------------HISTOGRAMS-------------------
        histogramsFolder = outputFolder + "/Completed Histograms"
        os.mkdir(histogramsFolder)

        #-------------ESTABLISHING IMPORTANT VARIABLES-------------------

        #adding other wl columns for overlay options, if not already defined
        if len(overlayOptions) == 0:
            print("Overlay options not specified. Using default options: [0, 1, 2, -1, -2].")
            overlayOptions = [0, 1, 2, -1, -2]

        #variable for getting the index of the wl columns so we can have the proper TIN interp settings later
        wlIndexes = []

        #LIST FOR HOLDING MERGED BLOCKS WITH INNER AND OUTER BOUNDARIES
        domeBlocks = []

        #calculating DEM stats: count, sum, mean, stdv
        demStats = processing.run("native:zonalstatisticsfb", {'INPUT':blocks,'INPUT_RASTER':dem,'RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2,4],'OUTPUT':demStatsFolder + "/Inital DEM Stats"})
        
        print("\n---------------------------------------------INITIAL BLOCK ANALYSIS------------------------------------------------------------------------")
        print("\n-> Initial block DEM Stats Created: " + "'" + demStats['OUTPUT'] + "'\n")

        #creating vector layer for demStats file
        demStatsVL = QgsVectorLayer(demStats['OUTPUT'], "DEMStats")
        
        #if the wl column is not already present in the layer:
        if wlColumnPresent == False:
            #creating a wl field for the blocks
            blockWLs = QgsField("wl", QMetaType.Double) 

            #opening editor
            with edit(demStatsVL):
                #getting data provider
                demStatsVLpr = demStatsVL.dataProvider()
                #adding wl
                demStatsVLpr.addAttributes([blockWLs])
                demStatsVL.updateFields()

                #adding wl (mean - 1stdv)
                for feature in demStatsVL.getFeatures():
                    feature.setAttribute(feature.fieldNameIndex('wl'), round(round((feature['_mean'] - feature['_stdev']) * 2) / 2, 2))
                    demStatsVL.updateFeature(feature)

        #splitting each block into its own layer
        splitBlocksInput = demStats["OUTPUT"] 
        splitBlocks = processing.run("native:splitvectorlayer", {'INPUT':splitBlocksInput,'FIELD':'block','PREFIX_FIELD':True,'FILE_TYPE':1,'OUTPUT':ProcessingFolder + "/All Blocks Split"})
        
        print("--> Blocks split: " + "'" + splitBlocks['OUTPUT'])

        #making grid for each block to determine highest point and add this as a dome feature to the block
        wlColIndexCollected = False
        for b in splitBlocks['OUTPUT_LAYERS']:
            #Getting base name of current block 
            currentBlock = os.path.basename(b).split(".")[0] 

            print("\n>>>>>>>>>>>>>>> Analyzing " + currentBlock + " <<<<<<<<<<<<<<<")
            
            #turning block path into a vector layer
            block = QgsVectorLayer(b, "block", "ogr")

            #getting area of current block
            blockArea = 0
            
            #getting area of each feature in layer and adding up
            for feature in block.getFeatures():
                geom = feature.geometry()
                blockArea += geom.area()

            #getting area in acres
            blockAreaAcres = round(blockArea / 43560, 1)
        
            print(f"\n-> Area of {currentBlock} = " + str(blockAreaAcres) + " acres")

            #creating grid 
            grid = processing.run("native:creategrid", {'TYPE':0,'EXTENT':block.extent(),'HSPACING':610,'VSPACING':610,'HOVERLAY':0,'VOVERLAY':0,'CRS':QgsCoordinateReferenceSystem(block.crs()),'OUTPUT':'TEMPORARY_OUTPUT'})

            #clipping grid to block 
            clippedGrid = processing.run("native:clip", {'INPUT':grid['OUTPUT'],'OVERLAY':block,'OUTPUT':'TEMPORARY_OUTPUT'})
        
            #buffering the grid
            buffered = processing.run("native:buffer", {'INPUT':clippedGrid['OUTPUT'],'DISTANCE':(blockArea/10000),'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'SEPARATE_DISJOINT':False,'OUTPUT':'TEMPORARY_OUTPUT'})
            
            #clipping buffer to block 
            clippedBuffer = processing.run("native:clip", {'INPUT':buffered['OUTPUT'],'OVERLAY':block,'OUTPUT':'TEMPORARY_OUTPUT'})

            #zonal stats on the grid vectors
            TODStats = processing.run("native:zonalstatisticsfb", {'INPUT':clippedBuffer['OUTPUT'],'INPUT_RASTER':dem,'RASTER_BAND':1,'COLUMN_PREFIX':'_','STATISTICS':[0,1,2,4],'OUTPUT':TODStatsFolder + "/" + currentBlock + "_TODStats"})
            
            print("--> Block grid created: " + "'" + TODStats['OUTPUT'])

            #Making this into a vector layer
            TODStatsVL = QgsVectorLayer(TODStats['OUTPUT'], "TODStatsVL_" + currentBlock, "ogr")
            
            #adding a wl column for easy merging
            wl = QgsField("wl", QMetaType.Double) 

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

            #getting feature id of max mean
            found_feature_id = None
            for feature in TODStatsVL.getFeatures():
                if feature['_mean'] == maxMean:
                    found_feature_id = feature.id()
                    break
            
        #selecting dome with highest mean
            TODStatsVL.selectByIds([found_feature_id])

            #creating a new vector file for dome top
            if TODStatsVL.selectedFeatureCount() > 0:
            
                save_options = QgsVectorFileWriter.SaveVectorOptions()
                save_options.driverName = "ESRI Shapefile"
                save_options.layerName = "new_layer_name"
                save_options.onlySelectedFeatures = True  # Set to True to export only selected features
                save_options.destCRS = TODStatsVL.crs() # Export with the same CRS
                save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
                transform_context = QgsProject.instance().transformContext()

                topOfDome = QgsVectorFileWriter.writeAsVectorFormatV3(layer=TODStatsVL, fileName=TODVectorsFolder + "/" + currentBlock + "_TOD_isolated", transformContext=transform_context, options=save_options)


                print("---> Dome selected for " + currentBlock)

            else:
                print("\n---> ERROR: No features selected from grid\n")
            
            
            #merging TOD with block        
            domeBlockMerged = processing.run("native:mergevectorlayers", {'LAYERS':[b, topOfDome[2]],'CRS':None,'OUTPUT':blocksInnerOuter + "/" + currentBlock + "_inner+outer"})
            print("----> Merged top of dome with block: " + "'" + domeBlockMerged['OUTPUT'])

            #making a vector layer from the merged path
            domeBlockMergedVL = QgsVectorLayer(domeBlockMerged['OUTPUT'], "domeBlockMergedVL", "ogr")

            #make sure to include the base overlay option 
            attribute = domeBlockMergedVL.fields().indexOf('wl')
            blockAttrIndex = domeBlockMergedVL.fields().indexOf('block')
        
            #editing vector layer
            domeBlockMergedVL.startEditing()

            #creating data provider to add wl data 
            domeBlockMergedVLpr = domeBlockMergedVL.dataProvider()

            innerID = 0
            TODwL = 0
            blockName = ''

            if wlColumnPresent == True:
                for feature in domeBlockMergedVL.getFeatures():
                    if QgsVariantUtils.isNull(feature['wl']) == False:
                        TODwL = feature['wl'] + feature['_stdev']
                        blockName = feature['block']
                    else:
                        innerID = feature.id()
            else:
                for feature in domeBlockMergedVL.getFeatures():
                    if QgsVariantUtils.isNull(feature['wl']) == False:
                        TODwL = feature['_mean']
                        blockName = feature['block']
                    else:
                        innerID = feature.id()

            #setting top of dome water level to mean 
            domeBlockMergedVL.changeAttributeValue(innerID, attribute, TODwL)
            #changing inner block name to match overall block name
            domeBlockMergedVL.changeAttributeValue(innerID, blockAttrIndex, blockName + "_inner")
            
            domeBlockMergedVL.updateFields()
            
            #adds in the column then fills
            for overlay in overlayOptions:
                wlFieldName = "wl_" + str(overlay)

                wlField = QgsField(wlFieldName, QMetaType.Double) 

                domeBlockMergedVLpr.addAttributes([wlField])
                domeBlockMergedVL.updateFields()            
            
                #and fills with corresponding overlay calc 
                for feature in domeBlockMergedVL.getFeatures():
        
                    feature.setAttribute(feature.fieldNameIndex(wlFieldName), float(feature['wl']) + overlay)
                    
                    domeBlockMergedVL.updateFeature(feature)
            
                if wlColIndexCollected == False:
                    wlIndexes.append(feature.fieldNameIndex(wlFieldName))
            
            wlColIndexCollected = True

            domeBlockMergedVL.commitChanges()
            domeBlocks.append(domeBlockMerged['OUTPUT'])
            
            print("-----> Initial block dome vector created and wls calculated: " + "'" + domeBlockMerged['OUTPUT'])

        
        #going through every option 
        
        overlayOptionIndex = 0

        print("\n--------------------------CREATING DOMES AND OVERYLAYS--------------------------\n")
        domedWaterTable = None

        for index in wlIndexes:

            #creating domes for each overlay option 
            print(f"\n>>>>>>>>>>>>>>> CREATING DOMES, OVERLAY AND HISTOGRAM FOR {overlayOptions[overlayOptionIndex]} ft OVERLAY OPTION <<<<<<<<<<<<<<<")
            domedWaterTable = domedWT(domeBlocks, domedWTOutputPath, index, overlayOptions[overlayOptionIndex])

            #resampling dome to match dem so it can successfully subtract it
            resampledDomeOutput = domedWTOutputPath + "/" + str(overlayOptions[overlayOptionIndex]) + "_resampled"
            DEMbaseName = os.path.basename(dem).split(".")[0]

            resampledDEMOutput = domedWTOutputPath + "/" + DEMbaseName + "_resampled.tif"
            processing.run("native:alignrasters", {'LAYERS':[{'inputFile': domedWaterTable['OUTPUT'],'outputFile': resampledDomeOutput,'resampleMethod': 0,'rescale': False},{'inputFile': dem,'outputFile': resampledDEMOutput,'resampleMethod': 0,'rescale': False}],'REFERENCE_LAYER':dem,'CRS':None,'CELL_SIZE_X':None,'CELL_SIZE_Y':None,'GRID_OFFSET_X':None,'GRID_OFFSET_Y':None,'EXTENT':dem})

            print("-> Dome resampled to match DEM")


            #creating overlay  
            overlay = rasterSubtractor(dem, resampledDomeOutput, overlaysFolder, overlayOptions[overlayOptionIndex])


            #creating histogram
            rasterHist(overlay, blocks, histogramsProgFolder, histogramsFolder, None, f"Overlay Option: {overlayOptions[overlayOptionIndex]} ft")
        

            overlayOptionIndex += 1
        


        print("\n--------------------------AUTO-OVERLAY COMPLETE--------------------------\n")




    #----> THINGS TO LOOK INTO:
    #WOULD BE NICE TO CREATE DIFFERENT FOLDERS FOR EACH OPTION FOR DOMED BLOCKS AND MERGED DOMED BLOCKS
    #EVENTUALLY WOULD BE SMART TO MAKE DEBUGGING FUNCTIONS, ESPECIALLY FOR INPUTS TO TELL THE USER WHAT WENT WRONG
    #ALSO WOULD BE GOOD TO RUN BACK THROUGH AND MAKE SURE EVERYTHING IS WELL COMMENTED
    #create cubsequent folders for histogram organization?
    #finish roadCalc, for some reason it never actually got done 



    #also produces a full site histogram 
    #histograms in acres ()

    #debugging funcs brainstormg
    #   checking for block column in block input and writing warning if there is no block column 
    #   checking for wl column in block input and either deleting or using that as the default 
    #               Warn the person there already is one
    #   checking that the input blocks layer has been split into single parts 
    #    checking for presence of folder of outputs
    #   make sure no repeat names / features in block input 
    #autoInstalls geopandas if not installed? 


