# import utility.router as router
# import experimental.raster as raster
# import math

'''
    r = router.Router('data/route/crosses.shp', 'data/route/roads.shp', 'data/route/stops.shp')
    r.indexGraph()
    paths = r.getPath()

    paths.save('data/route/out/route.geojson')
    print('done')
'''

'''
import mysql.connector as mysql
import psycopg2 as pg


pg.connect()

'''

import networkx as nx 
import matplotlib.pyplot as plt 

G = nx.DiGraph()

G.add_weighted_edges_from([(0, 1, 10), (1, 2, 5), (2, 4, 7), (0, 3, 14)])


plt.subplot(111)
nx.draw(G, with_labels=True)
# plt.subplot(122)

# nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

plt.show()


'''
mydb : mysql.Connect = mysql.connect(host="localhost",user="ubombar",passwd="123123",database="test")

mycursor = mydb.cursor()



for i in range(4):
	value = (i, 'Hello Everyone')
	ret = mycursor.execute("INSERT INTO test.test VALUES(%s, %s)", value)
	print('excecuted', ret)
    
mydb.commit()
mydb.close()
'''