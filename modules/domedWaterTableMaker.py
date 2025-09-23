#imports
import os
from qgis.core import QgsVectorLayer
import processing
from processing.core.Processing import Processing
Processing.initialize()


#INPUT = shapefile of block boundaries with specified outer WL attribute and inner WL attribute representing top of dome, output folder
#RETURNS = merged interpolated raster surface between the outer and inner WLs of each block

def domedWT(domedBlocks, outputFolder, columnIndicator = 1):
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
        
        #domeClipped = processing.run("gdal:cliprasterbymasklayer", {'INPUT':domeRough['OUTPUT'],'MASK':dome,'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':extent,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        domeClipped = processing.run("gdal:cliprasterbyextent", {'INPUT':domeRough['OUTPUT'],'PROJWIN': extent,'OVERCRS':False,'NODATA':None,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':outputPathClipped})
        #adding final clipped dome to a list
        clippedDomes.append(domeClipped['OUTPUT'])

    #merging all domes    
    merge = processing.run("gdal:merge", {'INPUT':clippedDomes,'PCT':False,'SEPARATE':False,'NODATA_INPUT':None,'NODATA_OUTPUT':0,'OPTIONS':None,'EXTRA':'','DATA_TYPE':5,'OUTPUT':outputFolder + '/all_domedWT_merged.tif'})
    
    print("COMPLETED DOME: " + baseName)

    return merge
        
        
        
        


