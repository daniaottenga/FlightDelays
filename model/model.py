import copy

import networkx as nx
from networkx.algorithms.components import node_connected_component

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.Graph() # semplice non orientato e pesato
        self._airports = DAO.getAllAirports()
        self._idMapAirports = {}
        for a in self._airports:
            self._idMapAirports[a.ID] = a


    def buildGraph(self, nMin):
        nodes = DAO.getAllNodes(nMin, self._idMapAirports)
        self._graph.add_nodes_from(nodes)
        print(f"Nodi: {len(self._graph.nodes)}, archi: {len(self._graph.edges)}")
        self.addEdges()
        print(f"Nodi: {len(self._graph.nodes)}, archi: {len(self._graph.edges)}")
        self._graph.clear_edges()
        self.addEdgesV2()


    def addEdges(self):
        allTratte = DAO.getAllEdgesV1(self._idMapAirports)

        for t in allTratte:
            if t.aeroportoP in self._graph and t.aeroportoA in self._graph:
                # se avevo già inserito i nodi vado solo ad aggiungere il peso
                if self._graph.has_edge(t.aeroportoP, t.aeroportoA):
                    self._graph[t.aeroportoP][t.aeroportoA]['weight'] += t.peso
                else:
                    self._graph.add_edge(t.aeroportoP, t.aeroportoA, weight = t.peso)


    def addEdgesV2(self):
        allTratte = DAO.getAllEdgesV2(self._idMapAirports)

        for t in allTratte:
            if t.aeroportoP in self._graph and t.aeroportoA in self._graph:
                self._graph.add_edge(t.aeroportoP, t.aeroportoA, weight=t.peso)


    def getGraphDetails(self):
        return len(self._graph.nodes), len(self._graph.edges)


    def getAllNodes(self):
        nodes = list(self._graph.nodes)
        nodes.sort(key=lambda x: x.IATA_CODE)
        return nodes


    def getViciniOrdinati(self, source):
        # restituisce i vicini di source ordinati per peso del'arco che li collega a source
        vicini = self._graph.neighbors(source) # mi restituisce i vicini del nodo source
        viciniT = []
        for v in vicini:
            viciniT.append((v, self._graph[source][v]['weight'])) # avrò una tupla (nodo peso)
        viciniT.sort(key=lambda x: x[1], reverse = True)
        return viciniT


    def hasPath(self, v0, v1):
        # restituisce true se un qualche cammino tra v0 e v1 esiste altrimenti false
        # calcolo la componente connessa del nodo v0 e vedo se è presente v1
        return v1 in nx.node_connected_component(self._graph, v0) # gli dò il grafo e il nodo di partenza
        #nx.connected_components() # questo mi ddà la lista delle componenti connesse


    def getPath(self, v0, v1):
        #dictOfPredecessors = dict(nx.bfs_predecessors(self._graph, v0)) # esplorazione breath first
        # è un dizionario che per ogni nodo (chiave) mapperà al nodo da cui sono arrivato e mi dice il nodo
        # precedente nell'albero di visita (valore)
        #path = [v1]
        #while path[0] != v0:
        #    path.insert(0, dictOfPredecessors[path[0]])
        # path = [v0, ---, v1]
        # breath first esplora in profondità quindi avrò percorsi molto lunghi

        #v2
        #path = nx.shortest_path(v0, v1)

        #v3 (migliore)
        path = nx.dijkstra_path(self._graph, v0, v1, weight = None)

        #v4
        #dictOfPredecessors = dict(nx.dfs_predecessors(self._graph, v0)) # esplorazione deapth first
        #path = [v1]
        #while path[0] != v0:
        #    path.insert(0, dictOfPredecessors[path[0]])

        return path


    def getCamminoOttimo(self, v0, v1, t): # dove t è il numero massimo di tratte percorribili
        self._bestCammino = []
        self._bestScore = 0
        parziale = [v0]

        self._ricorsione(parziale, v1, t)
        return self._bestCammino, self._bestScore


    def _ricorsione(self, parziale, v1, t):
        # verifico se parziale è una soluzione valida e in caso la salvo
        if parziale[-1] == v1: # se sono arrivato alla destinazione
            if self._getScore(parziale) > self._bestScore:
                self._bestCammino = copy.deepcopy(parziale)
                self._bestScore = self._getScore(parziale)

        # verifico se ha senso continuare ad aggiungere elementi in parziale, oppure esco
        if len(parziale) == t+1: # parziale ha raggiunto il numero massimo di tratte
            return

        # se non sono uscito faccio ricorsione con backtracking
        for n in self._graph.neighbors(parziale[-1]): # ciclo sui vicini dell'ultimo aggiunto
            # e lo aggiungo se non è già stato aggiunto
            if n not in parziale:
                parziale.append(n)
                self._ricorsione(parziale, v1, t)
                parziale.pop()


    def _getScore(self, parziale):
        sumPesi = 0
        for i in range(0, len(parziale)-1):
            sumPesi += self._graph[parziale[i]][parziale[i+1]]['weight']
        return sumPesi
