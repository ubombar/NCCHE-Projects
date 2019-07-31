'''
    This file contains the utility finctions for ogr
'''

import ogr 
import osr
from os.path import exists

# Head of Constants

''' Driver names '''
DN_SHP = 'ESRI Shapefile'
DN_GEOJSON = 'GeoJSON'

''' Geometry Types, later add more types  '''
GT_Point = ogr.wkbPoint
GT_Line = ogr.wkbLineString
GT_Polygon = ogr.wkbPolygon
GT_Empty = ogr.wkbNone

''' Data types '''
DT_String = ogr.OFTString
DT_Integer = ogr.OFTInteger
DT_Float = ogr.OFTReal
DT_Date = ogr.OFTDate
DT_Time = ogr.OFTTime
DT_Datetime = ogr.OFTDateTime

''' Frequently used driver names and their EPSG id '''
SRS = {
    'WGS 84 / Pseudo-Mercator':3857,
    'NAD83(2011) / UTM Zone 16N':6345,
    'NAD83(2011) / UTM Zone 15N':6344,
    'NAD83(2011) / UTM Zone 14N':6343,
    'NAD83(2011) / UTM Zone 13N':6342,
    'NAD83(2011) / UTM Zone 12N':6341,
    'NAD83(2011) / UTM Zone 11N':6340,
    'NAD83(2011) / UTM Zone 10N':6339}

# Head of Iterators

class UtilFeatureIterator:
    ''' For iterationg the features in a layer, automatically resets the readings '''
    def __init__(self, layer):
        self.layer : ogr.Layer = layer
    
    def __iter__(self):
        return self
    
    def __next__(self):
        feature = self.layer.GetNextFeature()

        if feature is None:
            self.layer.ResetReading()
            raise StopIteration
        
        return feature

class UtilPointIterator:
    def __init__(self, geometry : ogr.Geometry, withindex=False, jump=1):
        ''' Takes a point based geometry. Multi Geometries or collections does not work '''
        if jump == 0:
            raise ValueError('Illegal value for jump: 0')

        self.geometry : ogr.Geometry = geometry.Clone()
        self.withindex = withindex
        self.jump = jump
    
    def __iter__(self):
        if self.jump < 0:
            self.i = self.geometry.GetPointCount() - 1
        else:
            self.i = 0
        
        return self
    
    def __next__(self):
        if (self.jump < 0 and self.i >= 0) or (self.jump > 0 and self.i < self.geometry.GetPointCount()):
            self.i += self.jump
            point = self.geometry.GetPoint(self.i - self.jump)

            if self.withindex:
                return (self.i - self.jump, *point)
            else:
                return point
        else:
            self.__iter__()
            raise StopIteration

# End of Iterators

class UtilReader:

    def __init__(self, filepath : str):
        ''' Creates a new UtilReader '''
        if not exists(filepath):
            raise Exception('Cannot find the file')

        self.ds = ogr.Open(filepath, 0)
        self.active = self.ds.GetLayer()
    
    def getLayer(self, ilayer=None) -> ogr.Layer:
        ''' Returns the layer, if ilayer is not valid (None) then return active layer '''

        if ilayer is None:
            if self.active is None:
                raise Exception('There is no active layer!')
            return self.active
        return self.ds.GetLayer(ilayer)
    
    def setActiveLayer(self, ilayer):
        self.active = self.getLayer(ilayer)
    
    def setAttributeFilter(self, filter, ilayer=None):
        self.getLayer(ilayer).SetAttributeFilter(filter)
    
    def setGeometryFilter(self, geom, ilayer=None):
        self.getLayer(ilayer).SetSpatialFilter(geom)
        
    def getFeatureIterator(self, ilayer=None) -> UtilFeatureIterator:
        ''' Gets the feature iterator '''
        return UtilFeatureIterator(self.getLayer(ilayer))
    
    def getPointIterator(self, feature : ogr.Feature, withindex=False, jump=1) -> UtilPointIterator:
        return UtilPointIterator(feature.geometry, withindex, jump)
    
    def close(self):
        del self.ds

class UtilWriter(UtilReader):

    def __init__(self, filepath : str, driver=DN_SHP, srs=3857, override=True):
        if isinstance(srs, str):
            self.srsid = SRS.get(srs)
        else:
            self.srsid = srs
        
        if self.srsid is None:
            raise ValueError('Unknown spatial reference system: EPSG{}'.format(self.srsid))

        ndriver : ogr.Driver = ogr.GetDriverByName(driver)
        
        if exists(filepath):
            if override:
                ndriver.DeleteDataSource(filepath)
                self.ds = ndriver.CreateDataSource(filepath)
            else:
                self.ds = ogr.Open(filepath)
                # raise NotImplementedError('Non Override for existing path is not implemented yet!')
        else:
            self.ds = ndriver.CreateDataSource(filepath)

    def makeLayer(self, name : str, gtype : int, fields : dict):
        ''' Creates a new Layer, also changes the active layer '''
        reference = osr.SpatialReference()
        reference.ImportFromEPSG(self.srsid)
        
        layer = self.ds.CreateLayer(name, reference, gtype)

        for name, dtype in fields.items():
            layer.CreateField(ogr.FieldDefn(name, dtype))
        
        self.active = layer
    
    def makeEmplyFeature(self, ilayer=None) -> ogr.Feature:
        feature = ogr.Feature(self.getLayer(ilayer).GetLayerDefn())
        feature.SetGeometry(ogr.Geometry(ogr.wkbNone))

        return feature
    
    def saveFeature(self, fields : dict, geometry : ogr.Geometry, handle=None, ilayer=None):
        ''' Makes a single feature. Use makeFeatureByHandle to make multiple features '''
        layer = self.getLayer(ilayer)

        feature = handle

        if handle is None:
            feature = ogr.Feature(layer.GetLayerDefn())

        for name, value in fields.items():
            feature.SetField(name, value)
        
        if geometry is not None:
            feature.SetGeometry(geometry)
        
        layer.CreateFeature(feature)


def Point2Geometry(point):
    geo = ogr.Geometry(ogr.wkbPoint)
    geo.AddPoint(*point)

    return geo