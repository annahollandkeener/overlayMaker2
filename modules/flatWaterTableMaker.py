import sys
import os
import processing
from processing.core.Processing import Processing
Processing.initialize()

#INPUT: shapefile of block boundaries with specified WL attribute, output folder
#RETURNS: merged rasterized version of all blocks at their respective WLs

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



