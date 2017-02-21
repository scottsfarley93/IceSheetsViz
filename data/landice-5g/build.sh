## This script converts netcdf rasters to geojson vectors
## There's a lot of steps, so this file executes each step sequentially
## specifically designed for the ice-5g data
## data source: https://csdms.colorado.edu/wiki/Data:ICE-5G

## Author: Scott Farley

##Yes, I used four languages to do this task...

# setup directory
mkdir rasters
mkdir shapefiles
mkdir geojson

## convert the netcdfs to tiffs
## IMPORTANT: This step does the longitude wrapping
python fix_lat_lng.py ## note: this script iterates over the directory and calls convert_nc_to_tiff_with_lon_wrap.R

## convert the tiff rasters to shapefiles
python tiff_to_shp.py

## convert the shapefiles to geojson
python shp_to_geojson.py

## add ages to the properties of each geojson features
## Note: this will also check the geometries and make sure they're valid
node add_field_to_geojson.js

## At this point, the geojson should be ready to load into mapbox

## get rid of intermediate directories
rm -r rasters
rm -r shapefiles 
