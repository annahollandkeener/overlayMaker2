#test functions
import os
from qgis.core import QgsVectorLayer

def isPathValid(pathToTest):
    #check if valid path
    if not os.path.exists(pathToTest):
          print("ERROR: " + pathToTest + " is not a valid path.")
          print("Make sure your backslashes have been forwarded!")
          raise FileNotFoundError
    
#check if the attribute table has a wl column
def isWLColumn(blocksToTest):
    blocksVL = QgsVectorLayer(blocksToTest)
    field_index = blocksVL.fieldNameIndex('wl')

    if field_index == -1:
        print(f"The field 'wl' does not exist in layer '{blocksToTest.name()}'.")
        print("---> Creating new 'wl' column based on DEM for water table generation.")
        
        return False
      
    else:
        print(f"WARNING: The field 'wl' exists in layer '{blocksToTest.name()}'.")
        print(f"---> Using existing 'wl' for water table generation.")
        
        return True
        
        

