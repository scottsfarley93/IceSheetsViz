import os
from CreateFilledContours import doFillContour as dfc
import arcpy

outGDB = "C://users/student.shc/documents/LIG_ICE.gdb/"
contourInterval = 1000
baseContour = 0
zIndex = 1
inDir = "C://Users/student.shc/documents/icesheetsviz/data/lig/raster/"
outFolder = "C://users/documents/"

arcpy.env.overwriteOutput = True
try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        # raise a custom exception
        raise LicenseError

except LicenseError:
    print "Dying..."
    exit()

try:
    if arcpy.CheckExtension("3D") == "Available":
        arcpy.CheckOutExtension("3D")
    else:
        # raise a custom exception
        raise LicenseError

except LicenseError:
    print "Dying..."
    exit()


for f in os.listdir(inDir):
    inRaster = inDir + f
    out = f.replace(".tif", "")
    out = out.replace("ice5g_v1.2_",  "")
    out = out.replace("_1deg", "")
    out = out.replace(".", "")
    out = outGDB + out
    print "-----------------------------"
    print out
    dfc(inRaster, outGDB, out, contourInterval)
