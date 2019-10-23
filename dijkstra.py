##inf = float('inf')
##
##
### find the node with the least cost
##def get_lowest_cost(costs, unvisited):
##    least_cost = inf
##    least_node = ""
##    for node in unvisited:
##        print('least cost: ', least_cost, 'least node: ',
##              least_node, 'node checking: ', costs[node])
##        if costs[node] <= least_cost:
##            least_cost = costs[node]
##            least_node = node
##    return least_node
##
##
### find the cost and path for all nodes
##def dijkstra(costs, g):
##    unvisited = g.nodes
##    previus = {}
##    least_cost = get_lowest_cost(costs, unvisited)
##    while unvisited:
##        for node in g.graph[least_cost]:
##            if node in unvisited:
##                if costs[node] > costs[least_cost] + g.graph[least_cost][node]:
##                    costs[node] = costs[least_cost] + g.graph[least_cost][node]
##                    previus[node] = least_cost
##        unvisited.remove(least_cost)
##        least_cost = get_lowest_cost(costs, unvisited)
##    return previus
##
##
##def get_path(previus, beg, des):
##    path = [des]
##    last = des
##    while last != beg:
##        last = previus[last]
##        path.append(last)
##    return path
##
##
##class Graph:
##    def __init__(self, nodes):
##        self.nodes = nodes
##        self.graph = {}
##        for node in nodes:
##            self.graph[node] = {}
##
##    def add_path(self, beg, des, cost):
##        self.graph[beg][des] = cost
##
##
### nodes
##beg = 'a'
##des = 'd'
##nodes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
##
### make graph
##g = Graph(nodes)
##g.add_path('a', 'b', 3)
##g.add_path('a', 'c', 1)
##g.add_path('c', 'd', 5)
##g.add_path('c', 'b', 1)
##g.add_path('b', 'd', 1)
##g.add_path('a', 'e', 1)
##g.add_path('e', 'd', 1)
##
### get costs
##costs = {}
##
##for node in nodes:
##    if node == beg:
##        costs[node] = 0
##    else:
##        costs[node] = inf
##
##
##previus = dijkstra(costs, g)
##print("Costs: ", costs)
##print('Shortest path from ', beg, ' to ', des, ' is: ', get_path(previus, beg, des)[::-1])


import osmgraph



