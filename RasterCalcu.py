# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# RasterCalcu.py
# Created on: 2022-10-12 15:07:41.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Load required toolboxes
arcpy.ImportToolbox("Model Functions")


# Local variables:
DBoutput20 = "H:\\basicData\\MCD64A1_output\\DXAL_mcd64a1\\Jenks\\DBoutput20"
Name = "db_resultreclass_dxal_MCD64A1_2001_1"
db_resultreclass_dxal_MCD64A1_2001_1_tif = "H:\\basicData\\MCD64A1_output\\DXAL_mcd64a1\\Jenks\\DBoutput20\\db_resultreclass_dxal_MCD64A1_2001_1.tif"
v__Name___tif = "H:\\basicData\\MCD64A1_output\\DXAL_mcd64a1\\Jenks\\\"%Name%\".tif"

# Process: Iterate Rasters
arcpy.IterateRasters_mb(DBoutput20, "", "TIF", "NOT_RECURSIVE")

# Process: Raster Calculator
arcpy.gp.RasterCalculator_sa("SetNull(\"%db_resultreclass_dxal_MCD64A1_2001_1.tif%\" == 200, \"%db_resultreclass_dxal_MCD64A1_2001_1.tif%\")",v__Name___tif)

