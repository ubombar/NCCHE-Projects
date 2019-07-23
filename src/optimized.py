'''
    This file contains the optimized graph for mapping. 
'''
import ogr


class OptGraphJunction:
    def __init__(self, id : int, point : ogr.Geometry):
        self.id = id
        self.point = point.Clone()

class OptGraphRoad:
    def __init__(self, id : int, oneway : bool, speedlimit : int, size : int, length : float, deadend : bool, points : ogr.Geometry):
        self.id = id
        self.oneway = oneway
        self.speedlimit = speedlimit
        self.size = size
        self.length = length
        self.deadend = deadend
        self.points = points.Clone()
        self.ojid = None

class OptGraph:
    '''
        Optimized Graph. A weigthed graph for map calculation.
        Creation must be in order. Junctions first roads after.
        In ohter words nodes first connections after.
    '''

    def __init__(self):
        self.__roads = dict() # map rid : Object
        self.__junct = dict() # map jid : Object

        self.__rDict = dict() # map jid : adj jids

        self.__wDict = dict() # map (jid1, jid2) : rid
        self.__wRDict = dict() # map rid : (jid1, jid2)
    
    def getJuntionsByRoadId(self, rid : int) -> (int, int):
        return self.__wRDict.get(rid)
    
    def getJunctionById(self, jid : int) -> OptGraphJunction:
        return self.__junct.get(jid)
    
    def getRoadById(self, rid : int) -> OptGraphRoad:
        return self.__roads.get(rid)
    
    def getJunctionList(self) -> list:
        return self.__junct.keys()
    
    def getRoadList(self) -> list:
        return self.__roads
    
    def junctionExists(self, jid : int) -> bool:
        return self.getJunctionById(jid) is not None
    
    def roadExists(self, rid : int) -> bool:
        return self.getRoadById(rid) is not None

    def addJunction(self, junction : OptGraphJunction) -> bool:
        if self.junctionExists(junction.id):
            return False

        self.__junct[junction.id] = junction
        self.__rDict[junction.id] = list()
        
        return True
    
    def addRoad(self, road : OptGraphRoad, jid1 : int, jid2 : int) -> bool:
        if (self.roadExists(road.id)) or (not self.junctionExists(jid1)) or (not self.junctionExists(jid2)):
            return False
        
        # add to the road list
        self.__roads[road.id] = road
        
        # add the first way to roads
        if self.__rDict.get(jid1) is None:
            self.__rDict[jid1] = list()
        self.__rDict[jid1].append(jid2)
        self.__wDict[(jid1, jid2)] = road.id

        # add the reverse way if two way
        if not road.oneway:
            if self.__rDict.get(jid2) is None:
                self.__rDict[jid2] = list()
            self.__rDict[jid2].append(jid1)
            self.__wDict[(jid2, jid1)] = road.id
        
        # also add to the weight reverse dict
        self.__wRDict[road.id] = (jid1, jid2)

        return True
    
    def getConnectedJunctionIds(self, jid : int) -> list:
        return self.__rDict.get(jid)
    
    def getConnectedRoadIds(self, jid : int, getOneWays : bool = False) -> list:
        if not self.junctionExists(jid):
            return list()

        roads = list()
        for jid2 in self.__rDict.get(jid):
            connectionRoad = self.__wDict.get((jid, jid2))

            if getOneWays and connectionRoad is None:
                connectionRoad = self.__wDict.get((jid2, jid))
            
            roads.append(connectionRoad)
        return roads


    
    def DFS(self, jid1 : int, jid2 : int):
        path = list()
        visited = set([jid1])
        stack = [jid1]
        backward = {}

        while len(stack) != 0:
            node = stack.pop()
            visited.add(node)

            if node == jid2:
                p = backward.get(jid2)
                path.append(jid2)
                
                while p != jid1:
                    p = backward.get(p)
                    path.append(p)
                        
                return path
            
            for child in self.getConnectedJunctionIds(node):
                if child not in visited:
                    stack.append(child)
                    backward[child] = node
        return None
    
    def listConnections(self):
        print('listing: ', len(self.__wDict))
        for conn in self.__wDict.items():
            print(conn)
    
    

