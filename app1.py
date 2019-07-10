from osgeo import ogr

INTERVAL = 30 # must be bigger that the biggest gap in hours
NAME = 'Ufuk' # ok

def tomin(hour:str):
    spl = hour.split(':')
    ho = int(spl[0])
    mi = int(spl[1])
    if 0 <= ho < 24 and 0 <= mi < 60:
        return ho * 60 + mi
    else:
        raise Exception('Given hour format is illegal')

buckets = [set() for _ in range(1440 // INTERVAL)]

places_datasource = ogr.Open('data/places.geojson', 0)
areas_datasource = ogr.Open('data/areas.geojson', 0)

places_layer = places_datasource.GetLayer()
areas_layer = areas_datasource.GetLayer()

for place in places_layer:
    place_hour = place.GetFieldAsString(1)

    for area in areas_layer:
        area_name = area.GetFieldAsString(0)

        if place.geometry().Intersects(area.geometry()):
            buckets[tomin(place_hour) // INTERVAL].add(area_name)

    areas_layer.ResetReading()
places_layer.ResetReading()

print('Data has processed! Type "q" to exit.')

while True:
    print()
    user_input = input('Enter the hour of the day (HH:MM) ')

    if user_input == 'q':
        break

    probabilities = buckets[tomin(user_input) // INTERVAL]
    length = len(probabilities)

    if length == 1:
        print('> ', NAME, 'is most probably at', probabilities.pop())
    elif length == 0:
        print('> ', NAME, 'is most probably at we dont know')
    else:
        print('> There are couple of places where', NAME, 'can be at; ')

        for name in probabilities:
            print('\t"', name, '"', sep='')
        print()