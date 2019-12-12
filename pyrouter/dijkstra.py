inf = float('inf')


# find the node with the least cost
def get_lowest_cost(costs, unvisited):
    least_cost = inf
    least_node = None
    for node in unvisited:
        if costs[node] <= least_cost:
            least_cost = costs[node]
            least_node = node
    return least_node


# find the cost and path for all nodes
def dijkstra(costs, g):
    unvisited = list(g.keys())
    parents = {}
    least_cost = get_lowest_cost(costs, unvisited)
    while unvisited:
        for node in g[least_cost]:
            if node in unvisited:
                cost_from = costs[least_cost] + \
                    g[least_cost][node]
                if costs[node] > cost_from:
                    costs[node] = cost_from
                    parents[node] = least_cost
        unvisited.remove(least_cost)
        least_cost = get_lowest_cost(costs, unvisited)
    return parents


def get_path(parents, beg, des):
    path = [des]
    last = des
    while last != beg:
        last = parents[last]
        path.append(last)
    return path


class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
        self.graph = {}
        for node in nodes:
            self.graph[node] = {}

    def add_path(self, beg, des, cost):
        self.graph[beg][des] = cost


if __name__ == '__main__':
        # nodes
        beg = 'a'
        des = 'd'
        nodes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # make graph
        g = Graph(nodes)
        g.add_path('a', 'b', 3)
        g.add_path('a', 'c', 1)
        g.add_path('c', 'd', 5)
        g.add_path('c', 'b', 1)
        g.add_path('b', 'd', 1)
        g.add_path('a', 'e', 1)
        g.add_path('e', 'd', 1)

        # create costs data structure
        costs = {}
        for node in nodes:
            if node == beg:
                costs[node] = 0
            else:
                costs[node] = inf

        # find path
        parents = dijkstra(costs, g)
        print("Costs: ", costs)
        print('Shortest path from ', beg, ' to ', des,
              ' is: ', get_path(parents, beg, des)[::-1])
