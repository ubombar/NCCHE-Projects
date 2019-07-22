import ogr
import sys
import collections

class RoadNode:
    def __init__(self, pointGeometry : ogr.Geometry):
        self.point = pointGeometry.Clone()
        self.id = -1
    
    def getAsPointGeometry(self) -> ogr.Geometry:
        return self.point
    
    def getAsPoint(self) -> (float, float):
        return (self.point.GetX(), self.point.GetY())
    
    def __str__(self):
        return 'NODE{} {}'.format(self.id, self.point)
    
    def __repr__(self):
        return self.__str__()

class RoadGraph:
    def __init__(self):
        self.objects = list()
        self.graph = dict()
        self.weights = dict()
    
    def addConnection(self, node1 : int, node2 : int, weight : float = 0) -> bool:
        adj1 : set = self.graph.get(node1)
        adj2 : set = self.graph.get(node2)

        if adj1 is None or adj2 is None:
            return False

        adj1.add(node2)
        adj2.add(node1)

        self.weights[(node1, node2)] = weight
        self.weights[(node2, node1)] = weight
            
        return True
    
    def addNode(self, child : RoadNode) -> int:
        if child.id == -1:
            child.id = len(self.objects)

            self.objects.append(child)
            self.graph[child.id] = set()

            return child.id
        return -1
    
    def getChilds(self, child : int) -> set:
        return self.graph.get(child)
    
    def getNode(self, child : int) -> RoadNode:
        return self.objects[child]

    def isConnected(self, parent : int, child : int) -> bool:
        childs = self.graph.get(parent)

        if childs is None:
            return False

        return child in childs
    
    def exists(self, node : int) -> bool:
        return self.graph.get(node) is not None
    
    def getWeight(self, node1 : int, node2 : int) -> float:
        if self.exists(node1) and self.exists(node2):
            pair = (node1, node2)

            return self.weights.get(pair)
        return 0
    
    def DFS(self, node1 : int, node2 : int) -> list:
        path = list()
        visited = set([node1])
        stack = [node1]
        backward = {}

        while len(stack) != 0:
            node = stack.pop()
            visited.add(node)

            if node == node2:
                p = backward.get(node2)
                path.append(node2)
                while p != node1:
                    p = backward.get(p)
                    path.append(p)
                        
                return path
            
            for child in self.graph.get(node):
                if child not in visited:
                    stack.append(child)
                    backward[child] = node
        return None
    
    def shortestPath(self, node1 : int, node2 : int) -> list:
        path = list()
        visited = set([node1])
        queue = collections.deque([node1])
        backward = {}

        while len(queue) != 0:
            node = queue.pop()
            visited.add(node)

            if node == node2:
                p = backward.get(node2)
                path.append(node2)
                while p != node1:
                    p = backward.get(p)
                    path.append(p)
                        
                return path
            
            for child in self.graph.get(node):
                if child not in visited:
                    queue.appendleft(child)
                    backward[child] = node
        return None
