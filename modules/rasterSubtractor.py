#imports
import os
from qgis.core import QgsRasterLayer, QgsProject
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator


print("\n~ Performing Raster Subtraction ~\n")
#FYI: This will overwrite any previous version with the same name 

#Takes in path of elevation dem, path of dem representing water surface and a path of output folder
def rasterSubtractor(dem, waterTable, outputFolder):
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
        


