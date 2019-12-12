from loader import Loader
from dijkstra import *
import mplleaflet
import matplotlib.pyplot as plt


# infinity for routing
inf = float('inf')


class Router:
    def __init__(self, transport):
        self.transport = transport
        self.data = Loader("car")

    def get_costs(self, start):
        costs = {}
        for node in self.data.routing:
            if node == start:
                costs[node] = 0
            else:
                costs[node] = inf
        return costs


    def display_path(self, path, node1, node2):
        # showing on map with mplleaflet library
        lons = []
        lats = []
        for i in path:
            node = self.data.rnodes[i]
            lats.append(node[0])
            lons.append(node[1])
        fig = plt.figure()
        plt.plot(lons, lats, color="purple", linewidth=10)
        # draw red square for start of path
        plt.plot([self.data.rnodes[node1][1]],
                 [self.data.rnodes[node1][0]], "rs")
        # draw red square for end of path
        plt.plot([self.data.rnodes[node2][1]],
                 [self.data.rnodes[node2][0]], "rs")
        mplleaflet.show(fig=fig)

    def find_path(self, node1, node2):
        # find the closests node to the
        # given latitude and longitude
        node1 = self.data.findNode(*node1)
        node2 = self.data.findNode(*node2)

        # print(data.rnodes[node1])
        # print(data.rnodes[node2])

        # create costs data structure
        costs = self.get_costs(node1)
        # find path from node1 to all nodes
        parents = dijkstra(costs, self.data.routing)
        # get path from node1 to node2
        # print(parents[node1])
        path = get_path(parents, node1, node2)[::-1]

        # print('Shortest path from ', node1,
        #       ' to ', node2, ' is: ', route)

        self.display_path(path, node1, node2)



if __name__ == '__main__':

    # create router object with specific transport type
    router = Router("car")

    # enter latitude and longitude for
    # the start and destination positions
    node1 = (35.80521454717427, 51.43798828125)
    node2 = (35.79745295182983, 51.43717288970948)

    # find path and display path on map
    router.find_path(node1, node2)


