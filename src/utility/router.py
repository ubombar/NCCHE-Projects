'''
    This file contains classes and functions for indexing the roads in a given area.
'''
from utility import ogrutil as util
from utility.ogrutil import DN_GEOJSON, GT_Line, DT_Float
from utility import rgraph as graph
from collections import defaultdict
from ogr import Geometry

class Cross:
    def __init__(self, feature):
        self.point = feature.geometry().Clone()
        self.id = feature.GetFID()

class Road:
    def __init__(self, feature):
        self.points = feature.geometry().Clone()

        self.directed = feature.GetField('directed') == 1
        self.length = feature.GetField('length')
        self.id = feature.GetFID()
    
    def __abs__(self):
        return self.length
    
class Path:
    def __init__(self, graph, path, connector):
        self.graph = graph
        self.path = path
        self.connector = connector

        print(connector)
    
    def save(self, fname):
        writer = util.UtilWriter(fname, driver=DN_GEOJSON)
        writer.makeLayer('route', GT_Line, {'length':DT_Float})

        length = 0
        routeGeometry = Geometry(GT_Line)

        for i in range(len(self.path)):
            crossFID = self.path[i]

            crossPointGeom = self.graph.crossObjects[crossFID].point
            routeGeometry.AddPoint(*crossPointGeom.GetPoint())

            if i == 0: continue

            crossFIDPrev = self.path[i - 1]
            roadFID = self.graph.getRoadByCrosses(crossFID, crossFIDPrev)
            roadGeometry = self.graph.roadObjects[roadFID].points

            for roadPoint in util.UtilPointIterator(roadGeometry, jump=1):
                routeGeometry.AddPoint(*roadPoint)

        writer.saveFeature({'length':length}, routeGeometry)

class Router:
    BUFFER = 15
    def __init__(self, crosspath, roadpath):
        self.crossReader : util.UtilReader = util.UtilReader(crosspath)
        self.roadReader : util.UtilReader = util.UtilReader(roadpath)
        self.mapgraph : graph.MapperGraph = graph.MapperGraph()
    
    def indexGraph(self):
        graphDict = defaultdict(list)
        directedSet = set()
        roadToFeatureDict = dict()

        for crossFeature in self.crossReader.getFeatureIterator():
            crossGeometryBuffer = crossFeature.geometry().Buffer(Router.BUFFER)
            crossFID = crossFeature.GetFID()

            self.mapgraph.addCross(Cross(crossFeature), idd=crossFID)

            self.roadReader.setGeometryFilter(crossGeometryBuffer)

            for roadFeature in self.roadReader.getFeatureIterator():
                fromHead = roadFeature.geometry().Intersects(crossGeometryBuffer)
                roadFID = roadFeature.GetFID()
                roadDirected = roadFeature.GetField('directed') == 1

                if roadDirected:
                    directedSet.add(roadFID)

                roadToFeatureDict[roadFID] = roadFeature
                
                if fromHead:
                    graphDict[roadFID] = [crossFID] + graphDict[roadFID]
                else:
                    graphDict[roadFID] = graphDict[roadFID] + [crossFID]

        for roadFID, connections in graphDict.items():
            if len(connections) == 2: # fully connector road!
                self.mapgraph.addRoad(Road(roadToFeatureDict[roadFID]), *tuple(connections), idd=roadFID, directed=roadFID in directedSet)
            elif len(connections) == 1: # road is only connected to one cross
                pass
            else: # road is not connected to any cross
                pass
        
    def getPath(self, crossFID1, crossFID2) -> Path:
        path, connector = self.mapgraph.doDijkstra(crossFID1, crossFID2)
        return Path(self.mapgraph, path, connector)