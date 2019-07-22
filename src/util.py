import ogr
import osr
import os
import graph

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

def SaveGraphOnFile(rgraph : graph.RoadGraph, path : str) -> bool:
    '''
        author : Ufuk Bombar

        This function saves the graph in a shape file
    '''

    if rgraph is None or path is None:
        return False

    connected_ds = CreateDataSource(path)
    connected_ly = CreateLayer(connected_ds, 'connected', ogr.wkbLineString, 
        {   
            'graphid1':ogr.OFTString, 
            'graphid2':ogr.OFTString, 
            'distance':ogr.OFTReal
        })
    connected_hd = CreateFeatureHandle(connected_ly)

    for parent, children in rgraph.graph.items():
        for child in children:
            geom = ogr.Geometry(ogr.wkbLineString)
            geom.AddPoint(*rgraph.getNode(parent).getAsPoint())
            geom.AddPoint(*rgraph.getNode(child).getAsPoint())

            dis = rgraph.getWeight(parent, child)
            CreateFeature(connected_hd, connected_ly, geom, graphid1=parent, graphid2=child, distance=dis)
    
    return True

def SaveRoutes(graph : graph.RoadGraph, routeList : list(), path : str, dtype : str = 'geojson') -> None:
    '''
        author Ufuk Bombar

        This function saves the routs
    '''

    if routeList is None or path is None:
        return False

    routedataSource = CreateDataSource(path, dtype)
    routeLayer = CreateLayer(routedataSource, 'route', ogr.wkbLineString, {})
    routeHandle = CreateFeatureHandle(routeLayer)
    
    for route in routeList:
        routeGeometry = ogr.Geometry(ogr.wkbLineString)

        for nodeIndex in route: 
            routeGeometry.AddPoint(*graph.getNode(nodeIndex).getAsPoint())
        
        CreateFeature(routeHandle, routeLayer, routeGeometry)

def GetGeometryIterator(geom : ogr.Geometry):
    return iter(GeometryIterator(geom))

def GetPointIterator(geom : ogr.Geometry):
    return iter(PointIterator(geom))

def GetGeometryEnumerator(geom : ogr.Geometry):
    return iter(GeometryIterator(geom, False))

def GetPointEnumerator(geom : ogr.Geometry):
    return iter(PointIterator(geom, False))

'''
            elif j == 0 or j == linegeom.GetPointCount() - 1: # runtime will be O(2nk)
                # do spatial filtering
                spatialfilter = pointgeom.Clone().Buffer(BUFFER_RADIUS)

                easyroads_ly.SetSpatialFilter(spatialfilter)                

                for filteredroad in easyroads_ly:
                    filteredroadfid = filteredroad.GetFID()

                    allpoints_ly.ResetReading()
                    allpoints_ly.SetAttributeFilter('roadfid = {}'.format(filteredroadfid))
                    # allpoints_ly.SetSpatialFilter(spatialfilter)
                    x, y = point
                    allpoints_ly.SetSpatialFilterRect(x - BUFFER_RADIUS, y - BUFFER_RADIUS, x + BUFFER_RADIUS, y + BUFFER_RADIUS)

                    shortestdistance = 10 * BUFFER_RADIUS
                    shortestpointfeature = None

                    for filteredpoint in allpoints_ly:
                        if idx != filteredpoint.GetField('graphid'):
                            distancetmp = filteredpoint.geometry().Distance(pointgeom)
                            print(distancetmp, shortestdistance)

                            if shortestdistance > distancetmp:
                                shortestdistance = distancetmp
                                shortestpointfeature = filteredpoint
                        
                    if shortestpointfeature is not None:
                        print('{} and {} is connected!'.format(idx, shortestpointfeature.GetField('graphid')))
                        roadgraph.addConnection(idx, shortestpointfeature.GetField('graphid'))
                    
                    print()
                easyroads_ly.ResetReading()
'''