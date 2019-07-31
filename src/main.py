from utility.ogrutil import *
from utility.rgraph import *
import utility.router as router

r = router.Router('data/route/crosses.shp', 'data/route/roads.shp')
r.indexGraph()
path = r.getPath(4, 6)

path.save('data/route/out/route.shp')