inf = float('inf')


# find the node with the least cost
def get_lowest_cost(costs, unvisited):
    least_cost = inf
    least_node = None
    least_index = 0
    for index, node in enumerate(unvisited):
        if costs[node] <= least_cost:
            least_cost = costs[node]
            least_node = node
            least_index = index
    return least_node, least_index


# find the cost and path for all nodes
def dijkstra(costs, g, des, distances):
    unvisited = list(g.keys())
    parents = {}
    least_cost, least_index = \
        get_lowest_cost(costs, unvisited)
    while unvisited:
        for node in g[least_cost]:
            # if node in unvisited:
            cost_from = costs[least_cost]
            cost_from -= distances[least_cost]
            cost_from += g[least_cost][node]
            cost_from += distances[node]
            if costs[node] > cost_from:
                costs[node] = cost_from
                parents[node] = least_cost
        unvisited.pop(least_index)
        least_cost, least_index = get_lowest_cost(
            costs, unvisited)
        if least_cost == des:
            print("Reached des !")
            return parents
    return parents


def get_path(parents, beg, des):
    path = [des]
    last = des
    print('last', last)
    while last != beg:
        print(last)
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
