import collections
''' Lets implement a working genric graph class using hashmaps '''

class Node:
    def __init__(self):
        self.id : int = None
        # raise NotImplementedError

class Conn:
    def __init__(self):
        self.id : int = id
        self.undirected : bool = True
        self.start : int = None
        self.stop : int = None
        # raise NotImplementedError

class Graph:
    def __init__(self):
        ''' Creates stuff '''
        self.__mnode = list()
        self.__mconn = list()

        self.__weigthmap = dict() # {nid : [(nid, cid)]}
        self.__connmap = dict()  # {cid : (nid1, nid2, undirected)} 
    
    def _nodechk(self, *nids):
        ''' Checks if node exists in graph '''
        for nid in nids:
            if self.__mnode[nid] is None:
                raise Exception('Node: {}, does not exists'.format(nid))
    
    def _connchk(self, *cids):
        ''' Checks if connection exists in graph '''
        for cid in cids:
            if self.__mconn[cid] is None:
                raise Exception('Connection: {}, does not exists'.format(cid))
    
    def nodes(self) -> list:
        ''' Gets requested '''
        return self.__mnode

    def conns(self) -> list:
        ''' Gets requested '''
        return self.__mconn

    def nids(self) -> range:
        ''' Gets requested '''
        return range(len(self.__mnode))

    def cids(self) -> range:
        ''' Gets requested '''
        return range(len(self.__mconn))
    
    def asNode(self, nid : int) -> Node:
        ''' Gets the object '''
        self._nodechk(nid)
        return self.__mnode[nid]

    def asConn(self, cid : int) -> Conn:
        ''' Gets the object '''
        self._connchk(cid)
        return self.__mconn[cid]

    def addNode(self, node : Node) -> int:
        ''' Adds a node to the graph, returns the id and alters it in the object '''
        node.id = len(self.__mnode)
        self.__mnode.append(node)
        self.__weigthmap[node.id] = list()

        return node.id
    
    def addConn(self, conn : Conn, nid1 : int, nid2 : int, undirected : bool = True) -> int:
        ''' Takes nodeids, adds a connection to the graph, returns the id and alters it in the object '''
        self._nodechk(nid1, nid2)
        
        conn.id = len(self.__mconn)
        conn.undirected = undirected
        conn.start = nid1
        conn.stop = nid2

        self.__mconn.append(conn)
        
        self.__weigthmap[nid1].append((nid2, conn.id))
        self.__connmap[conn.id] = (nid1, nid2, undirected)

        if undirected:
            self.__weigthmap[nid2].append((nid1, conn.id))

        return conn.id
    
    def adjNodes(self, nid : int) -> list():
        ''' Gets the adjacent node ids '''
        self._nodechk(nid)
        return [nid2 for nid2, cid in self.__weigthmap[nid]]
    
    def adjConns(self, nid : int) -> list:
        ''' Gets the adjacent connection ids '''
        self._nodechk(nid)
        return [cid for nid2, cid in self.__weigthmap[nid]]
    
    def delNode(self, nid) -> bool:
        ''' Deletes the node and adj connections '''
        adjcids = self.adjConns(nid)

        for cid in adjcids:
            self.delConn(cid)
        
        self.__mnode[nid] = None
        del self.__weigthmap[nid]

        return True
    
    def delConn(self, cid : int) -> bool:
        ''' Deletes a connection entirely from graph '''
        self._connchk(cid)

        self.__mconn[cid] = None
        nid1, nid2, undir = self.__connmap[cid]

        del self.__connmap[cid]

        rem = None

        for nid3, cid3 in self.__weigthmap[nid1]:
            if cid3 == cid:
                rem = (nid3, cid3)
                break
        
        if rem is None:
            return False

        self.__weigthmap[nid1].remove(rem)
        
        if undir:
            for nid4, cid4 in self.__weigthmap[nid2]:
                if cid4 == cid:
                    rem = (nid4, cid4)
                    break

            if rem is None:
                return False

            self.__weigthmap[nid2].remove(rem)

        return True

    def __str__(self) -> str:

        print(self.__weigthmap)
        print(self.__connmap)
        return ''
    
    def adjConnsOfConn(self, cid : int) -> (list, list, bool):
        ''' Gets a the adj connections of two adjacent nodes '''
        self._connchk(cid)
        nid1, nid2, undir = self.__connmap[cid]

        l1 = self.adjConns(nid1)
        l2 = self.adjConns(nid2)

        return (l1, l2, undir)
    
    def adjNodesOfConn(self, cid : int) -> (int, int, bool):
        ''' Gets the nids and is undirected bool of nodes it is connecting. '''
        self._connchk(cid)

        return self.__connmap.get(cid)
    
    def isNodesAdj(self, nid1 : int, nid2 : int, countdirected : bool = True) -> bool:
        ''' Cheks if two nodes are adjacent, counts outwards going ones if specified '''
        self._nodechk(nid1, nid2)

        for nid3, _ in self.__weigthmap.get(nid1):
            if nid3 == nid2:
                return True

        if countdirected:
            for nid4, _ in self.__weigthmap.get(nid2):
                if nid4 == nid1:
                    return True
        return False
    
    def isNodeConnAdj(self, nid : int, cid : int) -> bool:
        raise NotImplementedError

    def isConnsAdj(self, cid1 : int, cid2 : int) -> bool:
        raise NotImplementedError
    
    def getConn(self, nid1 : int, nid2 : int, countdirected : bool = False) -> int:
        ''' Cheks if two nodes are adjacent, if true returns the connector '''
        self._nodechk(nid1, nid2)

        for nid3, rd in self.__weigthmap.get(nid1):
            if nid3 == nid2:
                return rd

        if countdirected:
            for nid4, rd in self.__weigthmap.get(nid2):
                if nid4 == nid1:
                    return rd
        return None
    
    def bfs(self, nid1 : int, nid2 : int) -> list:
        path = list()
        visited = set([nid1])
        queue = collections.deque([nid1])
        backward = dict()
        
        while len(queue) != 0:
            nid = queue.pop()
            visited.add(nid)

            if nid == nid2:
                p = backward.get(nid2)
                path.append(nid2)

                while p != nid1:
                    p = backward.get(p)
                    path.append(p)
                
                return path
            for adjnid, _ in self.__weigthmap.get(nid):
                if adjnid not in visited:
                    queue.appendleft(adjnid)
                    backward[adjnid] = nid
        return None