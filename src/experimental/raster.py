import gdal
import numpy as np 
from utility import ogrutil as util
import ogr

SIZE = (1000, 1000)
SRS = gdal.osr.SpatialReference()
DRIVER : gdal.Driver = gdal.GetDriverByName('gtiff')

SRS.ImportFromEPSG(3857)
SRS = SRS.ExportToWkt()

'''

def process_data():
    return np.ones(SIZE, dtype=np.int8) * 0


data = process_data()

driver : gdal.Driver = gdal.GetDriverByName('gtiff')
ref = gdal.osr.SpatialReference()
ref.ImportFromEPSG(3857)


dataset : gdal.Dataset = driver.Create('data/raster/HELLO.tiff', *SIZE)
dataset.SetProjection(ref.ExportToWkt())

band : gdal.Band = dataset.GetRasterBand(1)


dataset.SetGeoTransform((-9968426.1904, 2.2, 0, 4078845.3914, 0, -2.2))


band.WriteArray(data)

dataset.FlushCache()

del dataset



'''

r = 15
size2 = (SIZE[0] // r, SIZE[1] // r)

dataset : gdal.Dataset = gdal.Open('data/raster/HELLO.tiff', gdal.GA_Update)

driver : gdal.Driver = gdal.GetDriverByName('gtiff')


dataset2 : gdal.Dataset = driver.Create('data/raster/SALUTE.tiff', *size2)
dataset2.SetProjection(SRS)

dataset2.SetGeoTransform((-9968426.1904, 2.2 * r, 0, 4078845.3914, 0, -2.2 * r))

reader = util.UtilReader('data/route/bumbs.shp')

lyr = reader.getLayer()

for i in range(10):

    lyr.SetAttributeFilter('height={}'.format(i))

    gdal.RasterizeLayer(dataset, [1], lyr, burn_values=[i + 1])

gdal.ReprojectImage(dataset, dataset2, None, None, gdal.GRA_Bilinear)



reader.close()

dataset2.FlushCache()
dataset.FlushCache()
del dataset
del dataset2


'''
dataset : gdal.Dataset = gdal.Open('data/raster/HELLO.tiff', gdal.GA_Update)
memdriver : ogr.Driver = ogr.GetDriverByName('Memory')
memdriver.CreateDataSource('')

'''