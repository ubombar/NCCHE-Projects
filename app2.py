import ogr
import os

def calculate_crossing_paths(road_filename = 'data/app2/olemiss/roads.shp', roadintersections_filename = 'data/app2/olemiss/rint.shp', driver_name = 'ESRI Shapefile'):
    '''
        This function takes the road layer and computes the crossings of roads in a relational way. Crossings are
        marked on map and intialized with attributes denoting which roads are crossing.

        For showing direction function marks each crossing twice.

        Fields of the output file:
            "id"     : FID of the marking
            "name1"  : Name of the first road
            "name2"  : Name of the second road
            geometry : POINT
        
        Required fields of input file:
            "id"     : FID for easy use
            "name"   : Name of the road
            geometry : LINE
    '''

    driver = ogr.GetDriverByName(driver_name)

    if os.path.exists(roadintersections_filename):
        driver.DeleteDataSource(roadintersections_filename)

    roadintersections_ds = driver.CreateDataSource(roadintersections_filename)
    road_ds = ogr.Open(road_filename, 0)

    road_layer = road_ds.GetLayer()

    # creates a layer with the same spatial reference system
    roadintersections_layer = roadintersections_ds.CreateLayer('connections', road_layer.GetSpatialRef(), ogr.wkbPoint)

    # create fields
    roadintersections_layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    roadintersections_layer.CreateField(ogr.FieldDefn('name1', ogr.OFTString))
    roadintersections_layer.CreateField(ogr.FieldDefn('name2', ogr.OFTString))

    road_list = [road for road in road_layer]

    roadintersections_layer.ResetReading()

    temp_feature = ogr.Feature(roadintersections_layer.GetLayerDefn())

    n = 0

    for road_one in road_list:
        for road_two in road_list:
            if road_one is not road_two and road_one.geometry().Intersects(road_two.geometry()):
                # print(road_one.GetField('name'), 'crosses', road_two.GetField('name'))

                temp_feature.SetField('id', n)
                temp_feature.SetField('name1', road_one.GetField('name'))
                temp_feature.SetField('name2', road_two.GetField('name'))

                section = road_one.geometry().Intersection(road_two.geometry())

                if section.GetGeometryType() == ogr.wkbMultiPoint:
                    section = section.GetGeometryRef(0).Clone()

                temp_feature.SetGeometry(section)

                roadintersections_layer.CreateFeature(temp_feature)
                n += 1

    del roadintersections_ds

    print('Computation complete!')
    print('There are', n, 'intersections')
