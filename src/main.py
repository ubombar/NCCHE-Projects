import routetrack as rt
import optimized as g
import npgraph as graph
	

def main(args):
	# predict.PredictPlace()
	# route.MakeRoute(1)
	# kalman.RealTimeFilter(5000)
	g = rt.CreateGraph('data/opt/opt_roads.shp', 'data/opt/optimized_junctions.shp')
	rt.SaveGraph('data/opt/graph.shp', g)

	print(g.bfs(0, 3))

if __name__ == '__main__':
	import sys
	main(sys.argv)