'''
    This file contains classes and functions for indexing the roads in a given area.
'''
from utility import ogrutil as util
from utility.ogrutil import DN_GEOJSON, GT_Line, DT_Float
from utility import rgraph as graph
from collections import defaultdict, OrderedDict
from ogr import Geometry

class CostFunction:
    def __init__(self, router, costDist=0.1, costUrgency=1.2, useActualDistance=False):
        self.router = router
        self.costDist = costDist
        self.costUrgency = costUrgency
        self.useActualDistance = useActualDistance
    
    def __call__(self, cid1, cid2) -> float:
        ## Calcualte cost

        return 0

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

class Stop:
    def __init__(self, feature, connectedCrossFID, geometry):
        self.geometry = geometry.Clone()
        self.connectedCrossFID = connectedCrossFID
        self.urgency = feature.GetField('urgency')
        self.id = feature.GetFID()

class PathCollection:
    def __init__(self, paths):
        self.paths = paths

    def save(self, fname):
        writer = util.UtilWriter(fname, driver=DN_GEOJSON)
        writer.makeLayer('routes', GT_Line, {'length':DT_Float})

        for path in self.paths:
            pathGeometry = path.getGeometry()
            pathLength = pathGeometry.Length()
            writer.saveFeature({'length':pathLength}, pathGeometry)
        
        writer.close()
    
class Path:
    def __init__(self, graph, path, connector):
        self.graph = graph
        self.path = path
        self.connector = connector
    
    def getGeometry(self) -> Geometry:
        routeGeometry = Geometry(GT_Line)

        crossFID = self.path[0]
        crossPointGeom = self.graph.crossObjects[crossFID].point
        routeGeometry.AddPoint(*crossPointGeom.GetPoint())

        for i in range(len(self.path)):
            if i == 0: continue

            crossFID = self.path[i]
            crossFIDPrev = self.path[i - 1]

            roadFID = self.connector.get((crossFIDPrev, crossFID))

            if roadFID is None: 
                roadFID = self.connector.get((crossFID, crossFIDPrev))
            
            roadGeometry = self.graph.roadObjects.get(roadFID).points

            originalDirection = self.graph.crossGraph[roadFID][0] == crossFIDPrev
            
            for roadPoint in util.UtilPointIterator(roadGeometry, jump=1 if originalDirection else -1):
                routeGeometry.AddPoint(*roadPoint)

            crossPointGeom = self.graph.crossObjects[crossFID].point
            routeGeometry.AddPoint(*crossPointGeom.GetPoint())
        return routeGeometry
    
    def save(self, fname):
        writer = util.UtilWriter(fname, driver=DN_GEOJSON)
        writer.makeLayer('route', GT_Line, {'length':DT_Float})

        routeGeometry = self.getGeometry()
        length = routeGeometry.Length()
        writer.saveFeature({'length':length}, routeGeometry)
        writer.close()

class Router:
    ROAD_BUFFER = 15
    STOP_BUFFER = 30

    def __init__(self, crosspath, roadpath, stoppath):
        self.crossReader : util.UtilReader = util.UtilReader(crosspath)
        self.roadReader : util.UtilReader = util.UtilReader(roadpath)
        self.stopReader : util.UtilReader = util.UtilReader(stoppath)

        self.mapgraph : graph.MapperGraph = graph.MapperGraph()

        self.stopObjects = OrderedDict()
        self.cost = CostFunction(self)
    
    def getCrossBtStopIndex(self, index=0): # bad practice!
        return self.stopObjects.items()[index][0]
    
    def indexGraph(self):
        graphDict = defaultdict(list)
        directedSet = set()
        roadToFeatureDict = dict()

        for crossFeature in self.crossReader.getFeatureIterator():
            crossGeometryRBuffer = crossFeature.geometry().Buffer(Router.ROAD_BUFFER)
            crossGeometrySBuffer = crossFeature.geometry().Buffer(Router.STOP_BUFFER)

            crossFID = crossFeature.GetFID()

            self.mapgraph.addCross(Cross(crossFeature), idd=crossFID)
            self.roadReader.setGeometryFilter(crossGeometryRBuffer)
            self.stopReader.setGeometryFilter(crossGeometrySBuffer)

            for stopFeature in self.stopReader.getFeatureIterator():
                self.stopObjects[stopFeature.GetFID()] = Stop(stopFeature, crossFID, crossFeature.geometry())

            for roadFeature in self.roadReader.getFeatureIterator():
                roadHeadGeometry = util.Point2Geometry(roadFeature.geometry().GetPoint(0))

                fromHead = roadHeadGeometry.Intersects(crossGeometryRBuffer)
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
    
    def getPathCollection(self):
        # TODO: reorder the stops. This is the where magic happens.
        paths = []

        stopFIDPrev = None

        for stopFID, _ in self.stopObjects.items():
            if stopFIDPrev is None:
                stopFIDPrev = stopFID
                continue

            crossFID = self.stopObjects[stopFID].connectedCrossFID
            crossFIDPrev = self.stopObjects[stopFIDPrev].connectedCrossFID

            paths.append(self.getPath(crossFID, crossFIDPrev))

            stopFIDPrev = stopFID
        
        return PathCollection(paths)
    
    def getOptimizedPathCollection(self, excludeStartEnd=True):
        if excludeStartEnd:
            pathCollection = self.getOptimizedPathCollection(excludeStartEnd=False)
            pathCollection.addFront(self.getPath())

        orderedStops = OrderedDict()

        for i, stopFID in enumerate(self.stopObjects.items()):
            currentCrossFID = self.stopObjects[0].connectedCrossFID

        calccost = self.cost(cid1, cid2)
