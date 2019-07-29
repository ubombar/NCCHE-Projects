import util
import npgraph as graph
import ogr

class Junc(graph.Node):
    def __init__(self, point):
        super()
        self.point = point.Clone()

class Road(graph.Conn):
    def __init__(self, oneway : bool, speedlimit : int, size : int, length : float, deadend : bool, points : ogr.Geometry):
        super()
        self.oneway = oneway
        self.speedlimit = speedlimit
        self.size = size
        self.length = length
        self.deadend = deadend
        self.points = points.Clone()
        self.ojid = None

def CreateGraph(roadPath : str, juncPath : str, BUFFER : int = 7) -> graph.Graph:
    roadDatasource = util.OpenDataSource(roadPath)
    juncDatasource = util.OpenDataSource(juncPath)
    roadLayer = util.GetLayer(roadDatasource)
    juncLayer = util.GetLayer(juncDatasource)

    optGraph = graph.Graph()
    
    for junction in juncLayer:
        juncId = junction.GetField('id')
        juncNode = Junc(junction.geometry())
        optGraph.addNode(juncNode)
    juncLayer.ResetReading()

    roadIDs = dict()

    for junction in juncLayer:
        juncGeom = junction.geometry().Clone().Buffer(BUFFER)
        juncId = junction.GetField('id')
        roadLayer.SetSpatialFilter(juncGeom) 

        for road in roadLayer:
            rid = road.GetField('id')
            origin = util.GetPointGeomOfLineGeom(road.geometry().Clone(), 0).Intersects(juncGeom)

            # print(juncId, 'junc connects to row', rid)
            
            if roadIDs.get(rid) is None:
                if origin:
                    roadIDs[rid] = (juncId, None)
                else:
                    roadIDs[rid] = (None, juncId)
            else:
                first, second = roadIDs[rid]
                
                if first is None:
                    roadIDs[rid] = (juncId, second)
                else:
                    roadIDs[rid] = (first, juncId)            

        roadLayer.ResetReading()
    juncLayer.ResetReading()

    # print(roadIDs)
    nID = juncLayer.GetFeatureCount()

    roadLayer.SetSpatialFilter(None)
    for road in roadLayer:
        points = road.geometry()
        rid = road.GetField('id')
        oneway = road.GetField('oneway') != 0
        slimit = road.GetField('slimit')
        size = road.GetField('size')
        length = road.GetField('length')

        roadNode = Road(oneway, slimit, size, length, False, points)

        if roadIDs.get(rid) is None: # road is not connected to any junction, ignore the road
            continue
        else:
            jid1, jid2 = roadIDs[rid]

            # print(jid1, jid2)

            if jid1 is None and jid2 is not None: # road has no origin junction
                roadNode.ojid = nID
                roadNode.deadend = True
                optGraph.addNode(Junc(util.GetPointGeomOfLineGeom(points, 0)))
                optGraph.addConn(roadNode, nID, jid2, not oneway)
                nID += 1
            elif jid1 is not None and jid2 is None: # road has not ending junction
                roadNode.ojid = jid1
                roadNode.deadend = True
                optGraph.addNode(Junc(util.GetPointGeomOfLineGeom(points, -1)))
                optGraph.addConn(roadNode, jid1, nID, not oneway)
                nID += 1
            else: # road is a twoway connector
                roadNode.deadend = False
                roadNode.ojid = jid1
                optGraph.addConn(roadNode, jid1, jid2, not oneway)
    
    # optGraph.listConnections()
    return optGraph

def SaveGraph(graphPath : str, graph : graph.Graph) -> bool:
    print(graph.__str__())
    graphDatasource = util.CreateDataSource(graphPath)
    graphLayer = util.CreateLayer(graphDatasource, 'graph', ogr.wkbLineString, {})
    graphHandle = util.CreateFeatureHandle(graphLayer)

    for road in graph.cids():
        pointsGeom = graph.asConn(road).points
        pointGeom = ogr.Geometry(ogr.wkbLineString)

        for i in range(0, pointsGeom.GetPointCount()):
            pointGeom.AddPoint(*pointsGeom.GetPoint(i))

        util.CreateFeature(graphHandle, graphLayer, pointGeom)
        # print(road)

    for jid in graph.nids():
        print('hello')
        juncNode = graph.asNode(jid)
        juncPointGeom = juncNode.point.Clone()
        
        for rid in graph.adjConns(jid):
            
            print(jid, 'th junction connected to ', rid, 'th road')
            roadNode = graph.asConn(rid)
            roadPointGeomIndex = 0 if roadNode.ojid == jid else -1
            roadPointGeom = util.GetPointGeomOfLineGeom(roadNode.points, roadPointGeomIndex)
            connectorLineGeom = util.MergePointGeoms(juncPointGeom, roadPointGeom)
            util.CreateFeature(graphHandle, graphLayer, connectorLineGeom)

            if jid == 7 and rid == 3:
                print(roadNode.deadend)
    print('done doby')
    return True

def SavePath(pathName : str, path : list()) -> bool:
    pathDatasource = util.CreateDataSource(pathName)
    pathLayer = util.CreateLayer(pathDatasource, 'path', ogr.wkbLineString, {})
    pathHandle = util.CreateFeatureHandle(pathLayer)

    line = ogr.Geometry(ogr.wkbLineString)

    for i in range(len(path)):
        if i == 0:
            continue
        
        nid0 = path[i - 1]
        nid1 = path[i]

        

        

        
    
    util.CreateFeature(pathHandle, pathLayer, line)
    return True