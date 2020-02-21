import os
import xml.etree.ElementTree as etree
import json
import math
import mplleaflet
import matplotlib.pyplot as plt
# import sys
# sys.path.insert(0,'.')


'''
graph stucture (eventually for routing)

type(graph) = <class 'dict'>


graph = {

    node1: {

        neightbour1: weight to neightbour1 from node1
        neightbour2: weight to neightbour2 from node1
        neightbour3: weight to neightbour3 from node1

                       .
                       .
                       .

    }

    node2: {

        neightbour1: weight to neightbour1 from node2
        neightbour2: weight to neightbour2 from node2
        neightbour3: weight to neightbour3 from node2

                       .
                       .
                       .

    }

    .
    .
    .

}

'''


# infinity for find_node function
inf = float('inf')


class Map:
    def __init__(self, transport,
        filename="maps/map.osm", read=False):

        # distance of a node to
        # all other nodes (destination)
        self.distances = {}

        # graph
        self.graph = {}

        # node cordinates
        self.node_cords = {}

        # transprot type
        self.transport = transport

        # road types a car can travel in
        self.car_access = ('motorway', 'trunk',
                           'primary', 'secondary',
                           'tertiary',
                           'unclassified', 'minor',
                           'residential', 'service')

        # weights for different types
        # of roads (considering
        # thickness, road quality,
        # manuever, maneuverability, etc)
        self.weights = {
            'motorway': 1,
            'trunk': 1,
            'primary':  8.5,
            'secondary': 8.5,
            'tertiary': 9,
            'unclassified': 9,
            'minor': 9,
            'residential': 9.5,
            'track': 9,
            'service': 9,
        }

        # data filename
        self.filename = filename
        if not read:
            self.get_graph(self.filename)

    def get_weight(self, way_type):
        try:
            return self.weights[way_type]
        except KeyError:
            # if no weighting is defined,
            # then assume it can't be routed
            return 0

    def get_element_attributes(self, element):
        # xml stuff (lat lon and node name from here)
        result = {}
        for key, value in element.attrib.items():
            if key == "id":
                value = int(value)
            elif key == "lat":
                value = float(value)
            elif key == "lon":
                value = float(value)
            result[key] = value
        return result

    def get_element_tags(self, element):
        # xml stuff
        result = {}
        for child in element:
            if child.tag == "tag":
                key = child.attrib["k"]
                value = child.attrib["v"]
                result[key] = value
        return result

    def get_data(self, elem):
        # xml stuff
        data = self.get_element_attributes(elem)
        data["tag"] = self.get_element_tags(elem)
        return data

    def extract_data(self, filename):
        ''' extract needed data from a osm file
        for creating a graph '''

        nodes = {}
        ways = {}

        with open(filename, "r",
                  encoding="utf-8") as file:

            for event, elem in etree.iterparse(file):
                # element is node
                if elem.tag == "node":
                    data = self.get_data(elem)
                    nodes[data['id']] = data

                # element is way
                elif elem.tag == "way":
                    data = self.get_data(elem)
                    data["nd"] = []
                    for child in elem:
                        if child.tag == "nd":
                            data["nd"].append(int(
                                child.attrib["ref"]))
                    ways[data['id']] = data

        return nodes, ways

    def get_graph(self, filename):
        '''
        extract a graph (eventually for routing)
        from a data file (specificily .osm basicly
        xml format)
        '''

        # check if file with such a name exists
        if(not os.path.exists(filename)):
            error = "\nNo such file with name: \n"
            print(error + filename)
            return

        print("loading osm file ...")
        print("parsing osm file ...")

        # main function for opening
        # and extracting data for graph
        nodes, ways = self.extract_data(filename)

        print("parsing osm file done !")
        print("creating graph ...")

        # create a graph from extracted data
        for way_id, way_data in ways.items():

            # nodes in way
            way_nodes = []

            for nd in way_data['nd']:

                # check if node in way has
                # also been a node in data
                # (currently data is nodes)
                if nd not in nodes:
                    continue

                way_nodes.append([nodes[nd]['id'],
                                  nodes[nd]['lat'],
                                  nodes[nd]['lon']])

            # add way to graph
            self.add_way(way_id,
                         way_data['tag'],
                         way_nodes)

        '''
        remove nodes, which are neighbours
        to other nodes, but no data exists
        about them. (neighbour weights and data)
        to prevent errors in routing
        '''

        self.new_graph = {}

        for node in self.graph:
            neighbours = {}
            for neighbour in self.graph[node]:

                # check data about neighbour exists
                if neighbour in self.graph:
                    neighbours[neighbour] = \
                        self.graph[node][neighbour]

            self.new_graph[node] = neighbours

        self.graph = self.new_graph

        self.influence_distance()

        # remove nodes not needed
        self.clean_graph()

        print("creating graph done !")
        print("loading osm file done !")

    def influence_distance(self):
        for node in self.graph:
            for neighbour in self.graph[node]:
                node1 = self.node_cords[node]
                node2 = self.node_cords[neighbour]
                dis = self.geo_to_meter(node1, node2)
                self.graph[node][neighbour] *= dis * 10


    def add_way(self, wayID, tags, nodes):

        # Calculate what vehicles
        # can use this route (car)

        highway = self.equivalent(
            tags.get('highway', ''))

        # road is two way or one way
        oneway = tags.get('oneway', '')
        twoway = oneway not in ('yes', 'true', '1')

        access = {}
        access['car'] = highway in self.car_access

        if access[self.transport]:

            # Store routing information
            last = [None, None, None]

            for node in nodes:
                (node_id, x, y) = node
                if last[0]:

                    # get weight of the road
                    weight = self.get_weight(highway)

                    # create connection in graph
                    self.add_link(last[0],
                                  node_id, weight)

                    # add node cords (mostly
                    # for displaying in routing)
                    self.node_cords[last[0]] = \
                        [last[1], last[2]]

                    # add the opposite direction
                    # if road isn't oneway
                    if twoway:
                        self.add_link(node_id,
                                      last[0],
                                      weight)
                        self.node_cords[node[0]] = \
                            [node[1], node[2]]

                last = node

    def add_link(self, fr, to, weight=1):
        '''Add a edge to the graph between fr and to'''
        try:
            if to in list(self.graph[fr].keys()):
                return
            self.graph[fr][to] = weight
        except KeyError:
            self.graph[fr] = {to: weight}

    def equivalent(self, tag):
        """
        Simplifies a bunch of tags to
        nearly-equivalent ones
        """
        equivalent = {
            "primary_link": "primary",
            "trunk": "primary",
            "trunk_link": "primary",
            "secondary_link": "secondary",
            "tertiary": "secondary",
            "tertiary_link": "secondary",
            "residential": "unclassified",
            "minor": "unclassified",
            "steps": "footway",
            "driveway": "service",
            "pedestrian": "footway",
            "bridleway": "cycleway",
            "track": "cycleway",
            "arcade": "footway",
            "canal": "river",
            "riverbank": "river",
            "lake": "river",
            "light_rail": "railway"
        }

        try:
            return(equivalent[tag])

        except KeyError:
            return(tag)

    def find_node(self, lat, lon):
        """
        find the nearest node
        to a latitude and longitude
        """

        max_distance = inf
        nearest_node = None

        # ** changed node_cords to routing_graph **
        for node in self.node_cords:

            # pythagorean

            dy = self.node_cords[node][0] - lat
            dx = self.node_cords[node][1] - lon

            # not calculating square root
            # for speed improvment
            dist = dx * dx + dy * dy

            if (dist < max_distance):
                max_distance = dist
                nearest_node = node

        if nearest_node is None:
            print('No node found (function find_node, file map.py)')

        return nearest_node

    def write(self, filename=None):

        print('writing data ...')

        if filename is None:
            '''
            create a filename if no filename
            is given in the format:

            map_graph.json
            map_graph1.json
            map_graph2.json
            map_graph3.json
                    .
                    .
                    .

            choose the first filename which
            doesn't exist in directory
            '''

            filename = "map_graph.json"
            index = 1
            while os.path.exists(filename):
                filename = "map_graph{}.json"
                filename = filename.format(index)
                index += 1

        self.write_data = {
            "node_cords": self.node_cords,
            "graph": self.graph,
            # "deleted": self.deleted,
            # "routing_graph": self.routing_graph,
        }

        with open(filename, 'w') as file:
            json.dump(self.write_data, file)

        print('writing data done !')

    def read(self, filename):
        ''' create a graph from data (json file) '''

        print("reading data ...")

        # check file such name exists
        if not (os.path.exists(filename)):
            print("No such data file %s" % filename)

        # open file (json) end read graph data
        with open(filename, 'r') as file:
            data = json.load(file)

        # create graph
        self.graph = data['graph']
        # self.routing_graph = data["routing_graph"]
        self.node_cords = data['node_cords']
        # self.deleted = data['deleted']
        self.node_indexes = data['node_indexes']
        self.indexes_to_nodes = data['indexes_to_nodes']

        print('reading data done !')

    def get_distances(self, des_pos):
        '''
        find the distance of every node
        from a particular node (destination)
        '''

        self.distances = {}

        # find destination node in graph
        des = self.find_node(*des_pos)

        if des is None:
            print("\nfinding distances \
                destination not found!\n")

        des_pos = self.node_cords[des]

        for node in self.node_cords:
            # find distance in kilometers
            dist = self.geo_to_meter(des_pos,
                                     self.node_cords[node])

            self.distances[node] = dist

    def geo_to_meter(self, node1, node2):
        # get distance between two
        # nodes in kilometers

        lat1, lon1 = node1
        lat2, lon2 = node2

        # Radius of earth in KM
        earth_radius = 6378.137

        d_lat = lat2 * math.pi / 180
        d_lat += - lat1 * math.pi / 180
        d_lon = lon2 * math.pi / 180
        d_lon += - lon1 * math.pi / 180

        a1 = math.sin(d_lat / 2) * math.sin(d_lat / 2)
        a2 = math.cos(lat1 * math.pi / 180)
        a2 *= math.cos(lat2 * math.pi / 180)
        a2 *= math.sin(d_lon / 2)
        a2 *= math.sin(d_lon / 2)
        a = a1 + a2

        c = 2 * math.atan2(math.sqrt(a),
                           math.sqrt(1 - a))
        distance = earth_radius * c

        return distance

    def update_conn(self, node1, node2):
        '''
        add path:
        node1  --->  node2      case 1

        (if   node1  <---  node2  exists then
        it becomes twoway  node1  <-->  node2,     case 2)

        0 = oneway to node
        1 = oneway from node
        2 = two way
        '''

        if node1 in self.conns:
            # case 2
            if node2 in self.conns[node1]:
                if self.conns[node1][node2][0] == 0:
                    # make it twoway
                    self.conns[node1][node2][0] = 2
                    # add weight
                    self.conns[node1][node2][1] = \
                        self.graph[node1][node2]

                    # make neighbour twoway as well
                    self.conns[node2][node1][0] = 2
            else:
                # case2
                self.conns[node1][node2] = \
                    [1, self.graph[node1][node2]]
                if node2 in self.conns:
                    self.conns[node2][node1] = [0, None]

                else:
                    self.conns[node2] = {
                        node1: [0, None]
                    }


        else:
            # handling for first way connecting to node1
            self.conns[node1] = {
                    node2: [1, self.graph[node1][node2]]
            }

            # handling for first way connecting to node2
            if node2 in self.conns:
                self.conns[node2][node1] = [0, None]

            else:
                self.conns[node2] = {
                    node1: [0, None]
                }


    def clean_graph(self):
        '''
        create a graph from the graph made
        which doesn't have unnecessary
        nodes of a map, e.g. a map has multiple
        nodes for a bent road but in graph
        needed for path finding (routing)
        those nodes aren't needed.
        '''

        # 0 = oneway to node
        # 1 = oneway from node
        # 2 = two way

        self.deleted = {}
        self.conns = {}
        '''
        in the graph until know, we only know
        wether a node has a path to other
        nodes but we don't know if other
        nodes exist that have oneway paths to
        the node (i.e. you can't go from the
        node to the other node but you can come
        from the other node) so first we extract
        those data as well.
        '''
        for node in self.graph:
            for neighbour in self.graph[node]:
                self.update_conn(node, neighbour)

        '''
        to eliminate nodes not needed for
        pathfinding (routing) we remove
        nodes which have conditions such as
        node A which is shown below
        (A is only connected to two nodes,
        not considering direction)

            B --->  A  ---> C      case 1
                    or
            B <---  A  <--- C      case 2
                    or
            B <-->  A  <--> C      case 3

        (arrows indicate edge direction)
        '''

        items = list(self.conns)
        for node in items:
            if len(self.conns[node]) == 2:
                # if connected to two nodes
                node1, node2 = self.conns[node].keys()

                # if the two nodes have a path between them
                if node2 in self.conns[node1]:
                    if node1 in self.conns[node2]:
                        continue

                # case 1
                if self.conns[node][node1][0] == 0:
                    if self.conns[node][node2][0] == 1:
                        # store for graphicall route
                        # representation
                        self.deleted[node] = str(node2)

                        weight = self.conns[node1][node][1] + \
                            self.conns[node][node2][1]

                        # print(weight)

                        self.conns[node1][node2] = [1, weight]
                        self.conns[node2][node1] = [0, None]
                        del self.conns[node1][node]
                        del self.conns[node2][node]
                        del self.conns[node]
                        continue

                # case 2
                if self.conns[node][node2][0] == 0:
                    if self.conns[node][node1][0] == 1:
                        # store for graphicall route
                        # representation
                        self.deleted[node] = str(node1)

                        weight = self.conns[node2][node][1] + \
                            self.conns[node][node1][1]

                        # print(weight)

                        self.conns[node2][node1] = [1, weight]
                        self.conns[node1][node2] = [0, None]
                        del self.conns[node1][node]
                        del self.conns[node2][node]
                        del self.conns[node]
                        continue

                # case 3
                if self.conns[node][node1][0] == 2:
                    if self.conns[node][node2][0] == 2:
                        # store for graphicall route
                        # representation
                        self.deleted[node] = node1

                        weight = (self.conns[node1][node][1] + \
                            self.conns[node][node1][1] + \
                            self.conns[node][node2][1] + \
                            self.conns[node2][node][1]) / 2

                        # print(weight)

                        self.conns[node1][node2] = [2, weight]
                        self.conns[node2][node1] = [2, weight]
                        del self.conns[node1][node]
                        del self.conns[node2][node]
                        del self.conns[node]
                        continue


        # maintain previous graph structure
        self.routing_graph = {}
        for node in self.conns:
            self.routing_graph[node] = {}
            for neighbour in self.conns[node]:
                if self.conns[node][neighbour][0] != 0:
                    self.routing_graph[node][neighbour] = \
                        self.conns[node][neighbour][1]

    def find_graph_node(self, node):
        last = node
        # print(self.deleted)
        while last not in self.routing_graph:
            print(last)
            last = self.deleted[str(last)]
        return last

    def show_map(self):

        fig = plt.figure()

        for node in self.routing_graph:
            plt.plot([data.node_cords[node][1]],
                     [data.node_cords[node][0]],
                     "ro", markersize=10)
            for neighbour in self.graph[node]:
                plt.plot([data.node_cords[neighbour][1]],
                         [data.node_cords[neighbour][0]],
                         "ro", markersize=10)
                lons = [data.node_cords[node][1],
                        data.node_cords[neighbour][1]]
                lats = [data.node_cords[node][0],
                        data.node_cords[neighbour][0]]
                plt.plot(lons, lats, color="red",
                 linewidth=self.graph[node][neighbour] * 10)

        mplleaflet.show(fig=fig)


''' Parse an OSM file '''
if __name__ == "__main__":

    # filename = 'map_graph1.json'
    filename = 'highways.osm'

    # data = Map("car", filename, read=True)

    data = Map("car", filename)

    # data.read(filename)
    data.write("map_graph.json")

    # tehran nodes 481243, could clean 267986
    # final result: tehram 215321 nodes (removed 265922 nodes)!

    # example of finding a node
    node = (35.80367469044131, 51.438760757446296)
    node = data.find_node(*node)

    # node = data.find_graph_node(node)
    print("node found: ", node)
    # data.show_map()
