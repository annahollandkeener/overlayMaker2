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
from model import OMModel
from view import OMView
from controller import OMController
import tkinter as tk

#------------USER INPUTS--------------------
'''
#Shapefile (SHP) for block boundaries 
blockBoundaries = "C:\wfh\RA4\Roads.shp"

#Shapefile (SHP) for block boundaries you would like domed overlays for
domedBlocksBoundaries = []

#DEM of ground surface for project area
groundDEM = "C:/wfh/RA4/RA_4_5_DEM_3ft_ft.tif"
#"S:/KBE/Prj_2025/Pocosin Lakes IRA/GIS/2020_lidar/RA4_5/RA_4_5_DEM_3ft_ft.tif"
   
#Rasterized (TIF) version of your block boundaries
waterTableDEM = ""

#Vector file (SHP) of the roads within your project area
projectRoads = ""
     
overlay = "C:/wfh/RA4/Option 5 Overlay.tif"

#Where you would like the results to end up
outputFolder = "C:/wfh/python/overlayMaker outputs"
#"K:/Docs/Guidance & Processes/Python Tools/overlayMaker2Ouputs"

'''

#-------------DEFINING APP CLASS---------------------
class App:
    def __init__(self, root):
        self.root = root
        self.mode = None
        self.inputs = {}

        self.modeButtons = []

        SOInputs = ['Blocks', 'DEM', 'Output Folder']
        AOInputs = ['Blocks', 'DEM', 'Output Folder']
        histInputs = ['Blocks', 'Overlay','Output Folder']

    def getModeButtons(self):
        return self.modeButtons
    
    def getRoot(self):
        return self.root
    
    def getInputs(self):
        return self.inputs

#---------main function
def main():
    root = tk.Tk()
    root.title("KBE autoOverlay Tool")
    root.geometry("500x350") # Set the window size

    app = App(root)

    m = OMModel(app)
    c = OMController(m, None, app)
    v = OMView(c, root, app)
    c.view = v

    root.mainloop()

if __name__ == "__main__":
    main()

#-----------------------------------------------------

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory   

print("\nDONE! :)\n")

qgs.exitQgis()




