from utility.ogrutil import *
from utility.rgraph import *
import utility.router as router

r = router.Router('data/crosses.shp', 'data/roads.shp')
r.indexGraph()
path = r.getPath(4, 6)

path.save('data/out/route.shp')