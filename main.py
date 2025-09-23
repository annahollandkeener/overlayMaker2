#imports
from qgis.core import QgsApplication
#from qgis.analysis import QgsNativeAlgorithms

# Supply path to qgis install location
QgsApplication.setPrefixPath(QgsApplication.prefixPath(), True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

#QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

#modules - import the ones you need
from modules import rasterStats, domedWaterTableMaker

#------------USER INPUTS--------------------
#Shapefile (SHP) for block boundaries you would like flat overlays for
flatBlocksBoundaries = "C:/wfh/per1/updated/updated_blocks_split.shp"

#Shapefile (SHP) for block boundaries you would like domed overlays for
domedBlocksBoundaries = ["C:/wfh/per1/updated/split blocks/domed/block_G11A.shp",
"C:/wfh/per1/updated/split blocks/domed/block_F11 B.shp",
"C:/wfh/per1/updated/split blocks/domed/block_F11 A.shp",
"C:/wfh/per1/updated/split blocks/domed/block_E11 B.shp",
"C:/wfh/per1/updated/split blocks/domed/block_E11 A.shp",
"C:/wfh/per1/updated/split blocks/domed/block_H11 C.shp"]

#DEM of ground surface for project area
groundDEM = "C:/wfh/per1/elevation/CarolinaRanch_2020lidar_3ft (2).tif"

#Rasterized (TIF) version of your block boundaries
waterTableDEM = "C:/wfh/python/overlayMaker/testmaterials/E11A/E11A.shp"

#Vector file (SHP) of the roads within your project area
projectRoads = "C:/wfh/python/overlayMaker/testmaterials/E11A/E11A.shp"
     
overlay = "C:/wfh/per1/updated/updated_blocks_overlay.tif"

#Where you would like the results to end up
outputFolder = "C:/python/overlayMaker"

#-------------EXECUTIONS---------------------

#rasterSubtractor.rasterSubtractor(groundDEM, waterTableDEM, outputFolder)
#flatWaterTableMaker.flatWT(flatBlocksBoundaries, outputFolder)
#domedWaterTableMaker.domedWT(domedBlocksBoundaries, outputFolder)
#rasterSubtractor.rasterSubtractor(groundDEM, flatWaterTableMaker.flatWT(flatBlocksBoundaries, outputFolder), outputFolder)

#affectedRoadsCalc.roadCalc(groundDEM, projectRoads, waterTableDEM, outputFolder)

rasterStats.rasterHist(overlay, flatBlocksBoundaries, outputFolder)
#----------------------------------

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory

print("DONE! :)")

qgs.exitQgis()




