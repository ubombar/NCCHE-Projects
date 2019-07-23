import ogr
import osr
import os

class GeometryIterator:
    def __init__(self, geometry : ogr.Geometry, iterate : bool = True):
        self.gem = geometry
        self.i = 0
        self.iterate = iterate
    
    def __iter__(self):
        self.i = 0
        return self
    
    def __next__(self):
        if self.i < self.gem.GetGeometryCount():
            self.i += 1
            if self.iterate:
                return self.gem.GetGeometryRef(self.i - 1)
            else:
                return (self.i - 1, self.gem.GetGeometryRef(self.i - 1))
        else:
            self.i = 0
            raise StopIteration()


class PointIterator:
    def __init__(self, geometry : ogr.Geometry, iterate : bool = True):
        self.gem : ogr.Geometry = geometry
        self.i = 0
        self.iterate = iterate
    
    def __iter__(self):
        self.i = 0
        return self
    
    def __next__(self):
        if self.i < self.gem.GetPointCount():
            self.i += 1
            point = self.gem.GetPoint(self.i - 1)
            pgeom = ogr.Geometry(ogr.wkbPoint)
            pgeom.AddPoint(*point)
            
            if self.iterate:
                return pgeom
            else:
                return (self.i - 1, pgeom)
        else:
            self.i = 0
            raise StopIteration

def GetPointGeomOfLineGeom(geom : ogr.Geometry, index : int) -> ogr.Geometry:
    ngeom = ogr.Geometry(ogr.wkbPoint)

    if index == -1:
        index = geom.GetPointCount() - 1

    ngeom.AddPoint(*geom.GetPoint(index))

    return ngeom

def GeometryToPoint(geom : ogr.Geometry, index : int = 0) -> tuple:
    if index == -1:
        index = geom.GetPointCount() - 1
    
    if geom.GetGeometryType() == ogr.wkbPoint:
        return geom.GetX(), geom.GetY()
    return None

def MergePointGeoms(*geoms) -> ogr.Geometry:
    line = ogr.Geometry(ogr.wkbLineString)

    for geo in geoms:
        line.AddPoint(geo.GetX(), geo.GetY())
    
    return line


def CreateDataSource(path : str, driver : str = 'ESRI Shapefile', override : bool = True) -> ogr.DataSource:
    '''
        author : Ufuk Bombar

        This function createas a datasource. If the data source exists overrides it.
    '''

    mdriver : ogr.Driver = ogr.GetDriverByName(driver)

    if mdriver is None:
        raise Exception('Cannot find driver {}'.format(driver))

    if os.path.exists(path):
        mdriver.DeleteDataSource(path)
    
    return mdriver.CreateDataSource(path)


def CreateLayer(ds : ogr.DataSource, name : str, etype, fields : dict) -> ogr.Layer:
    '''
        author : Ufuk Bombar

        This function createas a layer by the definition.
    '''

    if ds is None:
        raise Exception('Given datasource is not defined')

    reference : osr.SpatialReference = osr.SpatialReference()
    reference.ImportFromEPSG(3857)
    
    layer : ogr.Layer = ds.CreateLayer(name, reference, etype)

    for name, dtype in fields.items():
        layer.CreateField(ogr.FieldDefn(name, dtype))
    
    return layer


def CreateFeatureHandle(layer : ogr.Layer) -> ogr.Feature:
    '''
        author : Ufuk Bombar

        This function createas a feature which is called handle.
    '''

    return ogr.Feature(layer.GetLayerDefn())


def CreateFeature(handle : ogr.Feature, layer : ogr.Layer, geometry : ogr.Geometry, **fields) -> None:
    '''
        author : Ufuk Bombar

        This function createas a feature by given parameters.
    '''

    if fields is not None:
        for key, value in fields.items():
            handle.SetField(key, value)
        
    if handle is None or layer is None or geometry is None:
        raise Exception('Given parameters are not defined')

    handle.SetGeometry(geometry)
    layer.CreateFeature(handle)


def OpenDataSource(path : str, w : int = 0) -> ogr.DataSource:
    '''
        author : Ufuk Bombar

        This function opens a datasource form a file.
    '''

    datasource = ogr.Open(path, w)

    if datasource is None:
        raise Exception('Cannot find the path')
    
    return datasource

def OpenLayerDirectly(path : str, w : int = 0, arg = 0) -> ogr.Layer:
    return GetLayer(OpenDataSource(path, w), arg)

def GetLayer(ds : ogr.DataSource, arg = 0) -> ogr.Layer:
    '''
        author : Ufuk Bombar

        This function gets the layer
    '''

    return ds.GetLayer(arg)
