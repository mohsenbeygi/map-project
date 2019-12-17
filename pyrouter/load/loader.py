import os
import re
import xml.etree.ElementTree as etree
from datetime import datetime
from load.weights import RoutingWeights
import json
import math

class Loader(object):
    """Parse an OSM file looking
    for routing information"""
    def __init__(self, transport, filename='map.osm',
                 read=False):
        """Initialise an OSM-file parser"""
        self.distances = {}
        self.routing = {}
        self.rnodes = {}
        self.transport = transport
        self.weights = RoutingWeights()
        self.car_access = ('motorway','trunk',
                            'primary', 'secondary',
                            'tertiary',
                            'unclassified', 'minor',
                            'residential', 'service')
        self.filename = filename
        if not read:
            self.loadOsm(self.filename)

    def getElementAttributes(self, element):
            result = {}
            for k, v in element.attrib.items():
                if k == "id":
                        v = int(v)
                elif k == "lat":
                        v = float(v)
                elif k == "lon":
                        v = float(v)
                result[k] = v
            return result

    def getElementTags(self, element):
        result = {}
        for child in element:
            if child.tag =="tag":
                k = child.attrib["k"]
                v = child.attrib["v"]
                result[k] = v
        return result

    def get_data(self, elem):
        data = self.getElementAttributes(elem)
        data["tag"] = self.getElementTags(elem)
        return data


    def parseOsmFile(self, filename):
        result = []
        with open(filename, "r",
            encoding="utf-8") as file:
            for event, elem in etree.iterparse(file):
                if elem.tag == "node":
                    data = self.get_data(elem)
                    result.append({
                        "type": "node",
                        "data": data
                    })
                elif elem.tag == "way":
                    data = self.get_data(elem)
                    data["nd"] = []
                    for child in elem:
                        if child.tag == "nd":
                            data["nd"].append(int(
                                child.attrib["ref"]))
                    result.append({
                        "type": "way",
                        "data": data
                    })
        return result


    def loadOsm(self, filename):
        print("loading osm file ...")
        if(not os.path.exists(filename)):
            print("No such data file %s" % filename)
            return

        nodes, ways = {}, {}

        print("parsing osm file ...")
        data = self.parseOsmFile(filename)
        print("parsing osm file done!")
        # data =
        # [{type:node|way|relation,data: {}},...]
        print("extracting nodes and ways ...")
        for x in data:
            try:
                if x['type'] == 'node':
                    nodes[x['data']['id']] = x['data']
                elif x['type'] == 'way':
                    ways[x['data']['id']] = x['data']
                else:
                    continue
            except KeyError:
                # Don't care about bad
                # data (no type/data key)
                continue
        print("extracting nodes and ways done !")
        print("creating graph ...")
        #end for x in data
        for way_id, way_data in ways.items():
            way_nodes = []
            for nd in way_data['nd']:
                if nd not in nodes:
                    continue
                way_nodes.append([nodes[nd]['id'],
                                 nodes[nd]['lat'],
                                 nodes[nd]['lon']])
            self.storeWay(way_id,
                          way_data['tag'], way_nodes)
        print("creating graph done !")


    def storeWay(self, wayID, tags, nodes):
        highway = self.equivalent(
            tags.get('highway', ''))
        oneway = tags.get('oneway', '')
        reversible = not oneway in('yes','true','1')

        # Calculate what vehicles can use this route
        # TODO: just use getWeight != 0

        access = {}
        access['car'] = highway in self.car_access

        # Store routing information
        last = [None,None,None]

        for node in nodes:
            (node_id,x,y) = node
            if last[0]:
                if(access[self.transport]):
                    weight = self.weights.get(highway)
                    self.addLink(last[0],
                                 node_id, weight)
                    self.makeNodeRouteable(last)
                    if reversible:
                        self.addLink(node_id,
                                     last[0], weight)
                        self.makeNodeRouteable(node)
            last = node

    def makeNodeRouteable(self,node):
        self.rnodes[node[0]] = [node[1],node[2]]

    def addLink(self,fr,to, weight=1):
        """Add a routeable edge to the scenario"""
        try:
            if to in list(self.routing[fr].keys()):
                return
            self.routing[fr][to] = weight
        except KeyError:
            self.routing[fr] = {to: weight}

    def equivalent(self,tag):
        """Simplifies a bunch of tags to
         nearly-equivalent ones"""
        equivalent = { \
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
        """Find the nearest node that
        can be the start of a route"""
        # self.getArea(lat,lon)
        maxDist = 1E+20
        nodeFound = None
        posFound = None
        for (node_id,pos) in list(self.rnodes.items()):
            dy = pos[0] - lat
            dx = pos[1] - lon
            dist = dx * dx + dy * dy
            if(dist < maxDist):
                maxDist = dist
                nodeFound = node_id
                posFound = pos
        # print("found at %s"%str(posFound))
        return(nodeFound)

    def write(self, filename=None):
        # get filename
        if filename is None:
            filename = "map_graph.json"
            index = 1
            while os.path.exists(filename):
                filename = "map_graph{}.json"
                filename = filename.format(index)
                index += 1

        else:
            if not (os.path.exists(filename)):
                print("No such data file %s" % filename)

        self.write_data = {}
        for node in self.routing:
            self.write_data[node] = self.routing[node]
            self.write_data[node]['lat'] = \
                self.rnodes[node][0]
            self.write_data[node]['lon'] = \
                self.rnodes[node][1]

        with open(filename, 'w')as file:
            json.dump(self.write_data, file)

        print('writing done !')

    def read(self, filename):
        if not (os.path.exists(filename)):
            print("No such data file %s" % filename)
        with open(filename, 'r') as file:
            data = json.load(file)
        self.routing = {}
        self.rnodes = {}
        for node in data:
            self.routing[node] = {}
            for neighbour in data[node]:
                # print(data[node][neighbour])
                if not (neighbour in ['lat', 'lon']):
                    # print(data[node][neighbour])
                    self.routing[node][neighbour] = \
                        data[node][neighbour]
            self.rnodes[node] = [data[node]['lat'],
                                 data[node]['lon']]
        # print('reading done !')

    def get_distances(self, des_pos):

        # find distance of every node to destiantion
        des = self.findNode(*des_pos)
        des_pos = self.rnodes[des]
        for node in self.rnodes:
            dist = self.get_dis(des_pos,
                                self.rnodes[node])
            self.distances[node] = dist


    def get_dis(self, des_pos, node_pos):
        # get distance between detination
        # and a node in kilometers

        lat1, lon1 = des_pos
        lat2, lon2 = node_pos
        # Radius of earth in KM
        earth_radius = 6378.137

        d_lat = lat2 * math.pi / 180 - lat1 * math.pi / 180
        d_lon = lon2 * math.pi / 180 - lon1 * math.pi / 180

        a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + \
        math.cos(lat1 * math.pi / 180) * \
        math.cos(lat2 * math.pi / 180) * \
        math.sin(d_lon / 2) * math.sin(d_lon / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = earth_radius * c
        return d


# Parse an OSM file
if __name__ == "__main__":

    filename = 'tehran.osm'

    data = Loader("car", filename)
    print('loading osm file done !')
    data.write("map_graph.json")
    print("done !")
