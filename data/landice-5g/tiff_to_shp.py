import os

for filename in os.listdir("tiff"):
    print filename
    f = filename.replace(".tiff", "")
    tiff = "tiff/" + filename
    out = "shapefiles/" + f + ".shp"

    cmd = "gdal_polygonize.py " + tiff + " -f 'ESRI Shapefile' " + out
    os.system(cmd)
