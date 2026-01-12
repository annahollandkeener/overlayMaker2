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

#Importing dependencies
import tkinter as tk


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
    root.title("KBE Overlay Maker")
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




