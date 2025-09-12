#imports
from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms

# Supply path to qgis install location
QgsApplication.setPrefixPath(QgsApplication.prefixPath(), True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

#QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

#modules - import the ones you need
from modules import flatWaterTableMaker, domedWaterTableMaker, rasterSubtractor

#------------USER INPUTS--------------------
#Shapefile (SHP) for block boundaries you would like flat overlays for
flatBlocksBoundaries = "S:/KBE/Prj_2024/Pantheon Carolina Ranch/GIS/withers_blocks_2.shp"

#Shapefile (SHP) for block boundaries you would like domed overlays for
domedBlocksBoundaries = ['K:/Docs/Guidance & Processes/Python Tools/overlays/testmaterials/E11A']

#DEM of ground surface for project area
groundDEM = "S:/KBE/Prj_2024/Pantheon Carolina Ranch/GIS/survey_surfaces_and_lidar_DEM_2264_ft_updated_2.tif"

#Rasterized (TIF) version of your block boundaries
waterTableDEM = "K:/Docs/Guidance & Processes/Python Tools/overlays/testmaterials/E11A/E11A.tif"

#Where you would like the results to end up
outputFolder = "S:/KBE/Prj_2024/Pantheon Carolina Ranch/GIS"

#-------------EXECUTIONS---------------------

#rasterSubtractor.rasterSubtractor(groundDEM, waterTableDEM, outputFolder)
#flatWaterTableMaker.flatWT(flatBlocksBoundaries, outputFolder)
#domedWaterTableMaker.domedWT(domedBlocksBoundaries, outputFolder)

rasterSubtractor.rasterSubtractor(groundDEM, flatWaterTableMaker.flatWT(flatBlocksBoundaries, outputFolder), outputFolder)

#----------------------------------

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory

print("\nDONE! :)\n")

qgs.exitQgis()




