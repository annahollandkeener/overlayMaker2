#WARNING: DEPENDENT ON RASTER SUBTRACTOR

#imports
import os
from qgis.core import QgsVectorLayer
import processing
from processing.core.Processing import Processing
from modules import rasterSubtractor
from qgis.core import QgsRasterLayer, QgsProject
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator

Processing.initialize()

#INPUTS:
        #shapefile of roads of interest/importance in the project area
        #DEM for the project
        #proposed rasterized water table        
#RETURNS:
        #a shapefile/vector layer depicting sections of road under water and within 1ft of water

def roadCalc(dem, roads, WT, outputFolder):
    print("\n~ Performing calculation of affected roads in project area ~\n")

    #getting basename of file being used
    baseName = os.path.basename(roads).split(".")[0] + "_overlay"
        
    outputPath = outputFolder + "/" + baseName

    roadRasterOP = "'" + outputFolder + "/" + "roadRaster.tif'"
    print(roadRasterOP)

    #clipping dem to roads
    roadsRaster = processing.run("gdal:cliprasterbymasklayer", {'INPUT':dem,'MASK':roads,'SOURCE_CRS':None,'TARGET_CRS':None,'TARGET_EXTENT':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':None,'DATA_TYPE':0,'EXTRA':'','OUTPUT':'C:/wfh/python/overlayMaker/RR'})

    #subtracting proposed water table from rasterized version of the roads
    #roadsOverlay = rasterSubtractor.rasterSubtractor(roadsRaster['OUTPUT'], WT, outputPath)

'''
    roadsDEM = QgsRasterLayer(roadsOverlay, "roadsDEM")
    
    roadsCalc = QgsRasterCalculatorEntry()
    roadsCalc.raster = roadsDEM
    roadsCalc.bandNumber = 1
    roadCalc.ref = 'roadsRaster@1'
    
    transform_context = QgsProject.instance().transformContext()
    
    calc=QgsRasterCalculator((("elevation@1" <= 0)), outputPath, 'GTiff', roadsDEM.extent(), roadsDEM.width(), roadsDEM.height(), [roadsCalc], transform_context)

    calc.processCalculation()

    #selecting parts of raster at or below 0ft
             
    #transforming to vector

    #selecting parts of raster at or below 1ft

    #transforming to vector

    #merging two vector types and saving 

    print(">>> AFFECTED ROADS LAYER GENERATED!: ")

#return affected roads
'''







