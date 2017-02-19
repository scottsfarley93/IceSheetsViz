import os

for filename in os.listdir("netcdf"):
    nc = "netcdf/" + filename
    f = filename.replace("ice5g_v1.2_", "")
    f = f.replace("_1deg.nc", "")

    xyz = "rasters/" + f + ".xyz"
    cmd = "gdal_translate NETCDF:" + nc + ":sftgif -of 'XYZ' " + xyz
    os.system(cmd)

    A = "rasters/" + f + "_A.tiff"
    B = "rasters/" + f + "_B.tiff"
    cmd = "gdal_translate -projwin 0 90 180 -90 " + xyz + " " + A
    os.system(cmd)

    cmd = "gdal_translate -projwin 180 90 360 -90 -a_ullr -180 90 0 -90 " + xyz + " " + B
    os.system(cmd)

    unproj = "rasters/" + f + ".tiff"

    cmd = "gdal_merge.py -o " + unproj + " " + A + " " + B

    os.system(cmd)

    final = "tiff/" + f + ".tiff"

    cmd = "gdalwarp -t_srs WGS84  -of 'GTiff'  " + unproj + " " + final
    os.system(cmd)
