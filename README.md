# <u> overlayMaker README </u>

## Creates flat and domed overlays for a project area

### Function Descriptions:

####  <u> AutoOverlay </u> 


* <i> Takes in block boundaries and DEM for a project area   </i>
* <i> Takes in "overlay options" which informs the script of other versions of the base overlay to create (ex. if the boards of the WCS were to all be placed 1ft higher or 2ft lower etc.)</i>
* <i> Calculates initial water level for WCS for each block </i>
* <i> Determines location of top of domed water table based on highest area of elevation in each block </i>
* <i> Creates a domed water table for each overlay option for each block  </i>
* <i> Creates an overlay for each overlay option from the domed water tables </i>
* <i> Creates a histogram sheet for each overlay option showing the distribution of depth to water table for each block in the overlay </i>





| Input | Descriprtion | 
| :---------------------- | :-----------------------: | 
| 'blockBoundaries' | Path of SHP file with project blocks. Has a 'block' feature in attribute table. Vector has valid geometries.  | 
| 'groundDEM'  | Path of 3ft Resolution DEM for project area. | 
| 'outputFolder'  | Path of desired output folder.  | 



<u> Things to note: </u>

* cant have the zonal stats open in qgis - it wont run cause its being used in two places
* For some reason windows paths use " \ " when copying and pasting. Make sure to change this to " / " before running. 
* Ensure that 

