from load.loader import Loader
from path.dijkstra import *
import mplleaflet
import matplotlib.pyplot as plt


# infinity for routing
inf = float('inf')


class Router:
    def __init__(self, transport):
        self.transport = transport
        self.data = Loader("car", read=True)
        self.data.read("./maps/map_graph.json")
        # self.data.get_distances(des_pos)
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

    def find_path(self, node1, node2):
        # find the closests node to the
        # given latitude and longitude
        node1 = self.data.findNode(*node1)
        node2 = self.data.findNode(*node2)

        # print(data.rnodes[node1])
        # print(data.rnodes[node2])

        # create costs data structure
        # costs = self.get_costs(node1)
        # find path from node1 to all nodes
        parents = dijkstra(self.data.routing,
                           node1,
                           sink = node2)
                           # self.data.distances)
        # get path from node1 to node2
        # print(parents[node1])
        path = get_path(parents, node1, node2)[::-1]

        # print('Shortest path from ', node1,
        #       ' to ', node2, ' is: ', route)

        self.display_path(path, node1, node2)



if __name__ == '__main__':

    # enter latitude and longitude for
    # the start and destination positions
    node1 = (35.803478935319305, 51.439270377159126)
    node2 = (35.78560464806688, 51.44317030906678)
    # node1 = tuple(map(float,
    #     input("Beginning:  ").split(',')))
    # node2 = tuple(map(float,
    #     input("Destination:  ").split(',')))

    # create router object with specific transport type
    router = Router("car")

    # find path and display path on map
    router.find_path(node1, node2)


