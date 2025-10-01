#Importing default repo functions
import overlayMakerFunctions

#Default imports; remove if desired
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

#------------WRITE YOUR FUNCTIONS HERE------------

def yourFunction():
    return

#-------------------------------------------------
