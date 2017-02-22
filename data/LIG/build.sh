## setup
mkdir raster
mkdir geojson

## This R script
## 1. rotates the grid
## 2. extracts each layer band and the associated time interval
## 3. saves the layer as a tiff
## 4. Contours the layer and saves the contours as geojson
RScript --vanilla process_thickness_data.R netcdf/ICE-6G_C_IceThickness_1deg.nc /users/scottsfarley/documents/icesheetsviz/data/lig/raster /users/scottsfarley/documents/icesheetsviz/data/lig/geojson


## add the age field to the geojson
node add_field_to_geojson.js geojson
