import os
import xml.etree.ElementTree as etree
import json
import math
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

inf = float('inf')

class Map:
    def __init__(self, transport,
        filename='./maps/map.osm', read=False):

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
        self.car_access = ('motorway','trunk',
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
            'primary':  9,
            'secondary': 9.5,
            'tertiary': 10,
            'unclassified': 10,
            'minor': 10,
            'residential': 10.3,
            'track': 10,
            'service': 10,
        }

        # data filename
        self.filename = filename
        if not read:
            self.get_graph(self.filename)

    def get_weight(self, wayType):
        try:
            return self.weights[wayType]
        except KeyError:
            # if no weighting is defined,
            # then assume it can't be routed
            return 0

    def get_element_attributes(self, element):
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
        result = {}
        for child in element:
            if child.tag == "tag":
                key = child.attrib["k"]
                value = child.attrib["v"]
                result[key] = value
        return result

    def get_data(self, elem):
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

    def add_way(self, wayID, tags, nodes):

        # Calculate what vehicles
        # can use this route (car)

        highway = self.equivalent(
            tags.get('highway', ''))

        # road is two way or one way
        oneway = tags.get('oneway', '')
        twoway = not oneway in ('yes','true','1')

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
        """Add a edge to the graph"""
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
            "primary_link":"primary",
            "trunk":"primary",
            "trunk_link":"primary",
            "secondary_link":"secondary",
            "tertiary":"secondary",
            "tertiary_link":"secondary",
            "residential":"unclassified",
            "minor":"unclassified",
            "steps":"footway",
            "driveway":"service",
            "pedestrian":"footway",
            "bridleway":"cycleway",
            "track":"cycleway",
            "arcade":"footway",
            "canal":"river",
            "riverbank":"river",
            "lake":"river",
            "light_rail":"railway"
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
            print('No node found !')

        return nearest_node

    def write(self, filename=None):
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

        if filename is None:
            filename = "map_graph.json"
            index = 1
            while os.path.exists(filename):
                filename = "map_graph{}.json"
                filename = filename.format(index)
                index += 1

        # else:
        #     # check if file with given filename exists
        #     if not (os.path.exists(filename)):
        #         error = "\nNo such file with name: \n"
        #         print(error + filename)
        #         return

        self.write_data = {
            "node_cords": self.node_cords,
            "graph": self.graph
        }

        with open(filename, 'w')as file:
            json.dump(self.write_data, file)

        print('writing done !')

    def read(self, filename):
        ''' create a graph from data (json file) '''

        # check file such name exists
        if not (os.path.exists(filename)):
            print("No such data file %s" % filename)

        # open file (json) end read graph data
        with open(filename, 'r') as file:
            data = json.load(file)

        # create graph
        self.graph = data['graph']
        self.node_cords = data['node_cords']

        print('reading done !')

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
            dist = self.geocode_to_kilometers(des_pos,
                self.node_cords[node])

            self.distances[node] = dist

    def geocode_to_kilometers(self, node1, node2):
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
        # 0 = oneway to node
        # 1 = oneway from node
        # 2 = two way

        if node1 in self.conns:
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
                self.conns[node1][node2] = \
                    [1, self.graph[node1][node2]]
                if node2 in self.conns:
                    self.conns[node2][node1] = [0, None]

                else:
                    self.conns[node2] = {
                        node1: [0, None]
                    }


        else:
            self.conns[node1] = {
                    node2: [1, self.graph[node1][node2]]
            }
            if node2 in self.conns:
                self.conns[node2][node1] = [0, None]

            else:
                self.conns[node2] = {
                    node1: [0, None]
                }


    def clean_graph(self):
        # 0 = oneway to node
        # 1 = oneway from node
        # 2 = two way

        # connections
        self.conns = {}
        for node in self.graph:
            for neighbour in self.graph[node]:
                self.update_conn(node, neighbour)

        count = 0
        for node in self.conns:
            if len(self.conns[node]) == 2:
                node1, node2 = self.conns[node].keys()
                count += 1
        # print(self.conns, count)



''' Parse an OSM file '''
if __name__ == "__main__":

    # filename = 'map.osm'

    # data = Map("car", filename)
    # print('loading osm file done !')

    # # write into json file for easy reading
    # data.write("map_graph1.json")
    # print("done !")

    filename = 'map_graph.json'

    data = Map("car", filename, read=True)

    # read into json file for easy reading
    data.read("map_graph.json")
    # start node count tehran  481243 could clean 267986
    print("node count: ", len(data.graph))
    data.clean_graph()
    # print("done !")
