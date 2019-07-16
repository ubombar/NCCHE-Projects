import ogr
import osr
import os

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


def CreateLayer(ds : ogr.DataSource, name : str, etype, **fields) -> ogr.Layer:
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

