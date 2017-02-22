import os

for f in os.listdir("geojson"):
    filename = "geojson/" + f
    out = "geojson/simple/" + f
    cmd = "mapshaper " + filename + " -simplify 40% -o format=geojson " + out
    os.system(cmd)
