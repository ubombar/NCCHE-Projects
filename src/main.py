import utility.router as router

r = router.Router('data/route/crosses.shp', 'data/route/roads.shp', 'data/route/stops.shp')
r.indexGraph()
paths = r.getPathCollection()

paths.save('data/route/out/route.geojson')
print('done')