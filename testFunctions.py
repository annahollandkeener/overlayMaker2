#test functions
import os
from qgis.core import QgsVectorLayer, QgsVariantUtils

#LET ME KNOW IF YOU RUN INTO ANY ISSUES WHEN RUNNING YOUR CODE AND WE CAN MAKE A NEW TEST CASE

def isPathValidTest(pathToTest):
    #check if valid path
    if not os.path.exists(pathToTest):
          print("ERROR: " + pathToTest + " is not a valid path.")
          print("Make sure your backslashes have been forwarded!")
          raise FileNotFoundError
    
#check if the attribute table has a wl column
def hasOptionalColumnTest(blocksToTest = str, colName = str):
    #making input block a vector layer in order to access attribute table
    blocksVL = QgsVectorLayer(blocksToTest)
    #getting index of colName
    field_index = blocksVL.fieldNameIndex(colName)

    #if the 'wl field doesn't exist, the index will be = -1  
    if field_index == -1:
        print(f"The field '" + colName + "' does not exist in layer '{blocksToTest.name()}'.")
        print("---> Creating new '" + colName + "'  column based on DEM for water table generation.")
        
        return False
      
    else:
        print(f"WARNING: The field '" + colName +"' exists in layer '{blocksToTest.name()}'.")
        print(f"---> Using existing '" + " for water table generation.")
        
        return True
    
def hasRequiredColumnTest(blocksToTest, colName):
    #making input block a vector layer in order to access attribute table
    blocksVL = QgsVectorLayer(blocksToTest)
    #getting index of 'wl'
    field_index = blocksVL.fieldNameIndex(colName)

    #if the field doesn't exist, the index will be = -1  
    if field_index == -1:
        raise KeyError(("The field" + colName + f" does not exist in layer '{blocksToTest}'. Add this field and associated features in the attribute table."))
    
    for feature in blocksVL.getFeatures():
        field_value = feature(colName)

        if QgsVariantUtils.isNull(field_value):
            raise Exception((f"Feature ID: {feature.id()}, Field '{colName}' IS null."))



        
        

#need to check that the blocks input has a block column 
