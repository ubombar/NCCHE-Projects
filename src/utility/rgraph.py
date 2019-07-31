'''
    This is a graph
'''
import collections
import heapq

class _SPHeap(object):
    def __init__(self, key=lambda x:x):
        self.len = 0
        self.key = key

        self._data = []

    def __len__(self):
        return self.len

    def __str__(self):
        return 'minheap: {}'.format(self._data)

    def push(self, item):
        self.len += 1
        heapq.heappush(self._data, (self.key(item), item))

    def pop(self):
        self.len -+ 1
        return heapq.heappop(self._data)[1]

class MapperGraph:
    def __init__(self):
        self.relationGraph = {}    # cid : [(cid, rid)] # Holds head connections
        self.crossGraph = {}       # rid : (cid1, cid2) # Holds crosses connections
        self.directedRoads = set() # rid : fromhead? # Holds the directed roads, if yes contains the direction

        self.lastRoadID = 0
        self.lastCrossID = 0

        self.roadObjects = {}  # rid : Road
        self.crossObjects = {} # cid : Cross
    
    def getRoadByCrosses(self, cid1, cid2, getorder=False):
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')

        for cid4, rid4 in self.relationGraph.get(cid1):
            if cid4 != cid2: continue
            if getorder:
                return rid4, self.crossGraph[rid4][0] == cid1
            else:
                return rid4
    
    def roadExists(self, rid) -> bool:
        return self.roadObjects.get(rid) is not None
    
    def crossExists(self, cid) -> bool:
        return self.crossObjects.get(cid) is not None
    
    def addCross(self, cross, idd=None) -> int:
        if idd is None:
            cid = self.lastCrossID
            self.lastCrossID += 1
        else:
            cid = idd

        self.crossObjects[cid] = cross
        self.relationGraph[cid] = set()

    def addRoad(self, road, cid1, cid2, idd=None, directed=False) -> int:
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')
        
        if idd is None:
            rid = self.lastRoadID
            self.lastRoadID += 1
        else:
            rid = idd
    
        self.roadObjects[rid] = road
        self.relationGraph[cid1].add((cid2, rid))
        self.relationGraph[cid2].add((cid1, rid))
        self.crossGraph[rid] = (cid1, cid2)

        if directed:
            self.directedRoads.add(rid)
    
    def getAdjCrosses(self, cid, getrids=False, ignoredirection=False):
        if not self.crossExists(cid):
            raise Exception('Road does not exist')
        
        adjList = []
        combiner = lambda cid, rid: cid if not getrids else (cid, rid)

        for cid2, rid in self.relationGraph.get(cid):
            cidA, _ = self.crossGraph.get(rid)

            if ignoredirection or (not rid in self.directedRoads) or (rid in self.directedRoads and cidA == cid):
                adjList.append(combiner(cid2, rid))
        
        return adjList
    
    def getWeight(self, cid1, cid2) -> float:
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')
        
        if cid1 == cid2:
            return 0

        for cid4, rid4 in self.relationGraph.get(cid1):
            if cid4 != cid2: continue
            
            return abs(self.roadObjects.get(rid4))
    
    def doBFS(self, cid1, cid2, getrids=False, ignoredirection=False):
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')

        if cid1 == cid2:
            return [cid1]

        visited = set()
        queue = collections.deque([(cid1, [])])

        combiner = lambda cid, rid: cid if not getrids else (cid, rid)
        
        while len(queue) != 0:
            cid, path = queue.pop()
            visited.add(cid)

            for cid3, rid in self.getAdjCrosses(cid, True, ignoredirection):
                if cid3 == cid2:
                    return path + [combiner(cid, rid), cid3]
                if cid3 in visited:
                    continue
                queue.appendleft((cid3, path + [combiner(cid, rid)]))
                visited.add(cid3)
        return None

    def doDFS(self, cid1, cid2, getrids=False, ignoredirection=False):
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')

        if cid1 == cid2:
            return [cid1]

        visited = set()
        queue = list([(cid1, [])])

        combiner = lambda cid, rid: cid if not getrids else (cid, rid)
        
        while len(queue) != 0:
            cid, path = queue.pop()
            visited.add(cid)

            for cid3, rid in self.getAdjCrosses(cid, True, ignoredirection):
                if cid3 == cid2:
                    return path + [combiner(cid, rid), cid3]
                if cid3 in visited:
                    continue
                queue.append((cid3, path + [combiner(cid, rid)]))
                visited.add(cid3)
        return None

    def doDijkstra(self, cid1, cid2):
        if not (self.crossExists(cid1) and self.crossExists(cid2)):
            raise Exception('Road does not exist')

        if cid1 == cid2:
            return [cid1]

        visited = set()
        distances = collections.defaultdict(lambda: float('inf'))
        path = list()

        previous = dict()
        heap = _SPHeap(key=lambda x: distances[x])
        distances[cid1] = 0
        heap.push(cid1)
        connectionDict = dict()

        while len(heap) != 0:
            cur = heap.pop()
            visited.add(cur)

            if cur == cid2:
                break
            
            for adj, rid in self.getAdjCrosses(cur, getrids=True):
                if adj in visited:
                    continue
                
                print(distances[cur], '+', (cur, adj))
                ndis = distances[cur] + self.getWeight(cur, adj)

                if ndis < distances[adj]:
                    distances[adj] = ndis
                    heap.push(adj)
                    previous[adj] = cur
                    connectionDict[(adj, cur)] = rid

                    # Do heap flush? no need?
        
        if cid2 in visited:
            p = previous.get(cid2)

            while p != cid1:
                path = [p] + path
                p = previous.get(p)
            
            return [cid1] + path + [cid2], connectionDict
        
        return None