import gdal
import numpy as np
from utility import ogrutil as util
import ogr
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

SIZE = (1000, 1000)
SRS = gdal.osr.SpatialReference()
DRIVER : gdal.Driver = gdal.GetDriverByName('gtiff')

SRS.ImportFromEPSG(3857)
SRS = SRS.ExportToWkt()


dem = gdal.Open('data/raster/SALUTE.tiff')
gt  = dem.GetGeoTransform()
dem = dem.ReadAsArray()

fig, ax = plt.subplots(figsize=(16,8), subplot_kw={'projection': '3d'})


xres = gt[1]
yres = gt[5]

X = np.arange(gt[0], gt[0] + dem.shape[1]*xres, xres)
Y = np.arange(gt[3], gt[3] + dem.shape[0]*yres, yres)

X, Y = np.meshgrid(X, Y)

surf = ax.plot_surface(X,Y,dem, rstride=1, cstride=1, cmap=plt.cm.RdYlBu_r, vmin=0, vmax=10, linewidth=0, antialiased=True)

ax.set_zlim(0, 10) # to make it stand out less
ax.view_init(60,-60)

fig.colorbar(surf, shrink=0.4, aspect=20)

plt.show()

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


'''
dataset : gdal.Dataset = gdal.Open('data/raster/HELLO.tiff', gdal.GA_Update)
memdriver : ogr.Driver = ogr.GetDriverByName('Memory')
memdriver.CreateDataSource('')

'''

