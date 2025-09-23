#takes in a set of blocks that have defined water levels
#splits the blocks
#for each block determines the area of highest elevation in the block 
#circles this area of highest elevation and adds as a feature to the current block vector layer
#sets the water level of this new feature as default +1 ft
#if to automate the inner water level determination
    #takes an elevation profile on the given DEM for project area at least in the four cardinal directions
    #for the length of the entire block and averages the slope of each profile together
    #then sets this averaged number as the water level of the new top of dome feature for the block