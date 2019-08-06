import utility.router as router
import experimental.raster as raster
import math

r = router.Router('data/route/crosses.shp', 'data/route/roads.shp', 'data/route/stops.shp')
r.indexGraph()
paths = r.getPathCollection()

paths.save('data/route/out/route.geojson')
print('done')