from load.map import Map
from path.dijkstra2 import *
import library.mplleaflet as mplleaflet
import matplotlib.pyplot as plt


# infinity for routing
inf = float('inf')


class Router:
    def __init__(self, transport):
        self.transport = transport
        # self.map = Map("car")
        self.map = Map("car", read=True)
        self.map.read("./maps/map_graph1.json")
        # print(self.map.distances)

    def display_path(self, path, node1, node2):
        # showing on map with mplleaflet library
        lons = []
        lats = []
        for i in path:
            node = self.map.node_cords[i]
            lats.append(node[0])
            lons.append(node[1])
        fig = plt.figure()
        plt.plot(lons, lats, color="purple",
                 linewidth=10)
        # draw red square for start of path
        plt.plot([self.map.node_cords[node1][1]],
                 [self.map.node_cords[node1][0]],
                 "rs")
        # draw red square for end of path
        plt.plot([self.map.node_cords[node2][1]],
                 [self.map.node_cords[node2][0]],
                 "rs")
        mplleaflet.show(fig=fig)

    def get_costs(self, start):
        # create costs data structure
        costs = {}
        for node in self.map.node_cords:
            if node == start:
                costs[node] = 0
            else:
                costs[node] = inf
        return costs

    def find_path(self, node1, node2):
        # find the closests node to the
        # given latitude and longitude
        self.map.get_distances(node2)
        node1 = self.map.findNode(*node1)
        node2 = self.map.findNode(*node2)

        # print(self.map.node_cords[node1])
        # print(self.map.node_cords[node2])

        ''' dijkstra routing '''
        # # create costs data structure
        # costs = self.get_costs(node1)
        # # print(self.map.graph['2170382002'])
        # parents = dijkstra(costs,
        #                    self.map.graph,
        #                    node2,
        #                    self.map.distances)



        ''' dijkstra2 routing '''
        parents = dijkstra(self.map.graph,
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
    # node2 = (35.79971568830117, 51.4386534690857)
    node2 = (35.801312188809185, 51.43841207027436)

    '''
    get start and end from user
    '''

    # node1 = tuple(map(float,
    #     input("Beginning:  ").split(',')))
    # node2 = tuple(map(float,
    #     input("Destination:  ").split(',')))


    # create router object with specific transport type
    router = Router("car")

    # find path and display path on map
    router.find_path(node1, node2)


