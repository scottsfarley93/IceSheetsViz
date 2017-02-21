import gdal
import numpy
import os
import csv

def calcThicknessSum(filename):
    ds = gdal.Open('NETCDF:"' + filename + '":sftgit')
    dat = ds.ReadAsArray()
    datSum = numpy.sum(dat)
    return datSum


attr = []

for f in os.listdir("netcdf"):
    filename = "netcdf/" + f
    fdcomp = f.split("_")
    if f != ".DS_Store":
        print fdcomp
        age = fdcomp[2]
        years = float(age.replace("k", ""))*1000
        thicknessSum = calcThicknessSum(filename)
        a = [years, age, thicknessSum]
        attr.append(a)
        print thicknessSum

writer = csv.writer(open("thicknessTable.csv", 'w'))

writer.writerow(["Years", "Age", "Sum"])
writer.writerows(attr)
