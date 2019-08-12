import gdal
import numpy as np
import osr

driver : gdal.Driver = gdal.GetDriverByName('gtiff')

inds : gdal.Dataset     = gdal.Open('data/raster/UTM2GTIF.tiff')

outds : gdal.Dataset    = driver.Create('data/raster/TEST.tiff', 200, 200)

'''
ds : gdal.Dataset = gdal.Open('data/raster/UTM2GTIF.tiff')
trans = ds.GetGeoTransform()
del ds

driver : gdal.Driver = gdal.GetDriver(0)
ds = driver.Create('data/raster/TEST.geotiff', 200, 200)
srs = osr.SpatialReference()

srs.ImportFromEPSG(3857)
ds.SetProjection(srs.ExportToWkt())
ds.SetGeoTransform(trans)

array = np.ndarray((200, 200), dtype=int)

band : gdal.Band = ds.GetRasterBand(1)
band.WriteRaster(0, 0, 200, 200)
'''

