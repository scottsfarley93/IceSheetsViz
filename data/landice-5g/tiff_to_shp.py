import os

for filename in os.listdir("rasters"):
    print filename
    f = filename.replace(".tiff", "")
    tiff = "rasters/" + filename
    out = "shapefiles/" + f + ".shp"

    cmd = "gdal_polygonize.py " + tiff + " -f 'ESRI Shapefile' " + out
    os.system(cmd)
