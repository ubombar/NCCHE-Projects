import util
import optimized as op
import ogr

# Its not working

def CreateGraph(roadPath : str, juncPath : str, BUFFER : int = 7) -> op.OptGraph:
    roadDatasource = util.OpenDataSource(roadPath)
    juncDatasource = util.OpenDataSource(juncPath)
    roadLayer = util.GetLayer(roadDatasource)
    juncLayer = util.GetLayer(juncDatasource)

    optGraph = op.OptGraph()
    
    for junction in juncLayer:
        juncId = junction.GetField('id')
        optGraph.addJunction(op.OptGraphJunction(juncId, junction.geometry()))
    juncLayer.ResetReading()

    roadIDs = dict()

    for junction in juncLayer:
        juncGeom = junction.geometry().Clone().Buffer(BUFFER)
        juncId = junction.GetField('id')
        roadLayer.SetSpatialFilter(juncGeom)

        for road in roadLayer:
            rid = road.GetField('id')
            origin = util.GetPointGeomOfLineGeom(road.geometry().Clone(), 0).Intersects(juncGeom)

            print(juncId, 'junc connects to row', rid)
            
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

    print(roadIDs)
    nID = juncLayer.GetFeatureCount()

    roadLayer.SetSpatialFilter(None)
    for road in roadLayer:
        points = road.geometry()
        rid = road.GetField('id')
        oneway = road.GetField('oneway') != 0
        slimit = road.GetField('slimit')
        size = road.GetField('size')
        length = road.GetField('length')

        roadNode = op.OptGraphRoad(rid, False, slimit, size, length, False, points)

        if roadIDs.get(rid) is None: # road is not connected to any junction, ignore the road
            continue
        else:
            jid1, jid2 = roadIDs[rid]

            print(jid1, jid2)

            if jid1 is None and jid2 is not None: # road has no origin junction
                roadNode.ojid = nID
                roadNode.deadend = True
                optGraph.addJunction(op.OptGraphJunction(nID, util.GetPointGeomOfLineGeom(points, 0)))
                optGraph.addRoad(roadNode, nID, jid2)
                nID += 1
            elif jid1 is not None and jid2 is None: # road has not ending junction
                roadNode.ojid = jid1
                roadNode.deadend = True
                optGraph.addJunction(op.OptGraphJunction(nID, util.GetPointGeomOfLineGeom(points, -1)))
                optGraph.addRoad(roadNode, jid1, nID)
                nID += 1
            else: # road is a twoway connector
                roadNode.deadend = False
                roadNode.ojid = jid1
                optGraph.addRoad(roadNode, jid1, jid2)
    
    optGraph.listConnections()
    return optGraph

def SaveGraph(graphPath : str, graph : op.OptGraph) -> bool:
    graphDatasource = util.CreateDataSource(graphPath)
    graphLayer = util.CreateLayer(graphDatasource, 'graph', ogr.wkbLineString, {})
    graphHandle = util.CreateFeatureHandle(graphLayer)

    for road in graph.getRoadList():
        pointsGeom = graph.getRoadById(road).points
        pointGeom = ogr.Geometry(ogr.wkbLineString)

        for i in range(0, pointsGeom.GetPointCount()):
            pointGeom.AddPoint(*pointsGeom.GetPoint(i))

        util.CreateFeature(graphHandle, graphLayer, pointGeom)
        # print(road)

    for jid in graph.getJunctionList():
        juncNode = graph.getJunctionById(jid)
        juncPointGeom = juncNode.point.Clone()
        
        for rid in graph.getConnectedRoadIds(jid):
            
            print(jid, 'th junction connected to ', rid, 'th road')
            roadNode = graph.getRoadById(rid)
            roadPointGeomIndex = 0 if roadNode.ojid == jid else -1
            roadPointGeom = util.GetPointGeomOfLineGeom(roadNode.points, roadPointGeomIndex)
            connectorLineGeom = util.MergePointGeoms(juncPointGeom, roadPointGeom)
            util.CreateFeature(graphHandle, graphLayer, connectorLineGeom)

            if jid == 7 and rid == 3:
                print(roadNode.deadend)
    return True                    