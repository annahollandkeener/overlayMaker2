#test functions
import os
from qgis.core import QgsVectorLayer

#LET ME KNOW IF YOU RUN INTO ANY ISSUES WHEN RUNNING YOUR CODE AND WE CAN MAKE A NEW TEST CASE

def isPathValid(pathToTest):
    #check if valid path
    if not os.path.exists(pathToTest):
          print("ERROR: " + pathToTest + " is not a valid path.")
          print("Make sure your backslashes have been forwarded!")
          raise FileNotFoundError
    
#check if the attribute table has a wl column
def isWLColumn(blocksToTest):
    #making input block a vector layer in order to access attribute table
    blocksVL = QgsVectorLayer(blocksToTest)
    #getting index of 'wl'
    field_index = blocksVL.fieldNameIndex('wl')

    #if the 'wl field doesn't exist, the index will be = -1  
    if field_index == -1:
        print(f"The field 'wl' does not exist in layer '{blocksToTest.name()}'.")
        print("---> Creating new 'wl' column based on DEM for water table generation.")
        
        return False
      
    else:
        print(f"WARNING: The field 'wl' exists in layer '{blocksToTest.name()}'.")
        print(f"---> Using existing 'wl' for water table generation.")
        
        return True
    
def hasColumn(blocksToTest, colName):
    #making input block a vector layer in order to access attribute table
    blocksVL = QgsVectorLayer(blocksToTest)
    #getting index of 'wl'
    field_index = blocksVL.fieldNameIndex(colName)

    #if the field doesn't exist, the index will be = -1  
    if field_index == -1:
        raise KeyError((f"The field" + colName + " does not exist in layer '{blocksToTest.name()}'. Add a 'block' field in the blocks layer with block names. "))
    





        
        

#need to check that the blocks input has a block column 
