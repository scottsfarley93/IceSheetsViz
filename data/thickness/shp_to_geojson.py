import os


for filename in os.listdir("shapefiles"):
    if ".shp" in filename:
        f = filename.replace(".shp", "")
        infile = "shapefiles/" + filename
        out = "geojson/" + f + ".geojson"
        cmd = 'ogr2ogr -where DN > 0  -f GeoJSON ' + out + ' ' + infile
        print cmd
        os.system(cmd)
