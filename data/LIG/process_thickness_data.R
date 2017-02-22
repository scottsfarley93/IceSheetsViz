library(raster)
library(ncdf4)
library(geojsonio)

args <- commandArgs(trailingOnly = TRUE)

a <- args[1]
rasterFolder <- args[2]
jsonFolder <- args[3]

fileStack <- stack(a)

rotatedStack <- rotate(fileStack)

stackNames = names(fileStack)
nStack = length(names(fileStack))

for (layerIdx in 1:nStack){
  layerName = stackNames[layerIdx]
  layer = rotatedStack[[layerName]]
  layerTimeValue = as.numeric(gsub("X", "", layerName))
  newLayerName <- paste(rasterFolder, "/LIG_", layerTimeValue, "k.tiff", sep="")
  writeRaster(layer, newLayerName, overwrite=TRUE)
  
  contourName = paste(jsonFolder, "/LIG_", layerTimeValue, "k_contours.geojson", sep="")
  contours <- rasterToContour(layer)
  geojsonio::geojson_write(contours, file=contourName)
  
  print(layerName)
}