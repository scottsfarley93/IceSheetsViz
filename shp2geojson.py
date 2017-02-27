import os

inDir = "C://users/student.shc/documents/icesheetsviz/data/lig/shapefile/"

outdir = "C://users/student.shc/documents/icesheetsviz/data/lig/geojson/"

for f in os.listdir(inDir):
    if f[-4:] == ".shp":
        filename = inDir + f
        out = outdir + f.replace(".shp", ".geojson")
        cmd = "ogr2ogr -f GeoJSON " + out + " " + filename
        os.system(cmd)
        print cmd
