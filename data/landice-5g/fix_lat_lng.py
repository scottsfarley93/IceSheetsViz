import os

for f in os.listdir("netcdf"):
    filename = "netcdf/" + f
    infile = filename 
    tiffName = f.replace(".nc", ".tiff")
    outfile = "rasters/" + tiffName

    var = "sftgif"
    cmd = "RScript --vanilla convert_nc_to_tiff_with_lon_wrap.R " + infile + " " + outfile + " " + var 
    print cmd
    os.system(cmd)
