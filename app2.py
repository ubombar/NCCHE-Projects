import util
import ogr

def CalculateRoute(roadsName:str, binsName:str, configName:str, configuration:int) -> None:
    '''
        Calculates the most officient route among the containers. The input file specifications are given.
        Imortant notice that input files ahould be in spatial reference system "WGS 84 / Pseudo-Mercator" (EPSG-3857)
        
        Road File
            Geometry    : Line (MultiLineString)
            Fields      : name:str
        
        Bins File
            Geometry    : Point
            Fields      : full:int name:str

        Config File
            Geometry    : Point
            Fields      : name:str startpoint:str{true/false} pairid:int
        
        The output files are given, all output files are located in out directory.

        Intersection File:
            Geometry    : Point
            Fields      : name1:str name2:str
        
        Attached Bin File
            Geometry    : Point
            Fields      : binname:str roadname:str index:int

        Route File
            Geometry    : Line (MultiLineString)
            Fields      : length:real

    '''

    # Initialize the output file names
    nbinsName               = 'data/app2/olemiss/out/newbins.shp'
    crossesName             = 'data/app2/olemiss/out/crosses.shp'
    routeName               = 'data/app2/olemiss/out/route.shp'

    # Create DataSource objects for output files
    nbinsDS                 = util.CreateDataSource(nbinsName)
    crossesDS               = util.CreateDataSource(crossesName)
    routeDS                 = util.CreateDataSource(routeName)

    # Create layers
    nbinsLayer              = util.CreateLayer(nbinsDS, 'newbins', ogr.wkbPoint,    
                                binname=ogr.OFTString,  
                                roadname=ogr.OFTString, 
                                index=ogr.OFTInteger)
    crossesLayer            = util.CreateLayer(crossesDS, 'crosses', ogr.wkbPoint,  
                                name1=ogr.OFTString, 
                                name2=ogr.OFTString)
    routeLayer              = util.CreateLayer(routeDS, 'route', ogr.wkbLineString, 
                                length=ogr.OFTReal)

    # After creating the layers load the existing datasources
    roadsDS                 = util.OpenDataSource(roadsName)
    binsDS                  = util.OpenDataSource(binsName)
    configDS                = util.OpenDataSource(configName)

    # And layers
    roadsLayer : ogr.Layer  = roadsDS.GetLayer()
    binsLayer : ogr.Layer   = binsDS.GetLayer()
    configLayer : ogr.Layer = configDS.GetLayer()

    # First misson is to calculate the crossings
    roadList = [road for road in roadsLayer]

    roadsLayer.ResetReading()

    crossHandle = util.CreateFeatureHandle(crossesLayer)

    for roadOne in roadList:
        for roadTwo in roadList:
            if roadOne is not roadTwo and roadOne.geometry().Intersects(roadTwo.geometry()):
                crossGeometry : ogr.Geometry = roadOne.geometry().Intersection(roadTwo.geometry())
                crossGeometries = list()

                name1 = roadOne.GetField('name')
                name2 = roadTwo.GetField('name')

                if crossGeometry.GetGeometryType() == ogr.wkbMultiPoint:
                    for i in range(crossGeometry.GetGeometryCount()):
                        crossGeometries.append(crossGeometry.GetGeometryRef(i).Clone())
                else:
                    crossGeometries.append(crossGeometry)
                
                for crosses in crossGeometries:
                    util.CreateFeature(crossHandle, crossesLayer, crosses, 
                        name1=name1, 
                        name2=name2)
    # Done calculation!


    # Second misson is to calculate the points which containers are close to
    nbinHandle = util.CreateFeatureHandle(nbinsLayer)

    for binn in binsLayer:
        binnPoint = binn.geometry().GetX(), binn.geometry().GetY()
        RECT_HALF = 100.000
        x, y = binnPoint

        roadsLayer.SetSpatialFilterRect(x - RECT_HALF, y - RECT_HALF, x + RECT_HALF, y + RECT_HALF)

        closestRoadPoint = None
        closestDistanceSquare = RECT_HALF ** 2
        closestRoadPointIndex = 0
        closestRoadName = ''
        
        for road in roadList:
            for i, roadPoint in enumerate(road.geometry().GetPoints()):
                distance = __distance_square(roadPoint, binnPoint)

                if closestDistanceSquare > distance:
                    closestDistanceSquare = distance
                    closestRoadPoint = roadPoint
                    closestRoadPointIndex = i
                    closestRoadName = road.GetField('name')

        if closestRoadPoint is None:
            raise Exception('Cannot find a route to the container! Maybe to far away from any road?')
    
        rx, ry = closestRoadPoint
        closestRoadGeometry = ogr.CreateGeometryFromWkt("POINT ({} {})".format(rx, ry))
        util.CreateFeature(nbinHandle, nbinsLayer, closestRoadGeometry, 
            binname=binn.GetField('name'), 
            roadname=closestRoadName, 
            index=closestRoadPointIndex)



def __distance_square(point1 : (float, float), point2 : (float, float)) -> float:
    return (point1[1] - point2[1]) ** 2 + (point1[0] - point2[0]) ** 2