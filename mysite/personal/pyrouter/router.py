from .map import Map
import os
from subprocess import Popen, PIPE

# infinity for routing
inf = float('inf')

# file directories
file_map = "maps/map_graph.json"
file_map = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_map))
file_pathfinding = "find_path.out"
file_pathfinding = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_pathfinding))
file_webcords = "cords.txt"
file_webcords = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_webcords))
file_cords = "nodes.txt"
file_cords = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_cords))
file_path = "path.txt"
file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_path))

cpp_graph_data = "graph_data.txt"
cpp_graph_data = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_graph_data))
cpp_nodes = "nodes.txt"
cpp_nodes = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_nodes))
cpp_path = "path.txt"
cpp_path = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_path))

transport = "car"


class Router:
    def __init__(self, transport):
        self.transport = transport
        # self.map = Map("car")
        self.map = Map("car", read=True)
        self.map.read(file_map)

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

        cord_path = []
        for i in path:
            node = self.map.node_cords[i]
            cord_path.append(node)

        return cord_path

    def write_node_cords(self, node1, node2, filename):
        # find the closests node to the
        # given latitude and longitude
        self.map.get_distances(node2)
        node1 = self.map.find_node(*node1)
        node2 = self.map.find_node(*node2)
        print("\n\n\n\node1:", node1, "  node2:", node2)
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
        # print(filename)
        # proc = subprocess.Popen([filename])
        # proc.wait()

        p = Popen([filename], shell=True, stdout=PIPE, stdin=PIPE)
        value = cpp_graph_data + '\n'
        value = bytes(value, 'UTF-8')  # Needed in Python 3.
        p.stdin.write(value)
        p.stdin.flush()

        value = cpp_nodes + '\n'
        value = bytes(value, 'UTF-8')
        p.stdin.write(value)
        p.stdin.flush()

        value = cpp_path + '\n'
        value = bytes(value, 'UTF-8')
        p.stdin.write(value)
        p.stdin.flush()

        p.wait()

        return


if __name__ == '__main__':
    # create router object with specific transport type
    router = Router(transport)

    router.cpp_find_path(
        node1,
        node2,
        file_pathfinding,
        file_cords,
        file_path
        )
