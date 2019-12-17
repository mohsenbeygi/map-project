from load.loader import Loader
from path.dijkstra2 import *
import library.mplleaflet as mplleaflet
import matplotlib.pyplot as plt


# infinity for routing
inf = float('inf')


class Router:
    def __init__(self, transport):
        self.transport = transport
        self.data = Loader("car", read=True)
        self.data.read("./maps/map_graph1.json")
        print('reading done !')
        # print(self.data.distances)


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

    def get_costs(self, start):
        # create costs data structure
        costs = {}
        for node in self.data.rnodes:
            if node == start:
                costs[node] = 0
            else:
                costs[node] = inf
        return costs

    def find_path(self, node1, node2):
        # find the closests node to the
        # given latitude and longitude
        self.data.get_distances(node2)
        node1 = self.data.findNode(*node1)
        node2 = self.data.findNode(*node2)

        # print(data.rnodes[node1])
        # print(data.rnodes[node2])

        ''' dijkstra routing '''
        # # create costs data structure
        # costs = self.get_costs(node1)
        # # print(self.data.routing['2170382002'])
        # parents = dijkstra(costs,
        #                    self.data.routing,
        #                    node2,
        #                    self.data.distances)



        ''' dijkstra2 routing '''
        parents = dijkstra(self.data.routing,
                           node1,
                           sink=node2)

        # get path from node1 to node2
        path = get_path(parents, node1, node2)[::-1]

        # print('Shortest path from ', node1,
        #       ' to ', node2, ' is: ', path)

        self.display_path(path, node1, node2)



if __name__ == '__main__':
    # enter latitude and longitude for
    # the start and destination positions
    node1 = (35.80367469044131, 51.438760757446296)
    node2 = (35.79971568830117, 51.4386534690857)

    ''' get start and end from user '''

    # node1 = tuple(map(float,
    #     input("Beginning:  ").split(',')))
    # node2 = tuple(map(float,
    #     input("Destination:  ").split(',')))


    # create router object with specific transport type
    router = Router("car")

    # find path and display path on map
    router.find_path(node1, node2)


