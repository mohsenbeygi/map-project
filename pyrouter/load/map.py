import os
import re
import xml.etree.ElementTree as etree
from datetime import datetime
from load.weights import RoutingWeights
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

        # weights of different roads
        self.weights = RoutingWeights()

        # road types a car can travel in
        self.car_access = ('motorway','trunk',
                            'primary', 'secondary',
                            'tertiary',
                            'unclassified', 'minor',
                            'residential', 'service')
        # data filename
        self.filename = filename
        if not read:
            self.get_graph(self.filename)

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
        remove nodes that other nodes
        are connected to but we don't have
        any data from them (we don't know
        what nodes there connected to)
        because they cause errors in routing
        '''

        self.new_graph = {}

        for node in self.graph:
            neighbours = {}
            for neighbour in self.graph[node]:
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
                    weight = self.weights.get(highway)

                    # create connection in graph
                    self.addLink(last[0],
                                 node_id, weight)

                    # add node cords (mostly
                    # for displaying in routing)
                    self.add_node_cords(last)

                    # add the opposite direction
                    # if road isn't oneway
                    if twoway:
                        self.addLink(node_id,
                                     last[0],
                                     weight)
                        self.add_node_cords(node)

                last = node

    def add_node_cords(self, node):
        self.node_cords[node[0]] = [node[1], node[2]]

    def addLink(self, fr, to, weight=1):
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

    def findNode(self, lat, lon):
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

        else:
            # check if file with given filename exists
            if not (os.path.exists(filename)):
                error = "\nNo such file with name: \n"
                print(error + filename)
                return

        self.write_data = {}
        for node in self.graph:
            neighbours = {}
            for neighbour in self.graph[node]:
                neighbours[neighbour] = \
                    self.graph[node][neighbour]

            self.write_data[node] = neighbours
            self.write_data[node]['lat'] = \
                self.node_cords[node][0]
            self.write_data[node]['lon'] = \
                self.node_cords[node][1]

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
        self.graph = {}
        self.node_cords = {}

        for node in data:
            self.graph[node] = {}

            # get neighbours of each node
            # (and) weight between them
            for neighbour in data[node]:
                if neighbour != 'lat':
                    if neighbour != 'lon':
                        self.graph[node][neighbour] = \
                            data[node][neighbour]

            # save node cordinates
            self.node_cords[node] = [data[node]['lat'],
                                     data[node]['lon']]

        print('reading done !')

    def get_distances(self, des_pos):
        '''
        find the distance of every node
        from a particular node (destination)
        '''

        self.distances = {}

        # find destination node in graph
        des = self.findNode(*des_pos)
        des_pos = self.node_cords[des]

        for node in self.node_cords:
            # find distance in kilometers
            dist = self.get_distance(des_pos,
                self.node_cords[node])

            self.distances[node] = dist

    def get_distance(self, node1, node2):
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


''' Parse an OSM file '''
if __name__ == "__main__":

    filename = 'map.osm'

    data = Map("car", filename)
    print('loading osm file done !')

    # wirte into json file for easy reading
    data.write("map_graph1.json")
    print("done !")
