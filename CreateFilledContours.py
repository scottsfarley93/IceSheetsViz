"""
Tool Name:  Create Filled Contours
Source Name: CreateFilledContours.py
Version: ArcGIS 10.0
Author: ESRI

This utility creates filled polygons from an input raster.

Limitations:
    - Cannot output to shapefile because of string length>254 required
      in SpatialJoin
    - If more than 3 contour lines cross a single cell you might want to
      Resample using half the original cellsize
"""
import os
import sys
import arcpy
from arcpy.sa import *

def int_if_youCan(x):
    """ Return string without decimals if value has none"""
    if x % 1.0 == 0:
        strX = str(int(x))
    else:
        strX = "%.6f" % (x)
    return strX

def FindZ(outContoursPolygons, in_raster):
    """ Use the point within the polygon to determine the low and high
        sides of the polygon"""
    outEVT = 'outEVT'
    outEVTjoinedLayer = 'outEVTjoinedLayer'
    outPolygPoints = 'outPolygPoints'
    print("  FeatureToPoint_management...")
    try:
        arcpy.FeatureToPoint_management(outContoursPolygons,
                                        outPolygPoints, 'INSIDE')
    except:
        if arcpy.Describe(
            outContoursPolygons).spatialReference.name == 'Unknown':
                print('This might be caused by data with '+
                               'Unknown spatial reference.' +
                               ' Define a projection and re-run')
        sys.exit()
    print("  ExtractValuesToPoints...")
    ExtractValuesToPoints(outPolygPoints, in_raster, outEVT,
                         'NONE', 'ALL')
    arcpy.MakeFeatureLayer_management(outContoursPolygons,
                                      outEVTjoinedLayer)
    print("  MakeFeatureLayer_management...")
    descFlayer = arcpy.Describe(outEVTjoinedLayer)
    descOutEVT = arcpy.Describe(outEVT)
    print("  AddJoin_management...")
    arcpy.AddJoin_management(outEVTjoinedLayer, descFlayer.OIDFieldName,
                             outEVT, descOutEVT.OIDFieldName, 'KEEP_ALL')
    return outEVTjoinedLayer, outEVT, outPolygPoints

def delete_trailing_zeros(strValue):
    """ Remove all the trailing zeros"""
    newStr = strValue
    if '.' in strValue:
        lStr = strValue.split('.')[0]
        rStr = strValue.split('.')[1].rstrip('0')
        newStr = lStr + '.' + rStr
        if rStr == '':
            newStr = lStr
    return newStr

def findUniqueContours(inlist):
    """ Find list of unique contours"""
    uniqueContourList = []
    for item in inlist:
        if item not in uniqueContourList:
            uniqueContourList.append(item)
    return uniqueContourList

def PerformSpatialJoin(target_fc, join_fc, out_fc, contour_interval):
    """ Perform Spatial Join between contours and filled contours to
        create low and high contour label"""
    try:
        # add a temp field called range
        field = arcpy.Field()
        field.name = "range"
        field.aliasName = "range"
        field.length = 65534
        field.type = "Text"
        # this is the field from where the contour values are coming
        fm = arcpy.FieldMap()
        fm.mergeRule = "Join"
        fm.joinDelimiter = ";"
        fm.addInputField(join_fc, "Contour")
        fm.outputField = field
        # add the field map to the fieldmappings
        fms = arcpy.FieldMappings()
        fms.addFieldMap(fm)
        # add a temp field called elevation
        field = arcpy.Field()
        field.name = "elevation"
        field.aliasName = "Elevation from raster"
        field.type = "Double"
        # this is the field from where raster elevation values are in
        fm2 = arcpy.FieldMap()
        fieldnames = [f.name for f in arcpy.ListFields(target_fc)]
        # find index of elevation field (RASTERVALU) in output
        # created by ExtractValuesToPoints
        rastervalu_index = [index for index, item in
                       enumerate(fieldnames) if 'RASTERVALU' in item][0]
        fm2.addInputField(target_fc, fieldnames[rastervalu_index])
        fm2.outputField = field
        fms.addFieldMap(fm2)
        print("  SpatialJoin_analysis...")
        arcpy.SpatialJoin_analysis(target_fc, join_fc, out_fc, '', '',
                                   fms, 'SHARE_A_LINE_SEGMENT_WITH')
        print("  AddField_management...")
        CreateOutputContourFields(out_fc, contour_interval)

    except Exception as ex:
        print(ex.args[0])

def CreateOutputContourFields(inFC, contour_interval):
    """ Create and populate the contour fields in the
                                               output feature class"""
    newFields = ['low_cont',  'high_cont', 'range_cont']
    newFieldAlias = ['Low contour',  'High contour', 'Contour range']
    icnt = 0
    for newField in newFields:
        arcpy.AddField_management(inFC, newField, 'TEXT', '#', '#', '#',
                                  newFieldAlias[icnt], 'NULLABLE',
                                  'REQUIRED', '#')
        icnt+=1
    cur = arcpy.UpdateCursor(inFC)
    icnt=0
    for row in cur:
        icnt+=1
        joinCount = row.getValue('Join_Count')
        contourString = row.getValue('range')
        pointElevation = row.getValue('elevation')
        contourList = []
        for i in contourString.split(';'):
            contourList.append(float(i))

        nuniques = findUniqueContours(contourList)

        try:
            if len(nuniques) > 2:
                contourList = [x for x in contourList if x > -999999]
            minValue = min(contourList)
            maxValue = max(contourList)
            if minValue == maxValue:
                joinCount = 1
            if minValue < -999999 or joinCount == 1:
                if pointElevation > maxValue:
                    minValue = maxValue
                    maxValue = minValue + contour_interval
                else:
                    minValue = maxValue - contour_interval

            sminValue = int_if_youCan(minValue)
            smaxValue = int_if_youCan(maxValue)
        except:
            sminValue = int_if_youCan(-1000000)
            smaxValue = int_if_youCan(-1000000)
        row.setValue(newFields[0], sminValue)
        row.setValue(newFields[1], smaxValue)
        row.setValue(newFields[2], delete_trailing_zeros(sminValue) + ' - ' + \
                                   delete_trailing_zeros(smaxValue))
        if minValue < -999999:
            row.setValue(newFields[2], '<NoData>')
        cur.updateRow(row)
    del cur, row
def doFillContour(in_raster, outWorkspace, out_polygon_features, contour_interval, base_contour=0, z_factor=1):
    print "Doing filled contour"
    # Setting variable names for temporary feature classes
    outContours = 'outContours'
    outPolygonBndry = 'outPolygonBndry'
    outContoursPolygons = 'outContoursPolygons'
    outBuffer = 'outBuffer'
    outBufferContourLine = 'outBufferContourLine'
    outBufferContourLineLyr = 'outBufferContourLineLyr'
    outContoursPolygonsWithPoints = 'outContoursPolygonsWithPoints'
#    # Input parameters
#    if ".shp" in out_polygon_features:
#        print("Only file geodatabase output is supported.")
#        sys.exit()

#    outFCext = os.path.splitext(out_polygon_features)
#    if (os.path.splitext(out_polygon_features)[1]).lower() == ".shp":
#        print("Only file geodatabase output is supported.")
#        sys.exit()
#    currentWS = arcpy.env.workspace
#    if outWorkspace.lower() != ".gdb":
#        print("Only file geodatabase workspace is supported.")
#        sys.exit()

    arcpy.env.workspace = outWorkspace

    ras_DEM = Raster(in_raster)
    ras_cellsize = ras_DEM.meanCellHeight

    print("  Contour...")
    arcpy.sa.Contour(in_raster, outContours, contour_interval, base_contour,
                     z_factor)

    print("  RasterToPolygon_conversion...")
    arcpy.RasterToPolygon_conversion(IsNull(ras_DEM), outPolygonBndry,
                                     "NO_SIMPLIFY")
    print("  Buffer_analysis...")
    try:
        arcpy.Buffer_analysis(outPolygonBndry, outBuffer, str(-ras_cellsize)
                              + ' Unknown', 'FULL', 'ROUND', 'NONE', '#')
    except:
        print('This might be caused by insufficient memory.'+
                        'Use a smaller extent or try another computer.')
        arcpy.Delete_management(outContours)
        arcpy.Delete_management(outPolygonBndry)
        sys.exit()

    print("  FeatureToLine_management...")
    arcpy.FeatureToLine_management([outContours, outBuffer],
                                    outBufferContourLine, '#', 'ATTRIBUTES')

    arcpy.MakeFeatureLayer_management(outBufferContourLine,
                                      outBufferContourLineLyr)
    arcpy.SelectLayerByAttribute_management(outBufferContourLineLyr,
                                            'NEW_SELECTION',
                                            '"BUFF_DIST" <> 0')
    arcpy.CalculateField_management(outBufferContourLineLyr, 'Contour',
                                    '-1000000', 'VB', '#')
    arcpy.SelectLayerByAttribute_management(outBufferContourLineLyr,
                                            'CLEAR_SELECTION')

    print("  FeatureToPolygon_management...")
    arcpy.FeatureToPolygon_management([outBuffer, outContours],
                                      outContoursPolygons, '#',
                                      'NO_ATTRIBUTES', '#')
    outContoursPolygonsWithPoints, outEVT, outPolygPoints = \
                                       FindZ(outContoursPolygons, in_raster)

    # Spatial Join and update contour labels
    PerformSpatialJoin(outContoursPolygonsWithPoints,
                       outBufferContourLineLyr, out_polygon_features,
                       contour_interval)

    fields = arcpy.ListFields(out_polygon_features)
    fields2delete = []
    for field in fields:
        if not field.required:
            fields2delete.append(field.name)
    print("  DeleteField_management...")
    # these fields include all the temp fields like
    # 'Join_Count', 'TARGET_FID', 'range', and 'elevation'
    arcpy.DeleteField_management(out_polygon_features, fields2delete)
    arcpy.AddField_management(out_polygon_features, "Height", "LONG")
    arcpy.CalculateField_management(out_polygon_features, "Height", 
                                "!high_cont!",
                                "PYTHON_9.3")
    
    arcpy.AddField_management(out_polygon_features, "Age", "LONG")
    age = out_polygon_features.split("/")[-1].replace("LIG_", "")
    age = age.replace("k", "")
    age = int(age)*100
    arcpy.CalculateField_management(out_polygon_features, "Age", 
                                    age,
                                    "PYTHON_9.3")
    
    
    with arcpy.da.UpdateCursor(out_polygon_features, "*") as cursor:
        for row in cursor:
            if row[7] < 100:
                cursor.deleteRow()

    print('  Deleting temp files.')
    arcpy.Delete_management(outBuffer)
    arcpy.Delete_management(outContours)
    arcpy.Delete_management(outContoursPolygons)
    arcpy.Delete_management(outBufferContourLine)
    arcpy.Delete_management(outPolygonBndry)
    arcpy.Delete_management(outEVT)
    arcpy.Delete_management(outPolygPoints)
