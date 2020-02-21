from map import Map
from path.dijkstra2 import *
import mplleaflet
import matplotlib.pyplot as plt
from read_cords import *
import os
import subprocess


# infinity for routing
inf = float('inf')

# file directories
file_map = "./maps/map_graph.json"
file_pathfinding = "./find_path.out"
file_webcords = "cords.txt"
file_cords = "cords.txt"
file_path = "./path.txt"

transport = "car"


class Router:
    def __init__(self, transport):
        self.transport = transport
        # self.map = Map("car")
        self.map = Map("car", read=True)
        self.map.read(file_map)

    def display_path(self, path, node1, node2):
        # showing on map with mplleaflet library
        print("displaying path ...")
        lons = []
        lats = []
        for i in path:
            node = self.map.node_cords[i]
            lats.append(node[0])
            lons.append(node[1])
        fig = plt.figure()
        plt.plot(lons, lats, color="purple",
                 linewidth=10)
        # draw green circle for start of path
        plt.plot([self.map.node_cords[node1][1]],
                 [self.map.node_cords[node1][0]],
                 "go", markersize=12)
        # draw red circle for end of path
        plt.plot([self.map.node_cords[node2][1]],
                 [self.map.node_cords[node2][0]],
                 "ro", markersize=12)
        mplleaflet.show(fig=fig)

        print("displaying path done !")

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
        node1 = self.map.find_node(*node1)
        node2 = self.map.find_node(*node2)
        print("node1:", node1, "  node2:", node2)
        # find nodes in graph made for routing
        node1 = self.map.find_graph_node(str(node1))
        node2 = self.map.find_graph_node(str(node2))
        print("node1:", node1, "  node2:", node2)
        print("start and destination nodes found !")
        print("starting pathfinding ...")


        if node1 == node2:
            raise ValueError("start and \
                destination are equal !")
            return

        ''' dijkstra routing (without fibonacci heap)'''

        # # create costs data structure
        # costs = self.get_costs(node1)
        # parents = dijkstra(costs,
        #                    self.map.routing_graph,
        #                    node2,
        #                    self.map.distances)

        ''' dijkstra2 routing (with fibonacci heap)'''

        parents = dijkstra(self.map.routing_graph,
                           node1,
                           self.map.distances,
                           sink=node2
                           )

        # get path from node1 to node2
        path = get_path(parents, node1, node2)[::-1]
        # print('Shortest path from ', node1,
        #       ' to ', node2, ' is: ', path)

        print("pathfinding done !")

        self.display_path(path, node1, node2)

    def cpp_find_path(self, node1, node2, file_pathfinding, file_nodes, file_path):
        print(
            "writing node cordinations for pathfinding (c++ file) ..."
            )
        self.write_node_cords(node1, node2, file_nodes)
        print(
            "writing node cordinations for pathfinding (c++ file) done!"
            )

        print("starting pathfinding (running c++ file) ...")
        self.run_file(file_pathfinding)
        print("pathfinding (running c++ file) done!")

        print("reading path from file (c++ file output) ...")
        path = self.read_path(file_path)
        print("reading path from file (c++ file output) done!")

        self.display_path(path, path[0], path[-1])

    def write_node_cords(self, node1, node2, filename):
        # find the closests node to the
        # given latitude and longitude
        self.map.get_distances(node2)
        node1 = self.map.find_node(*node1)
        node2 = self.map.find_node(*node2)
        print("node1:", node1, "  node2:", node2)
        # find nodes in graph made for routing

        # ** commented below code **

        # node1 = self.map.find_graph_node(str(node1))
        # node2 = self.map.find_graph_node(str(node2))
        # print("node1:", node1, "  node2:", node2)

        node_1 = self.map.node_indexes[node1]
        node_2 = self.map.node_indexes[node2]
        print("node1:", node_1, "  node2:", node_2)

        with open(filename, "w") as file:
            file.write("{}\n{}".format(node_1, node_2))

    def read_path(self, filename):
        print("reading path from file ...")
        with open(filename, "r") as file:
            path = file.readline()
            path = path.strip()
            path = list(map(str, path.split()))

        for index, node in enumerate(path):
            node = self.map.indexes_to_nodes[node]
            path[index] = node
        path = path[::-1]

        print("reading path from file done!")

        return path

    def run_file(self, filename):
        proc = subprocess.Popen([filename])
        proc.wait()
        return


if __name__ == '__main__':
    # c++ for fastness !
    cpp = True

    # enter latitude and longitude for
    # the start and destination positions
    read_cordinations = True

    if not read_cordinations:
        '''
        manual entry of information
        '''

        # start node
        node1 = (35.80367469044131, 51.438760757446296)
        # destination node
        node2 = (35.801312188809185, 51.43841207027436)

        '''
        get information from user
        '''

        # node1 = tuple(map(float,
        #     input("Beginning:  ").split(',')))
        # node2 = tuple(map(float,
        #     input("Destination:  ").split(',')))

    else:
        '''
        read information from file
        '''

        node1, node2 = get_node_cords(file_webcords)


    # create router object with specific transport type
    router = Router(transport)

    if not cpp:
        # find path and display path on map
        router.find_path(node1, node2)

    else:
        router.cpp_find_path(
            node1,
            node2,
            file_pathfinding,
            file_cords,
            file_path
            )
