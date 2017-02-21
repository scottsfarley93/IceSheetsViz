##This script converts a netcdf file with 0-360 longitude to a geotiff with -180 to 180 degrees longitude 

##initialize and load libraries  
library(ncdf4)
library(raster)

## get the arguments passed via commandline
args = commandArgs(trailingOnly = TRUE)
print(args)

inNC = args[1]
outRaster = args[2]
varName = args[3]

print(inNC)
print(outRaster)
print(varName)

## do the conversion
a <- raster(inNC, varname=varName)
rotated <- rotate(a)


# ## write the output
writeRaster(rotated, outRaster)
