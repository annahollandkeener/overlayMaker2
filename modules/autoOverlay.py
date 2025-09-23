#INPUTS:
    #Vector file of blocks for project area (block column necessary)
    #DEM for project area

#INITIAL BLOCK ANALYSIS
#checks if vector file has multiple features, and if not splits it into separate features 
#for each block, calc raster stats: figure out mean elev and figure out std. 
#from here, create a wl feature for block -> mean -1 std
#create a grid for block with 150 spacing (might need to standardize this somehow)
#buffer these points by 150
#zonal stats on the dem using this buffered layer
#select feature with highest mean and now this is the top of the dome for this block
#change attribute table to top of dome has wl and block column 
#wl -> mean of the block 
#block -> [BLOCKNAME]_inner
#merge top of dome with block 
#add more columns for other overlays to be generated
    #add 4 more columns (w2 -> +1, w3 -> +2, w4 -> -1, w5 -> -2)

#add all of these blocks + domes to a list


#OVERLAY GENERATION 
#for each block in the block list and for each column in the block attribute table, 
#   create a TIN interp dome and add to list for respective overlay (base, +1, -1, +2, -2)
#for each list of domes
#   merge all
#   create overlay
#   adds overlays to another list (5 total)

#HISTOGRAM GENERATION
#for each overlay in list 
#   create histogram window (get it to be saved as a png or something?)

#OUTPUTS 5 Overlay options and 5 histogram windows 



