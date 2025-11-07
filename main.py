#imports
from qgis.core import QgsApplication
#from qgis.analysis import QgsNativeAlgorithms

#Supply path to qgis install location
QgsApplication.setPrefixPath(QgsApplication.prefixPath(), True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

#Load providers
qgs.initQgis()

#Importing all overlay maker functions
import overlayMakerFunctions

#------------USER INPUTS--------------------
#Shapefile (SHP) for block boundaries 
blockBoundaries =  "C:/wfh/python/L&L Demo/blockBoundaries/updated_blocks_split.shp"

#Shapefile (SHP) for block boundaries you would like domed overlays for
domedBlocksBoundaries = []

#DEM of ground surface for project area
groundDEM = "C:/wfh/python/L&L Demo/groundDEM/CarolinaRanch_2020lidar_3ft (2).tif"
   
#Rasterized (TIF) version of your block boundaries
waterTableDEM = ""

#Vector file (SHP) of the roads within your project area
projectRoads = ""
     
overlay = ""

#Where you would like the results to end up
outputFolder = "C:/wfh/python/L&L Demo/output"

#-------------CALL FUNCTIONS HERE---------------------
overlayMakerFunctions.autoOverlay(blockBoundaries, groundDEM, outputFolder)




#-----------------------------------------------------

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory

print("\nDONE! :)\n")

qgs.exitQgis()




