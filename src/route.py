import util, graph
import ogr

def MakeRoute(config=0, saveGraph=True) -> graph.RoadGraph:
    # declare variables
    roadgraph = graph.RoadGraph()
    endingNodeInfoList = list()

    ALLPOINTS_FIELDS = {'roadname':ogr.OFTString, 'roadfid':ogr.OFTInteger, 'graphid':ogr.OFTInteger}
    BUFFER_RADIUS = 25
    # NEIGBOUR_LIMIT = 3 # maybe next iteration use this to have a better graph maker

    # loading the variables
    roadsDataSource = util.OpenDataSource('data/route/easy_roads.geojson')
    roadsLayer = util.GetLayer(roadsDataSource)

    configDataSource = util.OpenDataSource('data/route/easy_startstop.geojson')
    configLayer = util.GetLayer(configDataSource)

    allpointsDatasource = util.CreateDataSource('data/route/temp/allpoints.shp')
    allpointsLayer = util.CreateLayer(allpointsDatasource, 'allpoints', ogr.wkbPoint, ALLPOINTS_FIELDS)
    allpointsHandle = util.CreateFeatureHandle(allpointsLayer)

    for road in roadsLayer:
        roadGeometry, roadName, roadFID = road.geometry(), road.GetField('name'), road.GetFID()

        for lineGeometry in util.GetGeometryIterator(roadGeometry):

            for pointRoadIndex, pointGeometry in util.GetPointEnumerator(lineGeometry):
                nodeIndex = roadgraph.addNode(graph.RoadNode(pointGeometry))
                util.CreateFeature(allpointsHandle, allpointsLayer, pointGeometry, roadname=roadName, roadfid=roadFID, graphid=nodeIndex)

                if not pointRoadIndex == 0:
                    lastPointGeometry = roadgraph.getNode(nodeIndex - 1).getAsPointGeometry()
                    distance = lastPointGeometry.Distance(pointGeometry)
                    roadgraph.addConnection(nodeIndex, nodeIndex - 1, distance)

                if pointRoadIndex == 0 or pointRoadIndex == lineGeometry.GetPointCount() - 1:
                    endingNodeInfoList.append(
                        (roadFID, 
                        nodeIndex, 
                        pointRoadIndex, 
                        pointRoadIndex == 0))
    roadsLayer.ResetReading()
    allpointsLayer.ResetReading()

    for endingNodeInfo in endingNodeInfoList:
        roadFID, nodeIndex, pointRoadIndex, firstIndex = endingNodeInfo

        pointGeometry = roadgraph.getNode(nodeIndex).getAsPointGeometry()
        pointFilterGeometry = pointGeometry.Buffer(BUFFER_RADIUS)

        roadsLayer.SetSpatialFilter(pointFilterGeometry) # set the spatial filter

        for road in roadsLayer:
            allpointsLayer.SetSpatialFilter(pointFilterGeometry)

            shortestPointGraphID = -1
            shortestPointDistance = 10 * BUFFER_RADIUS

            for point in allpointsLayer:
                pointNodeIndex = point.GetField('graphid')
                distance = pointGeometry.Distance(point.geometry())

                if distance < shortestPointDistance and pointNodeIndex != nodeIndex:
                    shortestPointGraphID = pointNodeIndex
                    shortestPointDistance = distance

            if shortestPointGraphID != -1:
                #print('{} {}'.format(nodeIndex, shortestPointGraphID))
                roadgraph.addConnection(nodeIndex, shortestPointGraphID, shortestPointDistance)

        roadsLayer.ResetReading()
    if saveGraph:
        util.SaveGraphOnFile(roadgraph, 'data/route/temp/graph.shp')
    
    configLayer.SetAttributeFilter('pairid={}'.format(config))
    configGraphIDList = list()

    for configFeature in configLayer:
        allpointsLayer.SetSpatialFilter(configFeature.geometry().Buffer(3 * BUFFER_RADIUS))
        configGraphIDList.append(allpointsLayer.GetNextFeature().GetField('graphid'))
    allpointsLayer.ResetReading()

    print('Preprocessing Done!')

    routeList = list()
    
    for i in range(1, len(configGraphIDList)):
        routeList.append(roadgraph.shortestPath(configGraphIDList[i - 1], configGraphIDList[i]))
    
    util.SaveRoutes(roadgraph, routeList, 'data/route/out/route.geojson')

    print('Shortest Path Founded!')

def MakeOptimizedRoute():
    optRoadsLayer = util.OpenLayerDirectly('~/Documents/qgis/proper road index/test/optimized_roads.shp')
    optJunctLayer = util.OpenLayerDirectly('~/Documents/qgis/proper road index/test/optimized_junctions.shp')

    