# <b><span style="color: #7faeb3;"> overlayMaker README </span></b>
---
## The 'overlayMaker' is a suite of tools built from available pyqgis functions that allows for an efficient creation and analysis of overlays for pocosin restoration projects
---

###  <span style="color: #7faeb3"> Setting Up the 'overlayMaker' Workspace: </span>
* Activate your qgis environment 
    * See the [Python and QGIS Guide](https://docs.google.com/document/d/1FuxWWG3lmFlltaK0mbh07ZeaEtTw5XA0LBubkZIZ6Oc/edit?tab=t.0) for info on how to create a pyqgis environment
* Open VSCode 
* Navigate to chosen directory
* Clone the repository into your chosen directory 
    * See [Python and QGIS Guide](https://docs.google.com/document/d/1FuxWWG3lmFlltaK0mbh07ZeaEtTw5XA0LBubkZIZ6Oc/edit?tab=t.0) for info on Github and cloning repositories
* Operate the available functions in the repository by calling and running from the 'main.py' file 
---

### <span style="color: #7faeb3"> Making Your Own Functions: </span>
If you wish to make custom functions for your overlayMaker, you can use the 'customFunctions.py' file to create your own. This file is automatically imported into the main file, from which your functions can be called and ran. 

----



### <span style="color: #7faeb3">Function Descriptions: </span>
#### ----> <i> Located in 'overlayMakerFunctions.py' </i>

<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

###  <u><b> 'autoOverlay' </b></u> 


* <i> Takes in block boundaries and DEM for a project area   </i>
* <i> Takes in "overlay options" which informs the script of other versions of the base overlay to create (ex. if the boards of the WCS were to all be placed 1ft higher or 2ft lower etc.)</i>
* <i> Calculates initial water level for WCS for each block (mean - 1stdv). </i>
* <i> Determines location of top of domed water table based on highest area of elevation in each block </i>
* <i> Creates a domed water table for each overlay option for each block  </i>
* <i> Creates an overlay for each overlay option from the domed water tables </i>
* <i> Creates a histogram sheet for each overlay option showing the distribution of depth to water table for each block in the overlay </i>



| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'blockBoundaries' | Path of SHP file with project blocks. Has a 'block' feature in attribute table. Vector has valid geometries.  |  PATH (.shp) |
| 'groundDEM'  | Path of 3ft Resolution DEM for project area. | PATH (.tif) |
| 'outputFolder'  | Path of desired output folder.  | PATH



<u> Things to note: </u>

* Can't have the zonal stats open in qgis
* Windows paths use " \ " when copying and pasting. Make sure to change this to " / " before running. 

<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

### <u><b> 'rasterSubtractor' </b></u> 
* <i> Takes in a DEM and rasterized water table as well as an output folder. It also takes in anoptional parameter 'opt' that can specify the version of the overlay currently being calculated. </i>
* <i> Subtracts the water table from the DEM  </i>
* <i> Returns the output path of the calculated overlay </i>

| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'dem' | Path of 3ft Resolution DEM for project area. | PATH (.tif) |
| 'waterTable'  | Path to rasterized water table. | PATH (.tif) |
| 'outputFolder'  | Path of desired output folder.  | PATH |
| 'opt'  | Overlay option to be calculated. Default = 0. | int |

<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

### <u><b> 'rasterHist' </b></u> 
* <i> Takes in an overlay raster, the project blocks </i>
* <i> Reclassifies the raster, unless specified otherwise, to  '<0', '0-1', '1-2', '2-3', '>3' </i>
* <i> Creates a zonal histogram using the blocks on reclassified raster </i>
* <i> Creates a CSV from results </i>
* <i> Creates a histogram from CSV </i>
* <i> Adds all histograms for each block to one window and exports as .jpg</i>

| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'overlay' | Overlay raster. | PATH (.tif) |
| 'blocks'  | Path to project blocks. | PATH (.shp) |
| 'outputFolder'  | Path of desired output folder.  | PATH |
| 'reclass'  | Preferred reclassification ranges for overlay. Default = ['-1000','0','1','0','1','2','1','2','3','2','3','4','3','1000','5'] | [lowerBound, upperBound, lowerBound, upperBound...etc.]

<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

### <u><b>'flatWT' </b></u> 
* <i> Takes in the project blocks and an output folder </i>
* <i> Rasterizes the blocks to create a rasterized water table </i>

| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'blocks'  | Path to project blocks. | PATH (.shp) |
| 'outputFolder'  | Path of desired output folder.  | PATH |



<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

### <u><b> 'domedWT' </b></u> 
* <i> Takes in a list of blocks to be domed, an outputFolder, an indicator of which attribute field to use to interpolate, and the current overlay option.  </i>
* <i> Rasterizes the blocks to create a rasterized water table </i>

| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'domedBlocks'  | List of blocks to be domed. | [PATH (.shp), PATH (.shp), PATH (.shp)...]|
| 'outputFolder'  | Path of desired output folder.  | PATH |
| 'columnIndicator'  | Column to use for interpolation. Default = 2.  | int |
| 'opt'  | Corresponding overlay option.  | int |

<center><b><span style="color: #7faeb3">--------------------------</b></span></center>

### <u><b> 'roadCalc' [UNDER CONSTRUCION]</b></u> 

* <i> Takes in the project dem, a shapefile of roads in the project area, a rasterized water table, and an output folder </i>
* <i> Creates a buffer of the roads input </i>
* <i> Clips the project dem to the buffered roads </i>
* <i> Creates an overlay for the roads </i>
* <i> Reclassifies the road raster (<0, 0-1, 1-2, 2-3, >3) </i>
* <i> Vectorizes the road raster </i>
* <i> Exports each range into its own vector file </i>
* <i> Calculates the length of each vector file in feet </i>
* <i> Calculates the sum of all of the lengths </i>
* <i> Creates a csv file output with ranges and their sum lengths in feet </i>


| Input | Descriprtion | Type |
| :---------------------- | :-----------------------: | :-----------------------: | 
| 'dem'  | Project DEM. | PATH (.tif) |
| 'roads'  | Project roads. | PATH (.shp) |
| 'WT'  | Rasterized water table. | PATH (.tif) |
| 'outputFolder'  | Path of desired output folder. | PATH | 

---





