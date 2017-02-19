import os

dirList = os.listdir(".")
for filename in dirList:
    if ".nc" in filename:
        newName = filename
        newName = newName.replace("_1deg.nc", "")
        newName = newName.replace("ice5g_v1.2_", "")
        newName += ".tiff"
        cmd = 'gdal_translate NETCDF:' + filename  + ':sftgit  -of "GTiff" rasters/' + newName
        os.system(cmd)