from utility.ogrutil import *
from utility.rgraph import *
import utility.router as router

r = router.Router('data/route/crosses.shp', 'data/route/roads.shp', 'data/route/stops.shp')
r.indexGraph()
paths = r.getPathCollection()

paths.save('data/route/out/route.geosjon')
print('done')