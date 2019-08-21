import numpy as np 
import collections as col 
import heapq
import matplotlib.pyplot as plt

class AStarGraph(object):
    def __init__(self, shape=(10, 10), obstacles=set([1])):
        self.field = np.zeros(shape, dtype=np.int8)
        self.obstacles = obstacles
    
    @staticmethod
    def distance(a, b):
        ax, ay = a
        bx, by = b 
        return np.sqrt((ax - bx)**2 + (ay - by)**2)

    def adjacents(self, cur, boxsize=1):
        row, col = self.field.shape
        cx, cy = cur
        possible = []

        for i in range(-boxsize, boxsize + 1):
            for j in range(-boxsize, boxsize + 1):
                nx, ny = cx + i, cy + j

                if 0 > nx or nx >= col or 0 > ny or ny >= row or self.field[ny, nx] in self.obstacles: # or abs(i) == abs(j):
                    continue
                
                if i == j == 0:
                    continue

                possible.append((nx, ny))
        return possible
    
    def find(self, s, t, heuristic=None, marker=None):
        if heuristic is None: heuristic = AStarGraph.distance

        visited = set()
        distance = col.defaultdict(lambda: float('inf'))
        heap = []
        previous = dict()
        
        distance[s] = 0
        heapq.heappush(heap, (distance[s], s))

        while len(heap) != 0:
            dis, current = heapq.heappop(heap)
            visited.add(current)

            if current == t:
                break

            for adjacent in self.adjacents(current):
                if adjacent in visited: continue

                newdistance = dis + heuristic(current, adjacent) + heuristic(current, t)

                if distance[adjacent] > newdistance:
                    distance[adjacent] = newdistance
                    heapq.heappush(heap, (distance[adjacent], adjacent))
                    previous[adjacent] = current
        
        if t in visited:
            path = list()
            p = previous[t]

            while p != s:
                path = [p] + path
                p = previous[p]
            
            path = [s] + path + [t]

            if marker is not None:
                A = np.zeros(self.field.shape)
                for x, y in path:
                    A[y, x] = marker
                return path, A
            
            return path

        return None

graph = AStarGraph((151, 151))

for i in range(0, 150):
    graph.field[150-i, 80] = 1

path, A = graph.find((0, 150), (150, 150), marker=9)

plt.imshow(A)
plt.show()