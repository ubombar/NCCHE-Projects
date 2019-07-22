'''
    This file contains the optimized graph for mapping. 
'''

class OptGraphJunction:
    def __init__(self, id : int):
        self.id = id

class OptGraphRoad:
    def __init__(self, id : int, oneway : bool, speedlimit : int, size : int, length : float, deadend : bool, points : list):
        self.id = id
        self.oneway = oneway
        self.speedlimit = speedlimit
        self.size = size
        self.length = length
        self.deadend = deadend
        self.points = points

class OptGraph:
    '''
        Optimized Graph. A weigthed graph for map calculation.
        Creation must be in order. Junctions first roads after.
        In ohter words nodes first connections after.
    '''

    def __init__(self):
        self.__roads = dict()
        self.__roadjunct = dict()
        self.__junct = dict()
        self.__realtion = dict()
        self.__weights = dict()
    
    def getJunctionById(self, jid : int) -> OptGraphJunction:
        return self.__junct.get(jid)
    
    def getRoadById(self, rid : int) -> OptGraphRoad:
        return self.__roads.get(rid)
    
    def addJunction(self, junction : OptGraphJunction) -> bool:
        if self.__junct.get(junction.id) is not None:
            return False
        
        self.__junct[junction.id] = junction
        self.__realtion[junction.id] = list()
        return True
    
    def addRoad(self, road : OptGraphRoad, jid1 : int, jid2 : int) -> bool:
        if self.__roads.get(road.id) is not None:
            return False

        self.__roads[road.id] = road
        self.__roadjunct[road.id] = (jid1, jid2)
        self.__realtion.get(jid1).append(jid2)

        if not road.oneway:
            self.__roadjunct[road.id] = (jid2, jid1)
            self.__realtion.get(jid2).append(jid1)
        return True
    
    def junctionExists(self, jid : int) -> bool:
        return self.__junct.get(jid) is not None
    
    def getConnectedJunctionIds(self, jid : int) -> list:
        return self.__realtion.get(jid)
    
    def isJunctionsConnected(self, jid1 : int, jid2 : int) -> bool:
        return jid2 in self.getConnectedJunctionIds(jid1)
    
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
    
    

