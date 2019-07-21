from osgeo import ogr

def tomin(hour:str):
    spl = hour.split(':')
    ho = int(spl[0])
    mi = int(spl[1])
    if 0 <= ho < 24 and 0 <= mi < 60:
        return ho * 60 + mi
    else:
        raise Exception('Given hour format is illegal')
    

def PredictPlace(user='Ufuk', interval=30):
    buckets = [set() for _ in range(1440 // interval)]

    places_datasource = ogr.Open('data/predict/places.geojson', 0)
    areas_datasource = ogr.Open('data/predict/areas.geojson', 0)

    places_layer = places_datasource.GetLayer()
    areas_layer = areas_datasource.GetLayer()

    for place in places_layer:
        place_hour = place.GetFieldAsString(1)

        for area in areas_layer:
            area_name = area.GetFieldAsString(0)

            if place.geometry().Intersects(area.geometry()):
                buckets[tomin(place_hour) // interval].add(area_name)

        areas_layer.ResetReading()
    places_layer.ResetReading()

    print('Data has processed! Type "q" to exit.')

    while True:
        print()
        user_input = input('Enter the hour of the day (HH:MM) ')

        if user_input == 'q':
            break

        probabilities = buckets[tomin(user_input) // interval]
        length = len(probabilities)

        if length == 1:
            print('> ', user, 'is most probably at', probabilities.pop())
        elif length == 0:
            print('> ', user, 'is most probably at we dont know')
        else:
            print('> There are couple of places where', user, 'can be at; ')

            for name in probabilities:
                print('\t"', name, '"', sep='')
            print()